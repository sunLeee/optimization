---
name: task-executor
triggers:
  - "task executor"
description: "생성된 Task 목록을 하나씩 순차적으로 실행하고 진행 상황을 추적한다. Human-in-the-Loop 방식으로 각 Sub-task 완료 후 사용자 승인을 받는다."
argument-hint: "[task_file_path] - Task 파일 경로 (예: tasks/tasks-user-profile.md)"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
model: claude-sonnet-4-6[1m]
context: Task 실행 전문 스킬. 3-step-workflow의 Step 3에서 호출되며, 단독으로도 사용 가능. Haiku 모델로 빠르게 실행.
agent: Task 실행 관리자 - Task 목록을 하나씩 순차 실행하고, 각 단계마다 사용자 승인을 받는 Human-in-the-Loop 패턴을 엄격히 준수한다.
hooks:
  pre_execution: []
  post_execution: []
category: 워크플로우
skill-type: Atomic
references: []
referenced-by:
  - "@skills/3-step-workflow/SKILL.md"
  - "@skills/subagent-driven-dev/SKILL.md"

---
# Task Executor Skill

생성된 Task 목록을 **하나씩 순차적으로 실행**하고 진행 상황을 추적한다.
Human-in-the-Loop 방식으로 각 Sub-task 완료 후 사용자 승인을 받는다.

## 목적

1. **순차 실행**: Task를 하나씩 순서대로 실행
2. **Human-in-the-Loop**: 각 Sub-task 완료 후 사용자 승인 대기
3. **진행 추적**: Progress Summary 자동 업데이트
4. **품질 보장**: 각 단계별 검증으로 오류 조기 발견

## Prerequisites

이 스킬은 반복 실행이므로 빠른 모델 사용:
- **모델**: Haiku (claude-haiku-4-5-20250110)
- **extended thinking** 불필요

## 사용 시점

사용자가 다음과 같은 요청을 할 때 이 스킬을 사용한다:

- "task 시작하자", "task 실행해줘"
- "task 1.1부터 시작", "다음 task"
- "@tasks/tasks-{feature}.md 시작해줘"
- 3-step-workflow의 Step 3 진행 시

## 핵심 원칙

### ⚠️ Human-in-the-Loop (필수)

**절대 규칙**: 하나의 Sub-task만 실행한다. 완료 후 다음으로 넘어가지 **절대** 않는다.

사용자의 명시적 승인(`y`, `yes`, `다음`)을 받아야만 다음 task로 진행한다.

### One Task at a Time

```
현재 Task 실행 → 완료 → 보고 → 🛑 멈춤 → 사용자 승인 대기
```

**금지 사항**:
- ❌ "다음 task도 진행할까요?"라고 물으면서 자동 진행
- ❌ 여러 task를 한 번에 실행
- ❌ 사용자 승인 없이 다음 task로 이동

### Mark and Wait

Sub-task 완료 시:
1. 코드 변경 완료
2. `[ ]` → `[x]`로 체크
3. 완료 보고
4. **멈춤** - 다음 지시 대기

## 워크플로우

### 1. Task 목록 로드
- `tasks/tasks-{feature-name}.md` 읽기

### 2. 첫 번째 미완료 Sub-task 식별
- `[ ]` 상태인 가장 낮은 번호 찾기

### 3. 완료 기준 확인 (NEW)
- Task에 완료 기준 존재하는지 확인
- 없으면 자동 생성하여 추가
- 검증 명령어 준비

### 4. Sub-task 실행
- 코드 작성/수정
- 필요 시 테스트 실행
- 변경 사항 적용

### 5. 완료 기준 자동 검증 (NEW)
- 각 완료 기준별 검증 명령어 실행
- 실패 시 사용자에게 보고 및 선택 요청
- 모든 기준 통과 시 완료 처리

### 6. 완료 처리
- `[ ]` → `[x]` 체크
- Progress Summary 업데이트
- 완료 보고

### 7. 🛑 대기 (Human-in-the-Loop)
- "다음 task로 진행할까요? (y/n)"
- 사용자 응답 대기 (자동 진행 절대 금지)

