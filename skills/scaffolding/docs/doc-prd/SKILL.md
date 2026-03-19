---
name: doc-prd
triggers:
  - "doc prd"
description: "Product Requirements Document (PRD) 생성 스킬. 대화를 통해 요구사항을 수집하고 구조화된 PRD를 생성한다."
argument-hint: "[feature_name] - PRD를 작성할 기능/제품명"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - Task
model: claude-sonnet-4-6[1m]
context: |
  프로젝트 요구사항 정의 시 사용. brainstorming 이후 또는 독립적으로 사용 가능.

  통합된 기능:
  - prd-generator 로직 포함: 명확화 질문 → PRD 생성
  - 3-step-workflow에서 호출 (Step 1)
  - 단독 사용 가능
agent: |
  PRD 작성 전문가. 사용자의 기능 요청을 명확화 질문을 통해 구체화하고,
  Junior 개발자도 이해할 수 있는 체계적인 PRD 문서로 변환한다.
  요구사항을 체계적으로 수집하고 구조화하여 개발팀이 이해할 수 있는 명확한 문서를 생성한다.
hooks:
  pre_execution: []
  post_execution: []
category: 문서 생성
skill-type: Atomic
references: []
referenced-by:
  - "@skills/3-step-workflow/SKILL.md"
  - "@skills/prd-workflow/SKILL.md"
  - "@skills/project-init/SKILL.md"

---
# doc-prd

> Product Requirements Document 생성 스킬

---

## 목적

1. **요구사항 체계화**: 흩어진 아이디어를 구조화된 문서로 변환
2. **명확한 범위 정의**: In-Scope / Out-of-Scope 명시
3. **성공 기준 설정**: 측정 가능한 목표 정의
4. **개발 가이드**: 개발팀이 참조할 수 있는 명확한 명세

---

## PRD 구조

```
tasks/
├── {feature_name}-prd.md     # PRD 문서
└── {feature_name}-ux.md      # UX 상세 (선택)
```

---

## 실행 프로세스

### Phase 1: 정보 수집

```
1. 기존 문서 확인
   - tasks/ 에 관련 문서 존재 여부
   - docs/references/scenarios/ 에 관련 시나리오

2. 명확화 질문 (3-5개) - prd-generator 패턴
   필수 질문 영역:
   a) 문제 정의: 이 기능이 해결하려는 문제는?
   b) 사용자: 누가 이 기능을 사용하는가?
   c) 성공 기준: 어떻게 성공을 측정하는가?
   d) 범위: 포함되어야 할 것과 제외할 것은?
   e) 기술 제약: 알려진 기술적 제약사항은?

3. 기본 정보 수집 (AskUserQuestion)
   - 제품/기능명
   - 타겟 사용자
   - 핵심 문제 정의
   - 비즈니스 목표
```

#### AskUserQuestion 활용 지점

**지점 1: 명확화 질문 (prd-generator 패턴)**

**타이밍**: 초기 요청 수신 직후

```yaml
AskUserQuestion:
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
        - label: "기술 부채 해소"
          description: "기존 시스템 개선 또는 리팩토링"

    - question: "주요 사용자는 누구인가요?"
      header: "대상 사용자"
      multiSelect: false
      options:
        - label: "내부 팀"
          description: "개발팀, 운영팀 등 내부 사용자"
        - label: "최종 사용자"
          description: "서비스를 사용하는 고객"
        - label: "관리자"
          description: "시스템 관리자 또는 비즈니스 관리자"

    - question: "가장 중요한 요구사항은? (1-3개 선택)"
      header: "우선순위"
      multiSelect: true
      options:
        - label: "속도/성능"
          description: "빠른 응답 시간, 대용량 처리"
        - label: "사용 편의성"
          description: "직관적인 UI/UX"
        - label: "데이터 정확성"
          description: "데이터 무결성 및 신뢰성"
        - label: "확장성"
          description: "향후 확장 가능한 구조"
```

**지점 2: 제품 목적 확인**

```yaml
AskUserQuestion:
  questions:
    - question: "이 기능의 핵심 목적은 무엇인가요?"
      header: "핵심 목적"
      multiSelect: false
      options:
        - label: "문제 해결"
          description: "사용자의 특정 문제를 해결"
        - label: "가치 증대"
          description: "비즈니스 가치 또는 사용자 경험 향상"
        - label: "차별화"
          description: "경쟁사 대비 차별화 요소"
        - label: "기술 부채 해소"
          description: "기존 시스템 개선 또는 리팩토링"
```

**지점 3: 타겟 사용자 정의**

```yaml
AskUserQuestion:
  questions:
    - question: "주요 타겟 사용자는 누구인가요?"
      header: "타겟 사용자"
      multiSelect: true
      options:
        - label: "일반 사용자"
          description: "제품의 주 사용층"
        - label: "파워 유저"
          description: "고급 기능을 활용하는 사용자"
        - label: "관리자"
          description: "시스템 관리 및 모니터링"
        - label: "개발자"
          description: "API 또는 SDK 사용자"
```

