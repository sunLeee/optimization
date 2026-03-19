---
name: quality-ruff
triggers:
  - "quality ruff"
description: Ruff 린터/포맷터 설정 및 관리 스킬. pyproject.toml에 Ruff 설정을 구성하고 최적화한다. Flake8, isort, Black을 대체하는 고속 린터/포맷터 환경을 구축한다.
argument-hint: "[init|check|fix|format] - Ruff 설정 작업"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
model: claude-sonnet-4-6[1m]
context: Ruff 린터/포맷터 설정 및 관리를 담당한다. pyproject.toml 설정 최적화, 규칙 세트 관리, 포맷팅 설정을 수행한다.
agent: Ruff 설정 전문가. 프로젝트 특성에 맞는 규칙 세트를 설계하고, 성능 최적화를 수행한다.
hooks:
  pre_execution: []
  post_execution: []
category: 품질 관리
skill-type: Atomic
references: []
referenced-by:
  - "@skills/setup-quality/SKILL.md"

---
# Ruff 설정 관리

Ruff 린터/포맷터 환경을 구성하고 관리한다.

## 목적

- Ruff 린터/포맷터 설정
- 프로젝트별 규칙 세트 최적화
- pyproject.toml 설정 관리
- 기존 도구(Flake8, isort, Black) 마이그레이션

## 사용법

```
/quality-ruff init      # 초기 설정
/quality-ruff check     # 린트 검사
/quality-ruff fix       # 자동 수정
/quality-ruff format    # 코드 포맷팅
```

---

## 표준 설정

### pyproject.toml

```toml
# =============================================================================
# Ruff Configuration
# Documentation: https://docs.astral.sh/ruff/configuration/
# =============================================================================

[tool.ruff]
# 기본 설정
target-version = "py311"
line-length = 100
indent-width = 4

# 검사 대상
src = ["src", "tests"]
include = ["*.py", "*.pyi"]
exclude = [
    ".git",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "*.egg-info",
]

# 캐시 설정
cache-dir = ".ruff_cache"

# 출력 형식
output-format = "concise"

# =============================================================================
# Lint 설정
# =============================================================================
[tool.ruff.lint]
# 규칙 세트
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "RUF",    # Ruff-specific rules
]

# 무시 규칙
ignore = [
    "E501",   # line too long (포맷터가 처리)
    "B008",   # function call in default argument (FastAPI Depends)
    "B904",   # raise without from (불필요한 경우 많음)
]

# 자동 수정 가능 규칙
fixable = ["ALL"]
unfixable = []

# 더미 변수 패턴
dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"

# =============================================================================
# isort 설정 (I 규칙)
# =============================================================================
[tool.ruff.lint.isort]
known-first-party = ["src"]
force-single-line = false
lines-after-imports = 2
section-order = [
    "future",
    "standard-library",
    "third-party",
    "first-party",
    "local-folder",
]

# =============================================================================
# flake8-bugbear 설정 (B 규칙)
# =============================================================================
[tool.ruff.lint.flake8-bugbear]
extend-immutable-calls = [
    "fastapi.Depends",
    "fastapi.Query",
    "fastapi.Path",
    "fastapi.Body",
]

# =============================================================================
# 파일별 규칙 오버라이드
# =============================================================================
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "S101",   # assert 허용
    "ARG001", # 미사용 인자 허용 (fixtures)
    "ARG002", # 미사용 인자 허용
]
"__init__.py" = ["F401"]  # 미사용 import 허용
"conftest.py" = ["ARG001"]

# =============================================================================
# Format 설정
# =============================================================================
[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
docstring-code-format = true
docstring-code-line-length = 80
```

---

## 규칙 세트 가이드

### 핵심 규칙

| 코드 | 카테고리 | 설명 |
|------|----------|------|
| `E`, `W` | pycodestyle | PEP 8 스타일 검사 |
| `F` | Pyflakes | 논리 오류 검사 |
| `I` | isort | import 정렬 |
| `B` | flake8-bugbear | 버그 유발 패턴 |
| `C4` | flake8-comprehensions | 컴프리헨션 최적화 |
| `UP` | pyupgrade | 최신 Python 문법 |

