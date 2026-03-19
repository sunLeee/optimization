---
name: convention-galls-law
description: Gall's Law. 복잡한 시스템은 항상 단순한 것에서 진화한다. 처음부터 복잡한 시스템 설계 금지.
user-invocable: true
triggers:
  - "Gall's Law"
  - "복잡한 시스템"
  - "진화적 설계"
  - "단순부터 시작"
---

# convention-galls-law

**@AW-023** | @docs/design/ref/team-operations.md § AW-023

Gall's Law: "복잡하게 작동하는 시스템은 항상 단순하게 작동하는 것에서 진화한다. 처음부터 복잡한 시스템은 작동하지 않으며, 단순한 것을 대체할 수도 없다."

## VIOLATION 1: 처음부터 복잡한 멀티 에이전트 시스템

```python
# VIOLATION: Day 1부터 완전한 분산 에이전트 시스템 구축 시도
class AgentOrchestrator:
    def __init__(self) -> None:
        self.demand_agent = DemandAgent()      # 아직 단순 버전도 없음
        self.regional_agent = RegionalAgent()
        self.format_agent = FormatAgent()
        self.coordinator = MultiAgentCoordinator()
        self.message_queue = AsyncMessageQueue()
        self.state_manager = DistributedStateManager()

# 문제: 아무것도 작동 안 함. 단순한 CSV 읽기도 실패.
```

```python
# CORRECT: 단순한 것부터 작동시키고 진화
# Phase 1: 단일 스크립트로 작동 확인
def analyze_demand_v1(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path).groupby("zone_id")["demand"].sum()

# Phase 2: 작동하는 코드를 tool function으로 발전
def analyze_demand(tool_context: ToolContext) -> dict:
    df = pd.read_csv(tool_context.state["app:demand_file"])
    return {"result": df.groupby("zone_id")["demand"].sum().to_dict()}

# Phase 3: 작동하는 tool을 ADK agent로 발전 (필요해지면)
```

## VIOLATION 2: 데이터 파이프라인 과도한 초기 설계

```python
# VIOLATION: 단순한 CSV 처리에 과도한 파이프라인 인프라
class DataPipelineEngine:
    def __init__(self) -> None:
        self.plugins: list[PipelinePlugin] = []    # 아직 플러그인 없음
        self.stage_registry: dict = {}
        self.dependency_resolver = DAGResolver()   # 의존성 그래프
        self.parallel_executor = ThreadPoolExecutor()

# 실제로 필요한 것: CSV 읽기 → 전처리 → Parquet 저장

# CORRECT: 작동하는 3줄부터
def run_pipeline(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)
    df = preprocess(df)
    df.to_parquet(output_path)
# 여러 stage가 필요해지면 그때 추상화 (YAGNI + Gall's Law)
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-023 | @docs/design/ref/team-operations.md § AW-023 | Gall's Law |
| @AW-019 | @docs/design/ref/team-operations.md § AW-019 | YAGNI — 연계 원칙 |
| @AW-017 | @docs/design/ref/team-operations.md § AW-017 | KISS — 연계 원칙 |

## 참조

- @docs/design/ref/team-operations.md § AW-023
- @.claude/skills/convention-yagni/SKILL.md
- @.claude/skills/convention-kiss/SKILL.md
