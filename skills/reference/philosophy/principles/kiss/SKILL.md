---
name: convention-kiss
description: KISS (Keep It Simple, Stupid). 불필요한 복잡성을 금지한다. 단순한 해결책이 항상 우선이다.
user-invocable: true
triggers:
  - "KISS"
  - "단순하게"
  - "과도한 설계"
  - "over-engineering"
---

# convention-kiss

**@AW-017** | @docs/design/ref/team-operations.md § AW-017

KISS: 시스템은 가능한 한 단순하게 유지되어야 한다. 복잡성은 버그를 낳고, 유지보수를 어렵게 하며, 팀원이 이해하기 힘들게 만든다.

## VIOLATION 1: 단순한 집계에 과도한 추상화

```python
# VIOLATION: 단순한 합계 계산에 Strategy + Factory + Template Method 적용
class AggregationStrategy(ABC):
    @abstractmethod
    def aggregate(self, values: list[float]) -> float: ...

class SumStrategy(AggregationStrategy):
    def aggregate(self, values: list[float]) -> float:
        return sum(values)

class AggregationFactory:
    @staticmethod
    def create(strategy_type: str) -> AggregationStrategy:
        if strategy_type == "sum":
            return SumStrategy()
        raise ValueError(f"Unknown: {strategy_type}")

# 사용: 단 한 번, sum만 사용
factory = AggregationFactory()
strategy = factory.create("sum")
result = strategy.aggregate([1, 2, 3])
```

```python
# CORRECT: 한 줄로 충분
result = sum([1, 2, 3])

# 또는 pandas vectorization
result = df["demand"].sum()
```

## VIOLATION 2: ADK tool에서 불필요한 중간 레이어

```python
# VIOLATION: 단순한 데이터 로딩에 과도한 추상화 계층
class DataSource(ABC):
    @abstractmethod
    def fetch(self) -> pd.DataFrame: ...

class CSVDataSource(DataSource):
    def __init__(self, path: str) -> None: self.path = path
    def fetch(self) -> pd.DataFrame: return pd.read_csv(self.path)

class DataSourceFactory:
    def create(self, source_type: str, path: str) -> DataSource:
        if source_type == "csv":
            return CSVDataSource(path)
        raise ValueError(source_type)

def load_demand_data(tool_context: ToolContext) -> pd.DataFrame:
    factory = DataSourceFactory()
    source = factory.create("csv", tool_context.state["app:demand_file"])
    return source.fetch()
```

```python
# CORRECT: 직접 읽기로 충분 (현재 CSV만 사용)
def load_demand_data(tool_context: ToolContext) -> pd.DataFrame:
    """수요 데이터를 로드한다.

    Logics:
        state에서 파일 경로를 읽어 CSV를 반환한다.
    """
    return pd.read_csv(tool_context.state["app:demand_file"])
# Parquet 지원이 실제로 필요해지면 그때 추상화 (YAGNI와 연계)
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-017 | @docs/design/ref/team-operations.md § AW-017 | KISS — 단순한 해결책 우선 |
| @AW-019 | @docs/design/ref/team-operations.md § AW-019 | YAGNI — 필요할 때만 구현 |
| Simplicity First | CLAUDE.md § LLM 행동지침 | No abstractions for single-use code |

## 참조

- @docs/design/ref/team-operations.md § AW-017
- @.claude/skills/convention-yagni/SKILL.md
- @.claude/skills/convention-solid-srp/SKILL.md
