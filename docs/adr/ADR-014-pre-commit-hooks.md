# ADR-014: pre-commit Hooks로 코드 품질 자동 강제

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
`pre-commit install` 후 모든 commit에 ruff + mypy + bandit 자동 실행. `--no-verify` 금지.

## 이유
- AI가 생성한 코드도 품질 검사 통과해야 commit 가능
- "리뷰에서 잡는다"는 안전망 대신 commit 전 차단
- 개발자 실수를 즉시 피드백

## 결과
- `clone 후 pre-commit install` 1회 필수
- Stop hook에 "pre-commit 실행 권장" 안내 포함