**지점 3: 우선순위 분류 (MoSCoW)**

```yaml
AskUserQuestion:
  questions:
    - question: "각 기능을 MoSCoW로 분류하시겠습니까?"
      header: "우선순위"
      multiSelect: false
      options:
        - label: "예 - 대화형 분류 (권장)"
          description: "각 기능별로 Must/Should/Could/Won't 질문"
        - label: "아니오 - 나중에 수동 편집"
          description: "PRD 생성 후 직접 편집"
```

**지점 4: 범위 명확화**

```yaml
AskUserQuestion:
  questions:
    - question: "초기 버전에 반드시 포함할 기능은?"
      header: "In-Scope"
      multiSelect: true
      options:
        - label: "[기능 1]"
          description: "핵심 가치 제공"
        - label: "[기능 2]"
          description: "사용자 경험에 중요"
        - label: "[기능 3]"
          description: "기술적 기반 필요"
```

**지점 5: 성공 지표 정의**

```yaml
AskUserQuestion:
  questions:
    - question: "성공을 어떻게 측정할까요?"
      header: "성공 지표"
      multiSelect: true
      options:
        - label: "사용자 지표"
          description: "DAU, MAU, 사용 빈도"
        - label: "비즈니스 지표"
          description: "매출, 전환율, ROI"
        - label: "기술 지표"
          description: "응답 시간, 에러율, 가용성"
        - label: "품질 지표"
          description: "만족도, NPS, 리텐션"
```

**지점 6: 기존 PRD 버전 업데이트 여부**

```yaml
AskUserQuestion:
  questions:
    - question: "기존 PRD를 업데이트할까요?"
      header: "버전 관리"
      multiSelect: false
      options:
        - label: "새 버전 생성 (권장)"
          description: "기존 유지, 새 파일 생성 (v2.0)"
        - label: "기존 버전 수정"
          description: "같은 파일 업데이트"
```

### Phase 2: 요구사항 상세화

```
1. 기능 요구사항 (Functional)
   - 핵심 기능 목록
   - 사용자 스토리 형식으로 정리
   - 우선순위 (Must/Should/Could/Won't)

2. 비기능 요구사항 (Non-Functional)
   - 성능 요구사항
   - 보안 요구사항
   - 확장성 요구사항

3. 제약 조건
   - 기술적 제약
   - 비즈니스 제약
   - 일정 제약
```

### Phase 3: 문서 생성

```
1. PRD 마크다운 생성
2. 사용자 검토
3. 피드백 반영
4. 최종 저장
```

---

## PRD 템플릿

```markdown
# PRD: {제품/기능명}

> 버전: 1.0 | 작성일: {날짜} | 작성자: {작성자}

---

## 1. 개요

### 1.1 배경 및 목적
[이 제품/기능이 필요한 이유와 해결하고자 하는 문제]

### 1.2 타겟 사용자
| 사용자 유형 | 특징 | 주요 니즈 |
|------------|------|----------|
| [유형1] | [특징] | [니즈] |

### 1.3 비즈니스 목표
- [목표 1 - 측정 가능한 형태]
- [목표 2]

---

## 2. 범위

### 2.1 In-Scope (포함)
- [x] [포함 항목 1]
- [x] [포함 항목 2]

### 2.2 Out-of-Scope (제외)
- [ ] [제외 항목 1] - 이유: [이유]
- [ ] [제외 항목 2] - 이유: [이유]

### 2.3 향후 고려사항 (Future)
- [ ] [향후 항목 1]

---

## 3. 기능 요구사항

### 3.1 핵심 기능 (Must Have)

#### F-001: [기능명]
| 항목 | 내용 |
|------|------|
| **설명** | [기능 설명] |
| **사용자 스토리** | As a [사용자], I want to [행동], so that [가치] |
| **인수 조건** | 1. [조건1]<br>2. [조건2] |
| **우선순위** | Must |

#### F-002: [기능명]
...

### 3.2 보조 기능 (Should Have)
...

### 3.3 선택 기능 (Could Have)
...

---

## 4. 비기능 요구사항

### 4.1 성능
| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 응답 시간 | < 200ms | [방법] |
| 처리량 | 100 req/s | [방법] |

### 4.2 보안
- [ ] [보안 요구사항 1]
- [ ] [보안 요구사항 2]

### 4.3 확장성
- [확장성 요구사항]

### 4.4 사용성
- [사용성 요구사항]

---

## 5. 기술 제약

| 제약 | 설명 | 영향 |
|------|------|------|
| [제약1] | [설명] | [영향] |

---

## 6. 마일스톤

| 단계 | 목표 | 완료 조건 |
|------|------|----------|
| Phase 1 | [목표] | [조건] |
| Phase 2 | [목표] | [조건] |

---

## 7. 성공 지표

| KPI | 현재 | 목표 | 측정 주기 |
|-----|------|------|----------|
| [지표1] | [현재값] | [목표값] | [주기] |

---

## 8. 리스크 및 대응

| 리스크 | 확률 | 영향 | 대응 방안 |
|--------|------|------|----------|
| [리스크1] | 높음 | 높음 | [대응] |

---

## 9. 참고 자료

- [관련 문서 1]
- [관련 문서 2]

---

## 변경 이력

| 버전 | 날짜 | 변경자 | 변경 내용 |
|------|------|--------|----------|
| 1.0 | {날짜} | {작성자} | 초기 작성 |
```

