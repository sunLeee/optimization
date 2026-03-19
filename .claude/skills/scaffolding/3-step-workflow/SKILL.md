---
name: 3-step-workflow
triggers:
  - "3 step workflow"
description: "Ryan Carson의 3-Step Playbook 기반 구조화된 AI 개발 워크플로우. PRD → Task 분해 → 순차 실행의 체계적 프로세스를 제공한다. Human-in-the-Loop 패턴으로 각 단계마다 사용자 승인을 받는다."
argument-hint: "[feature_description] - 구현할 기능 설명"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Skill
  - AskUserQuestion
  - Bash
model: claude-sonnet-4-6[1m]
context: 복잡한 구현 작업 시 사용하는 체계적 워크플로우. prd-generator, task-generator, task-executor 3개 하위 스킬을 조합하여 실행.
agent: 3-Step Workflow 오케스트레이터 - 3개 하위 스킬을 순차적으로 조율하며 각 단계마다 사용자 승인을 받아 진행한다.
hooks:
  pre_execution: []
  post_execution: []
category: 워크플로우
skill-type: Composite
references:
  - "@skills/prd-generator/SKILL.md"
  - "@skills/task-generator/SKILL.md"
  - "@skills/task-executor/SKILL.md"
  - "@skills/subagent-driven-dev/SKILL.md"
referenced-by:
  - "@skills/doc-tasks/SKILL.md"
  - "@skills/prd-workflow/SKILL.md"
  - "@skills/project-init/SKILL.md"
  - "@skills/systematic-debugging/SKILL.md"

---
# 3-Step Workflow (Ryan Carson Playbook)

> PRD 생성 → Task 분해 → 순차 실행: 구조화된 AI 개발 워크플로우

Ryan Carson의 3-Step Playbook을 기반으로 한 체계적인 개발 프로세스다.
"Vibe Coding"의 무계획적 접근을 체계적인 프로세스로 전환한다.

---

## 핵심 철학

**Context is Everything**: AI에게 충분한 컨텍스트를 제공하면 속도가 빨라진다.

**One Step at a Time**: 한 번에 하나의 작업만 실행하고 검증한다.

**Human-in-the-Loop**: 각 단계에서 사람의 승인을 받는다.

---

## 목적

1. **품질 보장**: 계획 없이 바로 코딩하는 실수 방지
2. **요구사항 명확화**: 모호한 요구사항을 구체화
3. **추적 가능성**: 각 단계 완료 후 확인으로 진행 상황 추적
4. **Human-in-the-Loop**: 각 sub-task 완료 후 승인 대기로 제어권 유지

---

## 워크플로우 구조

### STEP 1: PRD 생성
- prd-generator skill 호출
- 명확화 질문 → 답변 수집
- `tasks/{feature}-prd.md` 생성

### STEP 2: Task 목록 생성
- task-generator skill 호출
- PRD 기반 세부 작업 분해
- `tasks/tasks-{feature-name}.md` 생성

### STEP 3: Task 실행
- task-executor skill 호출
- 1.1 → 1.2 → ... 순차 실행
- 각 sub-task 완료 후 [x] 체크
- 🛑 사용자 승인 후 다음 task 진행 (Human-in-the-Loop)

---

## ⚠️ 디렉토리 구조 (하이브리드)

**PRD + Task 통합** (tasks/)

```
project/
└── tasks/                           # PRD + Task 파일 통합 디렉토리
    ├── {feature}-prd.md             # Step 1: PRD
    ├── tasks-{feature-name}.md      # Step 2: Task 목록
    └── prd-*.md                     # 기타 PRD 파일
```

**규칙**:
- **PRD 문서**: `tasks/{feature}-prd.md` - 기능 요구사항 정의
- **Task 목록**: `tasks/tasks-{feature-name}.md` - 작업 추적, 체크박스 관리

---

## Sub-Skills (조합)

| Skill | 역할 | 모델 | 트리거 |
|-------|------|------|--------|
| **prd-generator** | PRD 문서 생성 | Opus | "PRD 만들어줘" |
| **task-generator** | Task 목록 분해 | Opus | "task 생성해줘" |
| **task-executor** | Task 순차 실행 | Haiku | "task 시작하자" |

---

## 사용 시점

사용자가 다음과 같은 요청을 할 때 이 스킬을 사용한다:

- "기능 개발해줘", "feature 만들어줘"
- "PRD 작성해줘", "요구사항 정의해줘"
- "체계적으로 개발하자", "structured development"
- "3-step으로 진행하자"

---

## Step 1: PRD 생성

### 실행

```bash
# prd-generator skill 호출
Skill tool: prd-generator "{feature_description}"
```

### 수행 내용

