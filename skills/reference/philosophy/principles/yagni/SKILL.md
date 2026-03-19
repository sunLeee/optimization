---
name: convention-yagni
description: YAGNI (You Ain't Gonna Need It). 현재 필요하지 않은 기능을 미리 구현하지 않는다.
user-invocable: true
triggers:
  - "YAGNI"
  - "미래 대비"
  - "speculative"
  - "you ain't gonna need it"
---

# convention-yagni

**@AW-019** | @docs/design/ref/team-operations.md § AW-019

YAGNI: 지금 필요하지 않은 것을 구현하지 말라. 미래 요구사항을 예측해서 미리 구현한 코드는 대부분 불필요한 복잡성을 추가할 뿐이다.

## VIOLATION 1: 요청하지 않은 다중 포맷 지원

```python
# VIOLATION: CSV만 요청받았는데 XML, JSON까지 지원하는 generic reader 구현
def load_data(
    file_path: str,
    format: str = "csv",           # 요청받지 않음
    encoding: str = "utf-8",
    delimiter: str = ",",          # 요청받지 않음
    xml_schema: str | None = None, # 요청받지 않음
    json_path: str | None = None,  # 요청받지 않음
) -> pd.DataFrame:
    if format == "csv":
        return pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
    elif format == "xml":
        return pd.read_xml(file_path, schema=xml_schema)
    elif format == "json":
        return pd.read_json(file_path)[json_path]
    raise ValueError(f"Unsupported: {format}")
```

```python
# CORRECT: 현재 필요한 CSV 읽기만 구현
def load_demand_csv(file_path: str) -> pd.DataFrame:
    """수요 데이터 CSV를 로드한다.

    Logics:
        UTF-8 인코딩으로 CSV를 읽어 DataFrame을 반환한다.
    """
    return pd.read_csv(file_path, encoding="utf-8")
# Parquet이 필요해지면 그때 추가 (ADR 작성 후)
```

## VIOLATION 2: 사용하지 않는 plugin 아키텍처 미리 구현

```python
# VIOLATION: 현재 에이전트가 1개인데 plugin system 미리 구현
class AgentPlugin(ABC):
    @abstractmethod
    def execute(self, context: dict) -> dict: ...

class AgentPluginRegistry:
    _plugins: dict[str, type[AgentPlugin]] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(plugin_cls: type) -> type:
            cls._plugins[name] = plugin_cls
            return plugin_cls
        return decorator

    @classmethod
    def get(cls, name: str) -> AgentPlugin:
        return cls._plugins[name]()

@AgentPluginRegistry.register("demand")
class DemandPlugin(AgentPlugin):
    def execute(self, context: dict) -> dict:
        return analyze_demand(context)
```

```python
# CORRECT: 에이전트 하나면 직접 구현
def run_demand_analysis(context: dict) -> dict:
    """수요 분석을 실행한다.

    Logics:
        입력 context에서 파일 경로를 읽어 분석 결과를 반환한다.
    """
    return analyze_demand(context)
# 에이전트가 3개 이상이 되면 그때 plugin 고려
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-019 | @docs/design/ref/team-operations.md § AW-019 | YAGNI — 필요할 때만 구현 |
| Simplicity First | CLAUDE.md § LLM 행동지침 | No features beyond what was asked |
| @AW-009 | @docs/design/ref/team-operations.md § AW-009 | ADR — 구조 변경 전 기록 |

## 참조

- @docs/design/ref/team-operations.md § AW-019
- @.claude/skills/convention-kiss/SKILL.md
- @.claude/skills/convention-dry/SKILL.md