### 8. 전체 완료 시 보고서 생성 (자동)

모든 Sub-task가 `[x]`로 완료되면 자동으로 완료 보고서를 생성한다.

#### 보고서 생성 프로세스

1. **완료 확인**
   ```python
   all_completed = all(task.status == "[x]" for task in subtasks)
   if all_completed:
       generate_completion_report()
   ```

2. **정보 수집**
   - Task 파일에서 feature name 추출
   - 완료된 Sub-task 목록
   - 변경된 파일 목록 (`git diff --name-only`)
   - 검증 결과 (pytest, mypy, ruff, coverage)
   - 소요 시간 계산

3. **이중 저장**
   ```bash
   # 자동 생성 (휘발성)
   logs/tasks/{feature}-completion-summary.md

   # 영구 보존 (Git 추적)
   docs/progress-references/T1.1_COMPLETION_SUMMARY.md
   docs/progress-references/T1.2_COMPLETION_SUMMARY.md
   ...
   ```

4. **README.md 업데이트**
   - `## Recent Improvements` 섹션에 자동 추가
   - 최신 10개 항목만 유지
   - 중복 방지

5. **보고서 경로 출력**
   ```markdown
   🎉 모든 Task 완료!

   📄 **완료 보고서 생성 완료**:
   - 자동 생성: `logs/tasks/{feature}-completion-summary.md`
   - 영구 보존: `docs/progress-references/T*.md` ({N}개 파일)
   - README 업데이트: `## Recent Improvements` 섹션
   ```

## 입력

```
Task 목록 파일: tasks/tasks-{feature-name}.md
```

## 실행 규칙

### Rule 1: 순차 실행

```
1.1 → 1.2 → 1.3 → 2.1 → 2.2 → ...
```

의존성이 명시된 경우 해당 의존성 task가 완료된 후에만 진행한다.

### Rule 2: 완료 보고 형식

```markdown
✅ **Task 1.1 완료**: Define Prisma schema for User model

**변경 사항:**
- `prisma/schema.prisma`: User 모델 추가
- `prisma/migrations/...`: 마이그레이션 파일 생성

**검증:**
- `npx prisma generate` 성공
- TypeScript 타입 생성 확인

---

다음 task로 진행할까요? (y/n)
현재 진행률: 1/7 (14%)
```

### Rule 3: 에러 처리

에러 발생 시:
1. 에러 내용 보고
2. 해결 방안 제시
3. 사용자 결정 대기 (재시도 / 스킵 / 중단)

```markdown
❌ **Task 1.2 실패**: Create database migration

**에러:**
```
Error: Migration failed - duplicate column name
```

**해결 방안:**
a) 기존 마이그레이션 삭제 후 재시도
b) 스키마 수정 후 재시도
c) 이 task 스킵

선택해주세요 (a/b/c):
```

### Rule 4: 완료 기준 자동 검증 및 추가 (NEW)

**목적**: 모든 Task에 완료 기준이 있는지 확인하고, 없으면 자동 추가

#### 실행 전 검증

Task 실행 전에 완료 기준 존재 여부를 확인한다:

```python
if "완료 기준:" not in task_content:
    # 자동 완료 기준 생성
    completion_criteria = generate_completion_criteria(task)
    # Task 파일에 추가
    add_completion_criteria(task_file, task_id, completion_criteria)
