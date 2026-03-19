# AGENTS.md — Shucle AI Agent Platform

> 이 파일은 Claude Code Agent들의 역할, 범위, 전문성을 정의한다.
> 브랜치: `shucle-ai-agent-general-rules`
> 관련: [CLAUDE.md](../CLAUDE.md) | [team-operations.md](../docs/design/ref/team-operations.md)

---

## Agent 계층 구조

```
Orchestrator
├── Planner (ralplan: 설계 합의)
├── Executor (ralph: 구현)
│   ├── ADK Specialist (에이전트 구현)
│   ├── Data Pipeline Specialist (전처리/집계)
│   └── Build Fixer (타입/린트 오류)
├── Verifier (구현 검증)
└── Reviewer
    ├── Code Reviewer (품질/패턴)
    ├── Security Reviewer (보안 취약점)
    └── Python Reviewer (PEP8/타입힌트)
```

---

## Python Reviewer Agent

**파일**: `.claude/agents/python-reviewer.md`

**전문성**: PEP 8 준수, type hint, Google docstring, 79자 제한 검증
**트리거**: Python 코드 리뷰 요청 시
**관련 skill**: `@convention-python`, `@check-python-style`
**AW 규칙**: @AW-010 (pre-commit 강제)

---

## ADK Specialist Agent (권장 추가)

**목적**: Google ADK 에이전트 구현 전문
**전문성**:
- `root_agent` export 패턴
- `ToolContext.state` schema 설계
- `PromptLoader` + Jinja2 템플릿
- File Path & Data Access Pattern 5원칙

**관련 skill**: `@convention-adk-agent`, `@check-data-pipeline`
**AW 규칙**: @AW-011 (데이터 구조 우선), @AW-016 (DIP), @AW-022 (Unix Philosophy)

```markdown
<!-- .claude/agents/adk-specialist.md 내용 예시 -->
당신은 Google ADK 에이전트 구현 전문가다.
반드시 다음을 준수한다:
1. 코드 작성 전 ToolContext.state schema 먼저 확정
2. tool function은 파일 경로를 인자로 받지 않음 (state에서 읽음)
3. agent __init__에서만 파일 존재 확인
4. /convention-adk-agent skill 반드시 참조
```

---

## Data Pipeline Specialist Agent (권장 추가)

**목적**: 데이터 수집/전처리/집계 파이프라인 구현 전문
**전문성**:
- Pandas vectorization (iterrows 금지)
- H3 지리공간 처리 (`libs/preprocessing`)
- OmegaConf 설정 관리
- Parquet/CSV I/O 패턴

**관련 skill**: `@check-data-pipeline`, `@convention-dry`, `@convention-soc`
**AW 규칙**: @AW-011 (Rob Pike), @AW-018 (DRY), @AW-020 (SoC)

---

## 에이전트 사용 규칙 (AW-001)

| 모델 | 용도 | 제한 |
|------|------|------|
| `claude-sonnet-4-6[1m]` | 모든 Claude Code 에이전트 | 내부망 opus 불가 |
| `gpt-5.2-codex` | Codex CLI 에이전트 | 내부망 고정 |
| Gemini | 고성능 분석 | 제한 없음 |

**3-agent 조사** (AW-002): claude + codex + gemini 병렬 질의 → 다수결 또는 사용자 결정

---

## OMC 워크플로우 연계

```
사용자 요청
  → deep-interview (모호성 5% 미만) [AW-005]
  → ralplan (Planner→Architect→Critic 합의) [AW-008]
  → ralph (구현 루프, max 100회) [AW-007]
    ├── ADK Specialist (에이전트 구현)
    ├── Data Pipeline Specialist (파이프라인)
    └── Python Reviewer (스타일 검증)
  → verifier (완료 검증)
```

**상세**: [docs/references/claude-code/omc.md](../docs/references/claude-code/omc.md)

---

## 관련 문서

- [CLAUDE.md](../CLAUDE.md) — 전체 Team Operations 규칙 (AW-001~045)
- [team-operations.md](../docs/design/ref/team-operations.md) — AW 규칙 상세
- [docs/references/claude-code/agents.md](../docs/references/claude-code/agents.md) — 에이전트 선택 기준
- [.claude/skill-catalog.md](./skill-catalog.md) — 사용 가능한 skill 목록
