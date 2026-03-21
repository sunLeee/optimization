from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from .agents import VesselAgent, TugboatAgent, BerthAgent, Position, VesselState, TugState, BerthState


@dataclass
class PortConfig:
    """항구 설정 — 실제 좌표 사용 예시 (부산항)."""
    name: str = "부산항"
    center: Position = field(default_factory=lambda: Position(35.10, 129.04))
    berth_positions: list[Position] = field(default_factory=lambda: [
        Position(35.098, 129.037),
        Position(35.101, 129.041),
        Position(35.104, 129.045),
        Position(35.096, 129.034),
        Position(35.107, 129.048),
    ])
    tug_home: Position = field(default_factory=lambda: Position(35.100, 129.039))


class PortSimulator:
    """항구 에이전트 기반 시뮬레이터.

    AnyLogic의 Simulation Model에 상당.
    """

    def __init__(
        self,
        config: PortConfig | None = None,
        seed: int = 42,
        dt_min: float = 5.0,  # 타임스텝 (분)
        delay_sigma_h: float = 0.85,
    ) -> None:
        self.config = config or PortConfig()
        self.rng = np.random.default_rng(seed)
        self.dt_h = dt_min / 60.0
        self.delay_sigma_h = delay_sigma_h
        self.current_time: float = 0.0  # hours

        self.vessels: dict[int, VesselAgent] = {}
        self.tugboats: dict[int, TugboatAgent] = {}
        self.berths: dict[int, BerthAgent] = {}

        self.event_log: list[dict] = []
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """기본 에이전트 초기화."""
        for i, pos in enumerate(self.config.berth_positions):
            self.berths[i] = BerthAgent(
                berth_id=i,
                name=f"Berth-{i+1}",
                position=pos,
            )
        for i in range(3):  # 예인선 3척
            offset_lat = self.rng.uniform(-0.002, 0.002)
            offset_lon = self.rng.uniform(-0.002, 0.002)
            home = Position(
                self.config.tug_home.lat + offset_lat,
                self.config.tug_home.lon + offset_lon,
            )
            self.tugboats[i] = TugboatAgent(
                tug_id=i,
                name=f"Tug-{i+1}",
                home_pos=home,
            )

    def add_vessel_schedule(
        self,
        vessels: list[VesselAgent],
        apply_weather_delay: bool = True,
    ) -> None:
        """선박 스케줄 추가. 날씨 지연 자동 적용."""
        for v in vessels:
            if apply_weather_delay:
                delay = float(np.clip(
                    self.rng.normal(0, self.delay_sigma_h),
                    -2.0, 2.0,
                ))
                v.eta_delay = delay
            self.vessels[v.vessel_id] = v

    def _dispatch_tug(self, vessel: VesselAgent) -> TugboatAgent | None:
        """가장 가까운 유휴 예인선 배정."""
        idle = [t for t in self.tugboats.values() if t.state == TugState.IDLE]
        if not idle:
            return None
        return min(idle, key=lambda t: t.position.distance_nm(vessel.position))

    def _find_berth(self, vessel: VesselAgent) -> BerthAgent | None:
        """가용 선석 중 가장 빨리 비는 선석 선택."""
        available = [b for b in self.berths.values() if b.can_accept(vessel)]
        return min(available, key=lambda b: b.free_at) if available else None

    def step(self) -> None:
        """타임스텝 진행."""
        t = self.current_time

        # 1. 도착 선박 처리
        for v in self.vessels.values():
            if v.state == VesselState.APPROACHING and v.eta <= t:
                v.state = VesselState.WAITING
                v.actual_arrival = t
                self._log("ARRIVAL", vessel_id=v.vessel_id, time=t)

        # 2. 대기 선박 → 선석 배정
        waiting = sorted(
            [v for v in self.vessels.values() if v.state == VesselState.WAITING],
            key=lambda v: (-v.priority, v.actual_arrival or t),
        )
        for v in waiting:
            berth = self._find_berth(v)
            tug = self._dispatch_tug(v)
            if berth and tug:
                v.state = VesselState.BERTHED
                v.assigned_berth = berth.berth_id
                v.assigned_tugs = [tug.tug_id]
                v.berth_start = t
                berth.state = BerthState.OCCUPIED
                berth.current_vessel = v.vessel_id
                berth.free_at = t + v.service_duration
                tug.state = TugState.TOWING
                tug.assigned_vessel = v.vessel_id
                fuel = tug.fuel_consumption(
                    tug.position.distance_nm(berth.position)
                )
                tug.total_fuel += fuel
                tug.position = Position(berth.position.lat, berth.position.lon)
                self._log("BERTHED", vessel_id=v.vessel_id, berth_id=berth.berth_id, time=t)

        # 3. 모든 에이전트 step
        for v in self.vessels.values():
            v.step(t)
        for tug in self.tugboats.values():
            if tug.state == TugState.TOWING:
                vessel = self.vessels.get(tug.assigned_vessel or -1)
                if vessel and vessel.state == VesselState.DEPARTING:
                    tug.state = TugState.IDLE
                    tug.assigned_vessel = None
            tug.step(t)
        for b in self.berths.values():
            b.step(t)

        self.current_time += self.dt_h

    def run(self, until_h: float = 24.0) -> None:
        """지정 시간까지 시뮬레이션 실행."""
        while self.current_time < until_h:
            self.step()

    def _log(self, event: str, **kwargs) -> None:
        self.event_log.append({'event': event, 'time': self.current_time, **kwargs})

    def get_vessel_tracks(self) -> list[dict]:
        """시각화용 선박 이동 경로 반환."""
        tracks = []
        for v in self.vessels.values():
            for h in v.history:
                tracks.append({
                    'vessel_id': v.vessel_id,
                    'name': v.name,
                    'state': h['state'],
                    'time': h['time'],
                    'lat': h['lat'],
                    'lon': h['lon'],
                })
        return tracks

    def summary(self) -> dict:
        """시뮬레이션 결과 요약."""
        completed = [v for v in self.vessels.values() if v.state.name in ('BERTHED', 'DEPARTING')]
        wait_times = [
            (v.berth_start or 0) - (v.actual_arrival or 0)
            for v in completed if v.actual_arrival is not None
        ]
        total_fuel = sum(t.total_fuel for t in self.tugboats.values())
        return {
            'completed_vessels': len(completed),
            'total_vessels': len(self.vessels),
            'avg_wait_h': float(np.mean(wait_times)) if wait_times else 0.0,
            'max_wait_h': float(np.max(wait_times)) if wait_times else 0.0,
            'total_tug_fuel': round(total_fuel, 2),
            'events': len(self.event_log),
        }
