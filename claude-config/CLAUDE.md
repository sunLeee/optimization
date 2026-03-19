# claude-config

개인/팀 Claude Code 환경 설정. Skills, Rules, AW 설계 규칙(AW-001~045) 관리.

> **초기 설정:** `bash .claude/setup.sh` — [상세: .claude/docs/setup.md](.claude/docs/setup.md)

---

## 전제 조건

> 문서: [.claude/docs/setup.md](.claude/docs/setup.md) § 1. 필수 도구 설치


| 도구                   | 필수  | 설치                                  | 문서 위치        |
| -------------------- | --- | ----------------------------------- | ------------ |
| **tmux**             | 필수  | `brew install tmux`                 | setup.md § 1 |
| **oh-my-claudecode** | 필수  | `/oh-my-claudecode:omc-setup`       | setup.md § 1 |
| **GitHub CLI**       | 권장  | `brew install gh`                   | setup.md § 1 |
| **Gemini CLI**       | 권장  | `npm install -g @google/gemini-cli` | setup.md § 1 |


---

## Session Start 체크리스트

Claude Code를 시작하는 즉시, **작업 전 반드시** 수행:

**1. 역할과 범위 선언 (이슈/PR 없어도 항상 필수)**

```
역할: {이 세션에서 내가 하는 일}
범위: {수정 대상 파일/디렉토리}
범위 외: 수정하지 않음
```

**2. 컨텍스트 확인 (가능한 경우)**

```bash
gh issue list --assignee @me && gh pr list
```

**3. 작업 목표 1줄 명시 후 시작**

---

## TASK-MODE-ACTIVATED 사용법

> 문서: [.claude/docs/hooks-guide-ko.md](.claude/docs/hooks-guide-ko.md) § TASK-MODE-ACTIVATED

`settings.json`의 UserPromptSubmit 훅이 구현/생성 키워드를 감지하면 발동한다.


| 항목            | 내용                                                    | 문서 위치                       |
| ------------- | ----------------------------------------------------- | --------------------------- |
| 감지 방식         | 정규식 키워드 매칭 (AI 판단 아님)                                 | hooks-guide-ko.md § 감지 메커니즘 |
| 발동 시 워크플로우    | omc-teams 사전조사 → ultrawork → deep-interview → ralplan | hooks-guide-ko.md § 워크플로우   |
| Write/Edit 차단 | deep-interview 완료 전 차단 (PreToolUse 훅)                 | hooks-guide-ko.md § 차단 메커니즘 |
| 차단 해제         | deep-interview 완료 후 자동 해제                             | hooks-guide-ko.md § 해제      |


---

## OMC 워크플로우

> 문서: [.claude/docs/omc.md](.claude/docs/omc.md) | 한국어: [.claude/docs/omc-workflows-ko.md](.claude/docs/omc-workflows-ko.md)
> ⚠️ OMC 설치 시 `~/.claude/CLAUDE.md`에 영어 섹션 자동 생성 (OMC:START~END). 수정 금지.

**필수 순서:** `omc-teams 사전조사 → deep-interview → ralplan → ralph (max 100)`

### omc-teams 병렬 조사

> 문서: [.claude/docs/setup.md](.claude/docs/setup.md) § 3. omc-teams 프롬프트 전달 방식

**지시사항 작성 표준:** setup.md § 3에 있으니 반드시 따른다. 요약:


| 방식  | 명령                                                                 | 저장 위치            | 문서 위치          |
| --- | ------------------------------------------------------------------ | ---------------- | -------------- |
| 짧음  | `omc-teams 2:codex "주제" 3:gemini "주제"`                             | 인라인              | setup.md § 방식1 |
| 긺   | `omc-teams 2:codex "$(cat /tmp/p.md)" 3:gemini "$(cat /tmp/p.md)"` | `/tmp/prompt.md` | setup.md § 방식2 |
| 다중  | pane 2부터 순차 증가                                                     | `.omc/research/` | setup.md § 방식3 |


**tmux pane 레이아웃:** setup.md § 2의 분할 로직을 지킨다 — 메인 좌 2/3, worker 우 1/3 세로 균등 분할

### AskUserQuestion vs deep-interview

> 문서: [.claude/docs/omc.md](.claude/docs/omc.md) § deep-interview


| 도구                | 성격                | 사용 시점             | 모호성       | 문서 위치                   |
| ----------------- | ----------------- | ----------------- | --------- | ----------------------- |
| `AskUserQuestion` | Claude Code 내장 UI | 단순 선택/확인만         | —         | Claude Code 기본 기능       |
| `/deep-interview` | OMC Socratic 인터뷰  | 구현/설계 요청 시 **항상** | **5% 미만** | omc.md § deep-interview |


**Agent 자의 판단 금지:**

