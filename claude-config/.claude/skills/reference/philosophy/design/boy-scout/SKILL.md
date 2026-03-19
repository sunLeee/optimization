---
name: convention-boy-scout-rule
description: Boy Scout Rule (보이스카우트 규칙). 캠프장은 왔을 때보다 깨끗하게. 코드를 건드릴 때 조금 더 나은 상태로 남겨라.
user-invocable: true
triggers:
  - "boy scout"
  - "보이스카우트"
  - "점진적 개선"
  - "코드 청소"
---

# convention-boy-scout-rule

**@AW-035** | @docs/design/ref/team-operations.md § AW-035

Boy Scout Rule: "캠프장을 왔을 때보다 조금 더 깨끗하게 남겨라." 코드를 수정할 때, 수정 범위를 벗어나지 않되 근처의 작은 문제를 함께 개선한다. 점진적으로 코드 품질을 높인다.

## VIOLATION 1: 버그 수정 중 주변 코드 방치

```python
# 현재 코드: load_demand_data()에서 버그 발견 (인코딩 하드코딩)
# 수정 범위: 인코딩만

# VIOLATION: 버그만 고치고 명백한 문제를 그냥 지나침
def load_demand_data(file_path):  # type hint 없음 — 오래된 코드
    # 버그: encoding 하드코딩 → utf-8로 수정
    df = pd.read_csv(file_path, encoding="utf-8")  # ← 버그 수정 완료
    # 아래 문제들을 그냥 두고 감
    result = []
    for i in range(len(df)):    # iterrows 안티패턴 — 방치
        result.append(df.iloc[i]["demand"])
    return result
```

```python
# CORRECT: 버그 수정 + 근처 작은 문제도 함께 개선 (범위 내에서)
def load_demand_data(file_path: str) -> pd.Series:  # type hint 추가
    """수요 데이터를 로드한다.

    Logics:
        UTF-8 인코딩으로 CSV를 읽고 demand 컬럼을 반환한다.
    """
    df = pd.read_csv(file_path, encoding="utf-8")     # 버그 수정
    return df["demand"]                                # vectorized로 개선 (Boy Scout)
# 단: 관련 없는 다른 함수는 건드리지 않음 (Surgical Changes)
```

## VIOLATION 2: docstring 없는 함수 그냥 지나침

```python
# 버그 수정 중 발견한 함수 — docstring이 없음
def aggregate_zones(df: pd.DataFrame, method: str) -> pd.DataFrame:
    # VIOLATION: 버그와 무관하지만 docstring이 없어 이해 어려움 → 그냥 둠
    return df.groupby("zone_id")[method].sum()

# CORRECT: docstring 추가 (Boy Scout — 작은 개선)
def aggregate_zones(df: pd.DataFrame, method: str) -> pd.DataFrame:
    """zone별 집계를 수행한다.

    Args:
        df: 집계 대상 DataFrame.
        method: 집계할 컬럼명.

    Returns:
        zone_id별 합계 DataFrame.

    Logics:
        groupby로 zone_id 기준 합계를 계산한다.
    """
    return df.groupby("zone_id")[method].sum()
```

## Boy Scout vs Surgical Changes 경계

```
수정 중 발견한 문제:

작은 문제 (Boy Scout 적용):        대형 리팩토링 (건드리지 않음):
- docstring 누락                   - 클래스 구조 재설계
- type hint 누락                   - 모듈 분리
- iterrows → vectorized (근처 코드) - API 인터페이스 변경
- 명백한 오타
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-035 | @docs/design/ref/team-operations.md § AW-035 | Boy Scout Rule |
| Surgical Changes | CLAUDE.md § LLM 행동지침 | 반드시 수정할 것만 건드려라 (경계 명시) |
| @AW-010 | @docs/design/ref/team-operations.md § AW-010 | pre-commit이 Boy Scout 변경도 검증 |

## 참조

- @docs/design/ref/team-operations.md § AW-035
- @.claude/skills/convention-dry/SKILL.md
- @.claude/skills/check-anti-patterns/SKILL.md
