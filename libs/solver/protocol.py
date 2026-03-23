"""
SolverStrategy Protocol + 공통 데이터 타입.

ObjectiveStrategy(libs/optimization/objective.py)와 동등한 인터페이스 추상화.
알고리즘(MILP/ALNS/Benders/Rolling)을 교체 가능한 단위로 정의한다.

참조:
  - ADR-007: SolverStrategy 위치 결정 (libs/solver/ 신규 패키지)
  - libs/optimization/objective.py: ObjectiveStrategy Protocol 패턴 참조
  - AW-007: evaluation → solver → scheduling/routing/stochastic → utils
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec


@dataclass
class ConvergenceCriteria:
    """통일된 수렴 기준 (알고리즘별 파라미터를 단일 인터페이스로 매핑).

    Tier별 매핑:
        MILP (Tier 1): time_limit_sec → HiGHS time_limit
        ALNS (Tier 2): time_limit_sec, max_iter → ALNSConfig
        Benders (Tier 3): time_limit_sec, max_iter, improvement_threshold → BendersConfig
        Rolling Horizon: time_limit_sec → 각 타임스텝 솔버

    단위:
        time_limit_sec: 초 (seconds)
        max_iter: 반복 횟수 (iterations)
        improvement_threshold: 상대 오차 (ratio, 0.0~1.0)
    """

    time_limit_sec: float = 60.0
    max_iter: int = 200
    improvement_threshold: float = 0.001  # |Δcost|/cost < threshold → 수렴


@dataclass
class SolveResult:
    """SolverStrategy 표준 결과 타입.

    모든 래퍼가 이 타입으로 결과를 반환한다.
    기존 솔버 결과(SolverResult, RouteResult, BendersResult)를 래핑.

    metadata 관례:
        "iterations"          : int   — 수행 반복 수 (ALNS, Benders)
        "convergence_history" : list  — [{"iter": i, "cost": c, "elapsed_sec": t}, ...]
                                         현재는 solvers가 iteration별 로그를 제공하지 않아
                                         outer loop 종료 시점 비용만 기록 (Phase 7 확장 예정)
        "lb_history"          : list  — Benders lower bound 이력
        "ub_history"          : list  — Benders upper bound 이력
        "n_cuts"              : int   — Benders cuts 수
        "solver_status"       : str   — MILP solver status 문자열
        "fallback_used"       : bool  — Benders ALNS fallback 여부
        "steps"               : int   — Rolling Horizon 타임스텝 수
    """

    assignments: list[SchedulingToRoutingSpec]
    solver_name: str
    solve_time_sec: float
    optimality_gap: float       # 0.0~1.0 (ALNS 휴리스틱은 0.0)
    converged: bool
    metadata: dict = field(default_factory=dict)


@runtime_checkable
class SolverStrategy(Protocol):
    """알고리즘 Strategy Protocol (ADR-007).

    ObjectiveStrategy와 동등한 플러거블 인터페이스.
    구현 의무:
        solve(windows, tug_fleet, berth_locations, objective, criteria) -> SolveResult
        name() -> str

    런타임 검증:
        isinstance(solver, SolverStrategy)  # @runtime_checkable

    사용 예:
        from libs.solver import MILPSolver, ALNSSolver, SolverStrategy
        solver: SolverStrategy = MILPSolver()
        result = solver.solve(windows, tug_fleet, berth_locs, objective)
    """

    def solve(
        self,
        windows: list[TimeWindowSpec],
        tug_fleet: list[str],
        berth_locations: dict[str, tuple[float, float]],
        objective: object,  # ObjectiveStrategy (순환 import 방지)
        criteria: ConvergenceCriteria | None = None,
    ) -> SolveResult:
        """알고리즘 실행.

        Args:
            windows: TimeWindowSpec 리스트 (BAP 출력)
            tug_fleet: 예인선 ID 목록
            berth_locations: {berth_id: (lat, lon)} 좌표
            objective: ObjectiveStrategy 구현체 (KPI 계산용)
            criteria: 수렴 기준. None이면 ConvergenceCriteria() 기본값

        Returns:
            SolveResult (assignments, solver_name, solve_time_sec, ...)
        """
        ...

    def name(self) -> str:
        """알고리즘 식별자 (예: 'MILP-Tier1', 'ALNS-Tier2')."""
        ...
