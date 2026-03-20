"""
TSP-T MILP 구현 — Phase 2 Step 1.

Pyomo + HiGHS 기반 예인선 스케줄링 문제 (Tier 1, n < 10).
목적함수: min w1·Σ(priority × wait_hours) + w2·Σ(alpha × dist_nm)

참조:
  - Rodrigues et al. (2021), EJOR: matheuristic approach for TSP-T
  - Viana et al. (2020), COR: scheduling tugboats in Brazilian port
  - phase2-strategy-v3.md, deep-interview-phase2-impl.md

수식 (단위: minutes):
  결정변수:
    x_ij_k ∈ {0,1}: 예인선 k가 job i 직후 job j 수행
    s_j_k  ≥ 0:    예인선 k의 job j 시작 시간 (minutes)
    y_j_k  ∈ {0,1}: 예인선 k가 job j를 수행
    d_j    ≥ 0:    job j의 대기 보조변수 (linearization)

  제약:
    (1) Σ_k y_j_k = 1                        각 job 정확히 하나의 예인선
    (2) Σ_i x_ij_k = y_j_k                   흐름 보존 (in)
        Σ_j x_ij_k = y_j_k                   흐름 보존 (out)
    (3a) s_j_k >= e_j * y_j_k               시간창 하한 (eta_j = earliest_start)
    (3b) s_j_k <= l_j * y_j_k + M*(1-y_j_k) 시간창 상한
    (3c) s_j_k <= M * y_j_k                 비배정 시 s=0 강제
    (3d) d_j >= Σ_k s_j_k - eta_j           대기 보조변수 하한 (linearization)
    (4)  s_j_k >= s_i_k + service_i + travel(i→j) - M*(1-x_ij_k) (순서)
    (5)  d_j >= 0                            비음수 (NonNegativeReals)
    (6)  d_j <= M * Σ_k y_j_k               서비스 안받는 job d=0 강제

  Big-M: max(l_j + d_j) - min(e_j) (데이터 기반, tight)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec

try:
    import pyomo.environ as pyo
    from pyomo.opt import SolverStatus, TerminationCondition
    _HAS_PYOMO = True
except ImportError:
    _HAS_PYOMO = False

# 더미 노드 (depot)
DEPOT = "__depot__"


@dataclass
class SolverResult:
    """TSP-T MILP 솔버 결과."""
    assignments: list[SchedulingToRoutingSpec]
    total_cost: float
    waiting_cost: float
    fuel_cost: float
    optimality_gap: float          # HiGHS 보고 gap (분율)
    solver_status: str
    solve_time_sec: float


def _haversine_nm(pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
    """두 (lat, lon) 좌표 사이 거리 (해리, Haversine)."""
    R = 3440.065  # 지구 반경 (해리)
    lat1, lon1 = math.radians(pos1[0]), math.radians(pos1[1])
    lat2, lon2 = math.radians(pos2[0]), math.radians(pos2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _compute_big_m(windows: list[TimeWindowSpec]) -> float:
    """데이터 기반 Big-M 계산.

    M = max(latest_start + service_duration) - min(earliest_start)

    toy_n5 예상값: 1080 - 60 = 1020분
    """
    return (
        max(w.latest_start + w.service_duration for w in windows)
        - min(w.earliest_start for w in windows)
    )


class TugScheduleModel:
    """Pyomo + HiGHS 기반 TSP-T MILP 모델.

    Phase 2 Step 1: 연료 선형화(F=α·d), 속도 고정.
    γ=2.5 비선형 처리는 Step 2 ALNS에서 담당.

    사용 예:
        model = TugScheduleModel(
            windows=TIME_WINDOWS,
            tug_fleet=["T0", "T1"],
            berth_locations={"B0": (35.098, 129.037), "B1": (35.101, 129.041)},
        )
        results = model.solve()
    """

    def __init__(
        self,
        windows: list[TimeWindowSpec],
        tug_fleet: list[str],
        berth_locations: dict[str, tuple[float, float]],
        w1: float = 1.0,    # 대기시간 가중치 (priority × wait_hours)
        w2: float = 0.01,   # 연료 가중치 (alpha × dist_nm)
        alpha: float = 0.5, # 연료 계수 (MT/nm, F=alpha·d 선형 모델)
        time_limit_sec: int = 60,
    ) -> None:
        if not _HAS_PYOMO:
            raise ImportError("pyomo를 설치하세요: uv add pyomo>=6.7 highspy>=1.7")

        self.windows = windows
        self.tug_fleet = tug_fleet
        self.berth_locations = berth_locations
        self.w1 = w1
        self.w2 = w2
        self.alpha = alpha
        self.time_limit_sec = time_limit_sec

        # 인덱스 준비
        self._job_ids: list[str] = [w.vessel_id for w in windows]
        self._window_map: dict[str, TimeWindowSpec] = {w.vessel_id: w for w in windows}
        self._nodes: list[str] = [DEPOT] + self._job_ids
        self._M: float = _compute_big_m(windows)

        # 거리 행렬 (해리): depot→job, job→job
        self._dist: dict[tuple[str, str], float] = self._build_distance_matrix()

    # ── 거리 행렬 ──────────────────────────────────────────────
    def _build_distance_matrix(self) -> dict[tuple[str, str], float]:
        dist: dict[tuple[str, str], float] = {}
        # depot 위치: 첫 번째 선석 위치로 대리
        first_berth = list(self.berth_locations.values())[0]

        nodes_with_pos: dict[str, tuple[float, float]] = {DEPOT: first_berth}
        for w in self.windows:
            nodes_with_pos[w.vessel_id] = self.berth_locations[w.berth_id]

        for i in self._nodes:
            for j in self._nodes:
                dist[(i, j)] = (
                    0.0 if i == j
                    else _haversine_nm(nodes_with_pos[i], nodes_with_pos[j])
                )
        return dist

    # ── 모델 빌드 ──────────────────────────────────────────────
    def _build_model(self) -> Any:
        """Pyomo ConcreteModel 생성.

        제약 8종:
        (1) 배정, (2) 흐름보존, (3a/3b/3c) 시간창,
        (3d) 대기 선형화 하한, (4) 순서, (5) 비음수, (6) 보조변수 상한
        """
        m = pyo.ConcreteModel()

        J = self._job_ids
        K = self.tug_fleet
        N = self._nodes
        M = self._M
        wmap = self._window_map
        dist = self._dist

        # ── 인덱스 집합 ──
        m.J = pyo.Set(initialize=J)
        m.K = pyo.Set(initialize=K)
        m.N = pyo.Set(initialize=N)

        # ── 결정 변수 ──
        m.x = pyo.Var(N, N, K, domain=pyo.Binary)       # arc
        m.s = pyo.Var(J, K, domain=pyo.NonNegativeReals) # 시작 시간 (minutes)
        m.y = pyo.Var(J, K, domain=pyo.Binary)           # 배정 여부
        m.d = pyo.Var(J, domain=pyo.NonNegativeReals)    # 대기 보조변수 (minutes)

        # ── 목적함수 (다목적 가중합) ──
        # eta_j = earliest_start_j (Step 1: 속도 고정, 연료 선형)
        # wait = priority × d_j / 60  (minutes → hours)
        # fuel = alpha × dist(i→j) × x_ij_k
        m.obj = pyo.Objective(
            expr=(
                self.w1 * sum(
                    wmap[j].priority * m.d[j] / 60.0
                    for j in J
                )
                + self.w2 * sum(
                    self.alpha * dist[(i, j)] * m.x[i, j, k]
                    for i in N for j in J for k in K if i != j
                )
            ),
            sense=pyo.minimize,
        )

        # ── 제약 (1): 각 job 정확히 하나의 예인선 ──
        def c1_single_tug(m, j):
            return sum(m.y[j, k] for k in K) == 1
        m.c1 = pyo.Constraint(J, rule=c1_single_tug)

        # ── 제약 (2): 흐름 보존 ──
        def c2_flow_in(m, j, k):
            return sum(m.x[i, j, k] for i in N if i != j) == m.y[j, k]
        m.c2_in = pyo.Constraint(J, K, rule=c2_flow_in)

        def c2_flow_out(m, i, k):
            if i == DEPOT:
                return pyo.Constraint.Skip
            return sum(m.x[i, j, k] for j in N if j != i) == m.y[i, k]
        m.c2_out = pyo.Constraint(N, K, rule=c2_flow_out)

        # ── 제약 (3a): 시간창 하한 ──
        def c3a_lb(m, j, k):
            # eta_j = earliest_start_j
            return m.s[j, k] >= wmap[j].earliest_start * m.y[j, k]
        m.c3a = pyo.Constraint(J, K, rule=c3a_lb)

        # ── 제약 (3b): 시간창 상한 ──
        def c3b_ub(m, j, k):
            return m.s[j, k] <= wmap[j].latest_start * m.y[j, k] + M * (1 - m.y[j, k])
        m.c3b = pyo.Constraint(J, K, rule=c3b_ub)

        # ── 제약 (3c): 비배정 시 s=0 강제 ──
        def c3c_zero(m, j, k):
            return m.s[j, k] <= M * m.y[j, k]
        m.c3c = pyo.Constraint(J, K, rule=c3c_zero)

        # ── 제약 (3d): 대기 선형화 하한 ── [Critic v3 추가]
        def c3d_wait_lb(m, j):
            # d[j] >= actual_start_j - eta_j
            # actual_start_j = sum(s[j,k] for k)  (하나의 k만 활성)
            eta_j = wmap[j].earliest_start
            return m.d[j] >= sum(m.s[j, k] for k in K) - eta_j
        m.c3d = pyo.Constraint(J, rule=c3d_wait_lb)

        # ── 제약 (4): 순서 (Big-M MTZ 변형) ──
        speed_kn = 12.0  # eco-speed (Step 1 고정, 단위: knots)
        def c4_sequence(m, i, j, k):
            if i == j or i == DEPOT:
                return pyo.Constraint.Skip
            travel_min = dist[(i, j)] / speed_kn * 60.0  # 해리/kn → hours → minutes
            return (
                m.s[j, k] >= m.s[i, k] + wmap[i].service_duration + travel_min
                - M * (1 - m.x[i, j, k])
            )
        m.c4 = pyo.Constraint(J, J, K, rule=c4_sequence)

        # ── 제약 (6): 보조변수 상한 ── [Critic v2 추가]
        def c6_aux_ub(m, j):
            return m.d[j] <= M * sum(m.y[j, k] for k in K)
        m.c6 = pyo.Constraint(J, rule=c6_aux_ub)

        return m

    # ── 풀이 ──────────────────────────────────────────────────
    def solve(self) -> SolverResult:
        """MILP 풀이 후 SchedulingToRoutingSpec 리스트 반환.

        Returns:
            SolverResult (assignments: list[SchedulingToRoutingSpec], ...)
        """
        model = self._build_model()

        solver = pyo.SolverFactory("highs")
        if not solver.available():
            raise RuntimeError(
                "HiGHS 솔버를 찾을 수 없습니다. "
                "`uv add highspy>=1.7 && uv sync`로 설치하세요."
            )

        results = solver.solve(
            model,
            tee=False,
            options={
                "time_limit": self.time_limit_sec,
                "mip_rel_gap": 0.05,  # SC-2: gap ≤ 5%
            },
        )

        status = str(results.solver.status)
        termination = str(results.solver.termination_condition)

        # gap 추출 (HiGHS 보고)
        gap = 0.0
        try:
            ub = pyo.value(model.obj)
            lb = results.problem.lower_bound
            if ub > 0 and lb is not None:
                gap = abs(ub - lb) / max(abs(ub), 1e-10)
        except Exception:
            pass

        # 배정 결과 추출
        assignments: list[SchedulingToRoutingSpec] = []
        J = self._job_ids
        K = self.tug_fleet
        wmap = self._window_map

        try:
            for j in J:
                for k in K:
                    if pyo.value(model.y[j, k]) > 0.5:
                        start_min = sum(
                            pyo.value(model.s[j, kk]) for kk in K
                        )
                        w = wmap[j]
                        spec = SchedulingToRoutingSpec(
                            vessel_id=j,
                            tug_id=k,
                            pickup_location=self.berth_locations[w.berth_id],
                            dropoff_location=self.berth_locations[w.berth_id],
                            time_window=w,
                            scheduled_start=start_min,
                            required_tugs=1,
                            priority=w.priority,
                        )
                        assignments.append(spec)
        except Exception:
            pass  # infeasible 시 빈 리스트

        # 비용 분해
        wait_h = sum(
            wmap[j].priority * max(0.0, pyo.value(model.d[j])) / 60.0
            for j in J
        )
        fuel = sum(
            self.alpha * self._dist[(i, j)] * pyo.value(model.x[i, j, k])
            for i in self._nodes for j in J for k in K if i != j
        )

        return SolverResult(
            assignments=assignments,
            total_cost=self.w1 * wait_h + self.w2 * fuel,
            waiting_cost=wait_h,
            fuel_cost=fuel,
            optimality_gap=gap,
            solver_status=f"{status}/{termination}",
            solve_time_sec=results.solver.wallclock_time or 0.0,
        )
