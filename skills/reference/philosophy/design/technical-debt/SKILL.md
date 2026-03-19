---
name: convention-technical-debt
description: Technical Debt (기술 부채). 빠른 해결책은 이자를 낸다. 의도적 vs 비의도적 부채를 구분하고 관리한다.
user-invocable: true
triggers:
  - "technical debt"
  - "기술 부채"
  - "TODO"
  - "임시 해결책"
  - "workaround"
---

# convention-technical-debt

**@AW-041** | @docs/design/ref/team-operations.md § AW-041

Technical Debt: 빠른 해결책을 선택하면 미래에 이자를 지불한다. 부채를 인식하고, 의도적으로 관리하고, 상환 계획을 세운다.

## VIOLATION 1: 비의도적 부채 — 인식 없이 쌓이는 부채

```python
# VIOLATION: 문서화 없는 임시 해결책 — 비의도적 부채
def get_zone_data(zone_id: int) -> pd.DataFrame:
    # TODO: 이거 나중에 고쳐야 함
    # 일단 파일을 직접 읽음 (임시)
    return pd.read_csv(f"/tmp/zone_{zone_id}.csv")

# 문제:
# 1. "나중에"가 언제인지 모름
# 2. 왜 임시인지 이유 없음
# 3. 팀원이 이 코드에 의존하기 시작함
```

```python
# CORRECT: 의도적 부채 — 명시적으로 문서화
def get_zone_data(zone_id: int) -> pd.DataFrame:
    """zone 데이터를 반환한다.

    Logics:
        임시: 파일 직접 접근. 추후 API 연결 예정.

    Note:
        TECH-DEBT-001: 임시 파일 접근 방식.
        이유: API 서버 준비 전 빠른 프로토타입 필요.
        상환 계획: API 서버 준비 후 (예상: 2026-04-01).
        영향 범위: 이 함수만 변경 필요.
    """
    # TECH-DEBT-001: 임시 파일 접근 — 추후 API 연결
    return pd.read_csv(f"/tmp/zone_{zone_id}.csv")
```

## VIOLATION 2: 부채 미상환 — 이자 누적

```python
# 6개월 전: "임시" 해결책
# VIOLATION: 임시 코드가 프로덕션에서 핵심 로직이 됨
class ZoneProcessor:
    def __init__(self) -> None:
        # 임시: hardcoded config (추후 config 파일로 이동)
        self.max_zones = 100          # 변경하려면 코드 수정 필요
        self.timeout = 30             # 여기저기 의존
        self.retry_count = 3          # 테스트도 이 값에 의존

    # ... 수백 줄의 코드가 이 값들에 의존함
```

```python
# CORRECT: 부채를 ADR로 기록하고 상환 계획 수립
# docs/adr/ADR-027-zone-processor-config.md 작성 후:
class ZoneProcessor:
    def __init__(self, config: ZoneProcessorConfig) -> None:
        """ZoneProcessor를 초기화한다.

        Args:
            config: 프로세서 설정. OmegaConf에서 주입.
        """
        self.config = config  # 설정 외부화 완료

# @.claude/skills/convention-adr/SKILL.md 참조
```

## 부채 유형 분류

| 유형 | 설명 | 대응 |
|------|------|------|
| 의도적/신중한 | 알면서 선택 + 문서화 | ADR 작성, 상환 계획 |
| 의도적/무모한 | "나중에 고치면 됨" | 코드 리뷰로 차단 |
| 비의도적/신중한 | 몰랐지만 발견 후 기록 | TECH-DEBT 태그 + 이슈 |
| 비의도적/무모한 | 발견 못하는 부채 | adversarial-review로 탐지 |

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-041 | @docs/design/ref/team-operations.md § AW-041 | Technical Debt — 의도적 관리 |
| @AW-009 | @docs/design/ref/team-operations.md § AW-009 | ADR — 부채 결정 기록 |
| @AW-035 | @docs/design/ref/team-operations.md § AW-035 | Boy Scout Rule — 작은 부채 상환 |

## 참조

- @docs/design/ref/team-operations.md § AW-041
- @docs/adr/ — 부채 결정 기록
- @.claude/skills/convention-adr/SKILL.md
- @.claude/skills/convention-boy-scout-rule/SKILL.md