```

#### 정량적 검증 원칙

**모든 검증은 수치로 측정 가능해야 한다:**

| 검증 항목 | 정량적 기준 | 측정 방법 |
|----------|-----------|----------|
| 테스트 통과 | 0 failed | `pytest` exit code = 0 |
| 타입 안전성 | 0 errors | `mypy` exit code = 0 |
| 코드 스타일 | 0 issues | `ruff` exit code = 0 |
| 커버리지 | >= 80% | `coverage report` 파싱 |
| 응답 시간 | p95 < 200ms | `curl -w time_total` |
| 메모리 사용 | < 500MB | `/usr/bin/time -v` |
| 복잡도 | < 10 | `radon cc` 파싱 |
| 모델 정확도 | >= 85% | `metrics.json` 파싱 |

#### 완료 기준 자동 생성 규칙

Task 유형별로 자동 생성:

**1. Python 모듈 구현**
```markdown
**완료 기준** (정량적):
- ✅ `pytest tests/test_{module}.py -v` 통과 (0 failed)
- ✅ `mypy src/{path}/{module}.py --strict` 통과 (0 errors)
- ✅ `ruff check src/{path}/{module}.py` 통과 (0 issues)
- ✅ Coverage >= 80% (line coverage)
- ✅ Cyclomatic Complexity < 10 (함수당)
```

**2. API 엔드포인트**
```markdown
**완료 기준**:
- ✅ `pytest tests/test_api_{endpoint}.py -v` 통과
- ✅ `curl http://localhost:8000/api/{endpoint}` 응답 200
- ✅ OpenAPI 스키마 검증 통과
```

**3. Jupyter Notebook**
```markdown
**완료 기준**:
- ✅ `jupyter nbconvert --execute --to notebook --inplace {notebook}.ipynb` 성공
- ✅ 함수 3개 이하 (convention-jupyter-setup)
- ✅ 시각화 포함
```

**4. 데이터베이스 마이그레이션**
```markdown
**완료 기준**:
- ✅ `alembic upgrade head` 성공
- ✅ `alembic downgrade -1 && alembic upgrade head` (롤백 테스트) 성공
```

#### 완료 후 자동 검증

Task 완료 처리 전에 완료 기준을 자동으로 검증한다:

```bash
# 1. 완료 기준 파싱
completion_criteria = parse_completion_criteria(task)

# 2. 각 기준별 검증 명령어 실행
for criterion in completion_criteria:
    result = run_verification_command(criterion)
    if result.failed:
        report_verification_failure(criterion, result)
        ask_user_to_fix_or_skip()

# 3. 모든 기준 통과 시 체크박스 변경
if all_criteria_passed:
    mark_task_as_complete(task_id)
```

#### 정량적 검증 결과 파싱

**각 도구의 출력에서 정량적 지표를 자동 추출:**

```python
# pytest 결과 파싱
# "5 passed in 0.23s" → passed: 5, failed: 0, time: 0.23s
parse_pytest_output(result.stdout)

# coverage 결과 파싱
# "TOTAL ... 85%" → coverage: 85%
parse_coverage_output(result.stdout)

# mypy 결과 파싱
# "Success: no issues found" → errors: 0
# "Found 3 errors in 1 file" → errors: 3
parse_mypy_output(result.stdout)

# ruff 결과 파싱
# "Found 2 errors" → issues: 2
parse_ruff_output(result.stdout)

# radon 복잡도 파싱
# "M 45:0 A - complexity 12" → complexity: 12
parse_radon_output(result.stdout)
```

#### 검증 실패 자동 분석 (NEW)

**목적**: 검증 실패 시 근본 원인을 자동으로 분석하고 구체적인 해결 방법을 제시

##### 에러 패턴 인식 시스템

**1. Import 에러**
```python
pattern: "ModuleNotFoundError: No module named 'xxx'"
cause: "패키지 설치 누락"
solution:
  - auto_fix: f"uv add {module_name}"
  - manual_fix: f"pyproject.toml에 {module_name} 추가"
  - success_rate: 95%
```

**2. 타입 에러**
```python
pattern: "error: Name \"xxx\" is not defined"
cause: "타입 힌트 미정의 또는 import 누락"
solution:
  - auto_fix: "타입 import 자동 추가"
  - manual_fix: "from typing import xxx 추가"
  - success_rate: 90%
```

**3. Lint 에러**
```python
pattern: "E501 line too long"
cause: "코드 포맷팅 미적용"
solution:
  - auto_fix: "ruff format {file} 실행"
  - manual_fix: "라인 분할 (수동)"
  - success_rate: 100%

pattern: "F401 'xxx' imported but unused"
cause: "미사용 import"
solution:
  - auto_fix: "ruff check --fix {file}"
  - manual_fix: "import 삭제"
  - success_rate: 100%
