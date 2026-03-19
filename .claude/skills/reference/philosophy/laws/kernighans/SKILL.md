---
name: convention-kernighans-law
description: Kernighan's Law. 디버깅은 코딩보다 2배 어렵다. 코드를 최대한 단순하게 써야 디버깅할 수 있다.
user-invocable: true
triggers:
  - "kernighan"
  - "커니건의 법칙"
  - "디버깅 어렵"
  - "clever code"
---

# convention-kernighans-law

**@AW-027** | @docs/design/ref/team-operations.md § AW-027

Kernighan's Law: "디버깅은 코드를 작성하는 것보다 두 배 어렵다. 따라서, 코드를 최대한 영리하게 작성하면, 정의상 당신은 그것을 디버깅할 수 없다." (Brian Kernighan)

핵심: **clever code는 디버깅할 수 없다. 단순하게 써라.**

## VIOLATION 1: 너무 영리한 one-liner

```python
# VIOLATION: 영리하지만 디버깅 불가
# 6개월 후 이 코드에서 버그 발생 시 어디서 문제인지 알 수 없음
result = {z: sum(d for d in df[df.zone_id==z].demand if d>0)
          for z in set(df.zone_id) - {0}
          if any(df[df.zone_id==z].demand > 0)}
```

```python
# CORRECT: 단순하고 각 단계가 디버깅 가능
def get_positive_zone_demands(df: pd.DataFrame) -> dict[int, float]:
    """양수 수요를 가진 zone별 합계를 반환한다.

    Logics:
        1. zone_id=0 제외 (H3 null cell)
        2. zone별 수요 합산
        3. 양수인 것만 반환
    """
    # 각 단계를 분리 → 중간 결과 확인 가능
    valid_zones = df[df["zone_id"] != 0]           # 단계 1: 디버깅 가능
    zone_sums = valid_zones.groupby("zone_id")["demand"].sum()  # 단계 2
    return {int(z): float(v) for z, v in zone_sums.items() if v > 0}  # 단계 3
```

## VIOLATION 2: 압축된 중첩 표현식

```python
# VIOLATION: 중첩이 깊어 디버깅 불가
config = next(iter(filter(lambda x: x.get("active"),
    map(lambda p: {**p, "processed": True},
        [c for c in load_configs() if c.get("zone_id") in valid_zones]))))
```

```python
# CORRECT: 단계별 분리 (디버깅 가능한 형태)
def get_active_zone_config(valid_zones: set[int]) -> dict | None:
    """활성 zone의 첫 번째 설정을 반환한다."""
    all_configs = load_configs()

    # 단계 1: 유효한 zone 필터링
    zone_configs = [c for c in all_configs if c.get("zone_id") in valid_zones]

    # 단계 2: processed 플래그 추가
    processed = [{**c, "processed": True} for c in zone_configs]

    # 단계 3: 활성 설정 찾기
    active = [c for c in processed if c.get("active")]

    return active[0] if active else None
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-027 | @docs/design/ref/team-operations.md § AW-027 | Kernighan's Law |
| @AW-017 | @docs/design/ref/team-operations.md § AW-017 | KISS — 단순하게 |
| @AW-021 | @docs/design/ref/team-operations.md § AW-021 | Zen: Readability counts |

## 참조

- @docs/design/ref/team-operations.md § AW-027
- @.claude/skills/convention-kiss/SKILL.md
- @.claude/skills/convention-zen-python/SKILL.md
