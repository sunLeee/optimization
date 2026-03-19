---
name: convention-least-astonishment
description: Principle of Least Astonishment (POLA). 사용자/개발자를 놀라게 하지 말라. 직관적이고 예측 가능하게 설계.
user-invocable: true
triggers:
  - "least astonishment"
  - "pola"
  - "놀라지 않게"
  - "예측 가능"
---

# convention-least-astonishment

**@AW-039** | @docs/design/ref/team-operations.md § AW-039

Principle of Least Astonishment (POLA): "시스템은 사용자를 놀라게 하는 방식이 아닌, 예상 가능한 방식으로 동작해야 한다." 함수 이름, 반환값, 사이드 이펙트가 모두 직관적이어야 한다.

## VIOLATION 1: 이름과 동작이 다름

```python
# VIOLATION: get_은 조회인데 수정까지 함 — 놀랍다
def get_zone_demand(tool_context: ToolContext) -> dict:
    zone_id = tool_context.state["app:zone_id"]
    result = zone_db.get(zone_id)
    # 놀라운 사이드 이펙트: 조회하면서 카운터 증가
    tool_context.state["agent:query_count"] += 1  # 예상 밖 동작
    zone_db.update_last_accessed(zone_id)          # 예상 밖 동작
    return result
```

```python
# CORRECT: 이름과 동작 일치 (CQS + POLA)
def get_zone_demand(tool_context: ToolContext) -> dict:
    """zone 수요를 조회한다. 상태 변경 없음.

    Logics:
        zone_id로 DB를 조회하여 수요 데이터를 반환한다.
    """
    zone_id = int(tool_context.state["app:zone_id"])
    return zone_db.get(zone_id) or {}  # 조회만, 수정 없음

def record_zone_query(tool_context: ToolContext) -> None:
    """zone 조회 이력을 기록한다. (별도 명시적 함수)"""
    tool_context.state["agent:query_count"] = (
        tool_context.state.get("agent:query_count", 0) + 1
    )
```

## VIOLATION 2: 반환값이 예상과 다름

```python
# VIOLATION: filter_라는 이름인데 원본을 수정
def filter_positive_demand(df: pd.DataFrame) -> pd.DataFrame:
    # 놀랍다: 원본 df도 수정됨 (예상 밖)
    df.drop(df[df["demand"] <= 0].index, inplace=True)
    return df

# 사용자는 원본 df가 유지된다고 기대했는데 수정됨
original = demand_df.copy()
filtered = filter_positive_demand(demand_df)
# demand_df가 바뀌어 있어 놀람
```

```python
# CORRECT: 원본 불변, 새 DataFrame 반환 (예측 가능)
def filter_positive_demand(df: pd.DataFrame) -> pd.DataFrame:
    """양수 수요만 포함한 새 DataFrame을 반환한다.

    Logics:
        원본 df를 수정하지 않고 필터링된 복사본을 반환한다.
    """
    return df[df["demand"] > 0].copy()  # 원본 불변
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-039 | @docs/design/ref/team-operations.md § AW-039 | Least Astonishment |
| @AW-033 | @docs/design/ref/team-operations.md § AW-033 | CQS — 예측 가능한 분리 |
| @AW-021 | @docs/design/ref/team-operations.md § AW-021 | Zen: Explicit > Implicit |

## 참조

- @docs/design/ref/team-operations.md § AW-039
- @.claude/skills/convention-cqs/SKILL.md
- @.claude/skills/convention-zen-python/SKILL.md
