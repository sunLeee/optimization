---
name: convention-ioc
description: IoC (Inversion of Control). 제어권을 프레임워크/외부에 위임한다. Hollywood Principle - Don't call us, we'll call you.
user-invocable: true
triggers:
  - "IoC"
  - "inversion of control"
  - "제어 역전"
  - "hollywood principle"
---

# convention-ioc

**@AW-042** | @docs/design/ref/team-operations.md § AW-042

IoC (Inversion of Control): "Don't call us, we'll call you." 코드가 프레임워크를 호출하는 대신, 프레임워크가 코드를 호출한다. ADK에서는 특히 중요한 패턴이다.

## VIOLATION 1: 코드가 프레임워크를 직접 제어

```python
# VIOLATION: 코드가 실행 흐름을 직접 제어 (IoC 없음)
class DemandPipeline:
    def run(self) -> None:
        # 코드가 모든 것을 직접 호출
        data = self._load_data()
        cleaned = self._clean(data)
        result = self._analyze(cleaned)
        self._save(result)
        self._notify(result)  # 모든 단계를 코드가 제어

# 문제: 테스트 어렵, 순서 변경 불가, 확장 어려움
```

```python
# CORRECT: 프레임워크(ADK)에 제어권 위임
# ADK가 tool 실행 순서를 제어 (IoC 적용)
def load_demand_data(tool_context: ToolContext) -> dict:
    """ADK가 호출 — 코드는 로직만 구현."""
    df = pd.read_csv(tool_context.state["app:demand_file"])
    tool_context.state["agent:loaded"] = True
    return {"rows": len(df)}

def analyze_demand(tool_context: ToolContext) -> dict:
    """ADK가 호출 — 이전 tool 결과를 state에서 읽음."""
    # ADK가 실행 순서 결정 (코드는 순서 모름)
    df = pd.read_csv(tool_context.state["app:demand_file"])
    return {"total": float(df["demand"].sum())}

# root_agent에 tool 등록 → ADK가 실행 순서 제어 (IoC)
root_agent = LlmAgent(
    tools=[load_demand_data, analyze_demand]
)
```

## VIOLATION 2: 의존성을 코드 내부에서 생성

```python
# VIOLATION: DemandAnalyzer가 자신의 의존성을 직접 생성 (IoC 없음)
class DemandAnalyzer:
    def __init__(self) -> None:
        # 코드가 의존성 생성 제어 — IoC 위반
        self.loader = CSVLoader()          # 하드코딩
        self.validator = StrictValidator() # 하드코딩
        self.repo = MongoRepository()     # 하드코딩
```

```python
# CORRECT: 의존성 주입 (IoC의 일종 — DIP와 연계)
class DemandAnalyzer:
    def __init__(
        self,
        loader: DataLoader,      # 외부에서 주입
        validator: DataValidator,
        repo: ZoneRepository,
    ) -> None:
        """의존성을 외부에서 주입받는다.

        Logics:
            프레임워크/테스트가 의존성 선택권을 가짐 (IoC).
        """
        self._loader = loader
        self._validator = validator
        self._repo = repo

# 프로덕션: 실제 구현 주입
analyzer = DemandAnalyzer(
    loader=CSVLoader(),
    validator=StrictValidator(),
    repo=MongoRepository(),
)

# 테스트: 목 주입
analyzer = DemandAnalyzer(
    loader=MockLoader(),
    validator=LenientValidator(),
    repo=InMemoryRepository(),
)
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-042 | @docs/design/ref/team-operations.md § AW-042 | IoC |
| @AW-016 | @docs/design/ref/team-operations.md § AW-016 | DIP — IoC의 구체화 |
| @AW-012 | @docs/design/ref/team-operations.md § AW-012 | SRP — IoC로 관심사 분리 |

## 참조

- @docs/design/ref/team-operations.md § AW-042
- @.claude/skills/convention-solid-dip/SKILL.md
- @.claude/skills/convention-adk-agent/SKILL.md
