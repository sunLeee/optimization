---
name: convention-hyrums-law
description: Hyrum's Law. 사용자가 충분하면 모든 관찰 가능한 동작이 의존된다. API 설계 시 암묵적 계약에 주의.
user-invocable: true
triggers:
  - "Hyrum's Law"
  - "하이럼의 법칙"
  - "API 하위 호환"
  - "암묵적 계약"
---

# convention-hyrums-law

**@AW-025** | @docs/design/ref/team-operations.md § AW-025

Hyrum's Law: "API 사용자가 충분히 많으면, 명세가 무엇이든 시스템의 모든 관찰 가능한 동작에 누군가가 의존하게 된다."

## VIOLATION 1: 정렬 순서에 의존하는 사용자

```python
# 내부 구현: 의도적으로 정렬하지 않음
def get_zones(region: str) -> list[int]:
    """지역의 zone 목록을 반환한다."""
    return list(zone_db.query(region))  # 순서 보장 없음

# 사용자: 반환 순서가 항상 오름차순이라고 가정
zones = get_zones("seoul")
first_zone = zones[0]  # "항상 가장 작은 zone_id"라고 잘못 가정

# 결과: 내부 DB가 변경되면 사용자 코드가 조용히 깨짐
```

```python
# CORRECT: 명세를 명시적으로 만들기 (정렬이 필요하면 보장)
def get_zones(region: str, *, sorted_asc: bool = False) -> list[int]:
    """지역의 zone 목록을 반환한다.

    Args:
        region: 지역 코드.
        sorted_asc: True이면 오름차순 정렬. 기본값은 순서 미보장.

    Logics:
        sorted_asc가 True일 때만 정렬을 보장한다.
        명시하지 않으면 순서는 구현 상세다.
    """
    zones = list(zone_db.query(region))
    return sorted(zones) if sorted_asc else zones
```

## VIOLATION 2: 에러 메시지 문자열에 의존

```python
# VIOLATION: 에러 메시지를 파싱해서 로직 분기
try:
    result = process_zone(zone_id)
except ValueError as e:
    if "zone not found" in str(e):   # 에러 메시지 문자열에 의존 — Hyrum's Law
        create_zone(zone_id)
    elif "invalid zone" in str(e):   # 메시지가 바뀌면 조용히 깨짐
        log_warning(zone_id)
```

```python
# CORRECT: 명시적 예외 타입으로 분기
class ZoneNotFoundError(ValueError):
    def __init__(self, zone_id: int) -> None:
        super().__init__(f"Zone {zone_id} not found")
        self.zone_id = zone_id

class InvalidZoneError(ValueError):
    pass

try:
    result = process_zone(zone_id)
except ZoneNotFoundError:              # 타입으로 분기 — 안전
    create_zone(zone_id)
except InvalidZoneError:
    log_warning(zone_id)
```

## ADK 도메인 적용

```python
# Hyrum's Law 위험: tool_context.state 키 순서나 내부 타입에 의존
# WRONG: state 값이 항상 str이라고 가정
zone_id = int(tool_context.state["app:zone_id"])  # str→int 변환 필요

# CORRECT: 명시적 타입 변환 + 방어적 접근
def get_zone_id(tool_context: ToolContext) -> int:
    """zone_id를 정수로 반환한다."""
    raw = tool_context.state.get("app:zone_id")
    if raw is None:
        raise KeyError("app:zone_id not in state")
    return int(raw)  # 타입 명시적 변환
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-025 | @docs/design/ref/team-operations.md § AW-025 | Hyrum's Law — 암묵적 계약 주의 |
| @AW-009 | @docs/design/ref/team-operations.md § AW-009 | ADR — API 변경 전 기록 |
| @AW-029 | @docs/design/ref/team-operations.md § AW-029 | Postel's Law — 입력 관대, 출력 엄격 |

## 참조

- @docs/design/ref/team-operations.md § AW-025
- @.claude/skills/convention-postels-law/SKILL.md
- @.claude/skills/convention-chestertons-fence/SKILL.md
