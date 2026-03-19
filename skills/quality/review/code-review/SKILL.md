---
name: code-review
triggers:
  - "code review"
description: "코드 리뷰 오케스트레이션 복합 스킬. check-* 스킬들을 순차 실행하여 코드 품질을 종합 검증한다. 레드팀/블루팀 적대적 리뷰를 통해 취약점과 개선점을 도출한다."
argument-hint: "[경로] [--auto-adr] - 예: src/, --auto-adr로 ADR 자동 생성"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Skill
model: claude-sonnet-4-6[1m]
context: |
  check-python-style, check-security, check-complexity, check-anti-patterns를 순차 실행한 후,
  adversarial-review로 레드팀/블루팀 관점의 적대적 분석을 수행한다.
agent: |
  코드 리뷰어 페르소나. 객관적 검증과 적대적 분석을 통해 품질을 보장한다.
category: 코드 검증
skill-type: Composite
references:
  - "@skills/check-python-style/SKILL.md"
  - "@skills/check-security/SKILL.md"
  - "@skills/check-complexity/SKILL.md"
  - "@skills/check-anti-patterns/SKILL.md"
  - "@skills/adversarial-review/SKILL.md"
referenced-by:
  - "@skills/check-logging/SKILL.md"
  - "@skills/code-refactor/SKILL.md"
  - "@skills/subagent-driven-dev/SKILL.md"

---
# code-review

> 코드 리뷰 오케스트레이션 - check-* 스킬 순차 실행 + 적대적 리뷰

---

## 목적

1. **종합 검증**: 스타일, 보안, 복잡도, 안티패턴을 순차 검사
2. **적대적 분석**: 레드팀(공격)/블루팀(방어) 관점의 취약점 발굴
3. **우선순위 제시**: 발견된 이슈 중 Top 15 우선순위 산정
4. **최상의 버전 생성**: 모든 이슈를 반영한 개선 코드 제시

---

## 스킬 유형

**Composite Skill** - 다음 check 스킬들을 순차 조합:

| 순서 | 스킬 | 역할 |
|------|------|------|
| 1 | [@skills/check-python-style/SKILL.md] | PEP 8, 타입 힌트, docstring 검사 |
| 2 | [@skills/check-security/SKILL.md] | 보안 취약점 탐지 (Bandit 기반) |
| 3 | [@skills/check-complexity/SKILL.md] | Cyclomatic Complexity, Maintainability Index |
| 4 | [@skills/check-anti-patterns/SKILL.md] | God Class, Long Method, Circular Dependency |
| 5 | [@skills/adversarial-review/SKILL.md] | 레드팀/블루팀 적대적 분석 |

---

## 사용법

### 기본 사용

```bash
/code-review src/
```

모든 check 스킬을 순차 실행하여 종합 리뷰 보고서 생성

### ADR 자동 생성

```bash
/code-review src/ --auto-adr
```

발견된 주요 이슈를 ADR(Architecture Decision Record)로 자동 문서화

### 특정 파일만 검사

```bash
/code-review src/api/main.py
```

---

## 검사 구성

### 1. check-python-style

**검사 항목**:
- PEP 8 컨벤션 준수
- 타입 힌트 누락
- Docstring 스타일 (Google/NumPy)
- 네이밍 규칙 (snake_case, PascalCase)

**도구**: Ruff, Mypy

### 2. check-security

**검사 항목**:
- SQL injection 위험
- 하드코딩된 비밀 정보
- eval(), exec() 사용
- pickle 역직렬화

**도구**: Bandit

### 3. check-complexity

**검사 항목**:
- Cyclomatic Complexity (> 10 경고)
- Maintainability Index (< 20 경고)
- 함수 라인 수 (> 50 경고)

**도구**: Radon

### 4. check-anti-patterns

**검사 항목**:
- God Class (> 500줄, 20개 이상 메서드)
- Long Method (> 50줄)
- Feature Envy (타 클래스 의존도 높음)
- Circular Dependency

### 5. adversarial-review

**레드팀 분석** (공격자 관점):
- 입력 검증 우회 가능성
- 인증/권한 누락
- 에러 처리 취약점

**블루팀 분석** (방어자 관점):
- 보안 강화 방안
- 에러 핸들링 개선
- 테스트 커버리지 확대

**우선순위 15가지**: 발견된 모든 이슈를 심각도/영향도 기준으로 정렬

---

## 실행 프로세스

### Phase 1: 순차 검사

```
1. check-python-style 실행
   → 스타일 이슈 수집

2. check-security 실행
   → 보안 이슈 수집

3. check-complexity 실행
   → 복잡도 이슈 수집

4. check-anti-patterns 실행
   → 안티패턴 이슈 수집
```

### Phase 2: 적대적 리뷰

