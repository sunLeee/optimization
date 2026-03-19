# ADR-001: uv를 패키지 매니저로 채택

- **상태**: Accepted
- **날짜**: 2026-03-01
- **범용 여부**: ✅ 모든 Python 프로젝트에 적용 가능

## 맥락

Python 패키지 관리 도구 선택. 기존에는 pip + venv 혼용.

## 결정

**uv**를 유일한 패키지 매니저로 채택한다. `pip install` 직접 사용 금지.

## 이유

- Rust 기반으로 pip보다 10-100x 빠름
- `uv sync`로 lock 파일 기반 재현 가능한 환경
- `uv run` 으로 venv 없이 바로 실행 가능
- `pyproject.toml` 표준 준수

## 사용법

```bash
# 의존성 설치
uv sync

# 패키지 추가
uv add pandas

# 스크립트 실행 (venv 자동)
uv run python script.py
uv run pytest

# Lint/Format
uv run ruff check .
uv run mypy . --strict
```

## Hook 내 uv run 사용

Claude Code hooks에서 Python 스크립트 실행 시 `uv run python3` 대신
표준 라이브러리만 사용하는 경우 `python3` 직접 호출도 허용한다.
이유: hook은 venv 외부에서 실행되며, stdlib(json, hashlib 등)은 venv 불필요.

패키지가 필요한 경우: `uv run python3 -c '...'` 사용.

## 결과

- `pip install` 금지 → 팀원 환경 불일치 방지
- `uv run pytest` 표준화 → CI/CD 통일
- Hook 내: stdlib → `python3`, 패키지 → `uv run python3`

## 참조

- [setup.md](../setup.md) § uv 설치
- [convention-python](../../skills/reference/python/SKILL.md)
