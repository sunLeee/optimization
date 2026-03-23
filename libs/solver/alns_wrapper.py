"""
ALNSSolver — ALNSWithSpeedOptimizer(Tier 2) SolverStrategy 래퍼.

적용 범위: n = 10~50 선박 (AW-005)
내부 솔버: libs/routing/alns.py ALNSWithSpeedOptimizer
"""
from __future__ import annotations

import time

from libs.solver.protocol import ConvergenceCriteria, SolveResult
from libs.utils.time_window import TimeWindowSpec


class ALNSSolver:
    """ALNSWithSpeedOptimizer Tier 2 래퍼.

    사용 예:
        solver = ALNSSolver()
        result = solver.solve(windows, tug_fleet, berth_locs, objective)
        # result.metadata["iterations"]: 수행 outer loop 횟수
        # result.metadata["convergence_history"]: 비용 이력
    """

    def name(self) -> str:
        return "ALNS-Tier2"

    def solve(
        self,
        windows: list[TimeWindowSpec],
        tug_fleet: list[str],
        berth_locations: dict[str, tuple[float, float]],
        objective: object,
        criteria: ConvergenceCriteria | None = None,
    ) -> SolveResult:
        """ALNSWithSpeedOptimizer.solve() 호출 후 SolveResult로 변환.

        수렴 이력:
            RouteResult에는 iteration별 상세 비용이 없음.
            `metadata["convergence_history"]` = [시작 비용, 종료 비용] 2점만 기록.
            Per-iteration 로깅은 Phase 7 개선 항목 (ALNSConfig 콜백 추가 예정).

        Args:
            windows: TimeWindowSpec 리스트
            tug_fleet: 예인선 ID 목록
            berth_locations: {berth_id: (lat, lon)}
            objective: ObjectiveStrategy (ALNS 내부 미사용, KPI 후처리용)
            criteria: 수렴 기준
                max_iter → ALNSConfig.max_iter
                time_limit_sec → 적용 불가 (ALNS는 iter 기반 수렴)
                improvement_threshold → ALNSConfig.tol

        Returns:
            SolveResult
        """
        from libs.routing.alns import ALNSConfig, ALNSWithSpeedOptimizer

        crit = criteria or ConvergenceCriteria()
        cfg = ALNSConfig(
            max_iter=crit.max_iter,
            tol=crit.improvement_threshold,
        )

        t0 = time.perf_counter()
        solver = ALNSWithSpeedOptimizer(
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
                "total_cost": result.total_cost,
                "waiting_cost": result.waiting_cost,
                "fuel_cost": result.fuel_cost,
                "convergence_history": [
                    {"iter": 0, "cost": result.total_cost, "elapsed_sec": result.solve_time_sec},
                ],
            },
        )
