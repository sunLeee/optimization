# Claude Code 참조문서

affaan-m의 longform guide를 이 프로젝트(omc + uv workspace + Google ADK)에 맞게 재구성한 고급 활용 가이드.

## 문서 목록

| 파일 | 목적 | 이런 상황에 읽어라 |
|------|------|-----------------|
| [omc.md](./omc.md) | oh-my-claudecode 사용법 | ralph/ralplan/omc-teams 워크플로우 선택 시 |
| [claude-md.md](./claude-md.md) | CLAUDE.md 작성 마스터 가이드 | CLAUDE.md 신규 작성 또는 리팩토링 시 |
| [agents.md](./agents.md) | 에이전트 오케스트레이션 가이드 | 어떤 에이전트를 어떻게 조합할지 모를 때 |
| [skill.md](./skill.md) | Skill 작성 및 관리 가이드 | 새 skill 만들거나 기존 skill 수정 시 |
| [memory.md](./memory.md) | 메모리 & 컨텍스트 관리 | context rot 발생 또는 세션 간 기억 유지 필요 시 |
| [orchestration.md](./orchestration.md) | 멀티에이전트 & 병렬화 | ralph/team/ultrawork 선택 기준 또는 토큰 최적화 필요 시 |

## 빠른 참조

**상황별 어느 문서로?**

| 상황 | 문서 |
|------|------|
| CLAUDE.md가 200줄 초과 | claude-md.md § 2 (200줄 제한 전략) |
| 어떤 에이전트를 써야 할지 모름 | agents.md § 1~2 (에이전트 목록 + 즉시 사용 원칙) |
| 새 convention skill 만들기 | skill.md § 3 (새 Skill 작성 절차) |
| 작업 기억이 context에서 사라짐 | memory.md § 1~2 (세션 로그 + OMC 메모리 도구) |
| ralph/ralplan/omc-teams 처음 사용 | omc.md § 3 (표준 개발 흐름) |
| ralph vs team vs ultrawork 선택 | orchestration.md § 1 (워크플로우 선택 기준) |
| 토큰 비용 줄이기 | orchestration.md § 5 (토큰 최적화 전략) |
| 병렬 Claude 인스턴스 실행 | orchestration.md § 2 (Git Worktrees) |

## 관련 기존 문서

- [docs/ref/bestpractice/claude-code-rule-convention.md](../../ref/bestpractice/claude-code-rule-convention.md) — 28개 best practice (기초)
- [docs/design/ref/team-operations.md](../../design/ref/team-operations.md) — AW-001~010 운영 규칙
- [docs/references/github-issues/issue-74-ai-pr-workflow.md](../github-issues/issue-74-ai-pr-workflow.md) — PR 철학

## 출처

- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — 원본 레포
- affaan-m X 포스트 longform guide — 토큰 경제, 메모리, 검증, 병렬화
