# Deep Interview Spec: claude-config 팀 워크플로우 및 General Rule 개선

## Metadata
- Interview ID: di-claude-config-ref-20260319
- Rounds: 4
- Final Ambiguity Score: 19%
- Type: brownfield
- Generated: 2026-03-19
- Threshold: 20%
- Status: PASSED

## Clarity Breakdown
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.85 | 35% | 0.298 |
| Constraint Clarity | 0.75 | 25% | 0.188 |
| Success Criteria | 0.80 | 25% | 0.200 |
| Context Clarity | 0.85 | 15% | 0.128 |
| **Total Clarity** | | | **0.813** |
| **Ambiguity** | | | **19%** |

## Goal
`everything-claude-code` + `context-hub` + X 기사를 레퍼런스로,
현재 claude-config 프로젝트의 팀 워크플로우와 Claude general rule을 개선하여
**신규 팀원이 와도 ruff/mypy/bandit pre-commit을 통과하는 Python 코드를 일관되게 산출**할 수 있게 한다.

## Constraints
- **Phase 1 (Bug Fix First)**: 기존 Stop hook 빈 변수 버그 및 설정 오류부터 수정
- **Phase 2 (Evaluate & Select)**: everything-claude-code 전 기능을 평가 후 필요한 것만 채택
- **Claude 일관성**: Claude가 AW 규칙을 더 자동으로 준수하도록 hook/skill 강화
- **기능 커버리지**: 누락된 핵심 기능(context-hub, hook profile, onboarding)만 추가
- **내부망 제약**: opus 불가, SSL 외부 접근 제한 환경

## Non-Goals
- everything-claude-code 전체 108+ 스킬 그대로 이식 (선별 채택만)
- TypeScript/Go/Swift/PHP 언어 규칙 추가 (Python 팀)
- 기존 AW-001~045 규칙 재작성 (확장만)

## Root Causes (Round 4 확인)
| 원인 | 현상 | 해결 방향 |
|------|------|-----------|
| 설정 부족 | Python restriction 세밀도 부족 | convention-python 강화 + 세세한 restriction 추가 |
| 문서화 부족 | 신규 팀원 온보딩 가이드 없음 | onboarding.md 작성 |
| 자동화 부족 | Claude가 규칙을 스스로 강제하지 않음 | hook runtime control + Stop hook 수정 |

## Acceptance Criteria (정량적)
1. Stop hook 빈 변수 버그 수정 → `bash .claude/check-criteria.sh` 정상 실행
2. Python pre-commit 통과율: 신규 팀원 첫 commit 시 ruff+mypy+bandit 100% 통과
3. Onboarding 가이드 작성 → `.claude/docs/onboarding.md` 생성, 30분 내 첫 commit 달성
4. Hook profile 시스템 추가 → `ECC_HOOK_PROFILE=minimal|standard|strict` 작동
5. context-hub(chub) 통합 → API 문서 조회 skill 추가 (`~/.claude/skills/get-api-docs/`)
6. Claude 규칙 자동 강제 향상 → 5회 연속 작업에서 manual intervention 없이 AW 준수
7. convention-python 세밀도 강화 → 신규 팀원 코드에서 mypy --strict 0 errors
8. Stop hook quality gate 수정 → score 변수 정상 계산, 90% 미달 시 exit 2
9. X 기사 인사이트 반영 → 5-phase workflow + MCP 10/80 rule + memory hooks 가이드 문서화
10. ADR 작성 → 주요 결정 사항 ADR-039 이상으로 문서화

## References
- everything-claude-code: 108+ skills, 5-phase workflow, MCP 10/80 rule, memory hooks, context window economics, ECC_HOOK_PROFILE, /learn+/evolve 연속학습
- context-hub (Andrew Ng): chub CLI, self-improving loop, API docs via SKILL.md
- X 기사 (@affaanmustafa, 2026-01-21): orchestrated sub-agents, context window economics, memory hooks

## Interview Transcript
- R1: Success Criteria → Claude 일관성 향상 + 기능 커버리지 + Python 신규팀원 일관성
- R2: Constraint → 버그 수정 먼저 + 전체 평가 후 선택
- R3: Success artifact → Python 코드 품질 (pre-commit 통과)
- R4 (Contrarian): 근본 원인 → 설정+문서화+자동화 모두 부족