```

**4. 테스트 실패**
```python
pattern: "AssertionError: assert xxx == yyy"
cause: "로직 오류 또는 테스트 기대값 오류"
solution:
  - auto_fix: None  # 로직 오류는 자동 수정 불가
  - manual_fix: "로직 검토 또는 테스트 수정"
  - success_rate: N/A
```

**5. 성능 기준 미달**
```python
pattern: "응답 시간 p95: 250ms (기준: 200ms)"
cause: "성능 최적화 필요"
solution:
  - auto_fix: None
  - manual_fix: [
      "쿼리 최적화 (N+1 문제 확인)",
      "캐싱 추가",
      "인덱스 생성",
      "비동기 처리"
    ]
  - success_rate: N/A
```

**6. 복잡도 초과**
```python
pattern: "complexity 12 (기준: 10)"
cause: "함수 복잡도 높음"
solution:
  - auto_fix: None
  - manual_fix: [
      "함수 분할 (Extract Method)",
      "조건문 단순화 (Guard Clauses)",
      "Early Return 패턴 적용"
    ]
  - success_rate: N/A
```

**7. Coverage 미달**
```python
pattern: "coverage: 75% (기준: 80%)"
cause: "테스트 커버리지 부족"
solution:
  - auto_fix: None
  - manual_fix: [
      "미테스트 라인 확인 (coverage report -m)",
      "엣지 케이스 테스트 추가",
      "에러 핸들링 테스트 추가"
    ]
  - success_rate: N/A
```

##### 자동 분석 출력 형식

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
자동 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**에러 분류**: [Import Error | Type Error | Lint Issue | Test Failure | Performance | Complexity]

**근본 원인**:
- {에러 상세 설명}
- {발생 원인 분석}

**추천 조치** (자동 수정 가능):
1. {자동 수정 명령어} (권장)
   - {수정 내용}
   - 예상 성공률: {%}

2. {대체 방법}
   - {수정 내용}
   - 예상 성공률: {%}

**수동 조치 필요** (자동 수정 불가):
- {수동 해결 방법 1}
- {수동 해결 방법 2}
- {참고 문서 링크}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

##### 예시: Import Error 자동 분석

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
자동 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**에러 분류**: Import Error

**근본 원인**:
- ModuleNotFoundError: No module named 'pandas'
- pandas 패키지가 설치되지 않음
- pyproject.toml 의존성 목록에 누락

**추천 조치** (자동 수정 가능):
1. `uv add pandas` (권장)
   - pandas를 pyproject.toml에 추가하고 설치
   - 예상 성공률: 98%

2. `pip install pandas` (임시 해결)
   - 현재 환경에만 설치 (비권장)
   - 예상 성공률: 95%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

선택:
a) 자동 수정 (uv add pandas) - 권장
b) 수동 설치 후 재검증
c) Task 미완료로 유지

선택해주세요 (a/b/c):
```

##### 예시: 테스트 실패 자동 분석

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
자동 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**에러 분류**: Test Failure

**근본 원인**:
- AssertionError: assert 5 == 4 (tests/test_calculator.py:15)
- 예상값(4)과 실제값(5) 불일치
- 가능한 원인:
  1. add() 함수 로직 오류
  2. 테스트 케이스 기대값 오류

**수동 조치 필요** (자동 수정 불가):
1. 로직 검증:
   - src/calculator.py:add() 함수 확인
   - 2 + 2 = 5가 되는 이유 확인

2. 테스트 검증:
   - tests/test_calculator.py:15 확인
   - 기대값이 4가 맞는지 확인

3. 디버깅:
   - pytest -vv --pdb tests/test_calculator.py::test_add
   - breakpoint() 추가하여 디버깅

**참고**:
- 테스트 실패는 자동 수정이 불가능합니다
- 로직을 직접 검토해야 합니다

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

선택:
a) 수동 수정 후 재검증
b) Task 미완료로 유지
c) 디버깅 모드 진입 (/systematic-debugging 호출)

선택해주세요 (a/b/c):
```

#### 사용자 확인 프롬프트 (정량적 결과 포함)

```markdown
## 완료 기준 검증 결과 (정량적)

