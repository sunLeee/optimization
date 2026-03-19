# Plan: Claude Code 참조문서 5종 구현

> 생성일: 2026-03-19
> 상태: 대기 (사용자 확인 필요)
> 저장 경로: `docs/references/claude-code/`

---

## RALPLAN-DR 요약

### Principles (설계 원칙)

1. **독자는 중급 Claude Code 사용자다** — 기초 설명 없이 실용 패턴과 판단 기준 중심으로 작성한다.
2. **기존 codebase와 연결한다** — 추상적 설명 대신 이 프로젝트의 실제 파일 경로·skill·workflow를 예시로 사용한다.
3. **검증 가능한 내용만 작성한다** — "해야 한다"는 주장마다 grep/test 명령어로 확인 가능한 기준을 제시한다.
4. **문서 간 역할을 명확히 분리한다** — 내용 중복 없이 cross-reference로 연결한다.
5. **현재 컨벤션과 일관성을 유지한다** — `docs/ref/bestpractice/claude-code-rule-convention.md` 및 기존 SKILL.md 포맷과 충돌하지 않는다.

### Decision Drivers (핵심 결정 요소)

1. **affaan-m 원본 콘텐츠 충실도** — X 포스트 핵심 5개 주제가 누락 없이 반영되어야 한다.
2. **이 프로젝트 특화** — 크로스플랫폼 일반론이 아닌, omc + uv workspace + Google ADK 환경에 맞춰야 한다.
3. **유지보수 용이성** — 각 문서가 단일 주제만 다뤄야 팀원이 해당 문서만 수정하면 된다.

### Options (구현 방식 비교)

| 방식 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **Option A: 5개 독립 파일 (채택)** | 각 주제를 별도 `.md` 파일로 분리 | 단일 책임, 검색 용이, git blame 명확 | 초기 작성 비용 |
| Option B: 단일 통합 파일 | 5개 주제를 하나의 파일에 통합 | 작성 빠름 | 200줄 제한 위반, 유지보수 어려움 |
| Option C: skill 파일로 통합 | `.claude/skills/` 하위에 등록 | 에이전트가 직접 호출 가능 | 팀원이 읽는 문서로는 부적합 |

Option A 채택 이유: 기존 `docs/ref/bestpractice/` 및 `docs/references/github-issues/` 패턴과 동일하며, 200줄 제한 컨벤션을 준수한다.

---

## Context

이 프로젝트는 이미 13개 skill과 28개 best practice 문서를 보유하고 있으나, Claude Code 고급 활용법(메모리 관리, 병렬화, 에이전트 패턴)을 별도로 정리한 참조문서가 없다. affaan-m의 longform guide 내용을 이 프로젝트 맥락으로 재구성하여 `docs/references/claude-code/` 에 5개 파일로 작성한다.

---

## Work Objectives

1. `docs/references/claude-code/` 디렉토리에 5개 참조문서를 생성한다.
2. 각 문서는 affaan-m 원본 개념을 이 프로젝트(omc, uv workspace, Google ADK)에 맞게 구체화한다.
3. 기존 `claude-code-rule-convention.md` 및 SKILL.md와 내용이 중복되지 않는다.
4. 각 문서에 이 프로젝트 실제 경로/명령어 예시가 최소 3개 이상 포함된다.

---

## Guardrails

### Must Have

- 각 파일 200줄 이하 (컨벤션 Practice 2 준수)
- 한국어 작성 (주석·설명 모두)
- 코드 블록 내 명령어는 실행 가능한 형태 (`uv run ...`, `grep ...` 등)
- `docs/references/claude-code/README.md` 인덱스 파일 포함
- 각 문서 하단에 관련 기존 문서 cross-reference 포함

### Must NOT Have

- `docs/ref/bestpractice/claude-code-rule-convention.md` 내용 재작성 (링크로 대체)
- 기존 skill 내용 복사 (링크로 대체)
- 에이전트 구현 코드 (.py, .ts 파일 변경 없음)
- 영어 주석/설명

---

## Task Flow (병렬 실행 가능)

5개 문서와 README는 모두 독립적이므로 병렬 실행한다.

```
[병렬 실행]
├── Task 1: claude-md.md 작성
├── Task 2: agents.md 작성
├── Task 3: skill.md 작성
├── Task 4: memory.md 작성
└── Task 5: orchestration.md 작성

[순차 실행 — Task 1~5 완료 후]
└── Task 6: README.md 작성 + 종료조건 검증
```

---

## Detailed TODOs

### Task 1: `docs/references/claude-code/claude-md.md`

