"""
확률적 불확실성 처리 모듈 (Orchestrator).

역할: libs/scheduling과 libs/routing을 조율하는 최상위 Orchestrator.
- Rolling Horizon Optimization (RHO): 실시간 dispatch 기본
- 2-stage Stochastic Programming: 사전 계획 buffer time 결정
- ETA 분포 모델링: Log-normal 기본, 데이터 >= 200 시 KDE

의존 방향 (단방향):
libs/stochastic → libs/scheduling → libs/utils
libs/stochastic → libs/routing → libs/utils
libs/stochastic → libs/fuel → libs/utils
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PortState:
    """Rolling Horizon 재최적화 시 포트 현재 상태.

    RollingHorizonOrchestrator.step()의 입력 타입.
    """
    current_time: float  # minutes from simulation start
    vessel_positions: dict[str, tuple[float, float]] = field(default_factory=dict)
    tug_assignments: dict[str, str | None] = field(default_factory=dict)  # tug_id -> vessel_id or None
    berth_occupancies: dict[str, str | None] = field(default_factory=dict)  # berth_id -> vessel_id or None
