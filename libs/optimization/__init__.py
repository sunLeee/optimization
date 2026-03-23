"""libs/optimization — 플러거블 목적함수 패키지.

공개 API:
    KPIResult           — 4대 KPI + 목적함수 값 결과 타입
    ObjectiveStrategy   — Protocol (runtime_checkable)
    MinWaitObjective    — OBJ-A: min Σ(priority × wait_h)
    MinIdleObjective    — OBJ-B: min Σ idle_h
    MinCompositeObjective — OBJ-C: min w2·idle_h + w3·priority×wait_h
    MinAllObjective     — OBJ-D: 사후집계 (idle + wait + λ·dist)

의존 방향 (AW-007):
    libs/optimization → libs/utils (time_window)
    libs/optimization → libs/fuel  (consumption) [현재 미사용, 향후 확장용]
"""

from libs.optimization.objective import (
    KPIResult,
    MinAllObjective,
    MinCompositeObjective,
    MinIdleObjective,
    MinWaitObjective,
    ObjectiveStrategy,
)

__all__ = [
    "KPIResult",
    "ObjectiveStrategy",
    "MinWaitObjective",
    "MinIdleObjective",
    "MinCompositeObjective",
    "MinAllObjective",
]
