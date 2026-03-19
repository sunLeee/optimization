---
name: check-complexity
triggers:
  - "check complexity"
description: 코드 복잡도를 측정한다. Cyclomatic Complexity와 Maintainability Index를 계산한다.
argument-hint: "[path] [--threshold N] - 검사 경로, CC 임계값"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Bash
  - Read
  - Glob
model: claude-sonnet-4-6[1m]
context: 코드 복잡도 측정 스킬이다. radon을 사용하여 복잡도 메트릭을 계산한다.
agent: 당신은 코드 품질 분석가입니다. 복잡도 메트릭을 해석하고 개선 방향을 제시합니다.
hooks:
  pre_execution: []
  post_execution: []
category: 코드 검증
skill-type: Atomic
references: []
referenced-by:
  - "@skills/code-review/SKILL.md"

---
# check-complexity

코드 복잡도를 측정하는 스킬.

## 목적

- Cyclomatic Complexity 측정
- Maintainability Index 계산
- 리팩토링 대상 식별

## 사용법

```
/check-complexity                        # 전체 코드베이스 검사
/check-complexity src/                   # 특정 경로 검사
/check-complexity src/ --threshold 15    # 임계값 조정
```

## 복잡도 등급

| 등급 | CC 범위 | 설명 | 조치 |
|------|---------|------|------|
| **A** | 1-5 | 낮음 | 리스크 낮음 |
| **B** | 6-10 | 보통 | 관리 가능 |
| **C** | 11-20 | 높음 | 리팩토링 권장 |
| **D** | 21-30 | 매우 높음 | 리팩토링 필요 |
| **F** | 31+ | 위험 | 즉시 리팩토링 |

## 프로세스

```
/check-complexity [path]
    |
    v
[Step 1] radon 설치 확인
    |-- uv pip list | grep radon
    |-- (없으면) uv pip install radon
    |
    v
[Step 2] radon cc 실행
    |-- Cyclomatic Complexity 측정
    |-- 함수별 복잡도 수집
    |
    v
[Step 3] radon mi 실행
    |-- Maintainability Index 측정
    |-- 파일별 MI 점수
    |
    v
[Step 4] 결과 분석
    |-- 임계값 비교 (기본: 10)
    |-- 복잡도 순 정렬
    |-- 등급 부여
    |
    v
완료
```

## 예제

### 기본 검사

```
User: /check-complexity src/

Claude:
=== Complexity Check: src/ ===

[1/2] Cyclomatic Complexity 측정 중...
> radon cc src/ -a -s

[2/2] Maintainability Index 측정 중...
> radon mi src/ -s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
복잡도 상위 10개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| 순위 | 파일:함수 | CC | 등급 |
|------|----------|-----|------|
| 1 | services/payment.py:process_payment | 18 | C |
| 2 | api/routes/auth.py:login | 15 | C |
| 3 | core/validator.py:validate | 12 | C |
| 4 | utils/parser.py:parse_config | 9 | B |
| 5 | services/user.py:update_profile | 8 | B |
| 6 | api/routes/user.py:get_user | 7 | B |
| 7 | core/config.py:load_config | 6 | B |
| 8 | utils/cache.py:get_or_set | 5 | A |
| 9 | models/user.py:validate_email | 4 | A |
| 10 | db/queries.py:fetch_one | 3 | A |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
임계값 초과 (CC > 10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[C] services/payment.py:78 - process_payment (CC=18)
    → 결제 단계별로 함수 분리 권장
    → validate_payment(), charge_payment(), create_receipt()

[C] api/routes/auth.py:23 - login (CC=15)
    → 인증 로직 분리 권장
    → validate_credentials(), generate_token()

[C] core/validator.py:45 - validate (CC=12)
    → 검증 규칙을 개별 함수로 분리 권장

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
통계
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| 항목 | 값 |
|------|-----|
| 검사 함수 수 | 87 |
| 평균 CC | 4.5 |
| 최대 CC | 18 |
| 임계값 초과 | 3개 (3.4%) |

Maintainability Index: 65/100 (B)
  → 유지보수성 보통

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
등급 분포
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A (1-5):   ████████████████████████████████ 60%
B (6-10):  ████████████████████ 35%
C (11-20): ███ 5%
D (21-30): 0%
F (31+):   0%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
다음 단계
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. C 등급 함수 리팩토링 (3개)
2. /code-refactor로 리팩토링 지원 가능
```

## 관련 스킬

| 스킬명 | 관계 | 설명 |
|--------|------|------|
| [@skills/code-review/SKILL.md] | 부모 (Composite) | 통합 코드 리뷰 |
| [@skills/code-refactor/SKILL.md] | 후행 | 복잡한 코드 리팩토링 |
| [@skills/check-anti-patterns/SKILL.md] | 관련 | 안티패턴과 복잡도는 연관 |

## Changelog

| 날짜 | 변경 내용 |
|------|----------|
| 2026-01-21 | 초기 스킬 생성 |

## Gotchas (실패 포인트)

- Cyclomatic Complexity가 높다고 무조건 나쁜 것은 아님 — 분기가 필요한 상황 존재
- radon CC ≤ 10이 목표이나, ADK tool function은 분기가 많아 예외 허용 가능
- 리팩토링이 오히려 복잡도 증가시키는 경우 (helper 함수 남발) — 측정 후 결정
- MI (Maintainability Index) 20 이하는 urgent refactoring 필요 신호
