---
name: convention-testing
triggers:
  - "convention testing"
description: pytest 테스트 코드를 작성할 때. AAA 패턴, 명명 규칙, fixture, marker 선택이 불명확할 때. TDD 방식으로 진행할 때.
argument-hint: "[섹션] - structure, naming, aaa, fixtures, mocking, markers, all"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
model: claude-sonnet-4-6[1m]
context: pytest 기반 테스트 작성 컨벤션 참조 스킬. AAA 패턴, fixture, mocking, marker 규칙을 제공한다. 검증은 check-test-quality 스킬이 담당한다.
agent: Python 테스트 전문가. AAA 패턴과 fixture 활용으로 유지보수 가능한 테스트 코드를 안내한다.
hooks:
  pre_execution: []
  post_execution: []
category: 프로세스
skill-type: Atomic
references: []
referenced-by: []
---

# convention-testing

pytest 기반 테스트 작성 컨벤션.

## AAA 패턴 (필수)

```python
def test_demand_aggregation_by_zone() -> None:
    # Arrange (준비)
    df = pd.DataFrame({"zone_id": [1, 1, 2], "demand": [10.0, 20.0, 5.0]})

    # Act (실행)
    result = aggregate_by_zone(df)

    # Assert (검증)
    assert result[1] == 30.0
    assert result[2] == 5.0
```

## 명명 규칙

```python
# 형식: test_{기능}_{조건}_{예상결과}
def test_load_demand_csv_when_file_missing_raises_error() -> None: ...
def test_aggregate_zones_with_empty_dataframe_returns_empty() -> None: ...
def test_adk_tool_state_has_app_prefix() -> None: ...
```

## Marker 분류 (필수)

```python
@pytest.mark.unit          # API key 불필요, 빠름
@pytest.mark.integration   # API key 필요
@pytest.mark.e2e           # 전체 흐름
```

```bash
uv run pytest -m unit         # Unit만 실행
uv run pytest -m integration  # Integration만 실행
```

## Fixture 패턴

```python
@pytest.fixture
def sample_demand_df() -> pd.DataFrame:
    return pd.DataFrame({"zone_id": [1, 2, 3], "demand": [10.0, 20.0, 5.0]})

@pytest.fixture
def mock_tool_context() -> ToolContext:
    ctx = MagicMock(spec=ToolContext)
    ctx.state = {"app:demand_file": "/tmp/test_demand.csv"}
    return ctx

def test_load_demand(mock_tool_context: ToolContext) -> None:
    result = load_demand_data(mock_tool_context)
    assert "rows" in result
```

## ADK Tool 테스트 패턴

```python
def test_adk_tool_reads_from_state(tmp_path: Path) -> None:
    # Arrange: 테스트 파일 생성
    csv = tmp_path / "demand.csv"
    csv.write_text("zone_id,demand\n1,10.0\n2,20.0\n")

    ctx = MagicMock(spec=ToolContext)
    ctx.state = {"app:demand_file": str(csv)}

    # Act
    result = load_demand_data(ctx)

    # Assert
    assert result["rows"] == 2
```

## Gotchas (실패 포인트)

- **@pytest.mark 누락**: marker 없으면 `uv run pytest -m unit` 실행 시 누락됨
- **ToolContext mock**: `MagicMock()` 아닌 `MagicMock(spec=ToolContext)` — spec 없으면 잘못된 attribute 탐지 못함
- **tmp_path vs /tmp**: `tmp_path` fixture 사용 — 테스트 간 격리 보장
- **pandas float 비교**: `assert result == 30.0` 대신 `assert abs(result - 30.0) < 1e-6`

## 커버리지 기준

- 최소 80% coverage
- Unit test: `libs/`, `utils/` (API key 불필요)
- Integration test: `agents/`, `apps/` (API key 필요)

## 참조

- CLAUDE.md § 테스트 — 80% coverage, TDD 원칙
- [check-test-quality](../../quality/check/check-test-quality/SKILL.md) — 테스트 품질 검증