**목적**: CLAUDE.md 파일을 효과적으로 작성하는 마스터 가이드

**섹션 목차 (세부)**:

```
# CLAUDE.md 작성 가이드

## 1. 파일 역할과 위치
  - Root CLAUDE.md vs 패키지 CLAUDE.md 분리 기준
  - 이 프로젝트의 현재 계층 구조 (루트, docs/, agents/ 예정)
  - .claude/rules/ vs CLAUDE.md 선택 기준표

## 2. 섹션 표준 구조
  - 5개 필수 섹션: Build/Run/Test, Code Style, Architecture, Git Workflow, Team Operations
  - 각 섹션에 넣어야 할 것 vs 넣으면 안 되는 것
  - 200줄 초과 시 분리 절차

## 3. 명령어 code block 필수화
  - 자연어 금지, 실행 가능한 code block 필수 규칙
  - 이 프로젝트 예시: uv run pytest -m unit

## 4. 동적 System Prompt 주입
  - claude --system-prompt "$(cat memory.md)" 패턴
  - 세션 시작 시 컨텍스트 주입 방법
  - SessionStart hook 연동

## 5. 언제 업데이트하는가
  - 새 패키지 추가 시, 새 컨벤션 확정 시, 새 에이전트 패턴 도입 시
  - 업데이트 후 에이전트 재검증 절차

## 참조
  - docs/ref/bestpractice/claude-code-rule-convention.md (Practice 1~4)
```

**수락 기준**:
- `wc -l docs/references/claude-code/claude-md.md` 결과 200 이하
- "동적 System Prompt" 섹션이 존재함: `grep -c "System Prompt" docs/references/claude-code/claude-md.md` >= 1
- 이 프로젝트 실제 경로 포함: `grep "uv run" docs/references/claude-code/claude-md.md | wc -l` >= 2
- 기존 문서 cross-reference 존재: `grep "claude-code-rule-convention" docs/references/claude-code/claude-md.md | wc -l` >= 1

---

### Task 2: `docs/references/claude-code/agents.md`

**목적**: 어떤 에이전트를 언제 어떻게 사용하는지 완전한 가이드

**섹션 목차 (세부)**:

```
# 에이전트 오케스트레이션 가이드

## 1. 에이전트 카탈로그
  - 역할별 표: Build/Analysis 그룹, Review 그룹, Domain 그룹, Coordination 그룹
  - 각 에이전트의 model 크기 (haiku/sonnet/opus) 및 이유
  - 이 프로젝트에서 실제 자주 쓰는 에이전트 Top 5

## 2. 선택 기준 — 언제 어떤 에이전트를
  - 파일 탐색 → explore (haiku)
  - 버그 원인 파악 → debugger (sonnet)
  - 구현 → executor (sonnet) / deep-executor (opus)
  - 검증 → verifier (haiku/sonnet/opus 사이징 규칙)
  - SDK/API 사용 → document-specialist 먼저

## 3. Immediate Usage (사용자 프롬프트 불필요)
  - 에이전트가 스스로 판단하여 호출하는 패턴
  - CLAUDE.md delegation_rules 참조
  - 예시: broad 요청 → explore 먼저

## 4. Agent Abstraction Tier List
  - Direct Buffs (쉬움, 즉시 효과): explore, executor, verifier
  - High Skill Floor (어려움, 설계 필요): deep-executor, critic, architect
  - 언제 High Skill Floor가 필요한가

## 5. Iterative Retrieval Pattern
  - orchestrator → sub-agent → 평가 → follow-up (max 3 cycles)
  - 이 프로젝트 예시: explore → planner → executor chain

## 6. 에이전트 간 컨텍스트 전달 규칙
  - 25% 이하 원칙
  - 요약본 + 핵심 파일 경로 패턴

## 참조
  - docs/ref/bestpractice/claude-code-rule-convention.md (Practice 6~8)
  - docs/design/ref/team-operations.md (AW-001: 모델 선택, AW-002: 3-agent 조사)
  - 전역 CLAUDE.md의 agent_catalog 섹션
```

**수락 기준**:
- `grep -c "haiku\|sonnet\|opus" docs/references/claude-code/agents.md` >= 5
- Tier List 섹션 존재: `grep -c "Tier" docs/references/claude-code/agents.md` >= 1
- Iterative Retrieval 섹션 존재: `grep -c "Iterative" docs/references/claude-code/agents.md` >= 1
- 이 프로젝트 예시 포함: `grep "explore\|executor\|verifier" docs/references/claude-code/agents.md | wc -l` >= 5

