# Deep Interview Spec: 팀 General Rules 완전 정의 시스템

## Metadata
- Interview ID: general-rules-001
- Rounds: 13
- Final Ambiguity Score: 3.5%
- Type: brownfield
- Generated: 2026-03-18
- Threshold: 5%
- Status: PASSED

## Clarity Breakdown
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.97 | 35% | 0.340 |
| Constraint Clarity | 0.97 | 25% | 0.243 |
| Success Criteria | 0.96 | 25% | 0.240 |
| Context Clarity | 0.95 | 15% | 0.143 |
| **Total Clarity** | | | **0.965** |
| **Ambiguity** | | | **3.5%** |

---

## Goal

`shucle-ai-agent-general-rules` repo를 git clone하면 팀원이 다음날부터 Claude Code로 일할 수 있는 완전한 툴킷을 만든다. 동시에 이 내용을 PR로 제출하여 팀 전체가 Claude Code 개발 워크플로우를 논의하는 출발점으로 삼는다.

핵심 철학 (Issue #74 기반):
- PR 범위 = 코드 양이 아니라 설계 결정 하나
- AI에게 일을 잘 시키려면 규칙이 명확해야 한다 (CLAUDE.md)
- deep-interview → ralplan → ralph 워크플로우로 모호성 제거 후 구현

---

## 전체 산출물 구조

### 1. 전역 규칙 (루트 CLAUDE.md — 이미 부분 존재)

추가/수정 필요 항목:
- `## Team Operations` 확장: AW-001~AW-005 (현재 일부만 있음)
- deep-interview 의무: 모호성 5% 미만까지 진행, 구현 전 필수
- omc-teams 의무: AskUserQuestion 전뿐만 아니라 deep-interview 시작 전에도 의무
- PR 규칙 섹션 신규: Rule of Small, ADR 의무, 설계문서 PR 먼저

### 2. Skills (`.claude/skills/` — 신규 생성 필요)

#### Python 코딩 컨벤션 강제 (convention-python 확장)
- 타입힌트 필수 (모든 함수 파라미터 + 반환값)
- 줄 길이 **79자** 엄격 적용 (80 아님)
- Docstring: Google style, **한국어**, **73자 이하**, **Logics 섹션 필수**
- 한국어 블록 주석: 모든 기능 단위에 반드시 작성
- 네이밍: `snake_case` (함수/변수), `PascalCase` (클래스), `UPPER_SNAKE_CASE` (상수)
- Import 순서: 표준 → 서드파티 → 로컬 (isort 기준)
- 실제 사고 사례: 타입 미선언 + 80자 미준수로 코드 대량 재작업 발생

#### Data Science / Pandas 규칙 (convention-python에 포함, .claude/skills/)

- pandas code: 반드시 DataFrame을 vector적 관점으로 최적화 (loop 대신 vectorization)
- Query 작성 시: 반드시 ANSI SQL로 구현
- 함수 구현: 사용자가 함수 구현을 명시적으로 요청할 때만 구현
- 모든 함수 정의 시: typing 명시 필수 (파라미터 + 반환값)
- 구체적 상황 예시: `df.iterrows()` 사용 → 금지, `df.apply()` 또는 vectorized 연산으로 대체

#### Git 커밋 컨벤션 (convention-commit)
- 포맷: `type(scope): subject` (50자 이내)
- 타입: feat, fix, docs, refactor, test, chore
- Co-Authored-By 푸터 금지
- 브랜치명: `{type}/{issue-number}-{brief-description}`

#### 설계 패턴 (convention-design)
- Factory, Strategy, Repository, Observer 패턴 언제 어떻게 사용할지
- SOLID 원칙별 구체적 상황 예시
- God Class, Long Method 안티패턴 탐지

#### Logging 컨벤션 (convention-logging)
- structlog vs logging 선택 기준
- TRACE 레벨 사용 조건
- 로그 포맷: JSON (production), 텍스트 (development)
- 레벨 기준: DEBUG/INFO/WARNING/ERROR/CRITICAL

#### ADR 작성 (convention-adr)
- 되돌리기 어려운 결정 = ADR 필수 (파일 포맷, API 계약, 좌표계 등)
- ADR 포맷: Status/Context/Decision/Consequences/Considered Options/Completion Checklist
- 되돌리기 쉬운 결정 = ADR 불필요 (변수명, 함수명, 주석)

#### 디자인 패턴 (convention-design-patterns)

- Factory Pattern: 객체 생성 로직 분리 상황과 예시
- Strategy Pattern: 알고리즘 교체 가능하게 설계하는 상황과 예시
- Repository Pattern: data access layer 분리 상황과 예시
- Observer Pattern: event 기반 처리 상황과 예시
- 각 패턴마다 구체적 상황 2개 이상 필수

#### 프로젝트 폴더 구조 (convention-folder-structure)

- Python monorepo (uv workspace) 구조
- 단일 패키지 구조
- Data Science 프로젝트 구조 (notebooks, src, data, output)
- Agent 프로젝트 구조 (agents, libs, apps)
- 각 구조마다 언제 사용할지 기준 + 구체적 상황 2개 이상

#### 브랜치 협업 규칙 (convention-pr에 포함 또는 Git Workflow 섹션)

- 하나의 branch = 하나의 작업 범위 (설계 결정 하나)
- 다른 사람의 branch가 수정 중인 파일은 건드리지 않는다
- branch 시작 전 작업 범위를 CLAUDE.md 또는 PR description에 명시
- 브랜치명: `{type}/issue-{number}-{subject}` (kebab-case, 예: `feat/issue-74-pr-rules`)
- 이 프로젝트 현재 branch: `shucle-ai-agent-general-rules` — general rules 정의만 수정 대상

**구체적 상황 1**: 같은 팀원이 `libs/CLAUDE.md`를 수정 중인 branch가 있으면 → 내 branch에서 그 파일을 건드리지 않고 PR 우선순위 협의
**구체적 상황 2**: 작업 시작 전 GitHub에서 open PR 목록 확인 → 충돌 가능한 파일 미리 파악

#### PR 규칙 (convention-pr)
- 하나의 PR = 하나의 설계 결정
- 코드 PR 전 설계문서 PR 통과 필수
- PR description: 1문장 요약 + 설계문서 링크
- check-design-doc 스킬로 코드-설계 일치 자동 검증

### 3. 설정 강제 (자동 안전망)

#### pre-commit hook
- ruff (line-length=79, PEP8 전체)
- mypy --strict (모든 타입힌트 필수)
- bandit (보안)
- --no-verify 금지 규칙 명시

#### Stop hook (Claude Code after-hook)
- Claude Code 응답 완료 후 자동 실행
- /check-python-style 스킬 자동 호출
- 위반 시 경고 메시지

### 4. Nested CLAUDE.md (디렉토리별)

- `.claude/CLAUDE.md`: 팀 운영 규칙 전체 (AW-001~AW-010)
- `agents/CLAUDE.md`: ADK 패턴, root_agent 수출, 프롬프트 구조
- `libs/CLAUDE.md`: uv workspace, import 스타일, 모듈 구조 규칙
- `apps/CLAUDE.md`: CLI 러너 패턴, config.py 구조

모든 nested CLAUDE.md: **200줄 이하** 엄격 준수

### 5. 설정 표준화

- 가상환경: **uv 전용** (pip install 직접 사용 금지)
- 설정 관리: **OmegaConf + YAML** 기반 3계층 (base → domain → env)
- 하드코딩 금지: 모든 설정값은 YAML로

### 6. GitHub Issues → md화 (사전지식 참조)

- `gh api` 기반 이슈 내용 추출
- 저장 경로: `docs/references/github-issues/`
- 파일명: `issue-{number}-{subject}.md` (subject: kebab-case 영어, 30자 이하)
  - 예: `issue-74-ai-pr-workflow.md`
- 작업 시작 전 관련 이슈를 md화하여 컨텍스트로 제공

### 7. Output Style 파일 (.claude/ 통합)

- 팀 공통 output style 파일을 `.claude/output-styles/` 에 배치
- 예: `.claude/output-styles/data-driven-minds.md`
- 새 팀원이 clone 후 `.claude/output-styles/` 를 참조하여 동일한 output style 적용
- 기존 `dotfiles/claude-code/output-styles/` 경로의 파일을 이 repo로 이전

### 8. 기술 어휘 언어 규칙

**규칙**: 기술적 단어는 영어 사용, 일반 설명은 한국어 사용.

| 영어 유지 | 한국어 사용 |
|-----------|-------------|
| class, function, method, import | 이 함수는, 이 클래스는 |
| pre-commit, hook, skill, plugin | 사전 검사, 자동화, 기능 |
| PR, ADR, CLAUDE.md | - |
| snake_case, PascalCase, UPPER_SNAKE_CASE | - |
| omc-teams, deep-interview, ralplan | - |

**kebab-case vs snake_case 사용 기준**:

| 용도 | 표기법 | 예시 |
|------|--------|------|
| Python 파일/모듈/변수/함수 | `snake_case` | `demand_analysis.py`, `zone_id` |
| Python class | `PascalCase` | `DataProcessor` |
| Python 상수 | `UPPER_SNAKE_CASE` | `MAX_RETRY` |
| 문서 파일 (.md, .yaml) | `kebab-case` | `issue-74-ai-pr.md` |
| Git 브랜치명 | `kebab-case` | `feat/issue-74-pr-rules` |
| Skills/plugin 이름 | `kebab-case` | `convention-python` |
| 디렉토리 (Python import 대상) | `snake_case` | `libs/data_processing/` |
| 디렉토리 (문서/설정) | `kebab-case` | `docs/github-issues/` |
| OmegaConf/YAML 키 | `snake_case` | `zone_id: 40` |

원칙: `snake_case` = Python namespace 안, `kebab-case` = 파일시스템/URL/CLI 단위

**프로젝트 특화 예시**:
- 나쁨: "질문하기 전에 팀 기능을 사용한다"
- 좋음: "AskUserQuestion 전에 omc-teams를 사용하여 codex + gemini에게 조사한다"
- 나쁨: "파이썬 클래스는 첫글자를 대문자로"
- 좋음: "Python class 이름은 PascalCase 사용. 예: `MyAgent`"

---

## Agent Workflow Rules (AW-001~AW-010)

| 규칙 | 내용 | 구체적 상황 예시 |
|------|------|-----------------|
| AW-001 | 모델: Claude=`claude-sonnet-4-6[1m]`, Codex=`gpt-5.2-codex`, Gemini=고성능 사고 | 내부망에서 opus 불가, codex는 gpt-5.2-codex 고정 |
| AW-002 | 3-agent 조사: claude+codex+gemini 병렬 → 다수결 또는 사용자 결정 | 기술 선택 시 항상 3개 에이전트 의견 수렴 |
| AW-003 | deep-interview 시작 전 omc-teams 사전조사 의무 | 요구사항 수집 전 해당 도메인 best practice 조사 |
| AW-004 | AskUserQuestion 전 omc-teams 사전조사 의무 | 선택지 제시 전 반드시 조사 후 (Recommended) 명시 |
| AW-005 | deep-interview: 모호성 5% 미만까지 진행, 구현 전 필수 | 요구사항 불명확 시 즉시 deep-interview 시작 |
| AW-006 | 설계문서 먼저, 코드 나중: 코드 PR 전 설계 PR 통과 필수 | 코드 없이 CLAUDE.md + docs/design/ 먼저 작성 |
| AW-007 | 모든 구현: `/ralph` 사용, max iteration 100 | 간단한 변경도 ralph 루프로 검증 |
| AW-008 | ralplan 종료조건 10개 이상 정량적 목표 | grep 명령어로 측정 가능한 조건만 인정 |
| AW-009 | 되돌리기 어려운 결정 = ADR 먼저 | 파일 포맷 변경, API 계약, DB 스키마 등 |
| AW-010 | Stop hook + pre-commit 이중 안전망 | Claude 응답 후 자동 ruff+mypy, commit 시 pre-commit |

---

## Constraints

- 모든 CLAUDE.md + nested CLAUDE.md: 200줄 이하
- Python 줄 길이: 79자 (ruff line-length=79 강제)
- 타입힌트: 모든 함수 파라미터 + 반환값 필수 (mypy strict)
- Docstring: Google style, 한국어, 73자 이하, Logics 섹션 필수
- 한국어 블록 주석: 모든 기능 단위 의무
- uv 전용 (pip install 직접 금지)
- pre-commit --no-verify 금지
- AskUserQuestion 전/deep-interview 전: omc-teams 사전조사 의무

## LLM 행동 지침 (한국어 번역 포함 — 전역 CLAUDE.md 추가 필요)

> 원문 출처: 사용자 제공 CLAUDE.md 가이드라인
> 이 내용을 한국어로 번역하여 루트 CLAUDE.md 또는 .claude/CLAUDE.md에 추가한다.

### 1. Think Before Coding

**가정하지 말라. 혼란을 숨기지 말라. Tradeoff를 드러내라.**

구현 전에:
- 가정을 명시적으로 말하라. 불확실하면 질문하라.
- 여러 해석이 가능하면 제시하라 — 조용히 선택하지 말라.
- 더 단순한 approach가 있으면 말하라. 필요하면 반론을 제기하라.
- 무언가 불명확하면 멈춰라. 무엇이 혼란스러운지 명시하고 deep-interview를 시작하라.

**상황 1**: function signature가 설계문서에 없으면 → 추측해서 구현하지 말고 질문하라.
**상황 2**: "이 API endpoint를 추가해줘"라고 했을 때 request/response schema가 없으면 → 구현 전에 schema를 먼저 정의하고 확인받아라.

### 2. Simplicity First

**문제를 해결하는 최소한의 code만. 추측성 code 금지.**

- 요청받지 않은 feature 추가 금지.
- 단일 사용 code에 abstraction 금지.
- 요청받지 않은 flexibility/configurability 금지.
- 불가능한 scenario의 error handling 금지.
- 200줄로 썼는데 50줄로 가능하면 다시 써라.

**기준**: "senior engineer가 이걸 보고 과복잡하다고 할까?" → Yes면 단순화하라.

**상황 1**: data pipeline 하나 만들 때 미래를 대비한 plugin system 추가 → 금지.
**상황 2**: CSV를 읽는 function 작성 시 XML, JSON, Parquet도 지원하는 generic reader 구현 → 요청받지 않았으면 금지. CSV만 읽어라.

### 3. Surgical Changes

**반드시 수정해야 하는 것만 건드려라. 내가 만든 것만 청소하라.**

기존 code 편집 시:
- 인접 code, comment, format "개선" 금지.
- 망가지지 않은 것 refactoring 금지.
- 내가 다르게 할지라도 기존 style을 맞춰라.
- 관련 없는 dead code를 발견하면 언급만 하고 삭제 금지.

내 변경이 orphan을 만들면:
- 내 변경으로 인해 사용되지 않는 import/변수/함수는 제거.
- 기존 dead code는 요청받기 전까지 제거 금지.

**기준**: 모든 변경된 줄이 사용자 요청으로 직접 추적 가능해야 한다.

**상황 1**: bug 수정 중 인접 function이 개선 가능해 보여도 → 건드리지 않는다.
**상황 2**: import 순서가 PEP8에 어긋난 기존 파일을 편집할 때 → import 정렬 "개선" 금지. 요청받은 변경만 한다.

### 4. Goal-Driven Execution

**Success criteria를 정의하라. 검증될 때까지 반복하라.**

Task를 검증 가능한 목표로 변환:
- "validation 추가" → "잘못된 input에 대한 test 작성 후 통과"
- "bug 수정" → "bug 재현 test 작성 후 통과"
- "X refactoring" → "전후 test 통과 확인"

다단계 task는 간략한 plan 제시:
```
1. [Step] → verify: [확인 방법]
2. [Step] → verify: [확인 방법]
```

**상황 1**: "잘 되게 해줘" → 거절하고 "어떤 상태가 되면 완료인가요?" → deep-interview 시작.
**상황 2**: "성능을 개선해줘" → "현재 응답시간이 얼마이고, 목표는 얼마인가요?" → 정량적 기준 확정 후 구현.

---

## Non-Goals

- 즉시 nested CLAUDE.md 내용 작성 (계획만, 내용은 추후)
- 기존 코드 리팩터링 (새 규칙은 신규 코드부터 적용)
- 외부망 전용 기능 (내부망 기준으로 작성)

## Acceptance Criteria

- [ ] 루트 CLAUDE.md 200줄 이하 유지
- [ ] AW-001~AW-010 모두 루트 CLAUDE.md 또는 .claude/CLAUDE.md에 존재
- [ ] `.claude/skills/convention-python` 생성 및 구체적 상황 예시 포함
- [ ] `.claude/skills/convention-commit` 생성
- [ ] `.claude/skills/convention-design` 생성
- [ ] `.claude/skills/convention-design-patterns` 생성 (2+ 상황 per 패턴)
- [ ] `.claude/skills/convention-folder-structure` 생성 (2+ 상황 per 구조)
- [ ] `.claude/skills/convention-logging` 생성
- [ ] `.claude/skills/convention-adr` 생성
- [ ] `.claude/skills/convention-pr` 생성
- [ ] pre-commit 설정: ruff(79자) + mypy(strict) + bandit
- [ ] Stop hook 설정: check-python-style 자동 실행
- [ ] nested CLAUDE.md 4개 위치 확정 및 템플릿 작성
- [ ] omc-teams 사전조사 규칙이 AskUserQuestion + deep-interview 둘 다에 적용
- [ ] 실제 사고 사례(타입 미선언 + 80자)가 rule에 반영됨
- [ ] ADR 작성 규칙: 되돌리기 어려운 결정 기준 명시
- [ ] PR 규칙: Rule of Small + 설계문서 먼저 + check-design-doc
- [ ] `.claude/output-styles/data-driven-minds.md` 존재
- [ ] `docs/references/github-issues/` 디렉토리 생성 + README 포함
- [ ] 파일명 규칙: `issue-{number}-{subject}.md` (kebab-case, 30자 이하) 문서화
- [ ] 기술 어휘 규칙 (영어/한국어 구분 기준표) CLAUDE.md 또는 convention skill에 포함
- [ ] LLM 행동지침 4개 (한국어 번역 + 구체적 상황) CLAUDE.md에 포함

---

## Technical Context (Brownfield)

현재 존재하는 것:
- 루트 CLAUDE.md: 177줄 (Team Operations 포함)
- `.claude/skills/`: python-testing, lint-fix, code-simplifier, python-patterns (4개)
- `.claude/agents/`: python-reviewer.md (1개)
- `docs/design/ref/team-operations.md`: 91줄 (AW-001~005 일부)

추가 필요:
- Skills 6개 신규: convention-commit, convention-design, convention-logging, convention-adr, convention-pr, check-design-doc
- pre-commit 설정 파일
- Stop hook 설정 (settings.json)
- nested CLAUDE.md 4개

---

## Interview Transcript Summary

| Round | 질문 주제 | 답변 요약 |
|-------|-----------|-----------|
| 1 | 규칙 관리 방식 | Skills로 호출 |
| 2 | 도메인 범위 | Python+Git+Test+Design/Review 패턴+프로젝트 필수 |
| 3 | 완료 행동 기준 | 코드 작성 시 자동 적용 + PR 전 자동 검증 |
| 4 | 자동 vs 의도적 | 가이드(CLAUDE.md) + 자동 안전망(hooks) 둘 다 |
| 5 | Nested 대상 | .claude, agents, libs, apps 4곳 + PR 이중 축 철학 |
| 6 | PR 규칙 포함 방식 | CLAUDE.md 명시 + PR 템플릿 + check-design-doc skill |
| 7 | 최종 산출물 | clone 후 즉시 사용 + PR로 팀 논의 둘 다 |
| 8 | PR 범위 규칙 | Rule of Small + ADR 의무 + 설계문서 먼저 + 1문장 요약 |
| 9 | Python 컨벤션 | typing+docstring+logics+wordwrap 강력 강제 |
| 10 | 추가 포함 항목 | Logging+디자인패턴+GitHub md화+uv+OmegaConf 전부 |
| 11 | 강제 메커니즘 | pre-commit+mypy strict+ruff 79자+after-hook |
| 12 | omc-teams 위치 | deep-interview 전 + AskUserQuestion 전 동등 의무 |
| 13 | Hook 트리거 | Stop hook + pre-commit 이중 안전망 |
