---
name: prd-workflow
triggers:
  - "prd workflow"
description: "PRD 생성 전체 워크플로우를 자동화한다. 대화 → 시나리오 → 레퍼런스 → PRD → 다이어그램 → 태스크."
argument-hint: "[feature-name] - 기능명"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Glob
  - Task
  - WebSearch
  - WebFetch
  - AskUserQuestion
model: claude-sonnet-4-6[1m]
context: PRD 생성 워크플로우 Composite 스킬이다. 여러 하위 스킬을 순차 호출하여 완전한 PRD 패키지를 생성한다.
agent: 당신은 프로덕트 매니저입니다. 요구사항을 체계적으로 정리하고 완전한 PRD 문서 세트를 생성합니다.
hooks:
  pre_execution: []
  post_execution: []
category: 워크플로우
skill-type: Composite
references:
  - "@skills/3-step-workflow/SKILL.md"
  - "@skills/diagram-generator/SKILL.md"
  - "@skills/doc-prd/SKILL.md"
  - "@skills/doc-spec/SKILL.md"
  - "@skills/doc-tasks/SKILL.md"
  - "@skills/ref-url-fetcher/SKILL.md"
  - "@skills/ref-web-search/SKILL.md"
  - "@skills/save-scenario/SKILL.md"
referenced-by:
  - "@skills/project-init-with-scenarios/SKILL.md"

---
# prd-workflow

PRD 생성 전체 워크플로우를 자동화하는 Composite 스킬.

## 목적

- PRD 생성 프로세스 표준화
- 대화에서 완전한 PRD 패키지까지 자동화
- 여러 스킬 조합하여 일관된 산출물 생성

## 사용법

```bash
/prd-workflow user-authentication
/prd-workflow payment-system --skip-ref
/prd-workflow dashboard --verbose
```

---

## 스킬 타입

**Composite Skill** - 다음 스킬들을 순차 조합:

| 순서 | 스킬 | 역할 | 조건 |
|------|------|------|------|
| 1 | [@skills/save-scenario/SKILL.md] | 시나리오 추출 & 저장 | **조건부** (파일 없을 때만) |
| 2 | [@skills/ref-web-search/SKILL.md] | 웹 검색으로 레퍼런스 수집 | 선택 |
| 3 | [@skills/ref-url-fetcher/SKILL.md] | 특정 URL 문서 수집 | 선택 |
| 4 | [@skills/doc-prd/SKILL.md] | PRD 문서 생성 | 항상 |
| 5 | [@skills/diagram-generator/SKILL.md] | 다이어그램 생성 & 삽입 | 선택 |
| 6 | [@skills/doc-tasks/SKILL.md] | 태스크 분해 | 항상 |

---

## 프로세스 플로우

```
1. 시나리오 확인
   - docs/references/scenarios/*{feature}*.md 검색
   - 없으면 /save-scenario 호출

2. 레퍼런스 수집 (선택)
   - /ref-web-search (기술 조사)
   - /ref-url-fetcher (문서 수집)
   → docs/references/

3. PRD 생성
   - /doc-prd 호출
   - 시나리오 + 레퍼런스 입력
   → tasks/{feature}-prd.md

4. 다이어그램 생성 (선택)
   - /diagram-generator 호출
   - Sequence/Component/ER 다이어그램
   - PRD에 자동 삽입

5. 태스크 분해
   - /doc-tasks 호출
   - PRD 기반 atomic task 분해
   → tasks/{feature}-tasks.md
```

**프로세스 플로우 다이어그램**: [@templates/skill-examples/prd-workflow/process-flow.md]

---

## 중복 방지 메커니즘

**STEP 1: 시나리오 파일 확인 (중요)**

기존 시나리오 파일을 먼저 확인하여 중복 저장을 방지한다.

**중복 확인 로직**: [@templates/skill-examples/prd-workflow/deduplication-check.py]

이를 통해 brainstorming → save-scenario → prd-workflow 체인에서 중복 저장을 방지한다.

---

## AskUserQuestion 활용

**지점 1: 시나리오 확인 후 진행 여부**

시나리오 파일 확정 후 다음 단계 진행 확인.

**지점 2: 레퍼런스 수집 필요 여부**

웹 검색 / URL 수집 / 둘 다 / 스킵 선택.

**지점 3: 다이어그램 추가 여부**

Sequence / Component / ER / 스킵 선택 (multiSelect: true).

**지점 4: 다음 단계 제안**

PRD 완성 후 구현 / 리뷰 / 완료 선택.

**상세 질문 형식**: [@templates/skill-examples/prd-workflow/askuserquestion-examples.md]

---

## 산출물

### 문서

| 파일 | 경로 | 내용 |
|------|------|------|
| 시나리오 | `docs/references/scenarios/` | 사용자 스토리, 사용 사례 |
| 레퍼런스 | `docs/references/` | 웹 검색 결과, URL 문서 |
| PRD | `tasks/{feature}-prd.md` | 제품 요구사항 문서 |
| Tasks | `tasks/{feature}-tasks.md` | 구현 태스크 목록 |

### 다이어그램 (선택)

- Sequence Diagram (상호작용 흐름)
- Component Diagram (아키텍처)
- ER Diagram (데이터 모델)

---

## 실행 예시

**전체 출력 예시**: [@templates/skill-examples/prd-workflow/output-example.md]

### 요약

```
╔══════════════════════════════════════════════════════════════╗
║                    PRD WORKFLOW COMPLETE                      ║
║              Feature: user-authentication                     ║
╚══════════════════════════════════════════════════════════════╝

✅ 생성된 파일:
   • docs/references/scenarios/2026-01-27_user-authentication.md
   • docs/references/jwt-auth-best-practices.md
   • tasks/user-authentication-prd.md
   • tasks/user-authentication-tasks.md

✅ 삽입된 다이어그램:
   • Sequence Diagram (로그인 플로우)
   • Component Diagram (인증 아키텍처)

📋 다음 단계:
   1. PRD 리뷰 요청
   2. /3-step-workflow로 구현 시작
   3. 태스크별 할당
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/brainstorming/SKILL.md] | 초기 아이디어 구체화 |
| [@skills/save-scenario/SKILL.md] | 시나리오 추출 & 저장 |
| [@skills/ref-web-search/SKILL.md] | 웹 검색 레퍼런스 수집 |
| [@skills/ref-url-fetcher/SKILL.md] | URL 문서 수집 |
| [@skills/doc-prd/SKILL.md] | PRD 생성 |
| [@skills/diagram-generator/SKILL.md] | 다이어그램 생성 |
| [@skills/doc-tasks/SKILL.md] | 태스크 분해 |
| [@skills/3-step-workflow/SKILL.md] | 구현 워크플로우 |
| [@skills/project-init-with-scenarios/SKILL.md] | 프로젝트 초기화 연계 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-02-12 | 1.3.0 | 저장 경로 통일: docs/prd/, docs/tasks/ → tasks/ |
| 2026-01-28 | 1.2.0 | 보수적 리팩토링 - 223→200줄. 중복 방지 메커니즘 템플릿 분리 |
| 2026-01-27 | 1.1.0 | 보수적 리팩토링 - 316→226줄. 상세 예시 템플릿 분리 |
| 2026-01-21 | 1.0.0 | 초기 생성 - PRD 워크플로우 자동화 |