1. **명확화 질문** (3-5개)
   - AskUserQuestion 활용
   - 기술적 결정 사항
   - 비즈니스 요구사항
   - 우선순위 확인

2. **PRD 생성**
   - tasks/{feature}-prd.md

3. **사용자 승인 대기**
   ```markdown
   PRD가 생성되었습니다:
   - tasks/{feature}-prd.md

   Step 2 (Task 분해)로 진행할까요? (y/n)
   ```

### 완료 조건

- [x] PRD 문서 생성 완료
- [x] 파일 저장 확인 (`ls tasks/`)
- [x] 사용자 승인 획득

---

## Step 2: Task 목록 생성

### 실행

```bash
# task-generator skill 호출
Skill tool: task-generator "tasks/{feature}-prd.md"
```

### 수행 내용

1. **PRD 분석**
   - tasks/{feature}-prd.md 읽기

2. **High-Level 계획 제안**
   - 주요 Task 목록 제시
   - AskUserQuestion으로 승인 요청

3. **세부 Task 생성**
   - Sub-task 분해 (15-30분 단위)
   - 의존성 명시
   - tasks/tasks-{feature-name}.md 저장

4. **사용자 승인 대기**
   ```markdown
   Task 목록이 생성되었습니다: tasks/tasks-{feature-name}.md

   총 {N}개의 Task, {M}개의 Sub-task가 있습니다.

   Step 3 (Task 실행)으로 진행할까요? (y/n)
   ```

### 완료 조건

- [x] Task 목록 파일 생성 완료
- [x] Progress Summary 초기화됨
- [x] 사용자 승인 획득

---

## Step 3: Task 실행

### 실행 모드 선택

**AskUserQuestion**:
```yaml
questions:
  - question: "Task 실행 방식을 선택해주세요"
    header: "실행 모드"
    multiSelect: false
    options:
      - label: "서브에이전트 모드 (권장)"
        description: "각 task를 독립 서브에이전트에 위임. 2단계 리뷰 자동 수행. 빠르고 품질 높음."
      - label: "순차 실행 모드"
        description: "Human-in-the-Loop 방식. 각 task 완료 후 사용자 승인 필요."
```

#### 모드 1: 서브에이전트 모드 (subagent-driven-dev)

```bash
# subagent-driven-dev skill 호출
Skill tool: subagent-driven-dev "tasks/tasks-{feature-name}.md"
```

**장점**:
- 각 task를 독립적인 서브에이전트가 처리
- 2단계 리뷰 자동 수행 (스펙 준수 → 코드 품질)
- 다수의 서브에이전트가 병렬로 작업 가능
- 높은 품질, 빠른 반복

**프로세스**:
```
Task 1 → 구현 서브에이전트 → 스펙 리뷰 → 품질 리뷰 → 완료
Task 2 → 구현 서브에이전트 → 스펙 리뷰 → 품질 리뷰 → 완료
...
```

#### 모드 2: 순차 실행 모드 (task-executor)

```bash
# task-executor skill 호출
Skill tool: task-executor "tasks/tasks-{feature-name}.md"
```

**프로세스**: Human-in-the-Loop 방식 (아래 "수행 내용" 참조)

### 수행 내용 (순차 실행 모드)

**⚠️ 핵심 규칙**: 한 번에 하나의 Sub-task만 실행. 완료 후 **반드시** 사용자 승인 대기.

```
Sub-task 1.1 실행 → 완료 → [x] 체크 → 🛑 승인 대기
→ 사용자 "y" 입력
→ Sub-task 1.2 실행 → 완료 → [x] 체크 → 🛑 승인 대기
→ 사용자 "y" 입력
...
```

### 실행 흐름

1. **첫 번째 미완료 Sub-task 식별**
   - `[ ]` 상태인 가장 낮은 번호 찾기

2. **Sub-task 실행**
   - 코드 작성/수정
   - 필요 시 테스트 실행
   - 변경 사항 적용

3. **완료 처리**
   - `[ ]` → `[x]` 체크
   - Progress Summary 업데이트
   - 완료 보고

4. **🛑 대기 (Human-in-the-Loop)**
   ```markdown
   ✅ **Task 1.1 완료**: [작업명]

   **변경 사항:**
   - `file.py`: [변경 내용]

   **검증:**
   - [검증 결과]

   ---
   다음 task로 진행할까요? (y/n)
   현재 진행률: 1/7 (14%)
   ```

5. **사용자 응답 대기**
   - `y`, `yes`, `다음` → 다음 Sub-task 진행
   - `n`, `no`, `중단` → 실행 중단
   - `skip` → 현재 task 스킵
   - `retry` → 현재 task 재시도

### 완료 조건

- [x] 모든 Sub-task `[x]` 체크됨
- [x] Progress Summary 100%
- [x] 테스트 통과 확인

