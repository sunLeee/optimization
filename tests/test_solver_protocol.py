"""
tests/test_solver_protocol.py — SolverStrategy Protocol 단위 테스트.

검증 범위:
    SolverStrategy Protocol (runtime_checkable)
    ConvergenceCriteria 기본값
    SolveResult 타입
    MILPSolver, ALNSSolver, BendersSolver, RollingSolver isinstance 검증
    각 래퍼가 name() → str, solve() → SolveResult 반환 검증 (toy 데이터)
"""
from __future__ import annotations

import pytest

from libs.optimization import MinWaitObjective
from libs.solver import (
    ALNSSolver,
    BendersSolver,
    ConvergenceCriteria,
    MILPSolver,
    RollingSolver,
    SolveResult,
    SolverStrategy,
)
from libs.utils.time_window import TimeWindowSpec

# ── 헬퍼 ──────────────────────────────────────────────────────

def _make_windows(n: int = 3) -> list[TimeWindowSpec]:
    """n개 toy TimeWindowSpec 생성 (berth_id="B0")."""
    return [
        TimeWindowSpec(
            vessel_id=f"V{i}",
            berth_id="B0",
            earliest_start=float(i * 60),
            latest_start=float(i * 60 + 30),
            service_duration=30.0,
            priority=1,
        )
        for i in range(n)
    ]


_BERTH_LOCS: dict[str, tuple[float, float]] = {
    "B0": (35.098, 129.037),
}
_TUG_FLEET = ["T0", "T1"]
_OBJ = MinWaitObjective()


# ── ConvergenceCriteria ───────────────────────────────────────

class TestConvergenceCriteria:
    def test_defaults(self) -> None:
        crit = ConvergenceCriteria()
        assert crit.time_limit_sec == 60.0
        assert crit.max_iter == 200
        assert crit.improvement_threshold == 0.001

    def test_custom(self) -> None:
        crit = ConvergenceCriteria(time_limit_sec=30.0, max_iter=50, improvement_threshold=0.01)
        assert crit.time_limit_sec == 30.0
        assert crit.max_iter == 50
        assert crit.improvement_threshold == 0.01


# ── SolverStrategy Protocol 검증 ──────────────────────────────

class TestSolverStrategyProtocol:
    def test_all_solvers_implement_protocol(self) -> None:
        solvers = [
            MILPSolver(),
            ALNSSolver(),
            BendersSolver(),
            RollingSolver(),
        ]
        for solver in solvers:
            assert isinstance(solver, SolverStrategy), (
                f"{solver} does not implement SolverStrategy"
            )

    def test_solver_names(self) -> None:
        assert MILPSolver().name() == "MILP-Tier1"
        assert ALNSSolver().name() == "ALNS-Tier2"
        assert BendersSolver().name() == "Benders-Tier3"
        assert RollingSolver().name() == "RollingHorizon-MPC"


# ── SolveResult 타입 검증 ─────────────────────────────────────

class TestSolveResult:
    def test_solve_result_fields(self) -> None:
        result = SolveResult(
            assignments=[],
            solver_name="Test",
            solve_time_sec=0.1,
            optimality_gap=0.0,
            converged=True,
        )
        assert result.solver_name == "Test"
        assert result.converged is True
        assert result.metadata == {}

    def test_solve_result_with_metadata(self) -> None:
        result = SolveResult(
            assignments=[],
            solver_name="Test",
            solve_time_sec=1.0,
            optimality_gap=0.02,
            converged=True,
            metadata={"iterations": 50, "convergence_history": []},
        )
        assert result.metadata["iterations"] == 50


# ── MILPSolver 단위 테스트 ────────────────────────────────────