```
5. adversarial-review 실행
   → 레드팀 분석: 공격 가능성 검토
   → 블루팀 분석: 방어 방안 제시
   → 우선순위 15가지 산정
   → 최상의 버전 생성
```

### Phase 3: 보고서 생성

```
6. 종합 보고서 작성
   - 전체 이슈 요약
   - 심각도별 분류
   - 우선순위 Top 15
   - 개선 코드 제시
```

### Phase 4: ADR 생성 (선택)

```
7. --auto-adr 옵션 시
   - 주요 이슈를 ADR 문서화
   - docs/adr/ 디렉토리에 저장
```

---

## 코드 리뷰 결과

### 출력 형식

```markdown
## 코드 리뷰 결과

### 검사 요약

| 스킬 | 이슈 수 | 심각도 |
|------|---------|--------|
| check-python-style | 12 | 🟡 Warning |
| check-security | 3 | 🔴 Critical |
| check-complexity | 5 | 🟠 High |
| check-anti-patterns | 2 | 🟠 High |

### 우선순위 Top 15

1. 🔴 **SQL injection 위험** (src/api/db.py:45)
2. 🔴 **하드코딩된 API 키** (src/config.py:12)
3. 🟠 **Cyclomatic Complexity 25** (src/utils.py:process_data)
...

### 최상의 버전

[개선된 코드 전문]
```

**상세 출력 형식**: [@templates/skill-examples/code-review/adversarial-output.md]

---

## --auto-adr 모드

발견된 주요 이슈(우선순위 Top 5)를 ADR로 자동 문서화한다.

### ADR 템플릿

```markdown
# ADR-{번호}: {이슈 제목}

## Status
Proposed

## Context
{이슈 발견 경위}

## Decision
{해결 방안}

## Consequences
{긍정적/부정적 영향}

## Source
code-review ({날짜})
```

**생성 위치**: `docs/adr/ADR-XXX-{이슈명}.md`

---

## 통합 명령

### Pre-commit 연동

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: code-review
        name: Code Review
        entry: claude code /code-review
        language: system
        pass_filenames: false
```

### CI/CD 연동

**GitHub Actions**:
```yaml
- name: Code Review
  run: |
    claude code /code-review src/
    if [ $? -ne 0 ]; then exit 1; fi
```

**GitLab CI**:
```yaml
code_review:
  stage: test
  script:
    - claude code /code-review src/
  allow_failure: false
```

---

## 심각도 기준

| 심각도 | 아이콘 | 기준 |
|--------|--------|------|
| Critical | 🔴 | 보안 취약점, 데이터 손실 위험 |
| High | 🟠 | 성능 저하, 유지보수 어려움 |
| Medium | 🟡 | 컨벤션 위반, 개선 권장 |
| Low | 🟢 | 스타일 이슈, 선택 사항 |

---

## 관련 스킬

| 스킬 | 관계 | 설명 |
|------|------|------|
| [@skills/check-python-style/SKILL.md] | 하위 | Python 스타일 검사 |
| [@skills/check-security/SKILL.md] | 하위 | 보안 취약점 탐지 |
| [@skills/check-complexity/SKILL.md] | 하위 | 복잡도 측정 |
| [@skills/check-anti-patterns/SKILL.md] | 하위 | 안티패턴 탐지 |
| [@skills/adversarial-review/SKILL.md] | 하위 | 적대적 리뷰 |
| [@skills/setup-quality/SKILL.md] | 연계 | 품질 도구 초기 설정 |

---

## 주의사항

1. **실행 시간**: 대규모 프로젝트는 수 분 소요 가능
2. **False Positive**: 일부 경고는 오탐일 수 있음 (수동 검토 필요)
3. **ADR 덮어쓰기**: --auto-adr 재실행 시 기존 ADR 덮어씀

---

## 참조

- **Adversarial Review 가이드**: [@skills/adversarial-review/SKILL.md]
- **출력 템플릿**: [@templates/skill-examples/code-review/]
- **ADR 템플릿**: [@skills/doc-adr/SKILL.md]

---

## Changelog

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 2.1.0 | 2026-01-28 | user-invocable: false로 변경 (내부 검증 도구화) |
| 2.0.0 | 2026-01-27 | 보수적 리팩토링 - 741줄 → 250줄. 템플릿 분리 |
| 1.0.0 | 2026-01-21 | 초기 생성 |

## Gotchas (실패 포인트)

- 리뷰 범위: 요청된 파일만 — 인접 코드 개선 금지 (Surgical Changes 원칙)
- Composite 스킬이므로 check-* 스킬 실행 결과를 통합해야 함
- 15개 우선순위 이상 지적 시 핵심이 묻힘 — 상위 3-5개에 집중
- 스타일 지적과 로직 결함 지적을 명확히 구분
