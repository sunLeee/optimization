---
name: convention-solid-ocp
description: OCP (Open/Closed Principle). 확장에 열려 있고, 수정에 닫혀 있다. 새 기능은 기존 코드 수정 없이 추가한다.
user-invocable: true
triggers:
  - "OCP"
  - "open closed"
  - "확장에 열려"
  - "수정에 닫혀"
---

# convention-solid-ocp

**@AW-013** | @docs/design/ref/team-operations.md § AW-013

OCP: 소프트웨어 엔티티는 확장에는 열려 있어야 하고, 수정에는 닫혀 있어야 한다. 새 기능 추가 시 기존 코드를 변경하지 않고 새 코드를 추가한다.

## VIOLATION 1: 새 포맷마다 기존 코드 수정

```python
# VIOLATION: 새 데이터 포맷이 생길 때마다 load_data() 수정 필요
def load_data(file_path: str, format: str) -> pd.DataFrame:
    if format == "csv":
        return pd.read_csv(file_path)
    elif format == "parquet":
        return pd.read_parquet(file_path)
    elif format == "json":           # 새 포맷 추가 = 기존 코드 수정 — OCP 위반
        return pd.read_json(file_path)
    # excel 추가하려면 또 수정...
    raise ValueError(f"Unknown format: {format}")
```

```python
# CORRECT: 새 포맷은 새 클래스로 추가 (기존 코드 무수정)
class DataLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> pd.DataFrame: ...

class CSVLoader(DataLoader):
    def load(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)

class ParquetLoader(DataLoader):
    def load(self, file_path: str) -> pd.DataFrame:
        return pd.read_parquet(file_path)

# 새 포맷 추가 = 새 클래스만 추가 (기존 코드 무변경)
class ExcelLoader(DataLoader):
    def load(self, file_path: str) -> pd.DataFrame:
        return pd.read_excel(file_path)
```

## VIOLATION 2: ADK tool 확장 시 기존 코드 수정

```python
# VIOLATION: 새 에이전트 타입마다 orchestrator 수정
def run_agent(agent_type: str, context: dict) -> dict:
    if agent_type == "demand":
        return run_demand_analysis(context)
    elif agent_type == "regional":
        return run_regional_analysis(context)
    elif agent_type == "format":     # 추가할 때마다 여기 수정 — OCP 위반
        return run_format_report(context)
```

```python
# CORRECT: 새 에이전트 = 새 클래스로 등록
class AgentRunner(ABC):
    @abstractmethod
    def run(self, context: dict) -> dict: ...

class DemandAgentRunner(AgentRunner):
    def run(self, context: dict) -> dict:
        return run_demand_analysis(context)

# 새 에이전트 = 새 클래스 추가만 (orchestrator 수정 없음)
class FormatAgentRunner(AgentRunner):
    def run(self, context: dict) -> dict:
        return run_format_report(context)
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-013 | @docs/design/ref/team-operations.md § AW-013 | OCP |
| @AW-019 | @docs/design/ref/team-operations.md § AW-019 | YAGNI — 확장 전 필요성 확인 |
| @AW-012 | @docs/design/ref/team-operations.md § AW-012 | SRP — 함께 적용 |

## 참조

- @docs/design/ref/team-operations.md § AW-013
- @.claude/skills/convention-solid-srp/SKILL.md
- @.claude/skills/convention-yagni/SKILL.md