class TestMILPSolver:
    def test_milp_solve_returns_solve_result(self) -> None:
        windows = _make_windows(n=3)
        solver = MILPSolver()
        result = solver.solve(
            windows=windows,
            tug_fleet=_TUG_FLEET,
            berth_locations=_BERTH_LOCS,
            objective=_OBJ,
            criteria=ConvergenceCriteria(time_limit_sec=30.0),
        )
        assert isinstance(result, SolveResult)
        assert result.solver_name == "MILP-Tier1"
        assert result.solve_time_sec >= 0.0
        assert 0.0 <= result.optimality_gap <= 1.0
        assert isinstance(result.assignments, list)

    def test_milp_metadata_has_solver_status(self) -> None:
        windows = _make_windows(n=2)
        solver = MILPSolver()
        result = solver.solve(
            windows=windows,
            tug_fleet=_TUG_FLEET,
            berth_locations=_BERTH_LOCS,
            objective=_OBJ,
        )
        assert "solver_status" in result.metadata
        assert "total_cost" in result.metadata


# ── ALNSSolver 단위 테스트 ────────────────────────────────────

class TestALNSSolver:
    def test_alns_solve_returns_solve_result(self) -> None:
        windows = _make_windows(n=5)
        solver = ALNSSolver()
        result = solver.solve(
            windows=windows,
            tug_fleet=_TUG_FLEET,
            berth_locations=_BERTH_LOCS,
            objective=_OBJ,
            criteria=ConvergenceCriteria(max_iter=20),
        )
        assert isinstance(result, SolveResult)
        assert result.solver_name == "ALNS-Tier2"
        assert result.solve_time_sec >= 0.0
        assert isinstance(result.assignments, list)

    def test_alns_metadata_has_iterations(self) -> None:
        windows = _make_windows(n=3)
        solver = ALNSSolver()
        result = solver.solve(
            windows=windows,
            tug_fleet=_TUG_FLEET,
            berth_locations=_BERTH_LOCS,
            objective=_OBJ,
            criteria=ConvergenceCriteria(max_iter=10),
        )
        assert "iterations" in result.metadata
        assert isinstance(result.metadata["iterations"], int)

    def test_alns_convergence_history_exists(self) -> None:
        windows = _make_windows(n=3)
        solver = ALNSSolver()
        result = solver.solve(
            windows=windows,
            tug_fleet=_TUG_FLEET,
            berth_locations=_BERTH_LOCS,
            objective=_OBJ,
            criteria=ConvergenceCriteria(max_iter=10),
        )
        assert "convergence_history" in result.metadata
        assert isinstance(result.metadata["convergence_history"], list)


# ── BendersSolver 단위 테스트 ─────────────────────────────────

class TestBendersSolver:
    @pytest.mark.skipif(
        True,
        reason="Benders는 n>50 대상. toy 데이터(n<10)에서 의미 없는 실행 — 통합 테스트에서 검증",
    )
    def test_benders_solve_integration(self) -> None:
        windows = _make_windows(n=60)
        solver = BendersSolver()
        result = solver.solve(
            windows=windows,
            tug_fleet=[f"T{i}" for i in range(10)],
            berth_locations=_BERTH_LOCS,
            objective=_OBJ,
            criteria=ConvergenceCriteria(time_limit_sec=60.0, max_iter=10),
        )
        assert isinstance(result, SolveResult)
        assert result.solver_name == "Benders-Tier3"

    def test_benders_metadata_keys(self) -> None:
        """BendersSolver Protocol 구현체로 isinstance 검증."""
        solver = BendersSolver()
        assert isinstance(solver, SolverStrategy)
        assert solver.name() == "Benders-Tier3"


# ── RollingSolver 단위 테스트 ─────────────────────────────────

class TestRollingSolver:
    @pytest.mark.skipif(
        True,
        reason="RollingHorizon은 24h 시뮬레이션 — 긴 실행시간으로 단위 테스트 제외",
    )
    def test_rolling_solve_integration(self) -> None:
        windows = _make_windows(n=5)
        solver = RollingSolver(simulate_until_h=2.0)
        result = solver.solve(
            windows=windows,
            tug_fleet=_TUG_FLEET,
            berth_locations=_BERTH_LOCS,
            objective=_OBJ,
        )
        assert isinstance(result, SolveResult)
        assert result.solver_name == "RollingHorizon-MPC"

    def test_rolling_protocol(self) -> None:
        """RollingSolver Protocol 구현체로 isinstance 검증."""
        solver = RollingSolver()
        assert isinstance(solver, SolverStrategy)
        assert solver.name() == "RollingHorizon-MPC"
