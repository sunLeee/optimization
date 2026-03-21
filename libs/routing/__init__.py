"""
경로 최적화 모듈.
- VRPTW (Vehicle Routing Problem with Time Windows)
- ALNS (Adaptive Large Neighborhood Search)

의존: libs/utils, libs/fuel
입력 타입: list[SchedulingToRoutingSpec]
"""
from .alns import ALNSWithSpeedOptimizer, ALNSConfig, RouteResult; __all__ = ['ALNSWithSpeedOptimizer','ALNSConfig','RouteResult']
