---
name: convention-cqs
description: CQS (Command-Query Separation). 함수는 질문하거나 명령하거나 — 둘 다 동시에 하지 않는다.
user-invocable: true
triggers:
  - "CQS"
  - "command query separation"
  - "side effect"
  - "질문과 명령"
---

# convention-cqs

**@AW-033** | @docs/design/ref/team-operations.md § AW-033

CQS: 모든 메서드는 둘 중 하나여야 한다.
- **Command**: 상태를 변경한다. 값을 반환하지 않는다. (`-> None`)
- **Query**: 정보를 반환한다. 상태를 변경하지 않는다. (side effect 없음)

## VIOLATION 1: ADK tool에서 조회와 저장을 동시에

```python
# VIOLATION: load()가 데이터를 읽고 + state를 수정하고 + 결과를 반환
def load_and_cache_demand(tool_context: ToolContext) -> pd.DataFrame:
    file_path = tool_context.state["app:demand_file"]
    df = pd.read_csv(file_path)

    # Query 역할 (데이터 반환) + Command 역할 (state 수정) 동시 수행 — CQS 위반
    tool_context.state["agent:demand_loaded"] = True    # side effect
    tool_context.state["agent:zone_count"] = len(df)    # side effect

    return df  # 반환도 함
```

```python
# CORRECT: Query와 Command를 분리
def load_demand_data(tool_context: ToolContext) -> pd.DataFrame:
    """수요 데이터를 조회한다. (Query — side effect 없음)

    Logics:
        state에서 경로를 읽어 DataFrame을 반환한다.
    """
    file_path = tool_context.state["app:demand_file"]
    return pd.read_csv(file_path)

def mark_demand_loaded(tool_context: ToolContext, zone_count: int) -> None:
    """수요 로딩 완료를 기록한다. (Command — 반환값 없음)

    Logics:
        state에 로딩 상태와 zone 수를 기록한다.
    """
    tool_context.state["agent:demand_loaded"] = True
    tool_context.state["agent:zone_count"] = zone_count
```

## VIOLATION 2: 데이터베이스 저장과 조회를 혼합

```python
# VIOLATION: save()가 저장하고 저장된 id를 반환 + 카운터도 증가
def save_result(result: dict) -> int:
    record = database.insert(result)          # Command: 저장
    stats.increment("saved_count")            # Command: 카운터 증가
    return record.id                          # Query: id 반환 — CQS 위반
```

```python
# CORRECT: 저장과 조회 분리
def save_result(result: dict) -> None:
    """결과를 저장한다. (Command)"""
    record = database.insert(result)
    stats.increment("saved_count")

def get_last_result_id() -> int:
    """마지막 저장 id를 반환한다. (Query)"""
    return database.last_insert_id()
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-033 | @docs/design/ref/team-operations.md § AW-033 | CQS — 질문과 명령 분리 |
| @AW-034 | @docs/design/ref/team-operations.md § AW-034 | Tell, Don't Ask — 연계 원칙 |
| File Path Pattern | CLAUDE.md § File Path Pattern | tool function은 Command (state 수정) 또는 Query |

## 참조

- @docs/design/ref/team-operations.md § AW-033
- @.claude/skills/convention-tell-dont-ask/SKILL.md
- @.claude/skills/convention-solid-srp/SKILL.md
