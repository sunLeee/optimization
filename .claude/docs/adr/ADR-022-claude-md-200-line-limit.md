# ADR-022: CLAUDE.md 200줄 이내 + 링크 기반 구조

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
CLAUDE.md는 200줄 이내. 상세 내용은 `.claude/docs/` 파일에 위임하고 링크만 유지.

## 이유
- CLAUDE.md는 매 세션 Claude Code가 로드 → 너무 길면 컨텍스트 낭비
- 섹션당 헤딩 + 표 + 링크 구조 → 빠른 탐색
- 상세 내용은 필요 시 링크를 통해 로드 (점진적 공개)

## Gotchas
- 200줄 초과 시 `.claude/docs/` 새 파일로 분리
- 모든 .claude/ md는 CLAUDE.md에서 최소 1회 참조 필요
