# ADR-012: GitHub PR 템플릿 도입

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
`.github/pull_request_template.md`로 PR 체크리스트 표준화.
포함 항목: 요약, 변경내용, 설계문서, 테스트계획, Breaking Changes, 브랜치 협업.

## 이유
- PR 작성자가 체크리스트를 누락 없이 따르도록
- 리뷰어가 필요한 정보를 일관된 형식으로 받음
- AW-006(설계문서 먼저) 준수 확인 자동화

## 결과
- `pytest, ruff, mypy` 통과 확인 체크박스 포함
- 설계문서 링크 필수 항목
