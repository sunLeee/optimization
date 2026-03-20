from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
import numpy as np

class VesselState(Enum):
    APPROACHING = auto()
    WAITING = auto()
    BERTHED = auto()
    DEPARTING = auto()

class TugState(Enum):
    IDLE = auto()
    ASSIGNED = auto()
    TOWING = auto()
    RETURNING = auto()

class BerthState(Enum):
    EMPTY = auto()
    OCCUPIED = auto()

@dataclass
class Position:
    lat: float  # WGS84 위도
    lon: float  # WGS84 경도

    def distance_nm(self, other: Position) -> float:
        """두 위치 사이의 거리 (해리, Haversine)."""
        from math import radians, sin, cos, sqrt, atan2
        R = 3440.065  # 지구 반경 (해리)
        lat1, lon1 = radians(self.lat), radians(self.lon)
        lat2, lon2 = radians(other.lat), radians(other.lon)
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        return 2 * R * atan2(sqrt(a), sqrt(1-a))

class VesselAgent:
    """선박 에이전트 — AnyLogic의 Active Object 패턴."""

    def __init__(
        self,
        vessel_id: int,
        name: str,
        arrival_time: float,   # simulation time (hours)
        service_duration: float,
        priority: int = 1,
        draft_m: float = 10.0,  # 흘수 (m)
        length_m: float = 200.0,
        start_pos: Position | None = None,
    ) -> None:
        self.vessel_id = vessel_id
        self.name = name
        self.arrival_time = arrival_time
        self.service_duration = service_duration
        self.priority = priority
        self.draft_m = draft_m
        self.length_m = length_m
        self.state = VesselState.APPROACHING
        self.position = start_pos or Position(37.45, 126.60)
        self.assigned_berth: int | None = None
        self.assigned_tugs: list[int] = []
        self.actual_arrival: float | None = None
        self.berth_start: float | None = None
        self.departure_time: float | None = None
        self.eta_delay: float = 0.0  # 날씨 지연 (hours)
        self.history: list[dict] = []  # 상태 이력 (시각화용)

    @property
    def eta(self) -> float:
        return self.arrival_time + self.eta_delay

    def step(self, current_time: float) -> None:
        """시뮬레이션 한 타임스텝 진행."""
        self.history.append({
            'time': current_time,
            'state': self.state.name,
            'lat': self.position.lat,
            'lon': self.position.lon,
        })
        if self.state == VesselState.BERTHED:
            if self.berth_start and current_time >= self.berth_start + self.service_duration:
                self.state = VesselState.DEPARTING
                self.departure_time = current_time


class TugboatAgent:
    """예인선 에이전트."""

    def __init__(
        self,
        tug_id: int,
        name: str,
        home_pos: Position,
        speed_kn: float = 12.0,  # 속도 (knots)
        fuel_coeff: float = 0.5,
    ) -> None:
        self.tug_id = tug_id
        self.name = name
        self.home_pos = home_pos
        self.position = Position(home_pos.lat, home_pos.lon)
        self.speed_kn = speed_kn
        self.fuel_coeff = fuel_coeff
        self.state = TugState.IDLE
        self.assigned_vessel: int | None = None
        self.total_fuel: float = 0.0
        self.history: list[dict] = []

    def fuel_consumption(self, distance_nm: float, speed_kn: float | None = None) -> float:
        """F = α·v^2.5·d (γ=2.5, AW-006)."""
        v = speed_kn or self.speed_kn
        return self.fuel_coeff * (v ** 2.5) * distance_nm

    def step(self, current_time: float) -> None:
        self.history.append({
            'time': current_time,
            'state': self.state.name,
            'lat': self.position.lat,
            'lon': self.position.lon,
        })


class BerthAgent:
    """선석 에이전트."""

    def __init__(
        self,
        berth_id: int,
        name: str,
        position: Position,
        length_m: float = 300.0,
        depth_m: float = 15.0,
    ) -> None:
        self.berth_id = berth_id
        self.name = name
        self.position = position
        self.length_m = length_m
        self.depth_m = depth_m
        self.state = BerthState.EMPTY
        self.current_vessel: int | None = None
        self.free_at: float = 0.0
        self.history: list[dict] = []

    def can_accept(self, vessel: VesselAgent) -> bool:
        return (
            self.state == BerthState.EMPTY
            and vessel.length_m <= self.length_m
            and vessel.draft_m <= self.depth_m
        )

    def step(self, current_time: float) -> None:
        if self.state == BerthState.OCCUPIED and current_time >= self.free_at:
            self.state = BerthState.EMPTY
            self.current_vessel = None
        self.history.append({
            'time': current_time,
            'state': self.state.name,
        })
