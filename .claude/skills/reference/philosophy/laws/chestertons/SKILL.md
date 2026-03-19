---
name: convention-chestertons-fence
description: Chesterton's Fence. 이유를 모르면 제거하지 말라. 기존 코드/설정이 왜 존재하는지 이해 후 변경.
user-invocable: true
triggers:
  - "chesterton"
  - "이유 모르면"
  - "왜 있는지"
  - "레거시 코드"
  - "기존 코드 제거"
---

# convention-chestertons-fence

**@AW-026** | @docs/design/ref/team-operations.md § AW-026

Chesterton's Fence: "울타리가 왜 거기 있는지 이해하기 전에는 제거하지 말라." 기존 코드가 이상해 보여도, 이유가 있을 수 있다.

## VIOLATION 1: 이유 없이 "불필요해 보이는" 검사 제거

```python
# 기존 코드 — "불필요해 보임"
def load_zone_config(zone_id: int) -> dict:
    if zone_id == 0:                     # 왜 0을 특별 처리?
        return get_default_config()
    if zone_id > 99999:                  # 왜 이 상한선?
        raise ValueError(f"Invalid: {zone_id}")
    return zone_db.get(zone_id)

# VIOLATION: 이유 모르고 제거
def load_zone_config(zone_id: int) -> dict:
    # "0 체크 불필요해 보여서 제거" — Chesterton's Fence 위반
    # "99999 제한 이유 모르지만 제거" — 위반
    return zone_db.get(zone_id)
    # 결과: zone_id=0이 H3 null cell이었음을 나중에 발견
    # 결과: zone_id>99999가 legacy DB 제한이었음을 나중에 발견
```

```python
# CORRECT: 이유 먼저 파악 (git blame, ADR, 팀원 문의) 후 결정
def load_zone_config(zone_id: int) -> dict:
    """zone 설정을 반환한다.

    Logics:
        zone_id=0: H3 null cell — 기본 설정 반환 (ADR-001)
        zone_id>99999: legacy DB 상한 — 검증 필요 (ADR-007)
    """
    if zone_id == 0:           # ADR-001: H3 null cell 처리
        return get_default_config()
    if zone_id > 99999:        # ADR-007: legacy DB 상한선
        raise ValueError(f"Invalid zone_id: {zone_id}")
    return zone_db.get(zone_id)
```

## VIOLATION 2: 레거시 설정 파일 임의 수정

```python
# 기존 config.yaml에 있는 항목
# retry_count: 5       # 왜 5? 줄이면 성능 개선될 것 같은데

# VIOLATION: 이유 모르고 변경
# retry_count: 2       # "빠를 것 같아서" — Chesterton's Fence 위반
# 결과: 외부 API 타임아웃이 가끔 발생하는 환경이었음을 나중에 발견

# CORRECT: git log / ADR 확인 후 주석 추가
# retry_count: 5  # ADR-018: 외부 API 불안정 시 최소 5회 필요
```

## 체크리스트

코드/설정 제거 전 확인:
- [ ] `git blame`으로 누가, 언제, 왜 추가했는지 확인
- [ ] 관련 ADR/이슈 검색 (`docs/adr/`, GitHub issues)
- [ ] 팀원에게 맥락 문의 (Slack, PR 댓글)
- [ ] 제거 후 어떤 동작이 바뀌는지 테스트로 검증

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-026 | @docs/design/ref/team-operations.md § AW-026 | Chesterton's Fence |
| @AW-009 | @docs/design/ref/team-operations.md § AW-009 | ADR — 결정 근거 기록 |
| Surgical Changes | CLAUDE.md § LLM 행동지침 | 반드시 수정할 것만 건드려라 |

## 참조

- @docs/design/ref/team-operations.md § AW-026
- @docs/adr/ — 결정 근거 참조
- @.claude/skills/convention-adr/SKILL.md
