# Open Questions

## general-rules-toolkit - 2026-03-18

- [ ] `python-patterns` skill과 `convention-python` skill의 역할 분리 — 기존 `python-patterns`를 deprecated 처리할지, 한국어 팀 규칙 버전으로 교체할지, 또는 두 파일을 공존시킬지 결정 필요. convention-python이 팀 특화(79자, Logics 섹션, 한국어 주석)라면 python-patterns는 일반 Python idiom 참조로 남길 수도 있음.

- [ ] `.claude/settings.json` 기존 파일 존재 여부 — Stop hook 추가 시 기존 설정을 덮어쓰지 않도록 확인 필요. 현재 탐색에서 파일 존재 확인 미완료.

- [ ] `check-python-style` skill 존재 여부 — Stop hook이 `/check-python-style`을 호출하는데, 해당 skill 파일이 현재 `.claude/skills/`에 없음. `lint-fix` skill로 대체할지, 신규 생성할지 결정 필요. (lint-fix가 이미 ruff 실행을 포함하면 동일 역할 가능)

- [ ] `convention-design`과 `convention-design-patterns` 분리 범위 — 스펙에서 `convention-design`(SRP/KISS/DRY/YAGNI + 안티패턴)과 `convention-design-patterns`(Factory/Strategy/Repository/Observer)가 별도 파일로 정의됨. 두 파일이 중복 없이 명확히 분리되는지 executor가 작성 전 확인 필요.

- [ ] `data-driven-minds.md` 원본 위치 — 스펙에 "기존 `dotfiles/claude-code/output-styles/` 경로의 파일을 이 repo로 이전"이라고 명시됨. 이전할 원본 파일이 로컬에 존재하는지, 내용을 그대로 복사할지 새로 작성할지 확인 필요.

- [ ] `uv run pre-commit install` 실행 주체 — `.pre-commit-config.yaml` 생성 후 팀원이 clone 시 pre-commit을 활성화하려면 `uv run pre-commit install`을 수동으로 실행해야 함. `Makefile`에 `make setup` target으로 자동화할지, README에 안내할지 결정 필요. (현재 Makefile 존재 확인됨)

## python-quality-enforcement - 2026-03-19

- [ ] ruff `select` 범위 결정 — `["E","F","I","B","UP"]` 5개 룰셋으로 시작할지, `["ALL"]` 후 제외 방식이 나은지 결정 필요. 도입 초기 오류 폭발량에 직접 영향을 미침.
- [ ] `.pre-commit-config.yaml`의 mypy hook 실효성 — 현재 리포에 실제 .py 파일이 없어 mypy가 항상 no-op. 샘플 스크립트(`.claude/scripts/*.py` 등)를 추가해 실제 검증할지 여부.
- [ ] `ECC_HOOK_PROFILE` 초기 기본값 — `strict`로 설정하면 기존 팀원도 즉시 영향받음. 기본값을 `standard`로 낮춰서 시작할지 여부 결정 필요.
- [ ] `get-api-docs` skill 오프라인 전략 — PyPI JSON API 직접 호출 시 사내 망(네트워크 제한) 환경에서 실패 가능. 로컬 캐시 또는 docs URL 수동 입력 fallback 필요 여부.
