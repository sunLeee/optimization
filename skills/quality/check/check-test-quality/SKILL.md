---
name: check-test-quality
triggers:
  - "check test quality"
description: 테스트 코드 품질 검증 스킬. 테스트 구조, AAA 패턴, 커버리지, 명명 규칙 준수 여부를 검사한다. convention-testing 스킬의 규칙을 기반으로 검증을 수행한다.
argument-hint: "[파일 경로] - 검증할 테스트 파일 또는 디렉토리"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
model: claude-sonnet-4-6[1m]
context: 테스트 코드의 품질과 컨벤션 준수 여부를 검증한다. convention-testing 스킬에 정의된 규칙을 기준으로 검사하며, pytest 도구를 활용하여 커버리지와 테스트 실행을 검증한다.
agent: 테스트 코드 품질 검증 전문가. 테스트의 구조적 품질과 효과성을 평가하고 개선점을 제시한다. AAA 패턴, 명명 규칙, 커버리지 기준 준수를 검증한다.
hooks:
  pre_execution: []
  post_execution: []
category: 코드 검증
skill-type: Atomic
references:
  - "@skills/convention-testing/SKILL.md"
referenced-by:
  - "@skills/convention-testing/SKILL.md"

---
# 테스트 품질 검증

테스트 코드의 품질과 컨벤션 준수 여부를 검증한다.

## 목적

- 테스트 구조 및 디렉토리 구성 검증
- AAA 패턴 준수 확인
- 테스트 명명 규칙 검증
- 커버리지 기준 충족 확인
- Fixtures 및 Mocking 사용 적절성 검토

## 사용법

```
/check-test-quality [파일 경로]
/check-test-quality tests/
/check-test-quality tests/unit/test_utils.py
```

---

## 검증 프로세스

### 1단계: 테스트 실행 및 커버리지

```bash
# 테스트 실행
pytest <path> -v

# 커버리지 측정
pytest <path> --cov=src --cov-report=term-missing

# 커버리지 기준 검사
pytest <path> --cov=src --cov-fail-under=70
```

### 2단계: 구조 검증

테스트 파일 구조가 컨벤션을 따르는지 확인:

```
tests/
├── conftest.py          # 공통 fixtures ✓
├── unit/                # 단위 테스트 ✓
├── integration/         # 통합 테스트 ✓
└── e2e/                 # E2E 테스트 (선택)
```

### 3단계: 코드 분석

각 테스트 함수를 분석하여 다음을 검증:

| 항목 | 검사 내용 |
|------|----------|
| 명명 규칙 | `test_<function>_<scenario>_<expected>` 형식 |
| AAA 패턴 | Arrange-Act-Assert 구조 준수 |
| Docstring | 테스트 목적 설명 존재 |
| Assert | 명확한 검증문 존재 |
| 독립성 | 다른 테스트에 의존하지 않음 |

### 4단계: 결과 보고

```markdown
## 테스트 품질 검증 결과

### 요약
- 테스트 파일: 8개
- 테스트 함수: 45개
- 통과: 42개
- 위반: 3개
- 커버리지: 78%

### 커버리지 분석
| 모듈 | 커버리지 | 기준 | 상태 |
|------|----------|------|------|
| src/utils | 92% | 80% | ✓ |
| src/api | 65% | 80% | ✗ |
| src/models | 85% | 80% | ✓ |

### 위반 목록

#### 구조 위반
| 파일 | 문제 | 권장 사항 |
|------|------|----------|
| tests/test_all.py | 테스트 유형 미분류 | unit/, integration/ 분리 |

#### 명명 규칙 위반
| 파일 | 라인 | 현재 이름 | 권장 이름 |
|------|------|----------|----------|
| test_utils.py | 15 | test_func | test_process_data_with_null_returns_empty |

#### AAA 패턴 위반
| 파일 | 라인 | 문제 |
|------|------|------|
| test_api.py | 45 | Arrange 섹션 없음 |
```

---

## 검증 규칙

**이 스킬은 검증(validation)만 수행합니다.**
**규칙 정의는 [@skills/convention-testing/SKILL.md] 스킬을 참조하세요.**

→ `@skills/convention-testing/SKILL.md`

### 검증 항목 요약

| 카테고리 | 검증 내용 | 심각도 |
|----------|----------|--------|
| **명명 규칙** | `test_<function>_<scenario>_<expected>` 형식 | Critical/Warning |
| **AAA 패턴** | Arrange-Act-Assert 구조 준수 | Critical/Warning |
| **커버리지** | 핵심 90%, 유틸 80%, 전체 70% | Critical/Warning |
| **구조** | conftest.py, unit/integration 분리 | Warning/Info |

**상세 규칙 (AAA 패턴 예시, Fixtures 스코프, Mocking 방법 등)**: `/convention-testing` 실행

### 심각도 기준

| 심각도 | 의미 | 동작 |
|--------|------|------|
| Critical | 테스트 신뢰성 저하 | 즉시 수정 필요 |
| Warning | 유지보수성 저하 | 수정 권장 |
| Info | 개선 권장 | 선택적 수정 |

---

## 예시

### 예시 1: 테스트 디렉토리 검증

```
/check-test-quality tests/
```

**출력**:
```
## 테스트 품질 검증 결과

### 요약
- 테스트 파일: 5개
- 테스트 함수: 28개
- 통과: 25개
- 위반: 3개
- 커버리지: 82%

### 커버리지 ✓
전체 커버리지 82%로 기준(70%) 충족

### 위반 목록

#### Critical
없음

#### Warning
| 파일 | 라인 | 규칙 | 설명 |
|------|------|------|------|
| test_api.py | 12 | NAMING | test_api → test_get_users_returns_list |
| test_utils.py | 45 | AAA | Arrange 섹션 주석 권장 |

### 권장 수정 사항
1. test_api.py:12 - 테스트 이름을 명확하게 변경
2. test_utils.py:45 - `# Arrange`, `# Act`, `# Assert` 주석 추가
```

### 예시 2: 단일 파일 검증

```
/check-test-quality tests/unit/test_models.py
```

**출력**:
```
## 테스트 품질 검증 결과

### 요약
- 테스트 함수: 8개
- 통과: 8개
- 위반: 0개

### 검증 통과 ✓
모든 테스트가 컨벤션을 준수합니다.

### 우수 사례
- AAA 패턴 일관 적용
- 명확한 테스트 명명
- 적절한 fixture 사용
```

---

## 자동 수정

일부 항목은 자동으로 개선 가능:

```bash
# 테스트 파일 정렬
isort tests/

# 테스트 포맷팅
ruff format tests/
```

명명 규칙, AAA 패턴은 수동 수정이 필요하다.

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-testing/SKILL.md] | 테스트 컨벤션 참조 |
| [@skills/test-generator/SKILL.md] | 테스트 코드 자동 생성 |
| [@skills/code-review/SKILL.md] | 전체 코드 리뷰 오케스트레이션 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-22 | 1.1.0 | convention-testing 참조 방식으로 리팩토링 |
| 2026-01-21 | 1.0.0 | 초기 생성 - 구조, AAA, 명명, 커버리지 검증 |

## Gotchas (실패 포인트)

- AAA 패턴 미준수 탐지는 자동화 어려움 — 수동 리뷰 필요
- 테스트 파일만 검사, `conftest.py` 별도 검토 필요
- Mock 과다 사용은 탐지 안 됨 — 실제 동작 테스트 여부 검토 필요
- `@pytest.mark` 없는 테스트는 카테고리 미분류 → 누락 위험
