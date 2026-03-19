# General Rules Integration Plan — v2 (Architect + Critic 피드백 반영)

> **작성일**: 2026-03-18
> **계획 유형**: 문서 통합 (코드 변경 없음)
> **기반**: Architect Synthesis 채택 — 루트 CLAUDE.md 단일 진실 소스

---

## Context

### 해결할 실제 갭

`docs/claude.md`의 General Rules(모델/AskUserQuestion/종료조건 규칙)가 Claude Code 세션에
**자동 로딩되지 않는다**. Claude Code는 프로젝트 루트의 `CLAUDE.md`만 자동 로딩한다.
`docs/claude.md`는 존재하지만 어떤 세션에서도 적용된 적이 없다.

### 확정된 제약

| 제약 | 이유 |
|------|------|
| `.claude/CLAUDE.md` 신규 파일 금지 | `~/.claude/CLAUDE.md`(전역)와 충돌 위험 |
| `docs/ref/` 신규 트리 금지 | `docs/design/ref/`에 14개 파일 이미 존재, 중복 트리 금지 |
| 루트 CLAUDE.md 200줄 상한 | 사용자 확인 완료 ("200자" = "200줄") |

### 현재 실측치

| 파일 | 줄 수 | 상태 |
|------|-------|------|
| `CLAUDE.md` (루트) | 147줄 | 기술 규칙 전용, Claude Code 자동 로딩 |
| `docs/claude.md` | 39줄 | General Rules 초안, 자동 로딩 안 됨 |
| `docs/design/ref/` | 14개 파일 | 설계 참조 문서 트리 이미 존재 |

### 채택된 방향

Architect Synthesis: **루트 CLAUDE.md에 Team Operations 섹션으로 통합**.
오버플로 내용은 `docs/design/ref/team-operations.md`로 분리 (기존 트리 활용).

---

## Work Objectives

1. `docs/claude.md`의 General Rules를 루트 `CLAUDE.md`에 "Team Operations" 섹션으로 통합하여
   Claude Code 세션에 자동 로딩되도록 한다.
2. 루트 `CLAUDE.md`를 200줄 이하로 유지하면서 상세 내용은 `docs/design/ref/team-operations.md`로 분리한다.
3. `docs/claude.md`를 삭제(또는 루트로 리다이렉트)하여 중복 소스를 제거한다.

---

## Guardrails

### Must Have

- 루트 `CLAUDE.md` 변경 후 줄 수 <= 200줄
- Team Operations의 모든 규칙(모델/AskUserQuestion/종료조건/설계문서)이 루트 `CLAUDE.md`에 존재
- `docs/design/ref/team-operations.md`가 생성되어 상세 내용을 보유
- `docs/claude.md` 중복 소스 제거

### Must NOT Have

- `.claude/CLAUDE.md` 신규 파일 생성
- `docs/ref/` 신규 디렉터리 생성
- 루트 `CLAUDE.md` 200줄 초과
- 기존 기술 규칙(Build/Run/Test, Code Style, Architecture 등) 훼손

---

## Task Flow

### Step 1: `docs/design/ref/team-operations.md` 생성

**작업**: `docs/claude.md`의 내용을 구조화하여 상세 참조 문서를 작성한다.

**파일**: `docs/design/ref/team-operations.md` (신규)

**포함할 내용**:
- 모델 선택 규칙 (Claude/Codex/Gemini 각각 상세)
- AskUserQuestion 사전 조사 절차 (단계별 상세)
- 설계문서 관리 규칙 (CLAUDE.md 200줄 제한, docs/design/ref 분리 기준)
- 종료조건 정의 절차 (3-agent 조사, deep-interview, 모호성 5% 미만)
- 예외 조건 (컨벤션 스킬로 해결 가능한 사항)

**예상 줄 수**: 60~80줄

**완료 기준**:
- 파일이 `docs/design/ref/team-operations.md`에 존재
- `docs/claude.md`의 모든 규칙이 빠짐없이 포함됨
- 기존 `docs/design/ref/` 문서 헤더 스타일(버전, 관련 문서 링크)을 따름

---

### Step 2: 루트 `CLAUDE.md`에 Team Operations 섹션 추가

**작업**: 루트 `CLAUDE.md` 끝에 `## Team Operations` 섹션을 삽입한다.
상세 내용은 Step 1에서 만든 파일을 링크로 참조하고, 섹션 자체는 핵심 규칙 요약만 담는다.

**삽입할 섹션 (정확한 내용)**:

```markdown
## Team Operations

> 상세 규칙: [docs/design/ref/team-operations.md](./docs/design/ref/team-operations.md)

### 모델 선택

- Claude Code: 내부망에서 opus 불가 — 모든 모델은 `claude-sonnet-4-6[1m]` 사용
- Codex CLI: 내부망 지원 모델 중 `gpt-5.2-codex` 사용
- Gemini: 모든 모델 사용 가능 — 최고 성능 사고 수준에는 Gemini 사용

### AskUserQuestion 사전 조사 (필수)

AskUserQuestion 호출 전 반드시 `/omc-teams`로 codex + gemini에게 best practice를 조사한다.
절차: `2:codex + 2:gemini` 병렬 실행 → pros/cons 비교 → (Recommended) 명시 → AskUserQuestion
예외: 컨벤션 스킬(`/convention-python` 등)로 답이 정해지는 사항은 직접 결정

### 설계문서 관리

- 모든 작업은 설계문서(CLAUDE.md)를 먼저 작성하고 준수한다
- CLAUDE.md 200줄 제한: 초과 시 `docs/design/ref/*.md`로 분리하여 링크 참조
- 설계문서 수정 시 반드시 `/ralplan`으로 계획 후 진행
- 설계문서와 구현 간 무모순성 유지 — 차이 발생 시 반드시 일치시킨다

### 종료조건

- ralph max iteration: 100
- ralplan 종료조건: 10개 이상 정량적 목표 (claude/codex/gemini 3-agent 조사로 도출)
- deep-interview 모호성: 5% 미만 유지
- 구현 확신 99.9999% 미만이면 계속 질문
```

**변경 후 줄 수 계산**:
- 현재 루트 CLAUDE.md: 147줄
- 추가할 Team Operations 섹션: ~30줄
- 예상 최종: **177줄** (200줄 상한 이내)

**완료 기준**:
- `CLAUDE.md` 파일 줄 수 <= 200줄: `wc -l CLAUDE.md`
- `## Team Operations` 섹션이 파일에 존재: `grep -n "Team Operations" CLAUDE.md`
- 4개 핵심 하위 섹션(모델/AskUserQuestion/설계문서/종료조건) 모두 존재
- 기존 섹션(Build/Run/Test, Code Style 등) 변경 없음: git diff 확인

---

### Step 3: `docs/claude.md` 중복 소스 제거

**작업**: `docs/claude.md`를 루트 `CLAUDE.md`로 리다이렉트 안내 파일로 교체하거나 삭제한다.

**선택지**:
- A. 파일 내용을 리다이렉트 안내로 교체 (규칙이 루트 CLAUDE.md로 이동했음을 명시)
- B. 파일 삭제 후 git에서 제거

권장: **A (리다이렉트 안내)** — 이 파일을 직접 열어본 사람이 혼란을 겪지 않도록.

**리다이렉트 내용**:
```markdown
# General Rules (이동됨)

이 파일의 내용은 루트 `CLAUDE.md`의 `## Team Operations` 섹션으로 통합되었다.

- 규칙 원문: [/CLAUDE.md#team-operations](../CLAUDE.md)
- 상세 참조: [docs/design/ref/team-operations.md](./design/ref/team-operations.md)
```

**완료 기준**:
- `docs/claude.md`에 원본 규칙이 더 이상 존재하지 않음
- 리다이렉트 안내 또는 파일 삭제로 중복 소스 제거 확인

---

## 변경 후 파일별 상태 요약

| 파일 | 변경 전 | 변경 후 |
|------|---------|---------|
| `CLAUDE.md` (루트) | 147줄, 기술 규칙만 | ~177줄, 기술 규칙 + Team Operations |
| `docs/claude.md` | 39줄, General Rules 원본 | 리다이렉트 안내 (3줄) 또는 삭제 |
| `docs/design/ref/team-operations.md` | 없음 | 신규 생성, 상세 규칙 60~80줄 |

---

## 정량적 종료조건 (10개 이상)

각 조건은 측정 명령어와 기준값을 포함한다.

| # | 조건 | 기준값 | 측정 명령어 |
|---|------|--------|------------|
| 1 | 루트 CLAUDE.md 줄 수 | <= 200줄 | `wc -l CLAUDE.md` |
| 2 | Team Operations 섹션 존재 | 1건 | `grep -c "## Team Operations" CLAUDE.md` |
| 3 | 모델 선택 규칙 존재 (Claude) | 1건 | `grep -c "claude-sonnet-4-6" CLAUDE.md` |
| 4 | 모델 선택 규칙 존재 (Codex) | 1건 | `grep -c "gpt-5.2-codex" CLAUDE.md` |
| 5 | AskUserQuestion 사전 조사 규칙 존재 | 1건 | `grep -c "omc-teams" CLAUDE.md` |
| 6 | 설계문서 200줄 제한 규칙 존재 | 1건 | `grep -c "200줄" CLAUDE.md` |
| 7 | ralph max iteration 규칙 존재 | 1건 | `grep -c "max iteration" CLAUDE.md` |
| 8 | deep-interview 모호성 5% 규칙 존재 | 1건 | `grep -c "5%" CLAUDE.md` |
| 9 | `docs/design/ref/team-operations.md` 존재 | 파일 있음 | `test -f docs/design/ref/team-operations.md && echo OK` |
| 10 | `docs/design/ref/team-operations.md` 줄 수 | >= 40줄 | `wc -l docs/design/ref/team-operations.md` |
| 11 | `docs/design/ref/team-operations.md` 링크가 CLAUDE.md에 존재 | 1건 | `grep -c "team-operations.md" CLAUDE.md` |
| 12 | `docs/claude.md` 원본 규칙 제거 | 0건 | `grep -c "gpt-5.2-codex" docs/claude.md` → 0 |
| 13 | 기존 기술 섹션 줄 수 유지 | 147줄 이상 유지 | `grep -c "Build, Run, and Test" CLAUDE.md` → 1 |
| 14 | `.claude/CLAUDE.md` 미생성 | 없음 | `test ! -f .claude/CLAUDE.md && echo OK` |
| 15 | `docs/ref/` 신규 트리 미생성 | 없음 | `test ! -d docs/ref && echo OK` |

---

## Success Criteria

1. Claude Code가 새 세션을 시작하면 Team Operations 규칙이 자동으로 적용된다
   (루트 CLAUDE.md가 자동 로딩되므로 보장됨)
2. 루트 CLAUDE.md는 200줄 이하를 유지한다
3. `docs/claude.md`는 더 이상 원본 규칙의 중복 소스가 아니다
4. 기존 기술 규칙(Build/Run/Test, Code Style, Architecture, Git Workflow)은 변경되지 않는다
5. `docs/design/ref/team-operations.md`가 상세 참조 문서로 기능한다

---

## Open Questions

없음 — 모든 제약사항이 확정되었고 Architect Synthesis 방향이 채택됨.
