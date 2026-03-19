---
name: convention-adk-agent
description: Google ADK 에이전트 구현 패턴. root_agent export, PromptLoader, ToolContext state schema 설계 우선, initial_state 구조.
user-invocable: true
triggers:
  - "ADK 에이전트"
  - "adk agent 생성"
  - "root_agent"
  - "ToolContext"
  - "Google ADK"
---

# convention-adk-agent

Google ADK 기반 에이전트 구현 시 준수해야 할 패턴. CLAUDE.md § Agent 구현과 AW-011(데이터 구조 우선 설계)을 따른다.

## 1. 에이전트 디렉토리 구조

```
agents/{agent_name}/
├── src/
│   └── {agent_name}/
│       ├── __init__.py       # root_agent export 필수
│       ├── agent.py          # 에이전트 정의
│       ├── tools.py          # tool function 모음
│       └── prompts/          # Jinja2 템플릿
│           └── system.yaml
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   └── test_tools.py
├── pyproject.toml
└── CLAUDE.md                 # 에이전트별 규칙
```

## 2. root_agent export (필수)

`__init__.py`에서 반드시 `root_agent`를 export한다.

```python
# agents/{agent_name}/src/{agent_name}/__init__.py
from {agent_name}.agent import root_agent

__all__ = ["root_agent"]
```

## 3. State Schema 설계 우선 (AW-011 Rule 5)

**코드 작성 전** `initial_state`와 `tool_context.state` key 목록을 먼저 확정한다.

```python
# STEP 1 (구현 전): state schema 문서화
# app: prefix = 파일 경로 및 설정값
# agent: prefix = 에이전트 내부 상태
INITIAL_STATE_SCHEMA = {
    "app:demand_file": "str — 수요 데이터 CSV 경로",
    "app:output_dir": "str — 출력 디렉토리",
    "agent:processed": "bool — 전처리 완료 여부",
    "agent:zone_count": "int — 처리된 zone 수",
}

# STEP 2: agent __init__에서 파일 존재 확인
class DemandAgent:
    def __init__(self, demand_file: str, output_dir: str) -> None:
        demand_path = Path(demand_file)
        if not demand_path.exists():
            raise FileNotFoundError(f"수요 데이터 없음: {demand_path}")

        self.initial_state = {
            "app:demand_file": str(demand_path),
            "app:output_dir": str(output_dir),
        }
```

## 4. Prompt 외부화 (Jinja2 + PromptLoader)

prompt를 코드에 하드코딩하지 않는다.

```python
# agents/{agent_name}/src/{agent_name}/agent.py
from utils.prompt_loader import PromptLoader

loader = PromptLoader(Path(__file__).parent / "prompts")

root_agent = LlmAgent(
    name="demand_analyst",
    model="gemini-2.0-flash",
    instruction=loader.load("system.yaml", zone_count="{zone_count}"),
)
```

```yaml
# prompts/system.yaml
system: |
  당신은 모빌리티 수요 분석 전문가입니다.
  분석 대상 zone 수: {{ zone_count }}

  입력 변수:
  - zone_count: 처리할 H3 zone 수
```

## 5. Tool Function 패턴 (CLAUDE.md § File Path Pattern)

```python
# tools.py
from google.adk.tools import ToolContext
import pandas as pd
from typing import Any


def load_demand_data(tool_context: ToolContext) -> dict[str, Any]:
    """수요 데이터를 로드하고 기본 통계를 반환한다.

    Logics:
        tool_context.state["app:demand_file"]에서 경로를 읽어
        CSV를 로드하고 zone별 집계 결과를 반환한다.

    Args:
        tool_context: ADK tool context. state에서 파일 경로를 읽음.

    Returns:
        zone별 수요 집계 결과 dict.
    """
    file_path = tool_context.state["app:demand_file"]
    df = pd.read_csv(file_path)

    # vectorized 연산 (iterrows 금지 — AW-011 Rule 3/4)
    result = df.groupby("zone_id")["demand"].sum().to_dict()

    tool_context.state["agent:processed"] = True
    tool_context.state["agent:zone_count"] = len(result)

    return {"zone_demands": result, "total_zones": len(result)}
```

## 6. 에이전트 등록 (pyproject.toml)

```toml
[tool.uv.sources]
utils = { workspace = true }
{agent_name} = { workspace = true }

[project]
name = "{agent_name}"
dependencies = [
    "google-adk>=0.1.0",
    "pandas>=2.0.0",
    "utils",
]
```

## 7. 체크리스트

구현 전:
- [ ] `initial_state` key 목록 확정 (state schema 문서화)
- [ ] `app:` prefix 파일 경로 key 식별
- [ ] tool function signature 확정 (ToolContext만 인자)

구현 중:
- [ ] `root_agent` export 확인
- [ ] 파일 존재 확인은 `__init__`에서만
- [ ] tool function 내 `os.path.exists` 금지
- [ ] prompt는 YAML 파일로 분리

검증:
- [ ] `/check-data-pipeline` 실행
- [ ] `/convention-python` 실행
- [ ] `uv run pytest -m unit` 통과

## 관련 규칙

- CLAUDE.md § Agent 구현 (Google ADK)
- CLAUDE.md § File Path & Data Access Pattern
- [team-operations.md](../../docs/design/ref/team-operations.md) § AW-011
- [check-data-pipeline](../check-data-pipeline/SKILL.md)
- [claude-code-rule-convention.md](../../docs/ref/bestpractice/claude-code-rule-convention.md) § Practice 8, 27