---

## 사용법

### 전체 워크플로우 시작

```bash
# 사용자 요청 예시
"새로운 기능을 개발하려고 해. 3-step workflow로 진행하자.
기능: 사용자 프로필 카드 컴포넌트"
```

### Step별 개별 실행

```bash
# Step 1만 실행
"PRD 생성해줘: 사용자 프로필 카드"

# Step 2만 실행 (PRD가 이미 있을 때)
"tasks/{feature}-prd.md를 기반으로 task 목록 생성해줘"

# Step 3만 실행 (Task 목록이 이미 있을 때)
"tasks/tasks-user-profile.md의 task 1.1부터 시작하자"
```

---

## 핵심 원칙

### 1. 급하지 마라 (Don't Rush)

AI에게 충분한 컨텍스트를 제공하는 것이 결국 더 빠르다.
명확화 질문에 성실히 답변하라.

### 2. 작게 쪼개라 (Decompose)

큰 기능을 작은 sub-task로 분해한다.
각 sub-task는 독립적으로 검증 가능해야 한다.

### 3. 검증하라 (Verify)

각 sub-task 완료 후 반드시 검증한다.
문제 발견 시 즉시 수정한다.

### 4. 추적하라 (Track)

완료된 task는 [x]로 체크한다.
진행 상황을 시각적으로 확인한다.

### 5. Human-in-the-Loop 엄수

**절대로** 사용자 승인 없이 다음 task로 넘어가지 않는다.
각 sub-task 완료 후 **반드시** 대기한다.

---

## AskUserQuestion 활용 지점

### 지점 1: 워크플로우 진입점 선택 (시작 시)

**타이밍**: 3-step-workflow 시작 직후

```yaml
AskUserQuestion:
  questions:
    - question: "워크플로우 진행 방식을 선택해주세요"
      header: "진입점"
      multiSelect: false
      options:
        - label: "전체 자동 진행 (권장)"
          description: "Step 1 → Step 2 → Step 3 순차 실행. 각 Step 완료 시 승인 요청"
        - label: "Step 1만 실행 (PRD 생성)"
          description: "PRD 문서만 생성하고 종료"
        - label: "Step 2부터 시작 (PRD 있음)"
          description: "기존 PRD로부터 Task 목록 생성"
        - label: "Step 3부터 시작 (Task 있음)"
          description: "기존 Task 목록 순차 실행"
```

### 지점 2: 다음 Step 진행 확인 (각 Step 완료 후)

**타이밍**: Step 1, Step 2 완료 후

```yaml
AskUserQuestion:
  questions:
    - question: "다음 단계로 진행할까요?"
      header: "진행 확인"
      multiSelect: false
      options:
        - label: "다음 Step 진행 (권장)"
          description: "자동으로 다음 Step skill을 호출합니다"
        - label: "현재 Step 결과 검토"
          description: "생성된 문서를 먼저 확인하고 수동으로 진행"
        - label: "워크플로우 중단"
          description: "현재까지 작업 저장하고 종료"
```

---

## 예시 실행 흐름

### 사용자
```
/3-step-workflow 사용자 프로필 카드 컴포넌트
```

### Claude (Step 1)
```markdown
🚀 3-Step Workflow 시작

**Feature**: 사용자 프로필 카드 컴포넌트

---

## Step 1: PRD 생성

Skill tool을 사용하여 prd-generator를 호출합니다...

[prd-generator 실행...]

✅ **Step 1 완료**

**생성된 문서:**
- tasks/{feature}-prd.md
- tasks/tasks-user-profile-card.md

---

Step 2 (Task 분해)로 진행할까요? (y/n)
```

### 사용자
```
y
```

### Claude (Step 2)
```markdown
## Step 2: Task 목록 생성

Skill tool을 사용하여 task-generator를 호출합니다...

[task-generator 실행...]

✅ **Step 2 완료**

**생성된 파일:**
- tasks/tasks-user-profile-card.md

**총 Task**: 4개의 Major Task, 12개의 Sub-task

---

Step 3 (Task 실행)으로 진행할까요? (y/n)
```

### 사용자
```
y
```

### Claude (Step 3)
```markdown
## Step 3: Task 실행

Skill tool을 사용하여 task-executor를 호출합니다...

[task-executor 실행...]

---

📋 **Task 1.1**: Define User model in Prisma schema

[코드 작성 중...]

✅ **Task 1.1 완료**

**변경 사항:**
- `prisma/schema.prisma`: User 모델 추가

---

다음 task로 진행할까요? (y/n)
현재 진행률: 1/12 (8%)
```

(사용자가 "y"를 입력할 때마다 다음 task 진행)

---

## 관련 Skills

