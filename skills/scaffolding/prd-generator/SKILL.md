---
name: prd-generator
triggers:
  - "prd generator"
description: "사용자의 기능 요청을 체계적인 Product Requirements Document(PRD)로 변환한다. Junior 개발자도 이해하고 구현할 수 있는 명확한 요구사항 문서를 생성한다."
argument-hint: "[feature_description] - 구현할 기능 설명"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: PRD 생성 전문 스킬. 3-step-workflow의 Step 1에서 호출되며, 단독으로도 사용 가능.
agent: PRD 생성 전문가 - 사용자의 기능 요청을 명확화 질문을 통해 구체화하고 체계적인 PRD 문서로 변환한다.
hooks:
  pre_execution: []
  post_execution: []
category: 문서 생성
skill-type: Atomic
references: []
referenced-by:
  - "@skills/doc-prd/SKILL.md"

---
# PRD Generator Skill

사용자의 기능 요청을 체계적인 **Product Requirements Document(PRD)**로 변환한다.
Junior 개발자도 이해하고 구현할 수 있는 명확한 요구사항 문서를 생성한다.

## 목적

1. **요구사항 명확화**: 사용자의 모호한 요청을 구체적인 요구사항으로 변환
2. **구현 가능성**: Junior 개발자도 이해하고 구현할 수 있는 수준의 명확성 제공
3. **문서화**: 프로젝트 설계 문서로 활용 가능한 체계적 구조
4. **커뮤니케이션**: 이해관계자 간 공통 이해를 위한 참조 문서

## Prerequisites

이 스킬은 복잡한 reasoning이 필요하므로:
- **모델**: Opus (claude-opus-4-5-20251101)
- **extended thinking** 활성화 권장

## 사용 시점

사용자가 다음과 같은 요청을 할 때 이 스킬을 사용한다:

- "PRD 만들어줘", "PRD 생성해줘"
- "요구사항 정의해줘", "기능 정의해줘"
- "기능을 만들고 싶어: {설명}"
- 3-step-workflow의 Step 1 진행 시

## 워크플로우

### 1. 초기 요청 수신
- 사용자의 기능 설명 입력

### 2. 명확화 질문 (3-5개)
- "무엇을" 구축할지
- "왜" 필요한지
- 옵션은 번호로 쉽게 선택 가능하게

### 3. PRD 생성
- `tasks/{feature}-prd.md` 저장

## 명확화 질문 가이드

### 필수 질문 영역

1. **문제 정의**: 이 기능이 해결하려는 문제는?
2. **사용자**: 누가 이 기능을 사용하는가?
3. **성공 기준**: 어떻게 성공을 측정하는가?
4. **범위**: 포함되어야 할 것과 제외할 것은?
5. **기술 제약**: 알려진 기술적 제약사항은?

### 질문 형식

```markdown
PRD 작성을 위해 몇 가지 질문이 있습니다:

1. **문제 정의**
   이 기능이 해결하려는 핵심 문제는 무엇인가요?
   a) 기존 프로세스의 비효율성
   b) 누락된 기능
   c) 사용자 경험 개선
   d) 기타: ___

2. **대상 사용자**
   주요 사용자는 누구인가요?
   a) 내부 팀
   b) 최종 사용자
   c) 관리자
   d) 기타: ___

3. **우선순위**
   가장 중요한 요구사항은? (1-3개 선택)
   a) 속도/성능
   b) 사용 편의성
   c) 데이터 정확성
   d) 확장성
   e) 기타: ___
```

## PRD 템플릿

```markdown
# PRD: {Feature Name}

## 1. 개요 (Overview)

### 1.1 문제 정의
{이 기능이 해결하려는 문제를 1-2문장으로 기술}

### 1.2 목표
{달성하려는 구체적인 목표}

## 2. 목표 (Goals)

- [ ] Goal 1: {구체적이고 측정 가능한 목표}
- [ ] Goal 2: {구체적이고 측정 가능한 목표}
- [ ] Goal 3: {구체적이고 측정 가능한 목표}

## 3. 사용자 스토리 (User Stories)

### US-1: {Story Title}
**As a** {user type}
**I want** {functionality}
**So that** {benefit}

**Acceptance Criteria:**
- [ ] AC-1.1: {구체적 수락 기준}
- [ ] AC-1.2: {구체적 수락 기준}

### US-2: {Story Title}
...

## 4. 기능 요구사항 (Functional Requirements)

### FR-1: {Requirement Title}
{상세 설명. Junior 개발자가 이해할 수 있도록 명확하게.}

### FR-2: {Requirement Title}
...

## 5. 비기능 요구사항 (Non-Functional Requirements)

- **성능**: {예: 응답시간 < 200ms}
- **확장성**: {예: 동시 사용자 1000명 지원}
- **보안**: {예: 인증 필요}

## 6. 비목표 (Non-Goals / Out of Scope)

명시적으로 이 PRD에서 **제외**되는 항목:
- {제외 항목 1}
- {제외 항목 2}

## 7. 설계 고려사항 (Design Considerations)

### UI/UX
{관련 UI/UX 요구사항 또는 "N/A"}

### 기술적 고려사항
- **의존성**: {기존 모듈, 라이브러리}
- **데이터 모델**: {필요한 스키마 변경}
- **API**: {필요한 엔드포인트}

## 8. 테스트 전략 (Testing Strategy)

- **Unit Tests**: {테스트할 핵심 로직}
- **Integration Tests**: {통합 테스트 시나리오}
- **E2E Tests**: {End-to-End 시나리오}

## 9. 마일스톤 (Milestones)

| Phase | 설명 | 예상 완료 |
|-------|------|----------|
| Phase 1 | {MVP 기능} | {날짜} |
| Phase 2 | {확장 기능} | {날짜} |

---
*Generated: {날짜}*
*Status: Draft*
```

