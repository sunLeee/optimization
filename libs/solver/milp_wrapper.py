"""
MILPSolver — TugScheduleModel(Tier 1) SolverStrategy 래퍼.

적용 범위: n < 10 선박 (AW-005)
내부 솔버: libs/scheduling/tsp_t_milp.py TugScheduleModel (Pyomo + HiGHS)
"""
from __future__ import annotations

import time

from libs.solver.protocol import ConvergenceCriteria, SolveResult
from libs.utils.time_window import TimeWindowSpec


class MILPSolver:
    """TugScheduleModel Tier 1 MILP 래퍼.

    사용 예:
        solver = MILPSolver()
        result = solver.solve(windows, tug_fleet, berth_locs, objective)
        assert isinstance(solver, SolverStrategy)
    """

    def name(self) -> str:
        return "MILP-Tier1"

    def solve(
        self,
        windows: list[TimeWindowSpec],
        tug_fleet: list[str],
        berth_locations: dict[str, tuple[float, float]],
        objective: object,
        criteria: ConvergenceCriteria | None = None,
    ) -> SolveResult:
        """TugScheduleModel.solve() 호출 후 SolveResult로 변환.

        Args:
            windows: TimeWindowSpec 리스트
            tug_fleet: 예인선 ID 목록
            berth_locations: {berth_id: (lat, lon)}
            objective: ObjectiveStrategy (현재 MILP 내부에서 직접 미사용 — MILP는 자체 목적함수 사용)
            criteria: 수렴 기준 (time_limit_sec → HiGHS time_limit)

        Returns:
            SolveResult

        주의:
            MILP는 자체 목적함수(w1·wait + w2·fuel)를 사용한다.
            `objective` 파라미터는 KPI 후처리에 활용되며 MILP 수식에 주입되지 않는다.
            N×M 벤치마크에서 objective KPI는 SolveResult.assignments로 별도 계산한다.
        """
        from libs.scheduling.tsp_t_milp import TugScheduleModel

        crit = criteria or ConvergenceCriteria()
        t0 = time.perf_counter()

        model = TugScheduleModel(
            windows=windows,
            tug_fleet=tug_fleet,
            berth_locations=berth_locations,
            time_limit_sec=int(crit.time_limit_sec),
        )
        result = model.solve()
        elapsed = time.perf_counter() - t0

        return SolveResult(
            assignments=result.assignments,
            solver_name=self.name(),
            solve_time_sec=elapsed,
            optimality_gap=result.optimality_gap,
            converged=result.optimality_gap <= 0.05,
            metadata={
                "total_cost": result.total_cost,
                "waiting_cost": result.waiting_cost,
                "fuel_cost": result.fuel_cost,
                "solver_status": result.solver_status,
            },
        )