- deep-interview는 사용자가 "skip", "그냥 해줘"를 명시하지 않는 한 항상 실행
- **5분 무응답 = skip으로 판단**: 이 때 omc-teams로 여러 관점 수집 후 결정
  - 만장일치면 즉시 진행
  - 의견 다르면 **가장 깊은 thinking 모델(대부분 Gemini) 의견 따름**

### 핵심 의무

- AskUserQuestion 전 → omc-teams 사전조사 (AW-004)
- 서브에이전트: Task당 최소 컨텍스트 (컨텍스트 창 25% 이하)

---

## Agent 티어 & 모델 라우팅

> 문서: [.claude/docs/agents.md](.claude/docs/agents.md) § 1. 사용 가능한 에이전트 목록


| 티어        | 모델                      | 대표 Agent                                                 | 역할       | 문서 위치          |
| --------- | ----------------------- | -------------------------------------------------------- | -------- | -------------- |
| **고성능**   | Gemini 최신 (opus 대체)     | `analyst`, `architect`, `deep-executor`, `code-reviewer` | 설계·분석·리뷰 | agents.md § 티어 |
| **표준**    | `claude-sonnet-4-6[1m]` | `executor`, `debugger`, `verifier`, `test-engineer`      | 구현·검증    | agents.md § 티어 |
| **경량**    | haiku                   | `explore`, `writer`                                      | 탐색·문서    | agents.md § 티어 |
| **Codex** | `gpt-5.2-codex`         | omc-teams worker                                         | 조사·분석    | setup.md § 3   |


**사내 환경:** Claude opus 불가 → Gemini 고성능 모델 우선 (AW-001) → [agents.md § 모델 라우팅](..claude/docs/agents.md)

---

## LLM 행동지침

> 문서: [.claude/docs/team-operations-guide.md](.claude/docs/team-operations-guide.md)


| 원칙                    | 요약                                    | 문서 위치                                 |
| --------------------- | ------------------------------------- | ------------------------------------- |
| Think Before Coding   | 불명확하면 deep-interview (5% 미만, 건너뛰기 금지) | team-operations-guide.md § Think      |
| Simplicity First      | 요청받은 것만. 200줄→50줄 가능하면 다시 써라          | team-operations-guide.md § Simplicity |
| Surgical Changes      | 반드시 수정할 것만. 내가 만든 orphan만 청소          | team-operations-guide.md § Surgical   |
| Goal-Driven Execution | success criteria 정의 → 검증 → 반복         | team-operations-guide.md § Goal       |


---

## 구현 정의 및 필수 스킬

> **"구현"이란:** 파일을 Write/Edit하거나 코드를 실행하여 시스템 상태를 변경하는 모든 행위.
> 단순 조회(Read, Grep, Glob)는 구현이 아니다.

> 문서: [.claude/skill-catalog.md](.claude/skill-catalog.md) § 구현 시 필수 스킬


| 스킬                            | 목적                                      | Gotchas                    | 문서 위치                             |
| ----------------------------- | --------------------------------------- | -------------------------- | --------------------------------- |
| `/convention-python`          | Python 컨벤션 (PEP8, type hint, docstring) | 79자 (88자 아님), Logics 섹션 필수 | reference/python                  |
| `/convention-design`          | 설계 원칙 요약 (SRP/KISS/DRY/YAGNI)           | 각 원칙 상세는 philosophy/ 참조    | quality/style/design              |
| `/convention-design-patterns` | 구현 패턴 (Factory/Strategy/Decorator 등)    | 패턴 선택 전 YAGNI 체크           | reference/design-patterns         |
| `/check-anti-patterns`        | God Class, Long Method 탐지               | ADK tool 내 파일 재확인도 탐지 대상   | quality/check/anti-patterns       |
| `/adversarial-review`         | 레드팀/블루팀 셀프 리뷰                           | 15개 우선순위, 요청받은 코드만         | quality/review/adversarial-review |


---

## Git Workflow

> 문서: [.claude/docs/omc.md](.claude/docs/omc.md) § Git | [.claude/skills/process/commit/SKILL.md](.claude/skills/process/commit/SKILL.md)


| 규칙        | 내용                                                | 문서 위치                    |
| --------- | ------------------------------------------------- | ------------------------ |
| commit 형식 | `type(scope): subject` (50자, scope 필수)            | process/commit           |
| branch    | `{type}/issue-{number}-{subject}` (kebab-case)    | process/commit           |
| PR 원칙     | PR = 설계 결정 하나 | 타인 branch 파일 불간섭                  | process/pr               |
| 외부 리포     | PR 없이 direct push 금지. force push 명시적 요청 없으면 절대 금지 | team-operations-guide.md |
| 이슈 참조     | `#숫자` 커밋 포함 시 cross-reference 생성 (삭제 불가)          | team-operations-guide.md |


