"""
Berth Allocation Problem (BAP) MILP — Phase 2-1.

Pyomo + HiGHS 기반 이산 BAP.
BAP 결과(time_windows)는 TugScheduleModel의 직접 입력으로 사용된다 ([I1] 인터페이스).

참조:
  - Imai et al. (2001), European Journal of Operational Research: discrete BAP, GA
  - Bierwirth & Meisel (2010, 2015): BAP survey
  - mathematical_formulation.md §4, §8.4 [I1]

수식 (단위: minutes):
  결정변수:
    z[i,b] ∈ {0,1}   선박 i가 선석 b에 배정
    t[i]   ≥ 0       선박 i의 접안 시작 시각
    δ[i,j,b] ∈ {0,1} 선석 b에서 선박 i가 j보다 먼저 처리 (i<j 쌍)

  목적함수:
    min Σ_i ω_i · (t[i] + p[i] - a[i]) / 60   [hours]
    = 가중 완료시간 총합 최소화

  제약:
    [B1] Σ_b z[i,b] = 1                         각 선박 정확히 한 선석
    [B2] t[i] ≥ a[i]                             도착 이후 접안
    [B3] l[i]·z[i,b] ≤ L[b]                     선체 길이 제약
    [B4] d[i]·z[i,b] ≤ D[b]                     흘수 제약
    [B5a] t[j] ≥ t[i]+p[i] - M(1-δ[i,j,b]) - M(2-z[i,b]-z[j,b])   (순서: i→j)
    [B5b] t[i] ≥ t[j]+p[j] - M·δ[i,j,b] - M(2-z[i,b]-z[j,b])      (순서: j→i)

  Big-M = horizon_min + max(p[i])
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec

try:
    import pyomo.environ as pyo
    _HAS_PYOMO = True
except ImportError:
    _HAS_PYOMO = False


# ── 입출력 타입 ───────────────────────────────────────────────

@dataclass
class BAPInput:
    """BAP 입력 데이터.

    모든 시간 단위: minutes. 거리/크기 단위: meters.
    """
    vessel_ids: list[str]
    berth_ids: list[str]
    arrival_times_min: dict[str, float]        # {vessel_id: arrival_time_min}
    service_durations_min: dict[str, float]    # {vessel_id: processing_time_min}
    vessel_lengths_m: dict[str, float]         # {vessel_id: length_m}
    berth_lengths_m: dict[str, float]          # {berth_id: length_m}
    berth_depths_m: dict[str, float]           # {berth_id: depth_m}
    vessel_drafts_m: dict[str, float]          # {vessel_id: draft_m}
    priorities: dict[str, int]                 # {vessel_id: priority 1-5}
    berth_positions: dict[str, tuple[float, float]]  # {berth_id: (lat, lon)}
    horizon_min: float = 1440.0               # 계획 기간 (분, 기본 24h)
    tug_service_duration_min: float = 30.0    # 예인선 서비스 시간 (BAP→TSP-T [I1])
    inbound_slack_min: float = 15.0           # 입항 time window 여유 (분)


@dataclass
class BAPResult:
    """BAP 풀이 결과.

    time_windows → TugScheduleModel 직접 연결 ([I1]).
    berth_positions는 TugScheduleModel.berth_locations에 전달한다.
    """
    assignments: dict[str, str]               # {vessel_id: berth_id}
    start_times_min: dict[str, float]         # {vessel_id: start_time_min}
    time_windows: list[TimeWindowSpec]        # TSP-T 입력
    berth_positions: dict[str, tuple[float, float]]  # TugScheduleModel 전달용
    total_weighted_delay_h: float
    solver_status: str
    solve_time_sec: float
    optimality_gap: float


# ── 모델 ──────────────────────────────────────────────────────

class BerthAllocationModel:
    """Pyomo + HiGHS 기반 이산 BAP MILP.

    사용 예:
        inp = BAPInput(vessel_ids=["V0","V1"], berth_ids=["B0","B1"], ...)
        model = BerthAllocationModel(inp)
        result = model.solve()
        tug_model = TugScheduleModel(result.time_windows,
                                      tug_fleet=["T0","T1"],
                                      berth_locations=result.berth_positions)
    """

    def __init__(
        self,
        bap_input: BAPInput,
        time_limit_sec: int = 60,
        mip_gap: float = 0.05,
    ) -> None:
        if not _HAS_PYOMO:
            raise ImportError("pyomo를 설치하세요: uv add pyomo>=6.7 highspy>=1.7")
        self.inp = bap_input
        self.time_limit_sec = time_limit_sec
        self.mip_gap = mip_gap
        self._M = self._compute_big_m()

    # ── 내부 헬퍼 ──────────────────────────────────────────────

    def _compute_big_m(self) -> float:
        """Big-M = horizon + max(service_duration). tight bound."""
        return self.inp.horizon_min + max(self.inp.service_durations_min.values())

    def _build_model(self) -> Any:
        """Pyomo ConcreteModel 생성.

        제약 종류: B1(배정), B2(도착 후), B3(길이), B4(흘수), B5a/B5b(비중복)
        """
        inp = self.inp
        M = self._M
        V = inp.vessel_ids
        B = inp.berth_ids
        # i < j 쌍 (비중복 제약용)
        pairs = [(V[i], V[j]) for i in range(len(V)) for j in range(i + 1, len(V))]

        m = pyo.ConcreteModel()

        # ── 결정 변수 ──
        m.z = pyo.Var(V, B, domain=pyo.Binary)            # 배정
        m.t = pyo.Var(V, domain=pyo.NonNegativeReals)     # 접안 시작 (분)
        m.delta = pyo.Var(pairs, B, domain=pyo.Binary)    # 순서

        # ── 목적함수: 가중 완료시간 최소화 ──
        m.obj = pyo.Objective(
            expr=sum(
                inp.priorities[i] * (m.t[i] + inp.service_durations_min[i]
                                     - inp.arrival_times_min[i]) / 60.0
                for i in V
            ),
            sense=pyo.minimize,
        )

        # ── [B1] 각 선박 정확히 한 선석 ──
        def b1_assignment(m, i):
            return sum(m.z[i, b] for b in B) == 1
        m.b1 = pyo.Constraint(V, rule=b1_assignment)

        # ── [B2] 도착 이후 접안 ──
        def b2_arrival(m, i):
            return m.t[i] >= inp.arrival_times_min[i]
        m.b2 = pyo.Constraint(V, rule=b2_arrival)

        # ── [B2b] 수평선 상한 ──
        def b2b_horizon(m, i):
            return m.t[i] <= inp.horizon_min
        m.b2b = pyo.Constraint(V, rule=b2b_horizon)

        # ── [B3] 선체 길이 제약 ──
        def b3_length(m, i, b):
            return inp.vessel_lengths_m[i] * m.z[i, b] <= inp.berth_lengths_m[b]
        m.b3 = pyo.Constraint(V, B, rule=b3_length)

        # ── [B4] 흘수 제약 ──
        def b4_draft(m, i, b):
            return inp.vessel_drafts_m[i] * m.z[i, b] <= inp.berth_depths_m[b]
        m.b4 = pyo.Constraint(V, B, rule=b4_draft)

        # ── [B5a] 비중복: i가 j보다 먼저 (δ=1) ──
        def b5a_order(m, i, j, b):
            return (
                m.t[j] >= m.t[i] + inp.service_durations_min[i]
                - M * (1 - m.delta[i, j, b])
                - M * (2 - m.z[i, b] - m.z[j, b])
            )
        m.b5a = pyo.Constraint(pairs, B, rule=b5a_order)

        # ── [B5b] 비중복: j가 i보다 먼저 (δ=0) ──
        def b5b_order(m, i, j, b):
            return (
                m.t[i] >= m.t[j] + inp.service_durations_min[j]
                - M * m.delta[i, j, b]
                - M * (2 - m.z[i, b] - m.z[j, b])
            )
        m.b5b = pyo.Constraint(pairs, B, rule=b5b_order)

        return m

    def _extract_results(self, model: Any) -> BAPResult:
        """Pyomo 풀이 결과를 BAPResult로 변환."""
        inp = self.inp
        V = inp.vessel_ids
        B = inp.berth_ids

        assignments: dict[str, str] = {}
        start_times: dict[str, float] = {}

        for i in V:
            for b in B:
                if pyo.value(model.z[i, b]) > 0.5:
                    assignments[i] = b
                    start_times[i] = max(
                        inp.arrival_times_min[i],
                        pyo.value(model.t[i]),
                    )
                    break

        # [I1] BAP → TSP-T time window 변환
        time_windows = self._to_time_windows(assignments, start_times)

        total_delay_h = sum(
            inp.priorities[i]
            * max(0.0, start_times.get(i, inp.arrival_times_min[i])
                  + inp.service_durations_min[i] - inp.arrival_times_min[i])
            / 60.0
            for i in V
        )

        return BAPResult(
            assignments=assignments,
            start_times_min=start_times,
            time_windows=time_windows,
            berth_positions=inp.berth_positions,
            total_weighted_delay_h=total_delay_h,
            solver_status="",   # solve()에서 채움
            solve_time_sec=0.0,
            optimality_gap=0.0,
        )

    def _to_time_windows(
        self,
        assignments: dict[str, str],
        start_times: dict[str, float],
    ) -> list[TimeWindowSpec]:
        """BAPResult → TimeWindowSpec 리스트 변환 ([I1] 인터페이스).

        입항 예인 time window:
          earliest_start = a_i (선박 도착 시각)
          latest_start   = t_i (접안 시작 시각) + inbound_slack
        """
        inp = self.inp
        windows: list[TimeWindowSpec] = []
        for vessel_id, berth_id in assignments.items():
            t_start = start_times.get(vessel_id, inp.arrival_times_min[vessel_id])
            windows.append(TimeWindowSpec(
                vessel_id=vessel_id,
                berth_id=berth_id,
                earliest_start=inp.arrival_times_min[vessel_id],
                latest_start=t_start + inp.inbound_slack_min,
                service_duration=inp.tug_service_duration_min,
                priority=inp.priorities[vessel_id],
            ))
        return windows

    # ── 공개 API ───────────────────────────────────────────────

    def solve(self, time_limit_sec: int | None = None) -> BAPResult:
        """MILP 풀이 후 BAPResult 반환.

        Returns:
            BAPResult.time_windows → TugScheduleModel 직접 입력 가능

        Raises:
            RuntimeError: HiGHS 솔버 없음
            ValueError: 선박-선석 매칭 불가 (길이/흘수 제약 모두 실패)
        """
        t_limit = time_limit_sec or self.time_limit_sec
        t0 = time.perf_counter()

        model = self._build_model()

        solver = pyo.SolverFactory("highs")
        if not solver.available():
            raise RuntimeError(
                "HiGHS 솔버를 찾을 수 없습니다. "
                "`uv add highspy>=1.7 && uv sync`로 설치하세요."
            )

        res = solver.solve(
            model,
            tee=False,
            options={
                "time_limit": t_limit,
                "mip_rel_gap": self.mip_gap,
            },
        )

        solve_time = time.perf_counter() - t0
        status = str(res.solver.status)
        termination = str(res.solver.termination_condition)

        result = self._extract_results(model)
        result.solver_status = f"{status}/{termination}"
        result.solve_time_sec = solve_time

        # gap 계산
        try:
            ub = pyo.value(model.obj)
            lb = res.problem.lower_bound
            if ub is not None and lb is not None and abs(ub) > 1e-10:
                result.optimality_gap = abs(ub - lb) / abs(ub)
        except Exception:
            pass

        if not result.assignments:
            raise ValueError(
                "BAP 풀이 실패: 선박-선석 매칭을 찾지 못했습니다. "
                "길이/흘수 제약 또는 계획 기간(horizon_min)을 확인하세요."
            )

        return result
