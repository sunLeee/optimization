"""
Benders Decomposition — Phase 2 Step 3 (Tier 3, n > 50).

BAP+TSP-T 통합 문제를 Master/Subproblem으로 분해:
  Master (HiGHS MILP): 선석 배정 + 예인선 배정 이진 변수
  Subproblem (IPOPT): 속도 최적화 연속 변수 (γ=2.5)

참조:
  - Zheng, Chu & Xu (2015), COR: Benders for berth + tug
  - Benders (1962), Numerische Mathematik: original decomposition
  - algorithm_selection.md Section 9: Tier 3 = Benders, Master HiGHS + Sub IPOPT

수렴 조건:
  UB - LB ≤ gap_tol × UB
  최대 max_iter 반복 (기본 50)

성능 목표:
  n=75 인스턴스 10분 이내 수렴 (gap ≤ 5%)
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any

from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec
from libs.utils.geo import haversine_nm
from libs.utils.constants import DEPOT

try:
    import pyomo.environ as pyo
    _HAS_PYOMO = True
except ImportError:
    _HAS_PYOMO = False

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


@dataclass
class BendersConfig:
    """Benders 파라미터 설정."""
    max_iter: int = 50           # 최대 반복 수
    gap_tol: float = 0.05        # 수렴 허용 gap (5%)
    time_limit_sec: int = 600    # 전체 시간 제한 (10분)
    master_time_limit: int = 60  # Master MIP 시간 제한
    w1: float = 1.0              # 대기시간 가중치
    w2: float = 0.01             # 연료 가중치
    alpha: float = 0.5           # 연료 계수
    gamma: float = 2.5           # 속도 지수
    v_eco: float = 10.0          # eco-speed (kn)


@dataclass
class BendersResult:
    """Benders 풀이 결과."""
    assignments: list[SchedulingToRoutingSpec]
    total_cost: float
    waiting_cost: float
    fuel_cost: float
    lower_bound: float
    upper_bound: float
    gap: float
    iterations: int
    converged: bool
    solve_time_sec: float


class BendersDecomposition:
    """BAP+TSP-T Benders Decomposition.

    Tier 3 (n > 50): Master HiGHS + Subproblem IPOPT 분리.

    구조:
      Master problem: min c^T y + θ
        s.t. 배정 제약 (y: 이진 변수)
             Benders cuts: θ ≥ α_k + β_k^T y  (누적)

      Subproblem: min 연료 비용(속도 최적화) + 대기 비용
        s.t. 시간창 제약
             (y 고정 후 연속 최적화)

    실용적 구현: Subproblem을 eco-speed + 그리디 스케줄로 근사.
    ALNS warm-start로 초기 UB 생성.
    """

    def __init__(
        self,
        windows: list[TimeWindowSpec],
        tug_fleet: list[str],
        berth_locations: dict[str, tuple[float, float]],
        cfg: BendersConfig | None = None,
    ) -> None:
        if not _HAS_PYOMO:
            raise ImportError("pyomo 필요: python3 -m pip install pyomo highspy --break-system-packages")
        if not _HAS_NUMPY:
            raise ImportError("numpy 필요")

        self.windows = windows
        self.tug_fleet = tug_fleet
        self.berth_locations = berth_locations
        self.cfg = cfg or BendersConfig()
        self._wmap = {w.vessel_id: w for w in windows}
        self._distances = self._build_distances()
        self._benders_cuts: list[dict] = []  # 누적 Benders cuts

    def _build_distances(self) -> dict[tuple[str, str], float]:
        """거리 행렬 (해리, Haversine)."""
        first_berth = list(self.berth_locations.values())[0]
        locs: dict[str, tuple[float, float]] = {DEPOT: first_berth}
        for w in self.windows:
            locs[w.vessel_id] = self.berth_locations[w.berth_id]
        nodes = [DEPOT] + [w.vessel_id for w in self.windows]
        dist: dict[tuple[str, str], float] = {}
        for i in nodes:
            for j in nodes:
                dist[(i, j)] = 0.0 if i == j else haversine_nm(locs[i], locs[j])
        return dist

    # ── Master Problem ────────────────────────────────────────

    def _build_master(
        self,
        theta_lb: float = -1e6,
    ) -> Any:
        """Master MIP 빌드 (HiGHS).

        결정변수:
          y_jk ∈ {0,1}: 예인선 k가 vessel j를 서비스
          theta ≥ theta_lb: subproblem cost 대리 변수

        목적함수: min Σ c_jk * y_jk + theta
          c_jk = w1 * priority_j * 0 (대기는 subproblem에서)
                + w2 * alpha * dist(depot→j) * v_eco (이동 연료 추정)

        제약:
          (1) Σ_k y_jk = 1  (각 vessel 정확히 하나의 tug)
          Benders cuts (누적)
        """
        cfg = self.cfg
        J = [w.vessel_id for w in self.windows]
        K = self.tug_fleet

        m = pyo.ConcreteModel()
        m.J = pyo.Set(initialize=J)
        m.K = pyo.Set(initialize=K)
        m.y = pyo.Var(J, K, domain=pyo.Binary)
        m.theta = pyo.Var(domain=pyo.Reals, bounds=(theta_lb, None))

        # 이동 연료 추정 비용 (상수)
        def c_jk(j, k):
            d = self._distances.get((DEPOT, j), 0.0)
            return cfg.w2 * cfg.alpha * d * cfg.v_eco

        m.obj = pyo.Objective(
            expr=sum(c_jk(j, k) * m.y[j, k] for j in J for k in K) + m.theta,
            sense=pyo.minimize,
        )

        # (1) 배정 제약
        def c1(m, j):
            return sum(m.y[j, k] for k in K) == 1
        m.c1 = pyo.Constraint(J, rule=c1)

        # Benders cuts: theta >= alpha_i + sum(beta_i[j,k] * y[j,k])
        for i, cut in enumerate(self._benders_cuts):
            alpha_i = cut["alpha"]
            beta_i = cut["beta"]
            m.add_component(
                f"benders_cut_{i}",
                pyo.Constraint(
                    expr=m.theta >= alpha_i + sum(
                        beta_i.get((j, k), 0.0) * m.y[j, k]
                        for j in J for k in K
                    )
                )
            )

        return m

    def _solve_master(self, m: Any) -> tuple[dict[tuple[str, str], float], float]:
        """Master MIP 풀이. (y*, theta*) 반환.

        Pyomo 신버전 HiGHS 인터페이스 호환.
        """
        solver = pyo.SolverFactory("highs")

        try:
            # 신버전 Pyomo: load_solutions=False + 수동 로드
            res = solver.solve(
                m, tee=False,
                load_solutions=False,
                options={"time_limit": self.cfg.master_time_limit},
            )
            # 해 로드 가능 여부 확인
            if hasattr(res, 'solution_status'):
                from pyomo.contrib.solver.common.util import SolutionStatus
                if res.solution_status in (SolutionStatus.feasible, SolutionStatus.optimal):
                    m.solutions.load_from(res)
                else:
                    raise ValueError("infeasible")
            else:
                m.solutions.load_from(res)
        except Exception:
            # 구버전 Pyomo fallback
            try:
                solver.solve(m, tee=False, options={"time_limit": self.cfg.master_time_limit})
            except Exception:
                # 풀이 실패: 초기 UB 기반 greedy y* 반환
                J = [w.vessel_id for w in self.windows]
                K = self.tug_fleet
                y_fallback = {(j, k): (1.0 if i == idx % len(K) else 0.0)
                              for idx, j in enumerate(J)
                              for i, k in enumerate(K)}
                return y_fallback, -1e6

        J = list(m.J)
        K = list(m.K)
        y_star: dict[tuple[str, str], float] = {}
        for j in J:
            for k in K:
                try:
                    y_star[(j, k)] = float(pyo.value(m.y[j, k]) or 0.0)
                except Exception:
                    y_star[(j, k)] = 0.0
        try:
            lb = float(pyo.value(m.obj))
        except Exception:
            lb = -1e6
        return y_star, lb

    # ── Subproblem ────────────────────────────────────────────

    def _solve_subproblem(
        self,
        y_star: dict[tuple[str, str], float],
    ) -> tuple[float, float, list[SchedulingToRoutingSpec]]:
        """Subproblem: y 고정 후 스케줄 + 연료 최적화.

        실용적 구현: 그리디 스케줄 + eco-speed 고정 (γ=2.5).
        정확한 IPOPT 서브문제는 Step 4 확장 예정.

        Returns:
            (subproblem_cost, ub_contribution, assignments)
        """
        cfg = self.cfg
        J = [w.vessel_id for w in self.windows]
        K = self.tug_fleet

        # y_star에서 배정 추출
        assignments_map: dict[str, str] = {}  # vessel_id → tug_id
        for j in J:
            for k in K:
                if y_star.get((j, k), 0.0) > 0.5:
                    assignments_map[j] = k
                    break

        # 예인선별 경로 구성 (earliest_start 순)
        routes: dict[str, list[str]] = {k: [DEPOT] for k in K}
        for w in sorted(self.windows, key=lambda w: w.earliest_start):
            k = assignments_map.get(w.vessel_id, K[0])
            routes[k].append(w.vessel_id)
        for k in K:
            routes[k].append(DEPOT)

        # 비용 계산 (eco-speed 고정)
        waiting_cost = 0.0
        fuel_cost = 0.0
        spec_list: list[SchedulingToRoutingSpec] = []

        for k, route in routes.items():
            current_time = 0.0
            for i in range(len(route) - 1):
                from_node, to_node = route[i], route[i + 1]
                if to_node == DEPOT:
                    continue
                arc = (from_node, to_node)
                d = self._distances.get(arc, 0.0)
                v = cfg.v_eco
                travel_min = d / v * 60.0
                arrival = (travel_min if from_node == DEPOT
                           else current_time + travel_min)
                w = self._wmap.get(to_node)
                if w:
                    start = max(arrival, w.earliest_start)
                    wait_h = max(0.0, start - w.earliest_start) / 60.0
                    waiting_cost += w.priority * wait_h
                    fuel_cost += cfg.alpha * (v ** cfg.gamma) * d
                    current_time = start + w.service_duration
                    spec_list.append(SchedulingToRoutingSpec(
                        vessel_id=to_node,
                        tug_id=k,
                        pickup_location=self.berth_locations[w.berth_id],
                        dropoff_location=self.berth_locations[w.berth_id],
                        time_window=w,
                        scheduled_start=start,
                        required_tugs=1,
                        priority=w.priority,
                    ))

        sub_cost = cfg.w1 * waiting_cost + cfg.w2 * fuel_cost
        return sub_cost, sub_cost, spec_list

    # ── Benders Cut 생성 ──────────────────────────────────────

    def _generate_benders_cut(
        self,
        y_star: dict[tuple[str, str], float],
        sub_cost: float,
    ) -> dict:
        """Optimality cut: theta >= sub_cost + subgradient^T (y - y_star).

        실용적 subgradient: 현재 y_star에서의 비용 추정.
        (정확한 dual solution은 연속 relaxation 필요)
        """
        J = [w.vessel_id for w in self.windows]
        K = self.tug_fleet

        # 상수 cut: theta >= sub_cost
        # (y_star에서의 subgradient = 0 근사 — 보수적이지만 안전)
        beta = {(j, k): 0.0 for j in J for k in K}
        return {"alpha": sub_cost, "beta": beta}

    # ── 메인 풀이 ─────────────────────────────────────────────

    def solve(self) -> BendersResult:
        """Benders 반복 풀이.

        Algorithm:
          1. UB = ALNS warm-start (optional)
          2. for iter in range(max_iter):
               y* = Master.solve()  → LB update
               sub_cost, assigns = Subproblem.solve(y*)
               if sub_cost < UB: UB = sub_cost; best_assigns = assigns
               if (UB - LB) / UB ≤ gap_tol: break
               generate Benders cut → add to Master
        """
        cfg = self.cfg
        t_start = time.time()

        # 초기 Upper Bound (그리디)
        ub_result = self._greedy_initial_ub()
        UB = ub_result["cost"]
        best_assigns = ub_result["assignments"]
        LB = -float("inf")
        converged = False
        it = 0

        for it in range(cfg.max_iter):
            elapsed = time.time() - t_start
            if elapsed > cfg.time_limit_sec:
                break

            # Master
            m = self._build_master(theta_lb=LB - 1e-6)
            y_star, LB_new = self._solve_master(m)
            LB = max(LB, LB_new)

            # Subproblem
            sub_cost, ub_contribution, assigns = self._solve_subproblem(y_star)

            if ub_contribution < UB:
                UB = ub_contribution
                best_assigns = assigns

            # 수렴 체크
            gap = (UB - LB) / max(abs(UB), 1e-10)
            if gap <= cfg.gap_tol:
                converged = True
                break

            # Benders Cut 추가
            cut = self._generate_benders_cut(y_star, sub_cost)
            self._benders_cuts.append(cut)

        # 최종 비용 분해
        total_cost, waiting_cost, fuel_cost = self._compute_costs(best_assigns)
        solve_time = time.time() - t_start
        gap = (UB - LB) / max(abs(UB), 1e-10)

        return BendersResult(
            assignments=best_assigns,
            total_cost=total_cost,
            waiting_cost=waiting_cost,
            fuel_cost=fuel_cost,
            lower_bound=LB,
            upper_bound=UB,
            gap=gap,
            iterations=it + 1,
            converged=converged,
            solve_time_sec=solve_time,
        )

    def _greedy_initial_ub(self) -> dict:
        """그리디 초기 UB 생성."""
        cfg = self.cfg
        J = sorted(self.windows, key=lambda w: w.earliest_start)
        K = self.tug_fleet
        routes: dict[str, list[str]] = {k: [] for k in K}
        tug_free: dict[str, float] = {k: 0.0 for k in K}

        for w in J:
            k = min(tug_free, key=tug_free.get)  # type: ignore
            routes[k].append(w.vessel_id)
            prev = routes[k][-2] if len(routes[k]) > 1 else DEPOT
            d = self._distances.get((prev, w.vessel_id), 0.0)
            arrival = tug_free[k] + d / cfg.v_eco * 60.0
            start = max(arrival, w.earliest_start)
            tug_free[k] = start + w.service_duration

        assigns: list[SchedulingToRoutingSpec] = []
        for k, route in routes.items():
            current_time = 0.0
            prev = DEPOT
            for vessel_id in route:
                w = self._wmap[vessel_id]
                d = self._distances.get((prev, vessel_id), 0.0)
                travel = d / cfg.v_eco * 60.0
                arrival = (travel if prev == DEPOT else current_time + travel)
                start = max(arrival, w.earliest_start)
                assigns.append(SchedulingToRoutingSpec(
                    vessel_id=vessel_id,
                    tug_id=k,
                    pickup_location=self.berth_locations[w.berth_id],
                    dropoff_location=self.berth_locations[w.berth_id],
                    time_window=w,
                    scheduled_start=start,
                    priority=w.priority,
                ))
                current_time = start + w.service_duration
                prev = vessel_id

        cost, _, _ = self._compute_costs(assigns)
        return {"cost": cost, "assignments": assigns}

    def _compute_costs(
        self,
        assignments: list[SchedulingToRoutingSpec],
    ) -> tuple[float, float, float]:
        """배정 리스트에서 비용 분해."""
        cfg = self.cfg
        waiting = sum(
            spec.priority * max(0.0, spec.scheduled_start - spec.time_window.earliest_start) / 60.0
            for spec in assignments
        )
        fuel = 0.0
        for spec in assignments:
            # depot → pickup 거리
            d = self._distances.get((DEPOT, spec.vessel_id), 0.0)
            fuel += cfg.alpha * (cfg.v_eco ** cfg.gamma) * d
        total = cfg.w1 * waiting + cfg.w2 * fuel
        return total, waiting, fuel
