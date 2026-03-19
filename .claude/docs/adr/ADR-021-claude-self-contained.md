# ADR-021: .claude/ 디렉토리 자기완결성 원칙

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
Claude Code 환경 관련 모든 문서를 `.claude/` 내부에 배치. `docs/references/claude-code/` 삭제 후 `.claude/docs/`로 이동.

## 이유
- git subtree `--prefix=.claude`로 배포 시 자기완결
- Claude Code 관련 문서가 프로젝트 `docs/`에 섞이면 혼란
- `.claude/` 하나만 배포하면 완전한 환경 구성

## 결과
- `docs/references/claude-code/` → `.claude/docs/`
- `docs/claude.md` → `.claude/docs/team-operations-guide.md`
