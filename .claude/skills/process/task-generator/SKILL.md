---
name: task-generator
triggers:
  - "task generator"
description: "PRD 문서를 세부 실행 가능한 Task 목록으로 분해한다. 각 Task는 독립적으로 실행 가능하고 검증 가능해야 한다."
argument-hint: "[prd_file_path] - PRD 파일 경로 (예: tasks/{feature}-prd.md)"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: Task 분해 전문 스킬. 3-step-workflow의 Step 2에서 호출되며, 단독으로도 사용 가능.
agent: Task 분해 전문가 - PRD를 분석하여 독립적으로 실행 가능한 세부 Task 목록으로 분해한다.
hooks:
  pre_execution: []
  post_execution: []
category: 워크플로우
skill-type: Atomic
references: []
referenced-by:
  - "@skills/3-step-workflow/SKILL.md"

---
# Task Generator Skill

PRD 문서를 **세부 실행 가능한 Task 목록**으로 분해한다.
각 Task는 독립적으로 실행 가능하고 검증 가능해야 한다.

## 목적

1. **PRD 실행화**: 추상적인 요구사항을 구체적인 실행 단계로 변환
2. **작업 추적**: 체크박스 기반 진행 상황 관리
3. **의존성 관리**: Task 간 선후 관계 명시
4. **검증 가능성**: 각 Task의 완료 조건을 명확히 정의

## Prerequisites

이 스킬은 복잡한 reasoning이 필요하므로:
- **모델**: Opus (claude-opus-4-5-20251101)
- **extended thinking** 활성화 권장

## 사용 시점

사용자가 다음과 같은 요청을 할 때 이 스킬을 사용한다:

- "task 생성해줘", "task 목록 만들어줘"
- "PRD를 task로 분해해줘"
- "@tasks/user-auth-prd.md로 task 생성해줘"
- 3-step-workflow의 Step 2 진행 시

## 워크플로우

### 1. PRD 파일 로드
- `tasks/{feature}-prd.md` 읽기

### 2. High-Level 계획 제안
- 주요 Task 목록 제시
- 사용자 승인 대기

### 3. 세부 Task 생성
- Sub-task 분해
- 관련 파일 목록
- 각 Task별 완료 기준 자동 생성 (NEW)

### 4. 완료 기준 검증
- 모든 Task에 완료 기준 존재 확인
- 검증 명령어 유효성 확인
- `tasks/tasks-{feature-name}.md` 저장

## 입력

```
PRD 파일: tasks/{feature}-prd.md
```

## Task 분해 원칙

### 1. Granularity (세분화)

각 Sub-task는 **15-30분 내 완료** 가능해야 한다.
너무 크면 검증이 어렵고, 너무 작으면 오버헤드가 증가한다.

### 2. Independence (독립성)

각 Sub-task는 독립적으로 실행 가능해야 한다.
순서 의존성이 있는 경우 명시한다.

### 3. Verifiability (검증 가능성)

각 Sub-task 완료 조건이 명확해야 한다.
"완료"의 정의가 모호하면 안 된다.

### 4. Testability (테스트 가능성)

구현 task에는 대응하는 테스트 task를 포함한다.
코드와 테스트는 쌍으로 관리한다.

## Task 목록 템플릿

**상세 템플릿**: [@templates/skill-examples/task-generator/task-template.md]

**핵심 내용**:
- **Relevant Files**: 관련 파일 목록 (신규/수정 상태 표시)
- **Tasks**: Major Task → Sub-task 계층 구조
- **Progress Summary**: 진행률 테이블 자동 생성

## 실행 지침

### Step 1: High-Level 계획 제안

PRD를 분석한 후, 먼저 상위 Task 목록만 제시하고 승인을 요청한다.

```markdown
PRD를 분석했습니다. 다음과 같은 구조로 Task를 생성하겠습니다:

**Task 1**: 데이터 모델 정의 (Prisma Schema)
**Task 2**: API 엔드포인트 구현
**Task 3**: 프론트엔드 컴포넌트
**Task 4**: 테스트 및 문서화

이 구조로 진행할까요? (y/n)
수정이 필요하면 말씀해주세요.
```

### Step 2: 사용자 승인 후 세부 분해

승인을 받은 후에만 Sub-task 목록을 생성한다.

### Step 3: Relevant Files 섹션 생성

