"""
RollingSolver — RollingHorizonOrchestrator(MPC) SolverStrategy 래퍼.

적용 범위: 실시간 dispatch (24h 시뮬레이션, Tier 자동 선택)
내부 솔버: libs/stochastic/rolling_horizon.py RollingHorizonOrchestrator
"""
from __future__ import annotations

import time

from libs.solver.protocol import ConvergenceCriteria, SolveResult
from libs.utils.time_window import TimeWindowSpec


class RollingSolver:
    """RollingHorizonOrchestrator MPC 래퍼.

    특징:
        - Tier 자동 선택 (n<10→MILP, n<50→ALNS, n≥50→Benders)
        - 매 dt_h마다 재최적화 (MPC 원칙)
        - 전체 시뮬레이션 배정 결과를 단일 assignments 리스트로 통합

    사용 예:
        solver = RollingSolver(simulate_until_h=24.0)
        result = solver.solve(windows, tug_fleet, berth_locs, objective)
        # result.metadata["steps"]: 재최적화 타임스텝 수
    """

    def __init__(self, simulate_until_h: float = 24.0) -> None:
        self._simulate_until_h = simulate_until_h

    def name(self) -> str:
        return "RollingHorizon-MPC"

    def solve(
        self,
        windows: list[TimeWindowSpec],
        tug_fleet: list[str],
        berth_locations: dict[str, tuple[float, float]],
        objective: object,
        criteria: ConvergenceCriteria | None = None,
    ) -> SolveResult:
        """RollingHorizonOrchestrator.run() 호출 후 SolveResult로 변환.

        Args:
            windows: TimeWindowSpec 리스트 (전체 계획 지평선)
            tug_fleet: 예인선 ID 목록
            berth_locations: {berth_id: (lat, lon)}
            objective: ObjectiveStrategy (MPC 내부 미사용, KPI 후처리용)
            criteria: 수렴 기준
                time_limit_sec → 각 타임스텝 내부 솔버에 전달 (현재 RollingHorizonConfig 미매핑)

        Returns:
            SolveResult
                optimality_gap=0.0 (MPC는 gap 미보고)
                converged=True (시뮬레이션 완료 = 수렴)
        """
        from libs.stochastic.rolling_horizon import (
            RollingHorizonConfig,
            RollingHorizonOrchestrator,
        )

        _ = criteria  # ConvergenceCriteria는 현재 RollingHorizonConfig에 미매핑
        cfg = RollingHorizonConfig(
            max_steps=int(self._simulate_until_h / 0.5),  # dt_h=0.5 기본
        )

        t0 = time.perf_counter()
        orchestrator = RollingHorizonOrchestrator(
            windows=windows,
            tug_fleet=tug_fleet,
            berth_locations=berth_locations,
            cfg=cfg,
        )
        result = orchestrator.run(simulate_until_h=self._simulate_until_h)
        elapsed = time.perf_counter() - t0

        return SolveResult(
            assignments=result.total_assignments,
            solver_name=self.name(),
            solve_time_sec=result.elapsed_sec if result.elapsed_sec > 0 else elapsed,
            optimality_gap=0.0,
            converged=True,
            metadata={
                "steps": result.steps,
                "total_cost": result.total_cost,
                "total_waiting_cost": result.total_waiting_cost,
                "total_fuel_cost": result.total_fuel_cost,
                "simulate_until_h": self._simulate_until_h,
            },
        )