Task 1.1: GTFS 데이터 로더 구현

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
기능 검증
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ pytest tests/test_gtfs_loader.py -v
   통과: 5개, 실패: 0개, 소요 시간: 0.23s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
코드 품질
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ mypy src/data/gtfs_loader.py --strict
   에러: 0개

❌ ruff check src/data/gtfs_loader.py
   이슈: 2개
   - E501 line too long (92 > 88) at line 45
   - F401 'datetime' imported but unused at line 12

✅ coverage report
   Line coverage: 85% (기준: 80% 이상)
   Statements: 120, Missing: 18

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
복잡도 (선택)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ radon cc src/data/gtfs_loader.py
   평균 복잡도: 8.2 (기준: 10 이하) ✅
   최대 복잡도: 12 (함수: load_gtfs) ⚠️ 기준 초과

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
종합 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

필수 기준: 3/4 통과 (75%)
권장 기준: 1/1 경고

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
자동 분석 (NEW)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**근본 원인 분석**:
- E501 (line too long): 코드 포맷팅 문제
  → 원인: 자동 포맷팅 미적용
  → 해결: `ruff format src/data/gtfs_loader.py` 실행

- F401 (unused import): import 정리 필요
  → 원인: datetime 사용하지 않음
  → 해결: `ruff check --fix`로 자동 제거 또는 수동 삭제

**추천 조치** (자동 수정 가능):
1. `ruff check --fix src/data/gtfs_loader.py` (권장)
   - E501, F401 모두 자동 수정 시도
   - 예상 성공률: 95%

2. `ruff format src/data/gtfs_loader.py` + 수동 import 제거
   - E501은 포맷터로, F401은 수동
   - 예상 성공률: 100%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

선택:
a) 자동 수정 시도 (ruff check --fix) - 권장
b) 자동 포맷팅 + 수동 import 정리
c) 수동 수정 후 재검증
d) 이슈 무시하고 완료 (경고: 기준 미충족)
e) Task 미완료로 유지하고 다음에 재시도

선택해주세요 (a/b/c/d/e):
```

### Rule 5: Progress Summary 자동 업데이트

각 Sub-task 완료 시 Task 목록 파일의 Progress Summary를 업데이트한다.

```markdown
## Progress Summary

| Task | Sub-tasks | Completed | Progress |
|------|-----------|-----------|----------|
| 1    | 3         | 2         | 67%      |  ← 업데이트
| 2    | 2         | 0         | 0%       |
| 3    | 2         | 0         | 0%       |
| **Total** | **7** | **2**     | **29%**  |  ← 업데이트
```

## 사용자 명령어

| 명령 | 동작 |
|------|------|
| `y`, `yes`, `다음` | 다음 Sub-task로 진행 |
| `n`, `no`, `중단` | 실행 중단 |
| `skip`, `스킵` | 현재 task 스킵, 다음으로 |
| `retry`, `재시도` | 현재 task 재시도 |
| `status`, `상태` | 현재 진행 상황 표시 |
| `task {n.m}` | 특정 task로 점프 |

## 상태 표시 형식

`status` 명령 시:

```markdown
## 현재 진행 상황

**Feature**: User Profile Card
**파일**: tasks/tasks-user-profile-card.md

### 완료된 Task
- [x] 1.1 Define Prisma schema
- [x] 1.2 Create migration
- [x] 1.3 Unit tests for model

### 진행 중
- [ ] **2.1 Implement GET /api/users** ← 현재

### 남은 Task
- [ ] 2.2 Add pagination
- [ ] 2.3 API unit tests
- [ ] 3.1 Integration test

**진행률**: 3/7 (43%)
**예상 남은 시간**: ~20분 (Sub-task당 ~5분 기준)
```

## 완료 기준 자동 생성 및 검증 예시

### 시나리오: 완료 기준이 없는 Task 실행

**원본 Task** (tasks/tasks-user-profile.md):

```markdown
- [ ] **T1.1 User 모델 구현**
  - 설명: Pydantic 기반 User 모델 작성
  - 산출물: src/models/user.py
  - 의존성: 없음
