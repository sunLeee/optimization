---
name: convention-simple-design
description: Four Rules of Simple Design (Kent Beck). 테스트 통과 > 의도 표현 > 중복 없음 > 최소 요소. 우선순위 순서로 적용.
user-invocable: true
triggers:
  - "simple design"
  - "kent beck"
  - "4 rules"
  - "단순한 설계"
---

# convention-simple-design

**@AW-043** | @docs/design/ref/team-operations.md § AW-043

Kent Beck의 단순한 설계 4원칙 (우선순위 순서):
1. **테스트를 통과한다** (작동해야 함)
2. **의도를 표현한다** (읽을 수 있어야 함)
3. **중복이 없다** (DRY 적용)
4. **요소가 최소화되어 있다** (불필요한 복잡성 제거)

## VIOLATION 1: 의도 표현 없는 코드

```python
# VIOLATION: 작동하지만 의도가 불명확 (Rule 2 위반)
def f(df: pd.DataFrame, t: float) -> pd.DataFrame:
    return df[df["d"] > t * df["d"].mean()]

# 테스트는 통과하지만 6개월 후 누구도 이해 못함
```

```python
# CORRECT: Rule 1 (작동) + Rule 2 (의도 표현) 모두 만족
def filter_high_demand_zones(
    df: pd.DataFrame, threshold_multiplier: float = 1.5
) -> pd.DataFrame:
    """평균 대비 임계값 이상의 수요를 가진 zone을 필터링한다.

    Logics:
        threshold = 평균 수요 × threshold_multiplier
        threshold를 초과하는 zone만 반환한다.
    """
    mean_demand = df["demand"].mean()
    threshold = mean_demand * threshold_multiplier
    return df[df["demand"] > threshold]
```

## VIOLATION 2: 4가지 원칙의 우선순위 혼동

```python
# VIOLATION: Rule 4(최소화)를 Rule 1(통과)보다 우선시
def analyze(df: pd.DataFrame) -> dict:
    # "코드를 짧게 만들어야 해" → 테스트 불가능한 압축
    return {k: v for k, v in
            {z: sum(df[df.zone_id==z].demand) for z in df.zone_id.unique()}.items()
            if v > 0}

# 하나의 표현식이지만 테스트하기 어렵고 의도 불명확
```

```python
# CORRECT: 우선순위대로 — Rule 1 먼저, 그 다음 Rule 2, 3, 4
def get_positive_zone_demands(df: pd.DataFrame) -> dict[int, float]:
    """양수 수요를 가진 zone별 합계를 반환한다.

    Logics:
        zone_id별 수요를 합산하고 양수인 것만 반환한다.
    """
    # Rule 1: 테스트 가능 (함수 단위)
    # Rule 2: 의도 명확 (함수명 + docstring)
    zone_demands = df.groupby("zone_id")["demand"].sum()   # Rule 3: DRY
    return {int(z): float(v) for z, v in zone_demands.items() if v > 0}
    # Rule 4: 필요한 복잡성만 (4보다 더 줄이면 Rule 2 위반)
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-043 | @docs/design/ref/team-operations.md § AW-043 | Simple Design 4원칙 |
| @AW-018 | @docs/design/ref/team-operations.md § AW-018 | DRY — Rule 3 |
| @AW-017 | @docs/design/ref/team-operations.md § AW-017 | KISS — Rule 4 |

## 참조

- @docs/design/ref/team-operations.md § AW-043
- @.claude/skills/convention-dry/SKILL.md
- @.claude/skills/convention-kiss/SKILL.md
