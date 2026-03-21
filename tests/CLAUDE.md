# tests/ — 테스트 모음

## 실행 방법

```bash
# 전체 테스트
uv run python -m pytest tests/ -v

# 특정 시나리오
uv run python -m pytest tests/ -k "toy_n5" -v
uv run python -m pytest tests/ -k "mid_n25" -v

# 커버리지
uv run python -m pytest tests/ --cov=libs --cov-report=term-missing
```

## 파일 목록

| 파일 | 테스트 대상 | 수용 기준 |
|------|-----------|---------|
| `test_core.py` | 연료 모델, 거리 계산, 상수 | 단위 테스트 |
| `test_integration.py` | BAP→TSP-T end-to-end | toy_n5: 5척 전원 배정, gap≤5%, ≤30s |
| `test_multi_tug.py` | ALNS 다중 예인선 | mid_n25: BKS 대비 ≤5%, ≤5min |
| `test_ais.py` | AIS 데이터 파싱 | — |
| `fixtures/` | 공통 테스트 픽스처 | toy_n5, mid_n25 시나리오 |

## 시나리오 정의

### toy_n5
```python
# 5척, 2예인선, 2선석 — Tier 1 검증
VESSELS = [
    {"id":"V0","arrival_min":60, "service_min":120, "priority":3},
    ...  # fixtures/toy_n5.py
]
```

### mid_n25
```python
# 25척, 8예인선, 3선석 — Tier 2 ALNS 검증
# Solomon R101 첫 25 node 변환
# BKS = 617.1 (Solomon R101 기준, 단위 변환 필요)
```

### large_n80
```python
# 80척, 20예인선, 6선석 — Tier 3 Benders 검증
# 수용: gap ≤ 5%, ≤ 1800s, n_cuts ≥ 10
```

## 완료 증명 커맨드 (AW-008)

```bash
# Phase 2 완료
uv run python -m pytest tests/ -k "toy_n5" -v                    # PASSED
bash .claude/check-criteria.sh --score                            # ≥ 90

# Phase 3a 완료
uv run python scripts/benchmark_benders.py --n 80 --tugs 20      # gap≤5%, time≤1800s

# Phase 4 완료
uv run python -m pytest tests/ --cov=libs --cov-report=term-missing  # coverage≥80%
```

## convention-testing 준수

- AAA 패턴 (Arrange / Act / Assert)
- 테스트명: `test_{대상}_{조건}_{기대결과}()`
- Fixtures: `conftest.py` 또는 `fixtures/` 디렉토리
- Mock 사용 최소화 (실제 솔버 호출 권장)