### 추가 권장 규칙

| 코드 | 카테고리 | 설명 |
|------|----------|------|
| `SIM` | flake8-simplify | 코드 간소화 |
| `TCH` | flake8-type-checking | 타입 힌트 최적화 |
| `PTH` | flake8-use-pathlib | pathlib 사용 권장 |
| `RUF` | Ruff-specific | Ruff 전용 규칙 |
| `ARG` | flake8-unused-arguments | 미사용 인자 검사 |

### Data Science 추가 규칙

| 코드 | 카테고리 | 설명 |
|------|----------|------|
| `NPY` | NumPy-specific | NumPy 규칙 |
| `PD` | pandas-vet | Pandas 규칙 |

---

## 프로젝트 유형별 설정

### 1. 일반 Python

```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "SIM", "RUF"]
```

### 2. Data Science

```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "NPY", "PD", "RUF"]
ignore = ["E501", "PD901"]  # df 변수명 허용
```

### 3. FastAPI/API 서버

```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "TCH", "RUF"]
ignore = ["B008"]  # Depends 허용

[tool.ruff.lint.flake8-bugbear]
extend-immutable-calls = ["fastapi.Depends", "fastapi.Query"]
```

---

## 실행 명령

### 린트 검사

```bash
# 기본 검사
uv run ruff check .

# 상세 출력
uv run ruff check . --verbose

# 자동 수정
uv run ruff check . --fix

# 안전하지 않은 수정 포함
uv run ruff check . --fix --unsafe-fixes

# 특정 규칙만 검사
uv run ruff check . --select E,W,F
```

### 포맷팅

```bash
# 포맷 검사 (변경 없이)
uv run ruff format --check .

# 포맷 적용
uv run ruff format .

# diff 출력
uv run ruff format --diff .
```

---

## VS Code 통합

### settings.json

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    },
    "ruff.lint.args": ["--config=pyproject.toml"],
    "ruff.format.args": ["--config=pyproject.toml"]
}
```

---

## 마이그레이션

### Flake8 → Ruff

```bash
# Flake8 규칙을 Ruff로 변환
ruff rule --all | grep "Flake8"
```

### isort → Ruff

```toml
# 기존 isort 설정
[tool.isort]
profile = "black"

# Ruff isort 설정으로 변환
[tool.ruff.lint.isort]
known-first-party = ["src"]
```

### Black → Ruff

```bash
# Ruff 포맷터는 Black과 99% 호환
uv run ruff format .
```

---

## 규칙 무시

### 파일 수준

```python
# ruff: noqa: E501
```

### 라인 수준

```python
x = "long line"  # noqa: E501
```

### 특정 규칙만 무시

```python
# noqa: E501, F401
```

---

## 트러블슈팅

### 캐시 초기화

```bash
rm -rf .ruff_cache
```

### 규칙 설명 확인

```bash
ruff rule E501
```

### 설정 검증

```bash
ruff check --show-settings
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/quality-precommit/SKILL.md] | Pre-commit hook 설정 |
| [@skills/quality-mypy/SKILL.md] | mypy 타입 검사 설정 |
| [@skills/check-python-style/SKILL.md] | 코드 스타일 검증 |
| [@skills/convention-python/SKILL.md] | Python 코딩 컨벤션 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-21 | 1.0.0 | 초기 생성 - Ruff 설정 관리 |

## Gotchas (실패 포인트)

- `ruff format` (포맷)과 `ruff check` (린트)는 별개 명령 — 둘 다 실행 필요
- Black과 충돌: ruff format은 Black 호환이나 rule 일부 충돌 가능
- `# noqa` 주석 남용 금지 — 근본 원인 수정 후 제거
- `E501` 비활성화 후 line-length 설정 누락 시 모순