```

**task-executor 실행**:

```markdown
⚠️ Task 1.1에 완료 기준이 없습니다.
자동으로 완료 기준을 생성하여 추가합니다...

생성된 완료 기준:
- ✅ `pytest tests/test_user.py -v` 통과
- ✅ `mypy src/models/user.py --strict` 통과
- ✅ `ruff check src/models/user.py` 통과

Task 파일에 완료 기준이 추가되었습니다.
이제 Task 1.1을 실행합니다...
```

### Task 완료 후 자동 검증

**구현 완료 후**:

```markdown
Task 1.1 구현이 완료되었습니다.
완료 기준을 검증하는 중...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
완료 기준 검증 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ pytest tests/test_user.py -v
   → 5 passed in 0.23s

✅ mypy src/models/user.py --strict
   → Success: no issues found in 1 source file

❌ ruff check src/models/user.py
   → src/models/user.py:12:1: E501 line too long (95 > 88 characters)
   → src/models/user.py:25:5: F401 'datetime' imported but unused

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2/3 기준 통과, 1/3 기준 실패

선택:
a) 자동 수정 시도 (ruff format --fix 실행)
b) 수동 수정 후 재검증
c) 이 기준 무시하고 완료 처리
d) Task 미완료로 유지하고 다음에 다시 시도

선택해주세요 (a/b/c/d):
```

**사용자가 'a' 선택 시**:

```markdown
자동 수정 실행 중...

$ ruff check src/models/user.py --fix
Fixed 2 errors

재검증 중...

✅ ruff check src/models/user.py
   → All checks passed!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
모든 완료 기준 통과! ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Task 1.1을 완료 처리합니다.
[x] **T1.1 User 모델 구현** ✅

다음 task로 진행할까요? (y/n)
```

### persistent-loop 연동 시

**완료 기준을 기반으로 자동 반복**:

```markdown
Task 1.1 실행 중... (iteration 1/10)

구현 시도 1:
❌ pytest 실패 (import error)

재시도... (iteration 2/10)

구현 시도 2:
✅ pytest 통과
❌ mypy 실패 (타입 힌트 누락)

재시도... (iteration 3/10)

구현 시도 3:
✅ pytest 통과
✅ mypy 통과
✅ ruff 통과

모든 완료 기준 통과! <completion>DONE</completion>
Task 1.1 완료 (3회 반복)
```

## DO (해야 할 것)

1. **한 번에 하나만**: 절대로 여러 Sub-task를 한 번에 실행하지 말 것
2. **명시적 체크**: `[ ]` → `[x]` 변경을 실제로 파일에 적용
3. **변경 사항 명시**: 어떤 파일이 변경되었는지 보고
4. **에러 투명성**: 에러 발생 시 숨기지 말고 보고
5. **승인 대기**: 각 task 완료 후 반드시 사용자 응답 대기

## DON'T (하지 말 것)

1. **자동 진행 금지**: 사용자 승인 없이 다음 task로 넘어가지 말 것
2. **건너뛰기 금지**: 의존성 있는 task를 건너뛰지 말 것
3. **과도한 변경 금지**: Task 범위를 벗어난 "개선" 금지
4. **묵시적 승인 금지**: "y"를 가정하고 진행하지 말 것

## 세션 관리

### 세션 시작

```markdown
🚀 Task 실행 시작

**Feature**: {Feature Name}
**총 Task**: {N}개의 Sub-task

Task 1.1부터 시작합니다.

---

📋 **Task 1.1**: {Task Title}
- 설명: {설명}
- 의존성: {없음 또는 의존 task}

실행을 시작합니다...
```

### 세션 종료

모든 task 완료 시:

```markdown
🎉 모든 Task 완료!

**Feature**: {Feature Name}
**완료된 Task**: {N}/{N}

### 생성/수정된 파일
- `src/components/UserCard.tsx` (신규)
- `src/hooks/useUser.ts` (수정)
- ...

### 완료 보고서
📄 **보고서 생성 완료**: `logs/tasks/{feature-name}-completion-summary.md`