---

### Task 3: `docs/references/claude-code/skill.md`

**목적**: 프로젝트 특화 skill을 만들고 관리하는 방법 가이드

**섹션 목차 (세부)**:

```
# Skill 작성 및 관리 가이드

## 1. Skill이란
  - SKILL.md 포맷: frontmatter(name, description, triggers, user-invocable) + 본문
  - skill vs CLAUDE.md 규칙의 차이: skill은 on-demand, CLAUDE.md는 항상 적용
  - 위치: .claude/skills/{skill-name}/SKILL.md

## 2. 이 프로젝트의 현재 Skill 목록 (동적 조회)
  - 정적 표 대신 실시간 조회 명령어 제공 (목록은 변하므로)
  - `ls .claude/skills/` — 현재 활성 skill 목록
  - `grep -r "deprecated" .claude/skills/*/SKILL.md` — deprecated skill 확인
  - 카테고리 설명: convention-*(코딩 컨벤션), check-*(검증), python-*(Python 특화)

## 3. 새 Skill 작성 절차
  - Step 1: /manage-skill로 파일 생성
  - Step 2: frontmatter 작성 (name, description, triggers)
  - Step 3: 본문: 규칙 + 상황 1/상황 2 예시 패턴
  - Step 4: /sync-skill-catalog로 등록
  - Step 5: CLAUDE.md "구현 시 필수 스킬" 테이블에 추가

## 4. 새 컨벤션 정의 절차 (도메인 없을 때)
  - omc-teams 조사 → 기준 정립 → adversarial-review → 스킬 등록
  - 이 프로젝트 예시: convention-adk-agent 스킬 신규 등록 시나리오

## 5. Continuous Learning — Stop Hook 기반 자동 갱신
  - Claude Code Stop hook에 /learn 연동
  - 세션 종료 시 새로운 패턴 자동 학습 및 skill 업데이트
  - .claude/hooks/ 설정 방법

## 6. Skill 폐기 절차
  - Supersedes 필드 활용 (python-patterns → convention-python 예시)
  - deprecated skill 처리 방법

## 참조
  - docs/ref/bestpractice/claude-code-rule-convention.md (Practice 5, 14)
  - 전역 CLAUDE.md의 구현 시 필수 스킬 테이블
```

**수락 기준**:
- 현재 13개 skill 목록 표 존재: `grep -c "convention-" docs/references/claude-code/skill.md` >= 5
- Stop Hook 섹션 존재: `grep -c "Stop hook\|Stop Hook" docs/references/claude-code/skill.md` >= 1
- SKILL.md 포맷 frontmatter 예시 존재: `grep -c "user-invocable" docs/references/claude-code/skill.md` >= 1
- `/manage-skill` 명령어 포함: `grep -c "manage-skill" docs/references/claude-code/skill.md` >= 1

---

### Task 4: `docs/references/claude-code/memory.md`

**목적**: 세션 간 기억 유지와 context rot 방지 가이드

**섹션 목차 (세부)**:

```
# 메모리 & 컨텍스트 관리 가이드

## 1. 세션 간 기억의 문제
  - context rot: 세션이 길어질수록 초기 맥락이 희미해지는 현상
  - 새 세션 시작 시 컨텍스트 재구축 비용
  - 이 프로젝트에서 발생하는 실제 시나리오

## 2. 세션 로그 & 요약 패턴
  - 세션 종료 전 .tmp 파일에 요약 저장 패턴
  - 요약 포맷: 완료된 작업, 미완료 작업, 관련 파일 경로, 다음 액션
  - 다음 세션 시작 시 요약 파일 주입

## 3. Hook 체인 설정 방법 (PreCompact / SessionStart / Stop)
  - **현재 상태**: `.claude/settings.json`에 Stop hook만 설정됨 (정보성 알림)
  - **목표 설정**: PreCompact → SessionStart → Stop 3단계 체인 (선택적 추가)
  - PreCompact hook: compact 직전 핵심 내용 보존 (현재 미설정)
  - SessionStart hook: 세션 시작 시 이전 요약 주입 (현재 미설정)
  - Stop hook: 세션 종료 시 변경 로그 기록 (현재 활성, 정보성 알림)
  - `.claude/settings.json` 설정 예시 포함 (현재 vs 목표 상태 비교)

## 4. Strategic Compact
  - 50 tool call마다 compact 제안 (PreToolUse hook 기반)
  - 언제 compact 해야 하는가 vs 하면 안 되는가
  - compact 전 보존해야 할 정보 체크리스트

## 5. omc Notepad & Project Memory 활용
  - notepad_write_priority: 세션 내 우선순위 컨텍스트 (500자 이하)
  - notepad_write_working: 타임스탬프 기반 작업 기록 (7일 자동 삭제)
  - project_memory_write: 영구 아키텍처 결정 및 파일 구조 요약
  - 이 프로젝트 예시: 패키지 entry point 경로를 project memory에 저장

## 6. 동적 System Prompt 주입
  - claude --system-prompt "$(cat .omc/notepad.md)" 패턴
  - 배치 실행 시 메모리 주입 방법

## 참조
  - docs/ref/bestpractice/claude-code-rule-convention.md (Practice 19~21)
  - .omc/notepad.md, .omc/project-memory.json
```

**수락 기준**:
- Hook 체인 3개 모두 언급: `grep -c "PreCompact\|SessionStart\|Stop hook" docs/references/claude-code/memory.md` >= 3
- Strategic Compact 섹션 존재: `grep -c "Strategic Compact\|50 tool" docs/references/claude-code/memory.md` >= 1
- omc notepad 명령어 포함: `grep -c "notepad_write\|project_memory" docs/references/claude-code/memory.md` >= 2
- 실행 가능한 명령어 code block: `grep -c '```' docs/references/claude-code/memory.md` >= 4

---

### Task 5: `docs/references/claude-code/orchestration.md`

**목적**: 멀티에이전트 & 병렬화 워크플로우 선택 가이드

**섹션 목차 (세부)**:

```
# 멀티에이전트 & 병렬화 가이드

## 1. 워크플로우 선택 기준표
  - ralph: 완전 자율, explore→plan→execute→verify→fix loop
  - ultrawork: 독립 모듈 최대 병렬화
  - team: 단계별 품질 보증 (plan→exec→verify→fix)
  - omc-teams: 외부 모델(codex, gemini) 활용
  - 선택 기준: 작업 규모 × 독립성 × 품질 요구 행렬

## 2. Git Worktrees 병렬화
  - 병렬 Claude 인스턴스를 독립 worktree에서 실행
  - Cascade method: 좌→우 tab 순서로 결과 전파
  - 3~4 인스턴스 상한 이유 (그 이상은 비생산적)
  - 의도적 병렬화 원칙: 필요한 것만 병렬화

## 3. Token Optimization
  - 에이전트 모델 크기 매칭 (haiku/sonnet/opus 티어)
  - Bash 도구 대신 ripgrep 사용 (토큰 50% 절감)
  - Background tmux 프로세스 (Claude 직접 스트리밍 불필요)
  - Modular codebase가 토큰 소비를 줄이는 이유
  - 이 프로젝트 예시: uv run pytest --co 대신 grep으로 테스트 목록

## 4. Verification Loops
  - Checkpoint-based evals: 단계 완료 시점에만 검증 (ralph 모드)
  - Continuous evals: 매 변경마다 검증 (pre-commit hook)
  - pass@k: k번 시도 중 한 번이라도 성공 (탐색적 작업)
  - pass^k: k번 모두 성공해야 통과 (프로덕션 코드)
  - 이 프로젝트에서 각 방식을 적용하는 시나리오

## 5. Sequential Phase Pattern
  - RESEARCH → PLAN → IMPLEMENT → REVIEW → VERIFY
  - 각 phase의 에이전트 매핑
  - Phase 간 컨텍스트 전달 규칙 (25% 이하)

## 6. 실패 패턴과 방지책
  - Context 오염: 탐색과 구현을 같은 에이전트에 맡길 때
  - 무한 루프: max cycle 미설정 시 (max 3 cycles 규칙)
  - 과도한 병렬화: 의존성 없는 작업에만 병렬화

## 참조
  - docs/ref/bestpractice/claude-code-rule-convention.md (Practice 9~12)
  - 전역 CLAUDE.md의 team_pipeline, parallelization 섹션
```

**수락 기준**:
- 4개 워크플로우 모두 언급: `grep -c "ralph\|ultrawork\|omc-teams\|team" docs/references/claude-code/orchestration.md` >= 4
- pass@k / pass^k 개념 포함: `grep -c "pass@k\|pass\^k" docs/references/claude-code/orchestration.md` >= 2
- 병렬화 상한 명시: `grep -c "3\|4" docs/references/claude-code/orchestration.md` >= 1 (맥락 확인 필요)
- Token 절감 섹션 존재: `grep -c "토큰\|token\|ripgrep" docs/references/claude-code/orchestration.md` >= 2

---

### Task 6: `docs/references/claude-code/README.md` (Tasks 1~5 완료 후)

**목적**: 5개 문서 인덱스 및 진입 가이드

**내용**:
- 5개 문서 표 (파일명, 목적, 주요 독자 상황)
- 빠른 참조: 상황별 → 어느 문서로 가야 하는가
- 관련 기존 문서: `docs/ref/bestpractice/claude-code-rule-convention.md`

**수락 기준**:
- 5개 파일 링크 모두 존재: `grep -c "claude-md\|agents\|skill\|memory\|orchestration" docs/references/claude-code/README.md` >= 5

---

## 종료 조건 (15개)

### 파일 존재 확인 (5개)

```bash
# AC-01: 6개 파일 존재 (5개 문서 + README)
ls docs/references/claude-code/{claude-md,agents,skill,memory,orchestration,README}.md

# AC-02: README 인덱스 존재
test -f docs/references/claude-code/README.md && echo "PASS"
```

### 줄 수 제한 (2개)

```bash
# AC-03: 모든 파일 200줄 이하
for f in docs/references/claude-code/*.md; do
  lines=$(wc -l < "$f"); [ "$lines" -le 200 ] && echo "PASS: $f ($lines)" || echo "FAIL: $f ($lines)"
done

# AC-04: 파일당 평균 100줄 이상 (내용 충분성)
for f in docs/references/claude-code/*.md; do
  lines=$(wc -l < "$f"); [ "$lines" -ge 80 ] && echo "PASS: $f ($lines)" || echo "WARN: $f ($lines)"
done
```

### 핵심 개념 포함 확인 (5개)

```bash
# AC-05: claude-md.md에 동적 System Prompt 섹션
grep -c "System Prompt" docs/references/claude-code/claude-md.md

# AC-06: agents.md에 Tier List 및 Iterative Retrieval
grep -c "Tier\|Iterative" docs/references/claude-code/agents.md

# AC-07: memory.md에 Hook 체인 3종
grep -c "PreCompact\|SessionStart\|Stop hook" docs/references/claude-code/memory.md

# AC-08: orchestration.md에 pass@k / pass^k
grep "pass@k\|pass\^k" docs/references/claude-code/orchestration.md

# AC-09: skill.md에 동적 조회 명령어 포함 확인 (정적 목록 금지)
grep -c "ls .claude/skills/" docs/references/claude-code/skill.md
# 기대값: >= 1 (ls 명령어 존재)
grep -c "grep -r.*SKILL.md" docs/references/claude-code/skill.md
# 기대값: >= 1 (deprecated 확인 명령어 존재)
```

### 이 프로젝트 특화 확인 (3개)

```bash
# AC-10: 실제 uv 명령어 포함
grep -r "uv run" docs/references/claude-code/ | wc -l
# 기대값: >= 3

# AC-11: omc 도구 참조 포함
grep -r "notepad\|project_memory\|omc" docs/references/claude-code/ | wc -l
# 기대값: >= 5

# AC-12: 기존 문서 cross-reference 존재
grep -r "claude-code-rule-convention\|Practice" docs/references/claude-code/ | wc -l
# 기대값: >= 5
```

### 형식 확인 (3개)

```bash
# AC-13: 한국어 주석 포함 (영어 전용 문서 없음)
grep -rL "[가-힣]" docs/references/claude-code/*.md | wc -l
# 기대값: 0 (모든 파일에 한국어 존재)

# AC-14: code block 포함 (실행 가능한 예시)
grep -c '```' docs/references/claude-code/claude-md.md
# 기대값: >= 4

# AC-15: README에 5개 파일 링크
grep -c "claude-md\|agents\|skill\|memory\|orchestration" docs/references/claude-code/README.md
# 기대값: >= 5
```

---

## 구현 순서

모든 5개 문서(Task 1~5)는 독립적이므로 동시에 병렬 실행한다. README(Task 6)는 5개 완료 후 작성한다.

```
병렬: Task 1 + Task 2 + Task 3 + Task 4 + Task 5
순차: Task 6 (위 5개 완료 후)
```

실행 명령:
```
/oh-my-claudecode:start-work claude-code-reference-docs
```

---

## 참조

- 기존 best practice: `docs/ref/bestpractice/claude-code-rule-convention.md`
- 기존 skill 포맷: `.claude/skills/convention-python/SKILL.md`
- 기존 참조문서 템플릿: `docs/references/github-issues/_template.md`
- affaan-m 원본: Context & Memory Management, Token Optimization, Verification Loops, Parallelization, Agent/Sub-agent Patterns
