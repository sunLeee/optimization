---
name: convention-design-patterns
description: 주요 design patterns 가이드. Factory, Strategy, Repository, Observer, Decorator, Command, Adapter, Template Method, Builder.
user-invocable: true
triggers:
  - "design pattern"
  - "디자인 패턴"
  - "Decorator"
  - "Command"
  - "Adapter"
  - "Builder"
---

# convention-design-patterns

## Factory Pattern

객체 생성 로직을 분리하여 생성 방법을 캡슐화한다.

**언제**: 생성할 객체 type이 runtime에 결정되거나 생성 로직이 복잡할 때

```python
class AgentFactory:
    @staticmethod
    def create(agent_type: str) -> BaseAgent:
        if agent_type == "demand":
            return DemandAgent()
        elif agent_type == "regional":
            return RegionalAgent()
        raise ValueError(f"Unknown agent type: {agent_type}")
```

**상황 1**: 여러 type의 agent를 if/elif로 직접 생성 → Factory로 분리
**상황 2**: 설정 파일에 따라 다른 processor 생성 → Factory 적용

## Strategy Pattern

알고리즘을 교체 가능하게 설계한다.

**언제**: 동일 목적의 알고리즘이 여러 개이고 runtime에 선택할 때

```python
class AggregationStrategy(ABC):
    @abstractmethod
    def aggregate(self, df: pd.DataFrame) -> pd.Series: ...

class SumStrategy(AggregationStrategy):
    def aggregate(self, df: pd.DataFrame) -> pd.Series:
        return df.sum()

class MeanStrategy(AggregationStrategy):
    def aggregate(self, df: pd.DataFrame) -> pd.Series:
        return df.mean()
```

**상황 1**: 집계 방식(합계/평균/최댓값)을 if/elif로 분기 → Strategy 적용
**상황 2**: 정규화 알고리즘이 도메인별로 다름 → Strategy 패턴으로 교체 가능하게

## Repository Pattern

data access logic을 분리한다.

**언제**: 여러 data source(CSV, DB, S3)를 동일 interface로 접근할 때

```python
class ZoneRepository(ABC):
    @abstractmethod
    def get(self, zone_id: int) -> pd.DataFrame: ...

class CSVZoneRepository(ZoneRepository):
    def get(self, zone_id: int) -> pd.DataFrame:
        return pd.read_csv(f"data/{zone_id}.csv")
```

**상황 1**: 직접 CSV 경로를 business logic에 하드코딩 → Repository로 분리
**상황 2**: test 시 실제 DB 대신 mock repository로 교체 가능

## Observer Pattern

event 기반 처리. publisher-subscriber 관계.

**언제**: 상태 변경 시 여러 곳에 알려야 할 때

```python
class PipelineEventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list] = {}

    def subscribe(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def publish(self, event: str, data: dict) -> None:
        for handler in self._handlers.get(event, []):
            handler(data)

# 사용
bus = PipelineEventBus()
bus.subscribe("demand_loaded", log_to_file)
bus.subscribe("demand_loaded", update_dashboard)
bus.publish("demand_loaded", {"rows": 1000})
```

**상황 1**: pipeline 진행 상황을 여러 logger에 알려야 할 때 → Observer 적용
**상황 2**: 데이터 처리 완료 시 알림/저장/시각화를 독립적으로 트리거

---

## Decorator Pattern

기존 객체를 수정하지 않고 동적으로 기능을 추가한다. (@AW-013 OCP 적용)

**언제**: 런타임에 기능을 선택적으로 추가/제거할 때

```python
# Python @decorator 방식
from functools import wraps
import time

def measure_time(func: Callable) -> Callable:
    """함수 실행 시간을 측정한다. (Decorator Pattern)"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"{func.__name__} 완료: {elapsed:.3f}초")
        return result
    return wrapper

def retry(max_attempts: int = 3) -> Callable:
    """실패 시 재시도한다."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
            return None
        return wrapper
    return decorator

@measure_time
@retry(max_attempts=3)
def load_demand_data(tool_context: ToolContext) -> dict:
    df = pd.read_csv(tool_context.state["app:demand_file"])
    return {"rows": len(df)}
```

**상황 1**: API 호출에 재시도 + 로깅을 동시에 추가 → 두 Decorator 조합
**상황 2**: 특정 함수에만 캐싱 적용 → `@lru_cache` Decorator 추가

---

## Command Pattern

요청을 객체로 캡슐화한다. 실행 취소(undo), 큐잉, 로깅 가능.

**언제**: 작업을 나중에 실행하거나 취소할 수 있어야 할 때

