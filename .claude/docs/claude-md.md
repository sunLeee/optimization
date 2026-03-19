# CLAUDE.md 작성 가이드

> 참조: [docs/ref/bestpractice/claude-code-rule-convention.md](../../ref/bestpractice/claude-code-rule-convention.md) (Practice 1~4)

## 0. CLAUDE.md vs README.md — 경계 명확히

| 항목 | CLAUDE.md | README.md |
|------|-----------|-----------|
| **독자** | Claude Code (AI) | 사람 (개발자, GitHub 방문자) |
| **목적** | AI 행동 지침, 규칙, 컨텍스트 | 프로젝트 설명, 설치법, 사용법 |
| **내용** | 코딩 컨벤션, 금지사항, 결정 근거 | 기능 소개, 데모, 기여 가이드 |
| **형식** | 짧고 핵심만 (200줄 이내) | 길어도 됨, 이미지/뱃지 허용 |

**원칙**: README는 "이 프로젝트가 뭐냐"고, CLAUDE.md는 "Claude야 이렇게 행동해".

**상황 1**: 설치 방법 → README에 작성 (사람이 읽음)
**상황 2**: "절대 force push 금지" → CLAUDE.md에 작성 (Claude가 따름)
**상황 3**: 같은 내용이 양쪽 → 중복 제거, CLAUDE.md 우선

## 1. CLAUDE.md 계층 구조

Claude Code는 현재 디렉토리에서 루트까지 모든 CLAUDE.md를 자동으로 병합하여 로딩한다.

### 로딩 순서 (우선순위 낮음 → 높음)

1. `~/.claude/CLAUDE.md` — 전역 사용자 규칙
2. 루트 `CLAUDE.md` — 프로젝트 전체 규칙
3. `.claude/CLAUDE.md` — 프로젝트 로컬 추가 규칙
4. 하위 디렉토리 `agents/CLAUDE.md`, `libs/CLAUDE.md` — 도메인 규칙

**이 프로젝트 실제 구조**:

- 루트: 138줄 (기술 규칙 + Team Operations)
- `agents/CLAUDE.md`: ADK 패턴 (에이전트 구현 규칙)
- `libs/CLAUDE.md`: uv workspace 규칙
- `apps/CLAUDE.md`: CLI 러너 규칙

**상황 1**: `libs/` 안에서 작업 시 → `libs/CLAUDE.md` + 루트 `CLAUDE.md` 모두 로딩

**상황 2**: `.claude/CLAUDE.md` 추가 시 `~/.claude/CLAUDE.md`와 동시 로딩 → 규칙 중복 주의

## 2. 200줄 제한 전략

각 CLAUDE.md는 200줄 이하로 유지한다. 초과 시 `docs/design/ref/*.md`로 분리 후 링크.

### 압축 기법

- 상세 패턴 설명 → `agents/CLAUDE.md` 등 하위 파일로 이동
- 코드 예시가 긴 섹션 → `docs/design/ref/`로 분리 + 링크
- 목록이 긴 섹션 → 번호 목록 + 상세는 링크

**이 프로젝트 예시**: 루트 CLAUDE.md의 "File Path & Data Access Pattern" 52줄 →
5줄 요약 + `agents/CLAUDE.md` 링크로 압축하여 138줄 달성.

**검증**:

```bash
wc -l CLAUDE.md                                       # 200 이하인지 확인
wc -l agents/CLAUDE.md libs/CLAUDE.md apps/CLAUDE.md  # 각각 200 이하
```

## 3. 섹션 표준 구조

CLAUDE.md 섹션을 일관되게 구성하여 에이전트가 빠르게 탐색 가능하게 한다.

```
# 프로젝트명

## Build, Run, and Test     <- 가장 자주 참조
## Code Style & Standards   <- 기술 컨벤션
## Repository Structure     <- 폴더 구조
## Architecture & Patterns  <- 설계 패턴
## Git Workflow              <- 브랜치/커밋
## 구현 시 필수 스킬         <- skill 참조 표
## LLM 행동지침              <- AI 운영 원칙
## Team Operations           <- AW 규칙 요약 표
```

**상황 1**: 새 규칙 추가 시 → 위 8개 섹션 중 가장 적합한 곳에만 배치

**상황 2**: 규칙 참조 시 → 에이전트가 섹션 이름으로 직접 탐색
(예: "Team Operations 참조")

## 4. 명령어 Code Block 필수화

모든 명령어는 실행 가능한 code block으로 작성한다.
자연어 설명만 있으면 에이전트가 잘못된 명령을 생성할 가능성이 높다.

```markdown
# 나쁜 예시
uv로 unit 테스트를 실행한다.

# 좋은 예시
`uv run pytest -m unit`
```

**이 프로젝트 명령어 예시**:

```bash
uv run pytest -m unit                               # Unit 테스트
uv run pytest -m integration                        # Integration 테스트
uv run ruff check . --fix                           # Lint + 자동 수정
uv run python -m cli_runner.runners.{name}          # Runner 실행
```

## 5. 동적 System Prompt 주입 (고급)

`.claude/rules/` 파일과의 차이: `--system-prompt`는 실제 system prompt에 주입되어
instruction 우선순위가 더 높다.

```bash
# 세션 시작 시 특정 컨텍스트 주입
claude --system-prompt "$(cat docs/design/ref/team-operations.md)"

# alias로 시나리오별 context 전환
alias claude-dev='claude --system-prompt "$(cat .claude/contexts/dev.md)"'
alias claude-review='claude --system-prompt "$(cat .claude/contexts/review.md)"'
```

**언제 사용**: 세션마다 다른 규칙이 필요할 때 (구현 vs PR 리뷰 vs 탐색)

**주의**: 대부분의 경우 CLAUDE.md로 충분. system prompt 주입은 미세 최적화.

**상황 1**: 특정 에이전트 패턴 집중 작업 →
`claude --system-prompt "$(cat agents/CLAUDE.md)"`

**상황 2**: 일반 개발 → 루트 CLAUDE.md + nested CLAUDE.md 자동 로딩으로 충분

## 참조

- [docs/design/ref/team-operations.md](../../design/ref/team-operations.md) — AW 규칙 상세
- [docs/ref/bestpractice/claude-code-rule-convention.md](../../ref/bestpractice/claude-code-rule-convention.md) — Practice 1~4
