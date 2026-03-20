"""
TSP-T → VRPTW 경계 인터페이스 데이터 계약.
TugScheduleModel 출력 / VRPTWModel 입력 타입.

좌표계: WGS84 (lat, lon) degrees.
"""
from __future__ import annotations

from .time_window import TimeWindowSpec, SchedulingToRoutingSpec

__all__ = ["TimeWindowSpec", "SchedulingToRoutingSpec"]
