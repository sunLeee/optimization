# ADR-029: AGENTS.md 파일로 서브에이전트 지시사항 관리

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
`.claude/AGENTS.md`에 에이전트 계층 구조 및 역할 정의. 서브디렉토리에도 AGENTS.md 배치 가능.

## 이유
- CLAUDE.md의 서브에이전트 버전 → 특정 디렉토리 작업 시 자동 로드
- 에이전트별 역할 명확화 → context 오염 방지
- deepinit skill이 계층적 AGENTS.md 생성 지원

## 결과
- `.claude/AGENTS.md`: 전체 에이전트 계층 (python-reviewer, adk-specialist)
- `agents/AGENTS.md`, `libs/AGENTS.md` 등 프로젝트별 가능
