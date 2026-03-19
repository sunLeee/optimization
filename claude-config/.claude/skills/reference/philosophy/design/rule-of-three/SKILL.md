---
name: convention-rule-of-three
description: Rule of Three. 코드가 3번 반복되면 리팩토링하라. 한 번은 괜찮고, 두 번은 주의, 세 번이면 추출.
user-invocable: true
triggers:
  - "rule of three"
  - "세 번 반복"
  - "리팩토링 기준"
  - "3번 쓰면"
---

# convention-rule-of-three

**@AW-038** | @docs/design/ref/team-operations.md § AW-038

Rule of Three: 같은 코드를 처음 쓸 때는 그냥 써라. 두 번째는 중복을 인식하라. 세 번째에는 반드시 리팩토링하라.

## VIOLATION 1: 세 곳에 같은 전처리 로직

```python
# VIOLATION: 동일한 전처리 로직이 3곳에 반복

# agents/demand_analyst/tools.py
def load_demand_data(tool_context: ToolContext) -> pd.DataFrame:
    df = pd.read_csv(tool_context.state["app:demand_file"])
    df = df.dropna()                          # 동일한 전처리
    df = df[df["demand"] >= 0]                # 동일한 필터링
    df = df.rename(columns={"zone": "zone_id"})  # 동일한 정규화
    return df

# agents/regional_analyst/tools.py
def load_regional_data(tool_context: ToolContext) -> pd.DataFrame:
    df = pd.read_csv(tool_context.state["app:regional_file"])
    df = df.dropna()                          # 반복
    df = df[df["demand"] >= 0]                # 반복
    df = df.rename(columns={"zone": "zone_id"})  # 반복
    return df

# agents/format_agent/tools.py
def load_format_data(tool_context: ToolContext) -> pd.DataFrame:
    df = pd.read_csv(tool_context.state["app:format_file"])
    df = df.dropna()                          # 3번째 반복 → 리팩토링 필요
    df = df[df["demand"] >= 0]
    df = df.rename(columns={"zone": "zone_id"})
    return df
```

```python
# CORRECT: 공통 전처리 함수로 추출 (libs/utils에 위치)
def preprocess_demand_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """수요 DataFrame을 전처리한다.

    Logics:
        1. 결측값 제거
        2. 음수 수요 필터링
        3. 컬럼 정규화 (zone → zone_id)
    """
    return (
        df.dropna()
          .loc[lambda x: x["demand"] >= 0]
          .rename(columns={"zone": "zone_id"})
    )

# 각 agent에서 재사용
def load_demand_data(tool_context: ToolContext) -> pd.DataFrame:
    df = pd.read_csv(tool_context.state["app:demand_file"])
    return preprocess_demand_dataframe(df)
```

## VIOLATION 2: 조건부 로직 3번 반복

```python
# VIOLATION: zone 유효성 검사 3곳에 반복
# create_zone.py
if zone_id < 0 or zone_id > 99999:
    raise ValueError(f"Invalid zone_id: {zone_id}")

# update_zone.py
if zone_id < 0 or zone_id > 99999:   # 반복
    raise ValueError(f"Invalid zone_id: {zone_id}")

# delete_zone.py
if zone_id < 0 or zone_id > 99999:   # 3번째 → 추출 필요
    raise ValueError(f"Invalid zone_id: {zone_id}")
```

```python
# CORRECT: 검증 함수로 추출 + @AW-018 DRY 적용
def validate_zone_id(zone_id: int) -> None:
    """zone_id 유효성을 검증한다."""
    if zone_id < 0 or zone_id > 99999:
        raise ValueError(f"Invalid zone_id: {zone_id}")

# 재사용
validate_zone_id(zone_id)  # 어디서든 동일하게
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-038 | @docs/design/ref/team-operations.md § AW-038 | Rule of Three |
| @AW-018 | @docs/design/ref/team-operations.md § AW-018 | DRY — 중복 제거 원칙과 연계 |
| @AW-035 | @docs/design/ref/team-operations.md § AW-035 | Boy Scout Rule — 발견 시 개선 |

## 참조

- @docs/design/ref/team-operations.md § AW-038
- @.claude/skills/convention-dry/SKILL.md
- @.claude/skills/convention-boy-scout-rule/SKILL.md
