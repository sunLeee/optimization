"""libs/evaluation — 실데이터 백테스팅 패키지.

공개 API:
    RealDataBacktester  — CSV 로드 → ObjectiveStrategy 평가 → KPI DataFrame
    BacktestResult      — 단일 전략 백테스팅 결과

의존 방향 (AW-007):
    libs/evaluation → libs/optimization (ObjectiveStrategy, KPIResult)
    libs/evaluation → libs/utils (TimeWindowSpec, SchedulingToRoutingSpec)
"""

from libs.evaluation.backtester import (
    DEFAULT_COLUMN_MAP,
    BacktestResult,
    RealDataBacktester,
)
from libs.evaluation.robustness import RobustnessAnalyzer, RobustnessResult

__all__ = [
    "RealDataBacktester",
    "BacktestResult",
    "DEFAULT_COLUMN_MAP",
    "RobustnessAnalyzer",
    "RobustnessResult",
]
