---
name: convention-law-of-demeter
description: Law of Demeter (최소 지식 원칙). 객체는 직접 친구에게만 말한다. 메서드 체인 a.b.c.d 금지.
user-invocable: true
triggers:
  - "LoD"
  - "law of demeter"
  - "최소 지식"
  - "메서드 체인"
  - "train wreck"
---

# convention-law-of-demeter

**@AW-032** | @docs/design/ref/team-operations.md § AW-032

Law of Demeter: 메서드는 자신이 직접 아는 객체에만 접근해야 한다. `a.b.c.d()` 형태의 깊은 체인은 내부 구조에 과도하게 의존하여 결합도를 높인다.

## VIOLATION 1: ADK 에이전트에서 깊은 체인 접근

```python
# VIOLATION: 깊은 객체 체인 접근 — Train Wreck
def process_demand(tool_context: ToolContext) -> dict:
    # tool_context → session → user → config → zone_list
    zones = tool_context.session.user.config.regional_settings.zone_list
    # 내부 구조 변경 시 여기도 수정 필요
    return {"zones": len(zones)}
```

```python
# CORRECT: 직접 접근 가능한 state에서만 읽기
def process_demand(tool_context: ToolContext) -> dict:
    """수요 데이터를 처리한다.

    Logics:
        tool_context.state에서 직접 zone 정보를 읽는다.
        내부 구조에 의존하지 않는다.
    """
    # tool_context는 직접 친구 → state는 직접 속성
    zones = tool_context.state.get("app:zone_list", [])
    return {"zones": len(zones)}
```

## VIOLATION 2: 데이터 처리에서 중첩 객체 깊이 접근

```python
# VIOLATION: config 객체 체인을 통해 설정값 접근
class DemandPipeline:
    def __init__(self, config: OmegaConf) -> None:
        self.config = config

    def get_output_path(self) -> str:
        # config → output → regional → base_path — 3단계 체인
        return self.config.output.regional.base_path + "/demand"

# 호출자도 체인 의존
pipeline = DemandPipeline(config)
path = pipeline.config.output.regional.base_path  # 외부에서도 체인 접근
```

```python
# CORRECT: 필요한 값을 직접 제공하거나 메서드로 캡슐화
class DemandPipeline:
    def __init__(self, output_base_path: str) -> None:
        self._output_base_path = output_base_path  # 직접 주입

    def get_output_path(self) -> str:
        """출력 경로를 반환한다."""
        return f"{self._output_base_path}/demand"

# 또는 config에서 한 번에 추출 후 주입
pipeline = DemandPipeline(
    output_base_path=config.output.regional.base_path  # 생성 시점에만 체인 허용
)
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-032 | @docs/design/ref/team-operations.md § AW-032 | LoD — 직접 친구에게만 |
| @AW-034 | @docs/design/ref/team-operations.md § AW-034 | Tell, Don't Ask |
| File Path Pattern | CLAUDE.md § File Path Pattern | state를 통해 경로 접근 — LoD 적용 |

## 참조

- @docs/design/ref/team-operations.md § AW-032
- @.claude/skills/convention-tell-dont-ask/SKILL.md
- @.claude/skills/convention-solid-srp/SKILL.md
