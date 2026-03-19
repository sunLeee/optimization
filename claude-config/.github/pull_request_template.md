## 요약 (1문장)

<!-- 이 PR이 무엇을 결정하는지 설계 결정 하나로 요약 -->

## 변경 내용

<!-- 구체적으로 어떤 파일이 왜 변경됐는가 -->

## 설계문서

<!-- 관련 설계문서 링크 (코드 PR이면 설계 PR이 먼저 merge됐어야 함) -->
- 설계문서:
- ADR (해당 시): `docs/adr/ADR-XXX-*.md`

## 테스트 계획

- [ ] `uv run pytest -m unit` 통과
- [ ] `uv run pytest -m integration` 통과 (해당 시)
- [ ] `uv run ruff check .` 통과
- [ ] `uv run mypy . --strict` 통과

## Breaking Changes

<!-- 없으면 "없음" 명시 -->

## 브랜치 협업

- [ ] 이 PR은 하나의 설계 결정만 다룬다 (Rule of Small)
- [ ] 타인이 수정 중인 파일을 건드리지 않았다
- [ ] 이 브랜치의 수정 범위가 CLAUDE.md 또는 PR description에 명시됐다
