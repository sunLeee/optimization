# libs/utils/ — 공통 유틸리티

## 역할

모든 모듈이 의존하는 공통 타입, 상수, 지리 계산을 제공.
의존성 없음 (최하위 계층).

## 공개 API

| 파일 | 심볼 | 설명 |
|------|------|------|
| `constants.py` | `DEPOT: str = "__depot__"` | 예인선 depot 노드 ID |
| `geo.py` | `haversine_nm(pos1, pos2) → float` | 두 좌표 사이 거리 (해리) |
| `time_window.py` | `TimeWindowSpec` | BAP→TSP-T 인터페이스 계약 |
| `time_window.py` | `SchedulingToRoutingSpec` | TSP-T→VRPTW 인터페이스 계약 |
| `result_protocol.py` | `OptResult` | Tier 간 통일 결과 Protocol |

## 인터페이스 계약 ([I1])

```python
# BAP 출력 → TSP-T 입력
TimeWindowSpec(
    vessel_id="V0",
    berth_id="B0",
    earliest_start=60.0,   # minutes
    latest_start=75.0,     # minutes (접안 시작 + slack)
    service_duration=30.0, # minutes
    priority=3,
)
```

## 단위 suffix 규칙

| suffix | 단위 | 예시 |
|--------|------|------|
| `_min` | minutes | `arrival_time_min` |
| `_h` | hours | `waiting_cost_h` |
| `_kn` | knots | `speed_kn` |
| `_nm` | nautical miles | `dist_nm` |
| `_mt` | metric tons | `fuel_cost_mt` |
| `_sec` | seconds | `solve_time_sec` |
| `_m` | meters | `length_m`, `draft_m` |

## 확장 규칙

- 새 공통 함수/상수 → 이 디렉토리에 추가
- `__init__.py`에 반드시 export
- `routing/`, `scheduling/` 등에서 직접 import 가능 (AW-007 준수)
