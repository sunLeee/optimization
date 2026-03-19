# ADR-040: CLAUDE.md 기반 세션 간 메모리 관리

- **상태**: Accepted
- **날짜**: 2026-03-19
- **범용 여부**: ✅ 모든 프로젝트 적용 가능

## 맥락
Claude Code 세션이 끊기면 이전 컨텍스트가 사라진다. 중요한 결정/패턴을 다음 세션에 전달할 방법 필요.

## 결정
CLAUDE.md를 주된 세션 간 메모리 수단으로 사용. 50회 대화마다 cleanup-memory skill 실행 권장.

## 이유
- CLAUDE.md는 매 세션 자동 로드 → 가장 확실한 메모리
- cleanup-memory + recommend-memory 워크플로우로 자동화
- 200줄 초과 시 `.claude/docs/`로 분리 (ADR-022)

## 대안 검토

| 대안 | 거부 이유 |
|------|---------|
| `.omc/notepad.md` | OMC 전용, 범용성 낮음 |
| 외부 DB | 설정 복잡, Claude와 직접 통합 어려움 |

## 결과
- recommend-memory: 10번 대화마다 실행 권장
- cleanup-memory: 50번 대화마다 실행 권장
- memory-workflow skill: 위 두 skill 통합

## Gotchas
- CLAUDE.md 수정 후 Claude Code 재시작 필요
- 중요 결정이 메모리 정리로 제거되지 않도록 ADR 먼저 작성

## 참조
- [memory.md](../memory.md) § 세션 간 메모리
- `.claude/skills/utility/memory-workflow/SKILL.md`
