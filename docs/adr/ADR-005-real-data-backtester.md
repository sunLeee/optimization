# ADR-005: RealDataBacktester 위치 + CSV column_map 설계

**날짜**: 2026-03-22
**상태**: Accepted
**작성자**: harbor-real-data-opt ralplan 합의

---

## Decision

`libs/evaluation/` 신규 패키지에 `RealDataBacktester`를 배치하고, CSV 컬럼 매핑을 `column_map: dict[str, str]` 파라미터로 처리한다.

```python
# libs/evaluation/backtester.py

class RealDataBacktester:
    def __init__(
        self,
        csv_path: str,
        tug_fleet: list[str],
        berth_locations: dict[str, tuple[float, float]],
        column_map: dict[str, str] | None = None,
    ) -> None:
        """
        Args:
            csv_path: 실데이터 CSV 경로 (2024-06_SchData.csv)
            tug_fleet: 예인선 ID 목록
            berth_locations: {berth_id: (lat, lon)}
            column_map: CSV 컬럼명 → 표준 컬럼명 매핑.
                None이면 DEFAULT_COLUMN_MAP 사용.
                DEFAULT_COLUMN_MAP은 Step 3 CSV 확인 후 확정.
        """
        ...

    def run_all(
        self, strategies: list[ObjectiveStrategy]
    ) -> list[BacktestResult]: ...

    def to_dataframe(
        self, results: list[BacktestResult]
    ) -> pd.DataFrame: ...
```

---

## Drivers

1. **한국어 컬럼명 처리**: `2024-06_SchData.csv`는 `기준예선`, `배정예선`, `실제 스케줄 시작 시각` 등 한국어 혼합 컬럼 포함 — 하드코딩 대신 column_map으로 처리
2. **단일 책임 원칙**: 평가(Evaluation) 로직을 `libs/stochastic/`에 혼입하면 SRP 위반
3. **솔버 교체 시 재사용성**: 백테스터가 `libs/optimization/` Protocol만 알면 솔버 구현 무관하게 재사용 가능
4. **K>1 확장 대비**: 추후 K>1 시나리오 평가 확장 시 이 패키지 활용 가능

---

## CSV → TimeWindowSpec 변환 파이프라인

```
CSV (한국어 컬럼)
  │ column_map 적용
  ▼
표준 컬럼명 (vessel_id, start_time, end_time, priority, ...)
  │ datetime 파싱 → float (minutes from midnight)
  ▼
TimeWindowSpec(vessel_id, earliest_start, latest_start, service_duration, priority)
  │
  ▼
ObjectiveStrategy.compute(assignments, windows) → KPIResult
```

**Step 3에서 확인할 실제 컬럼 목록 (예상)**:

| 표준 컬럼명 | 예상 실제 컬럼명 | 비고 |
|------------|----------------|------|
| `vessel_id` | `기준예선` or vessel MMSI | 확인 필요 |
| `start_time` | `실제 스케줄 시작 시각` | KST → UTC 변환 |
| `end_time` | `실제 스케줄 종료 시각` | KST → UTC 변환 |
| `berth_id` | 선석 관련 컬럼 | 확인 필요 |
| `priority` | 없을 경우 1.0 기본값 | 확인 필요 |

**DEFAULT_COLUMN_MAP**: Step 3 실행 후 확정. 위 표 업데이트 예정.

---

## Alternatives

### Option A — `libs/stochastic/backtester.py` (거부)

**거부 이유**:
- 백테스터는 오케스트레이터(stochastic) 관심사가 아닌 평가(evaluation) 관심사
- `libs/stochastic/`에 혼입 시 `stochastic → optimization → stochastic` 순환 위험

### Option B — `scripts/backtest.py` (단일 스크립트) (거부)

**거부 이유**:
- `scripts/`는 CLI 진입점. 재사용 가능한 라이브러리 로직을 스크립트에 배치하면 테스트 어려움
- `libs/evaluation/RealDataBacktester`를 클래스로 분리하면 단위 테스트 가능

---

## Consequences

### Positive
- `column_map` 파라미터로 CSV 스키마 변경 시 코드 수정 불필요
- 단위 테스트에서 toy fixture + column_map으로 실제 CSV 없이 검증 가능
- K>1 확장 시 `libs/evaluation/`에 새 클래스 추가

### Negative
- `DEFAULT_COLUMN_MAP`이 Step 3 전에는 비어 있음 → Step 4 착수 전 Step 3 필수
- `column_map`이 None이고 DEFAULT_COLUMN_MAP도 비어 있으면 `KeyError` 발생 가능

### Risks
- CSV 컬럼 스키마가 월별로 다를 경우 DEFAULT_COLUMN_MAP이 무효화될 수 있음 → 에러 메시지에 실제 컬럼명 출력으로 디버깅 지원

---

## Follow-ups

- Step 3에서 `pd.read_csv(..., nrows=5)`로 컬럼명 확인 후 DEFAULT_COLUMN_MAP 확정
- ADR-005 "DEFAULT_COLUMN_MAP" 항목을 Step 3 이후 업데이트
- 추후 K>1 시나리오 평가 확장 시 `libs/evaluation/` 패키지 활용
