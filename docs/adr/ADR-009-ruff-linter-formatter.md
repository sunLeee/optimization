# ADR-009: ruff를 린터/포맷터로 채택

- **상태**: Accepted
- **날짜**: 2026-03-19

## 맥락
Black(포맷) + flake8(린트) + isort(import 정렬) 세 도구를 개별 관리하는 것은 복잡.

## 결정
**ruff** 단일 도구로 통합 (포맷 + 린트 + import 정렬).

## 이유
- Rust 기반 → 10-100x 빠름
- Black, flake8, isort를 단일 도구로 대체
- 설정 pyproject.toml 하나로 통합

## 대안 검토
| 대안 | 거부 이유 |
|------|---------|
| Black + flake8 | 두 도구 관리 복잡, 느림 |
| pylint | 너무 많은 false positive |

## 결과
- `uv run ruff check . / ruff format .`
- pre-commit에 ruff 포함