---

## 사용 예시

### 예시 1: 새 기능 PRD 생성

```
User: /doc-prd 사용자 대시보드

Claude: 사용자 대시보드 PRD 작성을 시작합니다.

## 정보 수집

[AskUserQuestion 호출]
question: "대시보드의 주요 목적은 무엇인가요?"
header: "목적"
options:
  - "데이터 시각화 (Recommended)" - 지표와 차트 표시
  - "작업 관리" - 할 일 목록, 프로젝트 현황
  - "알림 센터" - 중요 알림과 업데이트

User: 데이터 시각화

Claude: [AskUserQuestion 호출]
question: "타겟 사용자는 누구인가요?"
header: "사용자"
options:
  - "일반 사용자" - 기본 기능 사용
  - "관리자" - 전체 현황 모니터링
  - "데이터 분석가" - 상세 분석 필요

...

Claude: PRD 초안을 생성했습니다.
파일: tasks/user-dashboard-prd.md

검토 후 수정사항을 알려주세요.
```

### 예시 2: brainstorming 결과로 PRD 생성

```
User: /doc-prd
(이전에 /brainstorming으로 결제 시스템 아이디어 정리됨)

Claude: .claude/docs/scenarios/에서 관련 시나리오를 찾았습니다:
- 2026-01-21_payment-system-brainstorm.md

이 내용을 기반으로 PRD를 작성할까요?

User: 네

Claude: 시나리오 문서를 분석하여 PRD를 생성합니다.
추가 확인이 필요한 사항:

[AskUserQuestion 호출]
question: "결제 수단 우선순위를 정해주세요"
header: "결제수단"
options:
  - "카드 결제 우선 (Recommended)"
  - "간편결제 우선"
  - "모두 동시 구현"

...
```

### 예시 3: 기존 PRD 업데이트

```
User: /doc-prd 대시보드 --update

Claude: 기존 PRD를 확인합니다.
파일: tasks/user-dashboard-prd.md

### 현재 버전: 1.0

변경할 섹션을 선택해주세요:
1. 기능 요구사항 추가
2. 범위 변경
3. 마일스톤 업데이트
4. 전체 검토

User: 1

Claude: 추가할 기능을 설명해주세요.

User: 대시보드에 실시간 알림 기능 추가

Claude: F-005로 새 기능 요구사항을 추가합니다.
...
```

---

## 질문 흐름 가이드

### 핵심 질문 순서

```
1. 목적/배경
   - "이 기능이 해결하는 핵심 문제는?"
   - "비즈니스 목표는?"

2. 사용자
   - "타겟 사용자는?"
   - "사용자의 주요 니즈는?"

3. 범위
   - "반드시 포함할 기능은?"
   - "제외할 항목은?"

4. 제약
   - "기술적 제약은?"
   - "일정 제약은?"

5. 성공 지표
   - "성공을 어떻게 측정?"
   - "목표 수치는?"
```

### 우선순위 결정 (MoSCoW)

```
Must Have    - 없으면 출시 불가
Should Have  - 중요하지만 대체 가능
Could Have   - 있으면 좋음
Won't Have   - 이번 버전에서 제외
```

---

## 관련 스킬

| 스킬 | 관계 | 설명 |
|------|------|------|
| [@skills/prd-workflow/SKILL.md] | 호출처 | PRD 워크플로우에서 호출 |
| [@skills/brainstorming/SKILL.md] | 입력 | 아이디어 정리 후 PRD 작성 |
| [@skills/save-scenario/SKILL.md] | 입력 | 시나리오에서 요구사항 추출 |
| [@skills/doc-tasks/SKILL.md] | 후속 | PRD 기반 작업 분해 |
| [@skills/3-step-workflow/SKILL.md] | 연계 | Discuss 단계에서 PRD 참조 |

---

## 출력 위치

```
tasks/
├── {feature}-prd.md      # PRD 문서
├── {feature}-ux.md       # UX 상세 (선택)
└── {feature}-tech.md     # 기술 명세 (선택)
```

---

## 주의사항

1. **측정 가능한 목표**: 모호한 목표 금지, 수치화된 기준 필수
2. **범위 명확화**: In/Out-Scope 반드시 구분
3. **사용자 스토리 형식**: 기능은 "As a... I want to... so that..." 형식 권장
4. **변경 이력 관리**: 버전 업데이트 시 변경 이력 기록

---

## Changelog

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.1.0 | 2026-02-12 | 저장 경로 통일: docs/prd/ → tasks/ |
| 1.0.0 | 2026-01-21 | 초기 생성 - PRD 템플릿 및 워크플로우 |
