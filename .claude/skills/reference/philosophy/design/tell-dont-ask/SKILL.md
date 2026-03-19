---
name: convention-tell-dont-ask
description: Tell, Don't Ask. 객체의 상태를 꺼내서 판단하지 말고 객체에게 직접 시켜라.
user-invocable: true
triggers:
  - "tell don't ask"
  - "tell dont ask"
  - "객체에게 시켜라"
  - "getter 남용"
---

# convention-tell-dont-ask

**@AW-034** | @docs/design/ref/team-operations.md § AW-034

Tell, Don't Ask: 객체에게 상태를 물어보고(Ask) 외부에서 결정하지 말고, 객체에게 직접 행동하라고(Tell) 지시하라.

## VIOLATION 1: 상태를 꺼내서 외부에서 판단

```python
# VIOLATION: zone 상태를 꺼내서 외부에서 처리 결정
class Zone:
    def __init__(self, zone_id: int, demand: float) -> None:
        self.zone_id = zone_id
        self.demand = demand
        self.is_processed = False

def process_zones(zones: list[Zone]) -> list[dict]:
    results = []
    for zone in zones:
        # Ask: 상태를 꺼내서 외부에서 판단 — Tell, Don't Ask 위반
        if not zone.is_processed and zone.demand > 0:
            result = analyze(zone.zone_id, zone.demand)
            zone.is_processed = True  # 외부에서 상태 변경
            results.append(result)
    return results
```

```python
# CORRECT: 객체에게 직접 시키기
class Zone:
    def __init__(self, zone_id: int, demand: float) -> None:
        self.zone_id = zone_id
        self._demand = demand
        self._is_processed = False

    def process_if_needed(self) -> dict | None:
        """필요시 분석을 수행하고 결과를 반환한다.

        Logics:
            미처리이고 수요가 있을 때만 분석을 실행한다.
        """
        if self._is_processed or self._demand <= 0:
            return None
        result = analyze(self.zone_id, self._demand)
        self._is_processed = True
        return result

def process_zones(zones: list[Zone]) -> list[dict]:
    # Tell: 객체에게 직접 시킴
    return [r for zone in zones if (r := zone.process_if_needed())]
```

## VIOLATION 2: ADK tool에서 상태 꺼내서 판단

```python
# VIOLATION: tool 밖에서 state를 꺼내서 조건 판단
class DemandOrchestrator:
    def run(self, tool_context: ToolContext) -> None:
        # Ask: 상태를 꺼내서 외부에서 판단
        if tool_context.state.get("agent:demand_loaded"):
            if tool_context.state.get("agent:zone_count", 0) > 0:
                self._run_analysis(tool_context)
```

```python
# CORRECT: tool 내부에서 판단하거나 메서드로 캡슐화
class DemandOrchestrator:
    def run(self, tool_context: ToolContext) -> None:
        # Tell: 분석 실행을 직접 지시 (내부에서 조건 판단)
        self._run_analysis_if_ready(tool_context)

    def _run_analysis_if_ready(
        self, tool_context: ToolContext
    ) -> None:
        """준비 완료 시 분석을 실행한다.

        Logics:
            데이터 로딩 여부와 zone 수를 내부에서 확인한다.
        """
        loaded = tool_context.state.get("agent:demand_loaded", False)
        zone_count = tool_context.state.get("agent:zone_count", 0)
        if loaded and zone_count > 0:
            self._run_analysis(tool_context)
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-034 | @docs/design/ref/team-operations.md § AW-034 | Tell, Don't Ask |
| @AW-033 | @docs/design/ref/team-operations.md § AW-033 | CQS — 연계 원칙 |
| @AW-032 | @docs/design/ref/team-operations.md § AW-032 | Law of Demeter — 직접 친구에만 |

## 참조

- @docs/design/ref/team-operations.md § AW-034
- @.claude/skills/convention-cqs/SKILL.md
- @.claude/skills/convention-law-of-demeter/SKILL.md