## 실행 지침

### DO (해야 할 것)

1. **질문은 3-5개로 제한**: 핵심 정보만 수집, 번호/옵션으로 쉽게 답변 가능하게
2. **명확한 언어 사용**: "시스템은 ~해야 한다" 형식, Junior 개발자 기준으로 작성
3. **측정 가능한 목표 설정**: 구체적 수치 포함, 성공 기준 명확화

### DON'T (하지 말 것)

1. **"어떻게(How)"에 집중하지 말 것**: PRD는 "무엇(What)"과 "왜(Why)"에 집중
2. **모호한 표현 금지**: "빠르게" → "200ms 이내", "많은 데이터" → "100만 건"
3. **과도한 질문 금지**: 80% 정보로 시작, 필요시 추가 질문

## 출력 위치 (하이브리드 구조)

### 저장소
```
tasks/{feature}-prd.md
```

**예시**:
- `tasks/user-profile-card-prd.md`
- `tasks/payment-system-prd.md`

**디렉토리 자동 생성**: tasks/ 디렉토리가 없으면 자동 생성

## AskUserQuestion 활용 지점

### 지점 1: 기능 명확화 (필수)

**타이밍**: 초기 요청 수신 직후

**질문 예시**:
```yaml
questions:
  - question: "이 기능이 해결하려는 핵심 문제는 무엇인가요?"
    header: "문제 정의"
    multiSelect: false
    options:
      - label: "기존 프로세스의 비효율성"
        description: "현재 수동으로 처리되는 작업을 자동화"
      - label: "누락된 기능"
        description: "완전히 새로운 기능 추가"
      - label: "사용자 경험 개선"
        description: "기존 기능의 UX 향상"
```

### 지점 2: 우선순위 결정 (권장)

**타이밍**: 요구사항 수집 중

**질문 예시**:
```yaml
questions:
  - question: "가장 중요한 요구사항을 선택해주세요 (복수 선택 가능)"
    header: "우선순위"
    multiSelect: true
    options:
      - label: "속도/성능"
        description: "빠른 응답 시간, 높은 처리량"
      - label: "사용 편의성"
        description: "직관적인 UI, 쉬운 학습 곡선"
      - label: "데이터 정확성"
        description: "오류 없는 데이터 처리"
      - label: "확장성"
        description: "향후 확장 가능한 구조"
```

## 다음 단계

PRD 생성 완료 후:

```
"PRD가 생성되었습니다:
- tasks/{feature}-prd.md

Task 목록을 생성하시겠습니까? (y/n)"
```

→ 'y' 선택 시 [@skills/task-generator/SKILL.md] skill 호출

## 관련 Skills

- `3-step-workflow/SKILL.md` - 전체 워크플로우
- `task-generator/SKILL.md` - 다음 단계 (PRD → Task 분해)
- `doc-prd/SKILL.md` - 일반 PRD 생성 (3-step과 무관)

## Changelog

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.2.0 | 2026-02-10 | 저장 경로 변경: docs/design/ → tasks/{feature}-prd.md (통일) |
| 1.1.0 | 2026-01-28 | user-invocable: false로 변경, doc-prd에 통합됨 |
| 1.0.0 | 2026-01-27 | 초기 생성 (archive 복원) |

## Gotchas (실패 포인트)

- 추상적 요구사항 PRD 생성 금지 — 'implement login' → 'JWT 기반 로그인, 만료 24h'
- PRD 완성 후 구현 없이 방치 시 문서화 비용만 발생
- 수락 기준 없는 PRD → 완료 여부 판단 불가
- scope creep 방지: PRD는 현재 sprint 범위만
