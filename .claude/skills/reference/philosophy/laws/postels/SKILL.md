---
name: convention-postels-law
description: Postel's Law (Robustness Principle). 보내는 것은 엄격하게, 받는 것은 관대하게.
user-invocable: true
triggers:
  - "postel"
  - "robustness principle"
  - "견고성 원칙"
  - "입력 관대"
---

# convention-postels-law

**@AW-029** | @docs/design/ref/team-operations.md § AW-029

Postel's Law: "보내는 것은 엄격하게 하고, 받는 것은 관대하게 하라." (Jon Postel, TCP/IP RFC 793)

- **입력(수신)**: 다양한 형식, 타입, 빠진 필드를 관대하게 처리
- **출력(송신)**: 항상 명세를 정확히 지키는 형식으로 전송

## VIOLATION 1: 입력에 너무 엄격

```python
# VIOLATION: zone_id를 int만 받음 → "123", 123.0 등 거절
def process_zone(zone_id: int) -> dict:
    if not isinstance(zone_id, int):   # 너무 엄격 — Postel's Law 위반
        raise TypeError("zone_id는 int여야 합니다")
    return zone_db.get(zone_id)

# 사용자가 "123" (문자열)이나 123.0 (float)을 넘기면 실패
```

```python
# CORRECT: 입력은 관대하게 (자동 변환), 출력은 엄격하게
def process_zone(zone_id: int | str | float) -> dict:
    """zone 데이터를 처리한다.

    Logics:
        zone_id를 int로 정규화 후 처리한다.
        입력 타입은 관대하게 허용, 반환값은 명세 준수.
    """
    # 입력: 관대하게 수용 + 정규화
    try:
        normalized_id = int(zone_id)
    except (ValueError, TypeError) as e:
        raise ValueError(f"zone_id 변환 불가: {zone_id!r}") from e

    # 처리
    result = zone_db.get(normalized_id)

    # 출력: 엄격하게 (항상 dict 반환)
    return result if result is not None else {}
```

## VIOLATION 2: ADK tool에서 입력 타입 과도하게 제한

```python
# VIOLATION: state의 값이 str일 수도 있는데 int만 허용
def analyze_zone(tool_context: ToolContext) -> dict:
    zone_id = tool_context.state["app:zone_id"]
    if not isinstance(zone_id, int):   # state는 종종 str로 저장됨
        raise TypeError("zone_id는 int여야 합니다")
```

```python
# CORRECT: 입력 관대 + 출력 엄격
def analyze_zone(tool_context: ToolContext) -> dict:
    """zone을 분석한다.

    Logics:
        state의 zone_id를 관대하게 수용하고 결과를 명확한 구조로 반환.
    """
    # 입력: 관대하게 수용
    raw_zone_id = tool_context.state.get("app:zone_id", 0)
    zone_id = int(raw_zone_id)  # str/float/int 모두 처리

    result = zone_db.get(zone_id, {})

    # 출력: 항상 명세된 구조로 반환
    return {
        "zone_id": zone_id,           # 정규화된 int
        "demand": float(result.get("demand", 0.0)),  # 항상 float
        "found": bool(result),        # 항상 bool
    }
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-029 | @docs/design/ref/team-operations.md § AW-029 | Postel's Law |
| @AW-025 | @docs/design/ref/team-operations.md § AW-025 | Hyrum's Law — 출력 명세 |
| Type Hint | CLAUDE.md § 코드 스타일 | 반환 타입 명시 (엄격한 출력) |

## 참조

- @docs/design/ref/team-operations.md § AW-029
- @.claude/skills/convention-hyrums-law/SKILL.md
- @.claude/skills/convention-adk-agent/SKILL.md
