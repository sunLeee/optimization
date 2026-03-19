# ADR-015: claude-config에서 GitHub Actions CI 삭제

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
`shucle-ai-agent`에서 복사된 `.github/workflows/test.yml`, `lint.yml` 삭제.

## 이유
- claude-config는 Python 프로젝트가 아님 → pytest, uv sync 등 실행 불가
- CI가 실패하면 오히려 신뢰성 저하
- 문서/skill/config 레포에 Python CI는 불필요

## 결과
- `.github/workflows/` 디렉토리에 Python CI 없음
- 향후 skill 검증 CI가 필요하면 별도 ADR로 결정
