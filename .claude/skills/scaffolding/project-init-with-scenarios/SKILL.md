---
name: project-init-with-scenarios
triggers:
  - "project init with scenarios"
description: "시나리오 수집 → 프로젝트 초기화 → PRD 생성을 통합한 워크플로우. 프로젝트 시작 전 해결할 문제들을 체계적으로 정의한다."
argument-hint: "[project_name] [project_type] [scenario_count] - 예: my-project data-science 3"
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
  - AskUserQuestion
  - Skill
model: claude-sonnet-4-6[1m]
context: >-
  프로젝트 초기화 전 시나리오 기반 설계 워크플로우.
  brainstorming, save-scenario, project-init, prd-workflow를 순차 조합하여
  시나리오 중심의 프로젝트 구조를 생성한다.
agent: >-
  프로덕트 아키텍트 페르소나로 작동. 사용자와 대화로 프로젝트가 해결할 문제들을
  명확히 하고, 각 시나리오를 구체화한 후 프로젝트 구조를 생성한다.
  "왜 이 프로젝트를 만드는가?"에서 시작하여 "무엇을 구현할 것인가"로 점진적으로 발전시킨다.
category: 워크플로우
skill-type: Composite
references:
  - "@skills/brainstorming/SKILL.md"
  - "@skills/save-scenario/SKILL.md"
  - "@skills/project-init/SKILL.md"
  - "@skills/prd-workflow/SKILL.md"
referenced-by:
  - "@skills/project-init/SKILL.md"
  - "@skills/save-scenario/SKILL.md"
  - "@skills/prd-workflow/SKILL.md"

---
# project-init-with-scenarios

> 시나리오 중심 프로젝트 초기화 워크플로우

---

## 목적

1. **문제 정의 우선**: 프로젝트 구조보다 해결할 문제를 먼저 정의
2. **시나리오 기반 설계**: 각 시나리오를 브레인스토밍으로 구체화
3. **추적 가능성**: 초기 시나리오 → 요구사항 → 구현까지 연결
4. **일관된 문서화**: 시나리오, PRD, 프로젝트 구조가 자동 연결

---

## 스킬 유형

**Composite Skill** - 다음 스킬들을 순차 조합:

| 순서 | Phase | 스킬 | 역할 |
|------|-------|------|------|
| 1 | 시나리오 수집 | [@skills/brainstorming/SKILL.md] | 각 시나리오를 대화로 구체화 |
| 2 | 시나리오 저장 | [@skills/save-scenario/SKILL.md] | 시나리오 문서 생성 (brainstorming이 자동 호출) |
| 3 | 프로젝트 초기화 | [@skills/project-init/SKILL.md] | 프로젝트 구조 생성 |
| 4 | PRD 생성 (선택) | [@skills/prd-workflow/SKILL.md] | 시나리오 기반 PRD 문서 생성 |

---

## 파라미터

| 파라미터 | 필수 | 기본값 | 설명 |
|----------|------|--------|------|
| `project_name` | No | (대화형) | 프로젝트 이름 (snake_case 권장) |
| `project_type` | No | (대화형) | 프로젝트 타입 (data-science, backend-fastapi 등) |
| `scenario_count` | No | 3 | 수집할 시나리오 개수 (1-5 권장) |

---

## 실행 프로세스

### Phase 0: 프로젝트 비전 수집

프로젝트 기본 정보를 수집한다. 파라미터로 제공되지 않은 경우 AskUserQuestion으로 대화형 입력을 받는다.

```
1. 프로젝트 기본 정보
   - project_name (인자 또는 질문)
   - project_type (인자 또는 질문)

2. 핵심 질문
   "이 프로젝트가 해결할 핵심 문제는 무엇인가요?"
   → 사용자 답변을 기반으로 시나리오 개수 제안

3. 시나리오 개수 확인
   질문: "프로젝트 시나리오를 몇 개 정의하시겠습니까?"
   옵션: 1개(MVP) / 3개(표준) / 5개(상세) / 건너뛰기
```

### Phase 1: 시나리오 수집 및 구체화

각 시나리오를 반복적으로 수집한다. brainstorming 스킬이 자동으로 save-scenario 호출 여부를 묻는다.

```
for i in range(1, scenario_count + 1):
    1. 시나리오 제목 입력 받기
       "시나리오 {i}/{scenario_count}의 주제를 입력해주세요:"

    2. /brainstorming 호출
       Skill tool: /brainstorming "{시나리오 제목}"

       → brainstorming 스킬 내부에서:
          - 사용자와 대화로 구체화
          - 완료 후 "저장할까요?" 질문 (AskUserQuestion)
          - 예 선택 시 /save-scenario 자동 호출

    3. 저장 상태 추적
       각 시나리오별로:
       - 제목 (title)
       - 저장 여부 (saved: true/false)
       - 파일 경로 (저장된 경우만)

    4. 계속 진행 확인
       "시나리오 {i} 완료. 다음 시나리오를 계속할까요?"
```

**출력 디렉토리**:
```
docs/references/scenarios/
├── 2026-01-27_scenario-1.md
├── 2026-01-27_scenario-2.md
└── 2026-01-27_scenario-3.md
```

### Phase 2: 시나리오 인덱스 생성

수집된 시나리오의 상태를 요약하여 사용자에게 제시한다.

