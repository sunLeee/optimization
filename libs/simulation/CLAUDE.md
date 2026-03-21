# libs/simulation/ — 에이전트 시뮬레이션 환경

## 역할

항구 내 선박·예인선·선석의 상태를 시뮬레이션. 시각화 및 검증용.
최적화 솔버와 독립적으로 동작.

## 주요 에이전트

| 클래스 | 파일 | 역할 |
|--------|------|------|
| `VesselAgent` | `agents.py` | 선박 상태 (APPROACHING→WAITING→BERTHED→DEPARTING) |
| `TugboatAgent` | `agents.py` | 예인선 상태 (IDLE→ASSIGNED→TOWING→RETURNING) |
| `BerthAgent` | `agents.py` | 선석 상태 (EMPTY→OCCUPIED) |
| `Position` | `agents.py` | WGS84 좌표 + Haversine 거리 |

## 연료 모델 (에이전트)

```python
# TugboatAgent.fuel_consumption() — AW-006 준수
v = speed_kn or self.speed_kn
return self.fuel_coeff * (v ** 2.5) * distance_nm  # γ=2.5
```

## 시뮬레이션 루프

```python
from libs.simulation.environment import PortEnvironment

env = PortEnvironment(vessels, tugs, berths)
for step in range(n_steps):
    env.step(current_time=step * dt_min)
# env.history → Gantt 차트 생성
```

## 시각화

```python
from libs.simulation.visualization import plot_gantt, plot_tug_routes
plot_gantt(assignments, time_windows)
plot_tug_routes(tug_paths, berth_positions)
```

## 확장 시 주의

- `TugboatAgent.fuel_consumption()`: γ=2.5 하드코딩 (AW-006)
- 시뮬레이션 시각화 결과는 최적화 결과 검증용으로만 사용
- 최적화 솔버(`libs/scheduling/`, `libs/routing/`)에서 이 모듈 import 금지 (AW-007)
