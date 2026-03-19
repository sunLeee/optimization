---
name: convention-leaky-abstractions
description: Law of Leaky Abstractions. 모든 비자명한 추상화는 결국 새어나온다. 추상화 한계를 인식하고 방어적으로 설계.
user-invocable: true
triggers:
  - "leaky abstraction"
  - "추상화 누수"
  - "ORM 문제"
  - "추상화 한계"
---

# convention-leaky-abstractions

**@AW-031** | @docs/design/ref/team-operations.md § AW-031

Law of Leaky Abstractions: "모든 비자명한 추상화는 결국 새어나온다." ORM, HTTP 클라이언트, 파일 시스템 추상화 등은 내부 구현의 세부사항이 노출될 수 있다.

## VIOLATION 1: ORM 추상화에 의존하다가 성능 문제

```python
# VIOLATION: ORM이 "SQL을 숨겨준다"고 믿고 N+1 쿼리 발생
class ZoneRepository:
    def get_zones_with_demand(self) -> list[Zone]:
        zones = Zone.objects.all()          # SELECT * FROM zones
        for zone in zones:
            # N+1: 각 zone마다 쿼리 발생 (추상화가 새어남)
            _ = zone.demand_set.all()       # SELECT * FROM demands WHERE zone_id=?
        return zones

# ORM은 SQL을 숨기지만, 성능 특성은 숨길 수 없다
```

```python
# CORRECT: 추상화 누수를 인식하고 명시적으로 처리
class ZoneRepository:
    def get_zones_with_demand(self) -> list[Zone]:
        """zone과 수요 데이터를 함께 로드한다.

        Logics:
            select_related로 N+1 방지. ORM 추상화 한계를 인식.
        """
        # 추상화 한계를 인식하고 prefetch 명시
        return Zone.objects.prefetch_related("demand_set").all()

# 또는 ADK 프로젝트에서는 Pandas vectorized 방식 사용 (@AW-011)
```

## VIOLATION 2: ADK ToolContext 추상화 누수

```python
# VIOLATION: ToolContext가 내부 상태를 완전히 캡슐화한다고 믿음
def process_data(tool_context: ToolContext) -> dict:
    # ToolContext.state는 dict-like이지만 정확히 dict는 아님
    data = dict(tool_context.state)     # 추상화 누수: deep copy 안 됨
    data["new_key"] = "value"           # 원본 state에 영향을 줄 수 있음
    return data
```

```python
# CORRECT: 추상화 누수를 인식하고 방어적으로 처리
def process_data(tool_context: ToolContext) -> dict:
    """데이터를 처리한다.

    Logics:
        ToolContext.state를 명시적으로 읽고 새 dict를 반환한다.
    """
    # 필요한 값만 명시적으로 읽음 (추상화에 의존하지 않음)
    demand_file = tool_context.state.get("app:demand_file")
    zone_count = tool_context.state.get("agent:zone_count", 0)
    return {"demand_file": demand_file, "zone_count": zone_count}
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-031 | @docs/design/ref/team-operations.md § AW-031 | Leaky Abstractions |
| @AW-011 | @docs/design/ref/team-operations.md § AW-011 | Rob Pike Rule 1/2 — 측정 먼저 |
| File Path Pattern | CLAUDE.md § File Path Pattern | state 접근 패턴 명시 |

## 참조

- @docs/design/ref/team-operations.md § AW-031
- @.claude/skills/convention-hyrums-law/SKILL.md
- @.claude/skills/convention-adk-agent/SKILL.md