```
1. 시나리오 추적 상태 수집
   - 저장된 시나리오 (파일 경로 포함)
   - 미저장 시나리오 (대화만 진행)

2. 시나리오 요약 출력
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   시나리오 수집 완료
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   수집된 시나리오: 3개 (저장됨: 2개, 미저장: 1개)

   ✅ 1. [시나리오-1] docs/references/scenarios/...
   ⚠️  2. [시나리오-2] (미저장)
      💡 저장하려면: /save-scenario "시나리오-2"
   ✅ 3. [시나리오-3] docs/references/scenarios/...
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 3: 프로젝트 초기화

project-init 스킬을 호출하여 프로젝트 구조를 생성한다.

```
1. /project-init 호출
   Skill tool: /project-init {project_name} {project_type}

   → 프로젝트 폴더 구조 생성
   → CLAUDE.md, README.md, pyproject.toml 등 생성

2. CLAUDE.md에 시나리오 링크 추가
   .claude/CLAUDE.md의 Quick Commands 섹션에:

   ## 프로젝트 시나리오

   - [시나리오 1](../docs/references/scenarios/...)
   - [시나리오 2](../docs/references/scenarios/...)

   시나리오 추가: `/brainstorming {새_시나리오}`
   PRD 생성: `/prd-workflow {시나리오명}`
```

### Phase 4: PRD 생성 (선택)

사용자에게 PRD 생성 여부를 질문한다.

```
1. PRD 생성 여부 확인
   질문: "수집된 시나리오를 PRD 문서로 변환할까요?"
   옵션:
     - "예 - 각 시나리오별 PRD 생성 (권장)"
     - "나중에 - 프로젝트 구조만 생성"

2. 선택 시 각 시나리오별 PRD 생성
   for scenario in saved_scenarios:
       Skill tool: /prd-workflow "{scenario.name}"

       → tasks/{scenario.name}-prd.md 생성
       → tasks/{scenario.name}-tasks.md 생성
```

### Phase 5: 완료 보고

생성된 산출물을 요약하여 보고한다.

```
╔══════════════════════════════════════════════════════╗
║    PROJECT INIT WITH SCENARIOS 완료                  ║
║    프로젝트: {project_name}                          ║
╚══════════════════════════════════════════════════════╝

생성된 산출물:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 시나리오 (docs/references/scenarios/)
   • 2026-01-27_scenario-1.md
   • 2026-01-27_scenario-2.md

📁 PRD (tasks/) - 선택 시
   • scenario-1-prd.md
   • scenario-2-prd.md

📁 프로젝트 구조
   • .claude/CLAUDE.md (시나리오 링크됨)
   • src/{project_name}/
   • tests/
   • pyproject.toml

다음 단계:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 첫 시나리오 구현 시작
   → /3-step-workflow "시나리오-1 구현"

2. 시나리오 추가
   → /brainstorming {새_기능}

3. CLAUDE.md 개인화
   → .claude/CLAUDE.md 검토 및 수정
```

---

## 사용 예시

### 예시 1: 완전 대화형 (파라미터 없음)

```bash
/project-init-with-scenarios
```

프로젝트명, 타입, 핵심 문제를 차례로 질문받는다. 시나리오 개수를 선택하고 각 시나리오를 브레인스토밍으로 구체화한다.

### 예시 2: 일부 파라미터 제공

```bash
/project-init-with-scenarios my-analytics data-science 3
```

프로젝트 정보는 제공되었으므로 핵심 문제와 시나리오 내용만 질문받는다.

### 예시 3: 시나리오 건너뛰기

```bash
/project-init-with-scenarios my-project backend-fastapi 0
```

시나리오 수집을 건너뛰고 프로젝트 구조만 생성한다. 시나리오는 나중에 `/brainstorming`으로 추가 가능하다.

---

## 관련 스킬

| 스킬 | 관계 | 설명 |
|------|------|------|
| [@skills/brainstorming/SKILL.md] | 하위 | 각 시나리오를 대화로 구체화 |
| [@skills/save-scenario/SKILL.md] | 하위 | 시나리오 문서 생성 (brainstorming이 호출) |
| [@skills/project-init/SKILL.md] | 하위 | 프로젝트 구조 생성 |
| [@skills/prd-workflow/SKILL.md] | 하위 (선택) | 시나리오 기반 PRD 생성 |
| [@skills/3-step-workflow/SKILL.md] | 후속 | 시나리오 구현 워크플로우 |

---

## 주의사항

1. **시나리오 개수**: 1-5개 권장 (너무 많으면 초기화가 길어짐)
2. **중단 및 재개**: Phase별로 중단 가능, 생성된 파일은 유지됨
3. **기존 프로젝트**: 이미 프로젝트가 있다면 `/brainstorming` → `/save-scenario`만 사용
4. **저장 상태**: 일부 시나리오만 저장해도 진행 가능 (나중에 복구 가능)

---

## Changelog

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.3.0 | 2026-02-12 | 저장 경로 통일: docs/prd/ → tasks/ |
| 1.2.0 | 2026-01-27 | 중복 제거 리팩토링 - 690줄 → 200줄 |
| 1.1.0 | 2026-01-27 | brainstorming 자동 연동 |
| 1.0.0 | 2026-01-27 | 초기 생성 |