```python
class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...

class LoadDemandCommand(Command):
    def __init__(self, pipeline: DemandPipeline) -> None:
        self._pipeline = pipeline
        self._backup: pd.DataFrame | None = None

    def execute(self) -> None:
        self._backup = self._pipeline.data.copy()
        self._pipeline.load_demand()

    def undo(self) -> None:
        if self._backup is not None:
            self._pipeline.data = self._backup

class CommandHistory:
    def __init__(self) -> None:
        self._history: list[Command] = []

    def execute(self, cmd: Command) -> None:
        cmd.execute()
        self._history.append(cmd)

    def undo_last(self) -> None:
        if self._history:
            self._history.pop().undo()
```

**상황 1**: 데이터 처리 단계를 큐에 넣어 순차 실행 → Command 큐
**상황 2**: 잘못된 처리를 undo → Command History

---

## Adapter Pattern

호환되지 않는 인터페이스를 연결한다. (@AW-016 DIP 적용)

**언제**: 기존 클래스를 수정하지 않고 다른 인터페이스와 연결할 때

```python
# 기존 레거시 데이터 로더 (수정 불가)
class LegacyCSVLoader:
    def read_file(self, path: str) -> list[dict]:
        import csv
        with open(path) as f:
            return list(csv.DictReader(f))

# 새 인터페이스 (팀 표준)
class DataReader(ABC):
    @abstractmethod
    def load(self, path: str) -> pd.DataFrame: ...

# Adapter: 레거시 → 새 인터페이스로 변환
class LegacyCSVAdapter(DataReader):
    """레거시 CSV 로더를 DataReader 인터페이스로 변환한다."""

    def __init__(self, legacy: LegacyCSVLoader) -> None:
        self._legacy = legacy

    def load(self, path: str) -> pd.DataFrame:
        """레거시 형식을 DataFrame으로 변환한다."""
        raw = self._legacy.read_file(path)
        return pd.DataFrame(raw)

# 사용: 레거시 수정 없이 새 시스템에 통합
adapter = LegacyCSVAdapter(LegacyCSVLoader())
df = adapter.load("data/demand.csv")  # DataReader 인터페이스 사용
```

**상황 1**: 외부 API 응답을 내부 DataFrame 형식으로 변환 → Adapter
**상황 2**: 구 DB 클라이언트를 Repository 인터페이스에 연결 → Adapter

---

## Template Method Pattern

알고리즘의 뼈대를 정의하고, 구체적 단계는 서브클래스가 구현한다. (@AW-013 OCP 적용)

**언제**: 알고리즘 구조는 같지만 일부 단계를 다르게 구현할 때

```python
class DataPipelineTemplate(ABC):
    """데이터 파이프라인 Template Method."""

    def run(self) -> dict:
        """파이프라인을 실행한다. (뼈대 — 변경 불가)"""
        data = self.load()          # 서브클래스 구현
        clean = self.preprocess(data)  # 서브클래스 구현
        result = self.analyze(clean)   # 서브클래스 구현
        self.save(result)           # 서브클래스 구현
        return result

    @abstractmethod
    def load(self) -> pd.DataFrame: ...

    @abstractmethod
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame: ...

    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> dict: ...

    def save(self, result: dict) -> None:
        """기본 저장 구현 — 필요시 오버라이드."""
        logger.info(f"결과 저장: {result}")

class DemandPipeline(DataPipelineTemplate):
    def load(self) -> pd.DataFrame:
        return pd.read_csv("data/demand.csv")

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna()

    def analyze(self, df: pd.DataFrame) -> dict:
        return {"total": float(df["demand"].sum())}
```

**상황 1**: 수요/공급/지역별 파이프라인이 같은 구조를 공유 → Template Method
**상황 2**: 기본 검증 로직은 공통, 도메인별 검증만 오버라이드

---

## @ 링킹 및 AW 규칙 참조

| Pattern | 핵심 AW 규칙 |
|---------|-------------|
| Factory | @AW-013 OCP, @AW-016 DIP |
| Strategy | @AW-013 OCP, @AW-019 YAGNI |
| Repository | @AW-016 DIP, @AW-020 SoC |
| Observer | @AW-033 CQS, @AW-020 SoC |
| Decorator | @AW-013 OCP, @AW-017 KISS |
| Command | @AW-033 CQS, @AW-035 Boy Scout |
| Adapter | @AW-016 DIP, @AW-026 Chesterton's Fence |
| Template Method | @AW-013 OCP, @AW-018 DRY |

## 참조

- @docs/design/ref/team-operations.md § AW-012~016 (SOLID)
- @.claude/skills/convention-solid-ocp/SKILL.md
- @.claude/skills/convention-solid-dip/SKILL.md
- [claude-code-rule-convention.md](../../docs/ref/bestpractice/claude-code-rule-convention.md) § Practice 5