- 기존 코드베이스를 분석하여 관련 파일 식별
- 새로 생성할 파일 목록 포함
- 테스트 파일은 항상 포함

**명명 규칙 참조**: [@templates/skill-examples/task-generator/task-template.md]

## 완료 기준 자동 생성

**상세 가이드**: [@templates/skill-examples/task-generator/completion-criteria-guide.md]
**지표 카탈로그**: [@templates/skill-examples/task-generator/metrics-catalog.md]

**핵심 원칙**:
- 모든 완료 기준은 정량적으로 측정 가능해야 함
- Task 유형별 자동 생성 (Python, API, Notebook, DB, ML, 문서)
- 프로젝트별 임계값 커스터마이징 지원

## DO (해야 할 것)

1. **PRD의 모든 요구사항 커버**: Functional Requirements → Task 매핑
2. **테스트 Task 포함**: 구현 Task에 대응하는 테스트 Task 필수
3. **의존성 명시**: Sub-task 간 의존 관계 명확화
4. **완료 조건 명확화**: 각 Sub-task의 "완료" 정의 (자동 생성 활용)

## DON'T (하지 말 것)

1. **너무 큰 Task**: 1시간 이상 걸리는 Sub-task는 더 분해
2. **모호한 Task**: "개선하기", "최적화하기" 같은 모호한 표현 금지
3. **테스트 누락**: 모든 구현 Task에 테스트 Task 대응
4. **완료 기준 누락**: 모든 Task에 구체적인 완료 기준 필수 (자동 생성 활용)

## 출력 위치

```
tasks/tasks-{feature-name}.md
```

**예시**:
- `tasks/tasks-user-profile-card.md`
- `tasks/tasks-email-notification.md`

**디렉토리 자동 생성**: tasks/ 디렉토리가 없으면 자동 생성

## AskUserQuestion 활용 지점

### 지점 1: High-Level 계획 승인 (필수)

**타이밍**: PRD 분석 직후, 세부 Task 생성 전

**질문 예시**:
```yaml
questions:
  - question: "다음 구조로 Task를 생성할까요?"
    header: "계획 승인"
    multiSelect: false
    options:
      - label: "승인 - 이대로 진행 (권장)"
        description: "제안된 구조로 세부 Task를 생성합니다"
      - label: "수정 필요"
        description: "구조를 수정한 후 다시 제안받습니다"
      - label: "Task 추가"
        description: "추가 Task를 제안합니다"
```

### 지점 2: 테스트 전략 선택 (권장)

**타이밍**: Task 분해 중

**질문 예시**:
```yaml
questions:
  - question: "테스트 전략을 선택해주세요"
    header: "테스트 전략"
    multiSelect: true
    options:
      - label: "Unit Tests"
        description: "각 함수/컴포넌트별 단위 테스트"
      - label: "Integration Tests"
        description: "모듈 간 통합 테스트"
      - label: "E2E Tests"
        description: "전체 시나리오 E2E 테스트"
```

## 완료 기준 생성 예시

**상세 예시**: [@templates/skill-examples/task-generator/metrics-catalog.md#완료-기준-생성-예시]

persistent-loop와 조합 시 완료 기준을 완료 신호로 사용 가능

## 다음 단계

Task 목록 생성 완료 후:

```markdown
Task 목록이 생성되었습니다: tasks/tasks-{feature-name}.md

총 {N}개의 Task, {M}개의 Sub-task가 있습니다.
모든 Task에 완료 기준이 자동 생성되었습니다. ✅

Task 1.1부터 시작하시겠습니까? (y/n)
```

→ 'y' 선택 시 [@skills/task-executor/SKILL.md] skill 호출

## 관련 Skills

- `3-step-workflow/SKILL.md` - 전체 워크플로우
- `prd-generator/SKILL.md` - 이전 단계 (기능 요청 → PRD)
- `task-executor/SKILL.md` - 다음 단계 (Task 순차 실행)

## Changelog

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.2.0 | 2026-02-12 | 저장 경로 통일: docs/design/, docs/prd/ → tasks/ |
| 1.1.0 | 2026-02-10 | 저장 경로 변경: docs/design/ → docs/prd/{feature}-prd.md (통일) |
| 1.0.0 | 2026-01-27 | 초기 생성 (archive 복원) |
