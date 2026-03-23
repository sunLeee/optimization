"""
Multi-Resource Tugboat Gang Scheduling MILP.

각 선박 서비스에 r_j척 예선을 동시 배정하는 Gang Scheduling 문제를
Pyomo + HiGHS로 풀어 최적 배정 및 시작 시각을 결정한다.

수식 (AW-010 기반 Gang Scheduling TSP-T 확장):
    y[j,k] ∈ {0,1}    예선 k가 서비스 j에 배정
    x[i,j,k] ∈ {0,1}  예선 k가 서비스 i를 j보다 먼저 수행
    s[j] ≥ 0           서비스 j 시작 시각 (분, 당일 기준)
    w[j] ≥ 0           대기 = max(0, s[j] - e[j])

C1: Σ_k y[j,k] = r_j
C2: e[j] ≤ s[j] ≤ l[j]
C3: x[i,j,k]+x[j,i,k] ≥ y[i,k]+y[j,k]-1
C4: x[i,j,k]+x[j,i,k] ≤ 1
C5: s[j] ≥ s[i]+d[i]+t[i→j] - M(1-x[i,j,k])
C6_ik: x[i,j,k] ≤ y[i,k]   (phantom arc 방지)
C6_jk: x[i,j,k] ≤ y[j,k]   (phantom arc 방지)
C7: w[j] ≥ s[j] - e[j]

의존 방향 (AW-007): libs/scheduling → libs/utils (역방향 금지)
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

import pyomo.environ as pyo

from libs.scheduling.multi_tug import (
    MultiTugAssignment,
    assign_multi_tug_greedy,
)
from libs.utils.time_window import TimeWindowSpec

logger = logging.getLogger(__name__)

_AW005_JOB_LIMIT = 50          # n_jobs > 이 값이면 그리디 fallback (AW-005)
_BIG_M_MAX_MIN = 3 * 1440.0   # Big-M 상한 (day-relative 보장용)
_MAX_TUGS_PER_JOB: int = 8   # 서비스당 최대 배정 예선 수 (C1_upper 상한)


@dataclass
class MultiTugResult:
    """MultiTugSchedulingModel 풀이 결과.

    Attributes:
        assignments: 배정 목록 (MultiTugAssignment per vessel)
        start_times: {vessel_id: 시작 시각(분, epoch 절대값)}
        wait_h: 비가중 선박 총 대기 (시간)
        idle_h: 예선 총 유휴 시간 (시간) — 현재 미계산, 0.0
        objective_value: 목적함수 값 (priority-weighted wait, 분)
        optimality_gap: MILP 최적성 격차 (0.0~1.0); Greedy이면 nan
        solve_time_sec: 총 풀이 시간 (초)
        solver_used: "MILP" | "Greedy"
        n_jobs: 처리한 서비스 건수
        feasible: 실행 가능 해 존재 여부
    """

    assignments: list[MultiTugAssignment]
    start_times: dict[str, float]
    wait_h: float
    idle_h: float
    objective_value: float
    optimality_gap: float
    solve_time_sec: float
    solver_used: str
    n_jobs: int
    feasible: bool


class MultiTugSchedulingModel:
    """Multi-Resource Gang Scheduling MILP.

    동시 투입이 필요한 다수 예선(r_j척)을 선박 서비스에 최적 배정한다.
    n_jobs > 50이면 AW-005에 따라 그리디 fallback을 사용한다.

    Args:
        services: 서비스 목록 (TimeWindowSpec, vessel_id별 고유)
        required_tugs_map: {vessel_id: r_j} 필요 예선 수
        tug_fleet: 예선 이름 목록
        travel_matrix: TravelTimeMatrix (get_time_min(from, to) → 분)
        berth_map: {vessel_id: (start_berth_code, end_berth_code)}
        time_limit_sec: HiGHS 시간 제한 (기본 60초)
        day_relative_epoch: 당일 기준 분 오프셋 (earliest_start에서 빼서 day-relative 변환)
    """

    def __init__(
        self,
        services: list[TimeWindowSpec],
        required_tugs_map: dict[str, int],
        tug_fleet: list[str],
        travel_matrix,
        berth_map: dict[str, tuple[str, str]],
        time_limit_sec: float = 60.0,
        day_relative_epoch: float = 0.0,
        bollard_pull: dict[str, float] | None = None,
        bp_required_map: dict[str, float] | None = None,
    ) -> None:
        self.services = services
        self.required_tugs_map = required_tugs_map
        self.tug_fleet = tug_fleet
        self.travel_matrix = travel_matrix
        self.berth_map = berth_map
        self.time_limit_sec = time_limit_sec
        self.day_relative_epoch = day_relative_epoch
        self.bollard_pull = bollard_pull or {}
        self.bp_required_map = bp_required_map or {}

    # ── 공개 API ────────────────────────────────────────────

    def solve(self) -> MultiTugResult:
        """최적 Gang Scheduling 풀이.

        n_jobs > 50이면 그리디 fallback (AW-005: 'n_jobs' 기준, total_slots 아님).

        Returns:
            MultiTugResult (solver_used 필드로 MILP/Greedy 구분)
        """
        t0 = time.time()
        n = len(self.services)

        if n > _AW005_JOB_LIMIT:
            logger.warning("n_jobs=%d > %d → 그리디 fallback (AW-005)", n, _AW005_JOB_LIMIT)
            return self._greedy_solve(time.time() - t0)

        try:
            return self._milp_solve(t0)
        except Exception as exc:
            logger.error("MILP 실패 (%s) → 그리디 fallback", exc)
            return self._greedy_solve(time.time() - t0)

    # ── 내부 구현 ────────────────────────────────────────────

    def _milp_solve(self, t0: float) -> MultiTugResult:
        """Pyomo + HiGHS MILP 풀이."""
        model = pyo.ConcreteModel()

        J = list(range(len(self.services)))
        K = list(range(len(self.tug_fleet)))

        # ── 볼라드 풀 설정 ──────────────────────────────────────
        use_bp = bool(self.bollard_pull and self.bp_required_map)
        bp_list: list[float] = (
            [self.bollard_pull.get(self.tug_fleet[k], 40.0) for k in K]
            if use_bp
            else []
        )
        bp_req: dict[int, float] = (
            {j: self.bp_required_map.get(self.services[j].vessel_id, 30.0) for j in J}
            if use_bp
            else {}
        )

        # VLCC 사전 불가능성 탐지 (max_fleet_bp = top-8 BP 합계)
        if use_bp and bp_list:
            sorted_bp = sorted(bp_list, reverse=True)
            max_fleet_bp = sum(sorted_bp[:_MAX_TUGS_PER_JOB])
            infeasible = [j for j in J if bp_req[j] > max_fleet_bp]
            if infeasible:
                logger.warning(
                    "BP 초과 서비스 %d건 (요구 최대=%.0ft, fleet 가용=%.0ft) → 그리디 fallback",
                    len(infeasible),
                    max(bp_req[j] for j in infeasible),
                    max_fleet_bp,
                )
                return self._greedy_solve(time.time() - t0)

        # 파라미터 (day-relative 분 기준)
        e: dict[int, float] = {}
        l_ub: dict[int, float] = {}
        d: dict[int, float] = {}
        r: dict[int, int] = {}
        p: dict[int, float] = {}

        for j in J:
            svc = self.services[j]
            # windows는 이미 day-relative (build_full_problem.py에서 epoch 차감 완료)
            e[j] = svc.earliest_start
            l_ub[j] = svc.latest_start
            d[j] = svc.service_duration
            r[j] = self.required_tugs_map.get(svc.vessel_id, 1)
            p[j] = float(svc.priority)

        # 예선 충분성 검증
        max_r = max(r.values())
        if max_r > len(K):
            logger.warning("서비스 최대 필요 예선(%d) > 가용 예선(%d)", max_r, len(K))

        # 이동시간 행렬 (i 종료지 → j 시작지)
        travel: dict[tuple[int, int], float] = {}
        for i in J:
            for j in J:
                if i == j:
                    continue
                _, eb_i = self.berth_map.get(self.services[i].vessel_id, ("", ""))
                sb_j, _ = self.berth_map.get(self.services[j].vessel_id, ("", ""))
                if eb_i and sb_j:
                    travel[(i, j)] = self.travel_matrix.get_time_min(eb_i, sb_j)
                else:
                    travel[(i, j)] = 0.0

        # Big-M (day-relative 기준) — Fix 4: 3×1440 이상이면 epoch 오류
        m_upper = max(l_ub[j] + d[j] for j in J)
        m_lower = min(e[j] for j in J)
        t_max = max(travel.values()) if travel else 0.0
        m_val = m_upper - m_lower + t_max

        if m_val > _BIG_M_MAX_MIN:
            raise ValueError(
                f"Big-M={m_val:.0f} > {_BIG_M_MAX_MIN:.0f}min. "
                "day_relative_epoch이 올바르게 설정되지 않았습니다 "
                "(epoch-relative 절대값이 아닌 day-relative 분을 사용해야 합니다)."
            )

        # ── 변수 ───────────────────────────────────────────
        model.y = pyo.Var(J, K, domain=pyo.Binary)
        model.x = pyo.Var(J, J, K, domain=pyo.Binary)
        model.s = pyo.Var(J, domain=pyo.NonNegativeReals)
        model.w = pyo.Var(J, domain=pyo.NonNegativeReals)

        # ── 목적함수 ────────────────────────────────────────
        model.obj = pyo.Objective(
            expr=sum(p[j] * model.w[j] for j in J),
            sense=pyo.minimize,
        )

        # ── 제약 ────────────────────────────────────────────
        # ── C1: 예선 배정 제약 ──────────────────────────────────
        if use_bp:
            # C1_bp: 볼라드 풀 하한 (견인력 충족)
            model.c1_bp = pyo.Constraint(
                J,
                rule=lambda m, j: sum(bp_list[k] * m.y[j, k] for k in K) >= bp_req[j],
            )
            # C1_upper: 최대 예선 수 상한
            model.c1_upper = pyo.Constraint(
                J,
                rule=lambda m, j: sum(m.y[j, k] for k in K) <= _MAX_TUGS_PER_JOB,
            )
            # C1_lower: 최소 1척 배정 보장 (Architect Fix 1)
            model.c1_lower = pyo.Constraint(
                J,
                rule=lambda m, j: sum(m.y[j, k] for k in K) >= 1,
            )
        else:
            # 기존 count 기반 equality fallback
            model.c1 = pyo.Constraint(
                J, rule=lambda m, j: sum(m.y[j, k] for k in K) == r[j]
            )

        # C2: 시간창
        model.c2_lo = pyo.Constraint(J, rule=lambda m, j: m.s[j] >= e[j])
        model.c2_hi = pyo.Constraint(J, rule=lambda m, j: m.s[j] <= l_ub[j])

        # C3: 순서 연결
        def _c3(m, i, j, k):
            if i == j:
                return pyo.Constraint.Skip
            return m.x[i, j, k] + m.x[j, i, k] >= m.y[i, k] + m.y[j, k] - 1

        model.c3 = pyo.Constraint(J, J, K, rule=_c3)

        # C4: 상호 배제
        def _c4(m, i, j, k):
            if i >= j:
                return pyo.Constraint.Skip
            return m.x[i, j, k] + m.x[j, i, k] <= 1

        model.c4 = pyo.Constraint(J, J, K, rule=_c4)

        # C5: 비겹침 (이동시간 포함)
        def _c5(m, i, j, k):
            if i == j:
                return pyo.Constraint.Skip
            t_ij = travel.get((i, j), 0.0)
            return m.s[j] >= m.s[i] + d[i] + t_ij - m_val * (1 - m.x[i, j, k])

        model.c5 = pyo.Constraint(J, J, K, rule=_c5)

        # C6_ik: arc-bound cut (phantom arc 방지) — Architect Fix 1
        def _c6_ik(m, i, j, k):
            if i == j:
                return pyo.Constraint.Skip
            return m.x[i, j, k] <= m.y[i, k]

        model.c6_ik = pyo.Constraint(J, J, K, rule=_c6_ik)

        # C6_jk: arc-bound cut (phantom arc 방지) — Architect Fix 1
        def _c6_jk(m, i, j, k):
            if i == j:
                return pyo.Constraint.Skip
            return m.x[i, j, k] <= m.y[j, k]

        model.c6_jk = pyo.Constraint(J, J, K, rule=_c6_jk)

        # C7: 대기 선형화
        model.c7 = pyo.Constraint(J, rule=lambda m, j: m.w[j] >= m.s[j] - e[j])

        # ── HiGHS 풀이 ──────────────────────────────────────
        solver = pyo.SolverFactory("appsi_highs")
        solver.options["time_limit"] = self.time_limit_sec
        solver.options["mip_rel_gap"] = 0.05

        res = solver.solve(model, tee=False)
        solve_time = time.time() - t0

        tc = res.solver.termination_condition
        if tc not in (
            pyo.TerminationCondition.optimal,
            pyo.TerminationCondition.feasible,
        ):
            logger.warning("MILP termination: %s → 그리디 fallback", tc)
            return self._greedy_solve(solve_time)

        # 결과 추출
        gap = float(getattr(res.solver, "relative_gap", 0.0) or 0.0)
        start_times: dict[str, float] = {}
        assignments: list[MultiTugAssignment] = []

        for j in J:
            vid = self.services[j].vessel_id
            s_val = float(pyo.value(model.s[j]))
            # s_val은 day-relative 분; greedy와 동일한 단위로 반환
            start_times[vid] = s_val
            assigned = [
                self.tug_fleet[k] for k in K if float(pyo.value(model.y[j, k])) > 0.5
            ]
            assignments.append(
                MultiTugAssignment(
                    vessel_id=vid,
                    tug_ids=assigned,
                    start_time=start_times[vid],
                    required_tugs=r[j],
                    actual_tugs=len(assigned),
                )
            )

        wait_h_raw = sum(
            max(0.0, float(pyo.value(model.s[j])) - e[j]) for j in J
        ) / 60.0

        logger.info(
            "MILP 완료: n=%d gap=%.4f wait_h=%.3f time=%.2fs",
            len(J), gap, wait_h_raw, solve_time,
        )

        return MultiTugResult(
            assignments=assignments,
            start_times=start_times,
            wait_h=wait_h_raw,
            idle_h=0.0,
            objective_value=float(pyo.value(model.obj)),
            optimality_gap=gap,
            solve_time_sec=solve_time,
            solver_used="MILP",
            n_jobs=len(J),
            feasible=True,
        )

    def _greedy_solve(self, elapsed: float) -> MultiTugResult:
        """그리디 fallback — assign_multi_tug_greedy 사용."""
        t0 = time.time()
        assignments = assign_multi_tug_greedy(
            windows=self.services,
            tug_fleet=self.tug_fleet,
            required_tugs_map=self.required_tugs_map,
        )
        solve_time = elapsed + (time.time() - t0)

        e_map = {w.vessel_id: w.earliest_start for w in self.services}
        wait_h = (
            sum(
                max(0.0, a.start_time - e_map.get(a.vessel_id, 0.0))
                for a in assignments
            )
            / 60.0
        )
        start_times = {a.vessel_id: a.start_time for a in assignments}

        return MultiTugResult(
            assignments=assignments,
            start_times=start_times,
            wait_h=wait_h,
            idle_h=0.0,
            objective_value=wait_h * 60.0,
            optimality_gap=float("nan"),
            solve_time_sec=solve_time,
            solver_used="Greedy",
            n_jobs=len(self.services),
            feasible=True,
        )
