# ADR-023: Session Start 체크리스트 패턴

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
CLAUDE.md에 Session Start 체크리스트 포함. 역할/범위 선언 → 컨텍스트 확인 → 목표 명시 순서.

## 이유
- Claude Code는 컨텍스트가 없으면 "무엇을 해야 하는지" 모름
- 역할/범위 명시 없으면 Surgical Changes 원칙 위반 위험
- `gh issue list`, `gh pr list` → 기존 작업 컨텍스트 파악

## 결과
- 이슈/PR 없어도 역할과 범위 반드시 선언
- CLAUDE.md 최상단에 위치 (가장 먼저 로드)
