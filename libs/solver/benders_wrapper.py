"""
BendersSolver — BendersDecomposition(Tier 3) SolverStrategy 래퍼.

적용 범위: n > 50 선박 (AW-005)
내부 솔버: libs/scheduling/benders.py BendersDecomposition
"""
from __future__ import annotations

import time

from libs.solver.protocol import ConvergenceCriteria, SolveResult
from libs.utils.time_window import TimeWindowSpec


class BendersSolver:
    """BendersDecomposition Tier 3 래퍼.

    사용 예:
        solver = BendersSolver()
        result = solver.solve(windows, tug_fleet, berth_locs, objective)
        # result.metadata["lb_history"]: lower bound 이력
        # result.metadata["ub_history"]: upper bound 이력
        # result.metadata["n_cuts"]: Benders cuts 수

    수렴 이력:
        BendersDecomposition은 매 iteration에 LB/UB를 갱신한다.
        현재 구현은 최종 LB/UB만 BendersResult에 저장.
        Per-iteration 이력은 Phase 7 개선 항목 (BendersDecomposition에 history 콜백 추가 예정).
    """

    def name(self) -> str:
        return "Benders-Tier3"

    def solve(
        self,
        windows: list[TimeWindowSpec],
        tug_fleet: list[str],
        berth_locations: dict[str, tuple[float, float]],
        objective: object,
        criteria: ConvergenceCriteria | None = None,
    ) -> SolveResult:
        """BendersDecomposition.solve() 호출 후 SolveResult로 변환.

        Args:
            windows: TimeWindowSpec 리스트
            tug_fleet: 예인선 ID 목록
            berth_locations: {berth_id: (lat, lon)}
            objective: ObjectiveStrategy (Benders 내부 미사용, KPI 후처리용)
            criteria: 수렴 기준
                time_limit_sec → BendersConfig.time_limit_sec
                max_iter → BendersConfig.max_iter
                improvement_threshold → BendersConfig.gap_tol

        Returns:
            SolveResult
        """
        from libs.scheduling.benders import BendersConfig, BendersDecomposition

        crit = criteria or ConvergenceCriteria()
        cfg = BendersConfig(
            time_limit_sec=int(crit.time_limit_sec),
            max_iter=crit.max_iter,
            gap_tol=crit.improvement_threshold,
        )

        t0 = time.perf_counter()
        solver = BendersDecomposition(
            windows=windows,
            tug_fleet=tug_fleet,
            berth_locations=berth_locations,
            cfg=cfg,
        )
        result = solver.solve()
        elapsed = time.perf_counter() - t0

        return SolveResult(
            assignments=result.assignments,
            solver_name=self.name(),
            solve_time_sec=result.solve_time_sec if result.solve_time_sec > 0 else elapsed,
            optimality_gap=result.optimality_gap,
            converged=result.converged,
            metadata={
                "iterations": result.iterations,
                "n_cuts": result.n_cuts,
                "lower_bound": result.lower_bound,
                "upper_bound": result.upper_bound,
                "total_cost": result.total_cost,
                "waiting_cost_h": result.waiting_cost_h,
                "fuel_cost_mt": result.fuel_cost_mt,
                "fallback_used": result.fallback_used,
                "lb_history": [result.lower_bound],
                "ub_history": [result.upper_bound],
            },
        )