**PR 체크리스트:** [.github/pull_request_template.md](.github/pull_request_template.md)

---

## Claude Code 환경 (.claude/)

> 모든 .claude/ 내 md 파일은 이 섹션에서 최소 한 번 참조된다.

```
.claude/
├── AGENTS.md               # 에이전트 계층 구조 및 역할
├── CLAUDE.md               # (이 파일) 전체 규칙 진입점
├── setup.sh                # 환경 초기화 스크립트 (tmux, skills, gh)
├── settings.json           # UserPromptSubmit/PreToolUse/PostToolUse 훅
│                           #   → ulw+deep-interview+ralplan 항상 묶기 규칙 정의 위치
│                           #   → haiku AI 분류 (regex 미매칭 시 fallback)
│                           #   → 상세: docs/hooks-guide-ko.md
├── skill-catalog.md        # 127개 skill 전체 인벤토리
├── docs/
│   ├── README.md           # .claude/docs/ 인덱스
│   ├── setup.md            # tmux, omc-teams, 프롬프트 전달 방식
│   ├── omc.md              # OMC 운영 가이드 (ralph/ralplan/omc-teams)
│   ├── omc-workflows-ko.md # OMC 워크플로우 한국어 설명
│   ├── agents.md           # 에이전트 선택 기준 + Tier List
│   ├── hooks-guide-ko.md   # TASK-MODE-ACTIVATED, 훅 사용법, 감지 메커니즘
│   ├── memory.md           # 세션 간 메모리, Strategic Compact
│   ├── orchestration.md    # 병렬화, Git worktrees, 토큰 최적화
│   ├── skill.md            # Skill 작성 + Gotchas + Anthropic 원칙
│   ├── claude-md.md        # CLAUDE.md 작성 마스터 가이드
│   ├── claude-code-convention.md  # Claude Code 운영 베스트 프랙티스
│   ├── naming-conventions.md      # 파일명/변수명/컬럼명 규칙 (일반)
│   ├── team-operations.md         # AW-001~045 전체 목록
│   ├── team-operations-guide.md   # AW 규칙 상세, LLM 행동지침
│   └── adr/
│       └── ADR-001-uv-package-manager.md  # uv 채택 결정
├── output-styles/
│   └── data-driven-minds.md  # 응답 스타일 정의
├── rules/                  # 경로별 자동 적용 규칙 (12개, 경로 매칭 시 자동 로드)
│   ├── api.md              # REST API, GraphQL 규칙
│   ├── cli.md              # CLI 라이브러리 (typer/click), 종료코드, 출력형식
│   ├── python-backend.md   # Python 백엔드 규칙
│   └── (config/docker/migrations/models/security/testing 등)
└── skills/                 # 127개 skill (Anthropic 9카테고리 구조)
    ├── reference/          # 라이브러리 & API 레퍼런스
    ├── quality/            # 코드 품질 & 리뷰
    ├── process/            # 비즈니스 프로세스 자동화
    ├── scaffolding/        # 코드 스캐폴딩
    ├── data-fetch/         # 데이터 패칭 & 분석
    ├── utility/            # 유틸리티
    └── (monitoring/incident/infra/ — 미래 확장)
```

---

## Team Operations (AW 규칙)

> 상세: [.claude/docs/team-operations-guide.md](.claude/docs/team-operations-guide.md)
> AW-001~045 전체 목록: [.claude/docs/team-operations.md](.claude/docs/team-operations.md)


| 그룹       | 규칙         | 핵심                                        | 문서 위치                             |
| -------- | ---------- | ----------------------------------------- | --------------------------------- |
| 모델 & 조사  | AW-001~004 | Claude=sonnet, opus→Gemini, 3-agent 조사 의무 | team-operations-guide.md § AW-001 |
| 인터뷰 & 설계 | AW-005~007 | deep-interview 5%↓, 설계먼저, ralph max 100   | team-operations-guide.md § AW-005 |
| 품질 & 결정  | AW-008~011 | ralplan 10+목표, ADR먼저, pre-commit, 측정먼저    | team-operations-guide.md § AW-008 |
| SOLID    | AW-012~016 | SRP/OCP/LSP/ISP/DIP                       | reference/philosophy/solid/       |
| 핵심 원칙    | AW-017~022 | KISS/DRY/YAGNI/SoC/Zen/Unix               | reference/philosophy/principles/  |
| 법칙       | AW-023~032 | Gall's/Conway's/Hyrum's/Chesterton's 등    | reference/philosophy/laws/        |
| 설계 규칙    | AW-033~045 | CQS/Tell-Don't-Ask/Boy Scout 등            | reference/philosophy/design/      |


