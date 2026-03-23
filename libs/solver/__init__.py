"""
libs/solver/ — SolverStrategy 추상화 패키지.

알고리즘을 ObjectiveStrategy처럼 교체 가능한 인터페이스로 추상화.
AW-007 의존 방향 준수: evaluation → solver → scheduling/routing/stochastic → utils

공개 API:
    SolverStrategy   — Protocol (runtime_checkable)
    SolveResult      — 표준 결과 타입
    ConvergenceCriteria — 통일된 수렴 기준
    MILPSolver       — TugScheduleModel 래퍼 (Tier 1)
    ALNSSolver       — ALNSWithSpeedOptimizer 래퍼 (Tier 2)
    BendersSolver    — BendersDecomposition 래퍼 (Tier 3)
    RollingSolver    — RollingHorizonOrchestrator 래퍼 (MPC)
"""
from __future__ import annotations

from libs.solver.alns_wrapper import ALNSSolver
from libs.solver.benders_wrapper import BendersSolver
from libs.solver.milp_wrapper import MILPSolver
from libs.solver.protocol import (
    ConvergenceCriteria,
    SolveResult,
    SolverStrategy,
)
from libs.solver.rho_wrapper import RollingSolver

__all__ = [
    "SolverStrategy",
    "SolveResult",
    "ConvergenceCriteria",
    "MILPSolver",
    "ALNSSolver",
    "BendersSolver",
    "RollingSolver",
]
