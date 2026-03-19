---
name: convention-worse-is-better
description: Worse Is Better (Richard Gabriel). 단순한 인터페이스 > 완벽한 구현. 80% 해결책이 먼저 작동하고 개선된다.
user-invocable: true
triggers:
  - "worse is better"
  - "worse-is-better"
  - "단순한 인터페이스"
  - "80% 해결책"
---

# convention-worse-is-better

**@AW-036** | @docs/design/ref/team-operations.md § AW-036

Worse Is Better (Richard Gabriel, 1989): "단순한 인터페이스와 구현이 완벽한 인터페이스와 복잡한 구현보다 낫다." 작동하는 80% 해결책이 완벽한 100% 해결책보다 더 가치 있을 수 있다.

## 두 철학 비교

| MIT 방식 (The Right Thing) | New Jersey 방식 (Worse Is Better) |
|---|---|
| 인터페이스가 완벽해야 함 | 인터페이스는 단순해야 함 |
| 구현이 복잡해도 됨 | 구현도 단순해야 함 |
| 모든 엣지케이스 처리 | 80% 케이스만 처리, 나머지는 나중에 |
| 출시가 늦어짐 | 빠르게 작동하고 개선 |

## VIOLATION: 완벽한 인터페이스를 위해 출시 지연

```python
# VIOLATION: 모든 케이스를 처음부터 완벽하게 처리
class DemandAnalyzer:
    def analyze(
        self,
        file_path: str | Path | io.TextIOWrapper | pd.DataFrame,
        encoding: str = "utf-8",
        delimiter: str = ",",
        zone_filter: list[int] | None = None,
        date_range: tuple[str, str] | None = None,
        aggregation: Literal["sum", "mean", "max"] = "sum",
        output_format: Literal["dict", "dataframe", "json"] = "dict",
    ) -> dict | pd.DataFrame | str:
        # 모든 케이스 처리하다가 출시 못함
        ...
```

```python
# CORRECT (Worse Is Better): 단순하게 작동하는 것부터
def analyze_demand(file_path: str) -> dict[int, float]:
    """zone별 수요 합계를 반환한다.

    Logics:
        CSV를 읽어 zone_id별 demand 합계를 계산한다.
        엣지케이스는 사용자 피드백 후 추가.
    """
    df = pd.read_csv(file_path)  # CSV만 지원 (우선)
    return df.groupby("zone_id")["demand"].sum().to_dict()
    # 개선은 실제 필요가 생기면: @AW-019 YAGNI
```

## 언제 적용할까

**Worse Is Better 적용:**
- 프로토타입, MVP
- 요구사항이 불명확한 초기 단계
- 빠른 피드백이 필요한 상황

**완벽한 설계 필요:**
- 공개 API (변경 불가)
- 보안 관련 기능
- 데이터 손실 위험 있는 부분 (@AW-009 ADR 필수)

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-036 | @docs/design/ref/team-operations.md § AW-036 | Worse Is Better |
| @AW-019 | @docs/design/ref/team-operations.md § AW-019 | YAGNI — 필요한 것만 |
| @AW-023 | @docs/design/ref/team-operations.md § AW-023 | Gall's Law — 단순부터 |

## 참조

- @docs/design/ref/team-operations.md § AW-036
- @.claude/skills/convention-yagni/SKILL.md
- @.claude/skills/convention-galls-law/SKILL.md