보고서 내용:
- Sub-task 완료 현황
- 산출물 목록
- 변경된 파일 목록
- 검증 결과
- 주요 발견 및 인사이트

### 다음 단계 제안
1. 완료 보고서 검토 (`cat logs/tasks/{feature-name}-completion-summary.md`)
2. 코드 리뷰 요청
3. PR 생성
4. 스테이징 환경 배포

수고하셨습니다!
```

### 세션 중단

```markdown
⏸️ Task 실행 중단

**현재 진행**: Task {n.m}
**완료율**: {X}%

나중에 재개하려면:
"task {n.m}부터 재시작해줘"

진행 상황은 tasks/tasks-{feature}.md에 저장되어 있습니다.
```

## 예시 실행 흐름

### 사용자
```
tasks-user-profile.md의 task 시작해줘
```

### Claude
```markdown
🚀 Task 실행 시작

**Feature**: User Profile Card
**총 Task**: 7개의 Sub-task

---

📋 **Task 1.1**: Define User model in Prisma schema
- 설명: prisma/schema.prisma에 User 모델 정의
- 의존성: 없음

실행을 시작합니다...

[코드 작성 중...]

✅ **Task 1.1 완료**

**변경 사항:**
- `prisma/schema.prisma`: User 모델 추가

**검증:**
- `npx prisma format` 성공

---

다음 task로 진행할까요? (y/n)
현재 진행률: 1/7 (14%)
```

### 사용자
```
y
```

### Claude
```markdown
📋 **Task 1.2**: Create database migration
- 설명: Prisma 마이그레이션 실행
- 의존성: 1.1 ✅

실행을 시작합니다...

[마이그레이션 실행 중...]

✅ **Task 1.2 완료**

**변경 사항:**
- `prisma/migrations/20240115_add_user/`: 마이그레이션 파일 생성

**검증:**
- `npx prisma migrate dev` 성공

---

다음 task로 진행할까요? (y/n)
현재 진행률: 2/7 (29%)
```

## 관련 Skills

- `3-step-workflow/SKILL.md` - 전체 워크플로우
- `prd-generator/SKILL.md` - Step 1 (기능 요청 → PRD)
- `task-generator/SKILL.md` - Step 2 (PRD → Task 분해)

## 완료 보고서 자동 생성 로직

전체 Task 완료 시 완료 보고서를 자동으로 생성한다.

**상세 템플릿**: [@templates/skill-examples/task-executor/completion-report-template.md]

**핵심 내용**:
- **트리거**: 모든 Sub-task [x] 체크 시
- **생성 파일**: logs/tasks/, docs/progress-references/, README.md
- **포함 섹션**: Executive Summary, 정량적 검증 결과, 변경 파일, 인사이트

## 완료 체크리스트

각 Sub-task 완료 시:
- [ ] 코드 변경 적용됨
- [ ] [ ] → [x] 체크됨
- [ ] Progress Summary 업데이트됨
- [ ] 변경 사항 보고됨
[ ] 검증 결과 보고됨
[ ] 사용자 대기 상태
[ ] 자동 진행하지 않음 (Human-in-the-Loop 준수)

전체 완료 시:
[ ] logs/tasks/ 디렉토리 존재 확인 (없으면 생성)
[ ] docs/progress-references/ 디렉토리 존재 확인
[ ] 통합 완료 보고서 생성 (logs/tasks/{feature}-completion-summary.md)
[ ] Task별 보고서 생성 (docs/progress-references/T*.md)
[ ] README.md 업데이트 (## Recent Improvements 섹션)
[ ] 보고서 경로 출력 (3개 파일 경로)
```

## Changelog

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.1.0 | 2026-01-28 | 완료 보고서 자동 생성 기능 추가 (logs/tasks/{feature}-completion-summary.md) |
| 1.0.0 | 2026-01-27 | 초기 생성 (archive 복원) |
| 1.0.0 | 2026-01-27 | Human-in-the-Loop 패턴 강조 |
| 1.0.0 | 2026-01-27 | Haiku 모델 사용 (빠른 반복 실행) |
