# ADR-008: mypy --strict 모드 적용

- **상태**: Accepted
- **날짜**: 2026-03-19

## 맥락
mypy 기본 모드는 많은 타입 오류를 허용. strict 없이는 타입 힌트 효과 반감.

## 결정
`mypy --strict` 모드 의무화.

## 이유
- `--strict`는 가장 엄격한 타입 검사 → 숨겨진 버그 조기 탐지
- 팀 전체 타입 안전성 보장
- CI/pre-commit에서 강제 → 느슨한 코드 차단

## Gotchas
- 서드파티 라이브러리 stubs 없으면 `ignore-missing-imports` 필요
- 기존 코드베이스에 적용 시 단계적 도입 필요

## 결과
- pyproject.toml `[tool.mypy] strict = true`
- pre-commit hook에 포함