| 스킬 | 관계 | 설명 |
|------|------|------|
| [@skills/prd-generator/SKILL.md] | **조합 (Step 1)** | PRD 문서 생성 |
| [@skills/task-generator/SKILL.md] | **조합 (Step 2)** | Task 목록 분해 |
| [@skills/task-executor/SKILL.md] | **조합 (Step 3)** | Task 순차 실행 |
| [@skills/subagent-driven-dev/SKILL.md] | 대안 | 각 Task를 독립 에이전트에 위임 |
| [@skills/systematic-debugging/SKILL.md] | 연계 | 실행 중 버그 발생 시 디버깅 |
| [@skills/doc-prd/SKILL.md] | 대안 | 단독 PRD 생성 (대화형, prd-generator와 유사) |
| [@skills/done/SKILL.md] | 후속 | 워크플로우 완료 후 정리 |

---

## 주의사항

1. **Step 건너뛰기 금지**: 반드시 Step 1 → Step 2 → Step 3 순서 준수
2. **사용자 확인 필수**: 각 Step 완료 후 다음 진행 전 확인
3. **Human-in-the-Loop 엄수**: Step 3에서 각 sub-task 완료 후 승인 대기
4. **문서 저장 확인**: 각 Step에서 파일 생성 확인 (`ls` 명령)

---

## 완료 보고서 자동 생성

Step 3 (Task 실행) 완료 시 자동으로 완료 보고서가 생성된다.

### 자동 생성 메커니즘

| 실행 모드 | 생성 스킬 | 출력 파일 |
|----------|----------|----------|
| **순차 실행** | task-executor | `logs/tasks/{feature}-completion-summary.md`<br/>`docs/progress-references/T*.md` (Task별) |
| **서브에이전트** | subagent-driven-dev | `logs/workflows/subagent-driven-dev-{timestamp}.md`<br/>`docs/progress-references/PHASE_*_COMPLETION_REPORT.md` |

### 보고서 내용

1. **Executive Summary** - 완료 작업 요약, 진행률, 산출물
2. **정량적 검증 결과** - pytest, mypy, ruff, coverage 수치
3. **기술 구현 상세** - 변경 파일, 코드 스니펫, 아키텍처 결정
4. **교훈 및 베스트 프랙티스** - 인사이트, 개선 제안
5. **추가 개선 사항** - README.md 자동 반영 대상

### README.md 자동 업데이트

완료 보고서의 "추가 개선 사항" 섹션이 프로젝트 README.md의 `## Recent Improvements`에 자동으로 추가된다.

```markdown
## Recent Improvements

- **2026-01-28**: [T1.1 GTFS 데이터 로더 구현](docs/progress-references/T1.1_COMPLETION_SUMMARY.md)
```

최신 10개 항목만 유지하며, 중복 방지 메커니즘이 적용된다.

### 디렉토리 구조

```
project-root/
├── logs/                                # 자동 생성 (Git 무시)
│   ├── tasks/
│   │   └── {feature}-completion-summary.md
│   └── workflows/
│       └── subagent-driven-dev-{timestamp}.md
│
└── docs/progress-references/           # 영구 보존 (Git 추적)
    ├── T1.1_COMPLETION_SUMMARY.md
    └── PHASE_1_COMPLETION_REPORT.md
```

**참고**: 보고서 템플릿은 `templates/completion-report-template.md` 참조

---

## Changelog

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 3.1.1 | 2026-02-03 | 논리적 모순 수정: doc-prd → prd-generator 통일, 디렉토리 경로 정규화, AskUserQuestion header 명확화 |
| 3.1.0 | 2026-01-28 | 완료 보고서 자동 생성 기능 추가 (logs/ + docs/progress-references/) |
| 3.1.0 | 2026-01-28 | README.md 자동 업데이트 메커니즘 추가 |
| 3.0.0 | 2026-01-27 | Ryan Carson Playbook 통합 - 3개 하위 스킬로 재구성 |
| 3.1.0 | 2026-02-10 | 저장 경로 변경: docs/design/ → docs/prd/{feature}-prd.md (통일) |
| 3.0.0 | 2026-01-27 | 디렉토리 구조 적용 (docs/prd/ + tasks/) |
| 3.0.0 | 2026-01-27 | Human-in-the-Loop 패턴 명시 |
| 3.0.0 | 2026-01-27 | Composite 스킬로 전환 (prd-generator, task-generator, task-executor) |
| 2.1.0 | 2026-01-27 | doc-workflow 통합 - 각 Phase에서 문서 자동 생성 |
| 2.0.0 | 2026-01-21 | GSD 4단계로 업그레이드 - Phase 4 Verify 추가 |
| 1.0.0 | 2026-01-21 | 초기 생성 - 3단계 워크플로우 구현 |
