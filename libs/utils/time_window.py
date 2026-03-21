"""
BAP → TSP-T 경계 인터페이스 데이터 계약.
BerthAllocationModel 출력 / TugScheduleModel 입력 타입.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class TimeWindowSpec:
    """BAP에서 TSP-T로 전달되는 time window 계약 타입.

    모든 시간 단위: minutes (프로젝트 전역 기준).
    BAP 결정변수 z_ibt의 함수로 생성된다.
    """
    vessel_id: str
    berth_id: str
    earliest_start: float  # e_j(z) from BAP, minutes
    latest_start: float    # l_j(z) from BAP, minutes
    service_duration: float  # minutes
    priority: int = 1      # 우선순위 가중치 (목적함수: priority × wait_hours)


@dataclass
class SchedulingToRoutingSpec:
    """TugScheduleModel → VRPTWModel 경계 인터페이스 계약.

    libs/scheduling 출력 / libs/routing 입력 타입.
    """
    vessel_id: str
    tug_id: str
    pickup_location: tuple[float, float]   # (lat, lon) degrees
    dropoff_location: tuple[float, float]  # (lat, lon) degrees
    time_window: TimeWindowSpec
    scheduled_start: float = 0.0  # MILP solve() 결과 시작 시간 (minutes)
    required_tugs: int = 1
    priority: int = 1
