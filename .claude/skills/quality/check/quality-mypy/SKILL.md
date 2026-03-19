---
name: quality-mypy
triggers:
  - "quality mypy"
description: mypy 타입 검사 설정 및 관리 스킬. pyproject.toml에 mypy 설정을 구성하고 최적화한다. 정적 타입 검사 환경을 구축하여 타입 안전성을 확보한다.
argument-hint: "[init|check|strict] - mypy 설정 작업"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
model: claude-sonnet-4-6[1m]
context: mypy 타입 검사 설정 및 관리를 담당한다. pyproject.toml 설정 최적화, strict 모드 관리, 모듈별 오버라이드를 수행한다.
agent: mypy 설정 전문가. 프로젝트 특성에 맞는 타입 검사 수준을 설계하고, 점진적 타입 적용을 지원한다.
hooks:
  pre_execution: []
  post_execution: []
category: 품질 관리
skill-type: Atomic
references: []
referenced-by:
  - "@skills/setup-quality/SKILL.md"

---
# mypy 설정 관리

mypy 타입 검사 환경을 구성하고 관리한다.

## 목적

- mypy 타입 검사 환경 설정
- 프로젝트별 strict 수준 최적화
- 모듈별 타입 검사 오버라이드
- 타입 스텁 관리

## 사용법

```
/quality-mypy init      # 초기 설정
/quality-mypy check     # 타입 검사 실행
/quality-mypy strict    # strict 모드 설정
```

---

## 표준 설정

### pyproject.toml

```toml
# =============================================================================
# mypy Configuration
# Documentation: https://mypy.readthedocs.io/en/stable/config_file.html
# =============================================================================

[tool.mypy]
# Python 버전
python_version = "3.11"

# 검사 대상
files = ["src", "tests"]
exclude = [
    "^build/",
    "^dist/",
    "^\\.venv/",
]

# =============================================================================
# 기본 설정
# =============================================================================
# strict 모드 (권장)
strict = true

# 또는 개별 설정
# disallow_untyped_defs = true
# disallow_incomplete_defs = true
# check_untyped_defs = true
# disallow_untyped_decorators = true
# warn_redundant_casts = true
# warn_unused_ignores = true
# warn_return_any = true
# no_implicit_reexport = true
# strict_equality = true

# =============================================================================
# 추가 검사
# =============================================================================
warn_unreachable = true
show_error_codes = true
show_column_numbers = true
pretty = true

# =============================================================================
# import 처리
# =============================================================================
ignore_missing_imports = true
follow_imports = "normal"

# =============================================================================
# 플러그인
# =============================================================================
plugins = [
    "pydantic.mypy",
]

# =============================================================================
# Pydantic 플러그인 설정
# =============================================================================
[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true

# =============================================================================
# 모듈별 오버라이드
# =============================================================================
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false

[[tool.mypy.overrides]]
module = [
    "pandas.*",
    "numpy.*",
    "sklearn.*",
    "matplotlib.*",
    "seaborn.*",
]
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "conftest"
disallow_untyped_defs = false
```

---

## Strict 모드 구성 요소

### strict = true 포함 옵션

| 옵션 | 설명 |
|------|------|
| `warn_unused_configs` | 미사용 설정 경고 |
| `disallow_any_generics` | 제네릭 Any 금지 |
| `disallow_subclassing_any` | Any 서브클래싱 금지 |
| `disallow_untyped_calls` | 타입 없는 함수 호출 금지 |
| `disallow_untyped_defs` | 타입 없는 함수 정의 금지 |
| `disallow_incomplete_defs` | 불완전한 타입 정의 금지 |
| `check_untyped_defs` | 타입 없는 함수 본문 검사 |
| `disallow_untyped_decorators` | 타입 없는 데코레이터 금지 |
| `warn_redundant_casts` | 불필요한 캐스트 경고 |
| `warn_unused_ignores` | 미사용 # type: ignore 경고 |
| `warn_return_any` | Any 반환 경고 |
| `no_implicit_reexport` | 암시적 재수출 금지 |
| `strict_equality` | 엄격한 동등성 검사 |

---

## 프로젝트 유형별 설정

### 1. 일반 Python (점진적 적용)

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # 점진적 적용
check_untyped_defs = true
ignore_missing_imports = true
```

### 2. 라이브러리/API (strict)

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_unreachable = true
show_error_codes = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### 3. Data Science

```toml
[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = false
check_untyped_defs = true
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = ["pandas.*", "numpy.*", "sklearn.*"]
ignore_missing_imports = true
```

---

## 실행 명령

### 기본 검사

```bash
# 전체 검사
uv run mypy src/

# 특정 파일
uv run mypy src/module.py

# 설정 파일 지정
uv run mypy --config-file pyproject.toml src/
```

### 출력 형식

```bash
# 상세 오류 (컬럼 번호 포함)
uv run mypy src/ --show-column-numbers

# 오류 코드 표시
uv run mypy src/ --show-error-codes

# 컬러 출력
uv run mypy src/ --pretty
```

### 캐시 관리

```bash
# 캐시 사용 안 함
uv run mypy src/ --no-incremental

# 캐시 삭제
rm -rf .mypy_cache
```

---

## 타입 스텁 관리

### 스텁 패키지 설치

```bash
# 일반적인 스텁
uv add --dev types-requests types-PyYAML types-toml

# Data Science
uv add --dev pandas-stubs

# 모든 스텁 자동 설치
uv add --dev mypy
uv run mypy --install-types
```

### 프로젝트 내 스텁

```
src/
├── mymodule/
│   ├── __init__.py
│   └── core.py
└── stubs/
    └── external_lib/
        └── __init__.pyi
```

```toml
[tool.mypy]
mypy_path = "src/stubs"
```

---

## 오류 억제

### 라인 수준

```python
x = some_untyped_function()  # type: ignore[no-untyped-call]
```

### 특정 오류만 억제

```python
# type: ignore[arg-type, return-value]
```

### 파일 수준

```python
# mypy: ignore-errors
```

---

## VS Code 통합

### settings.json

```json
{
    "python.analysis.typeCheckingMode": "basic",
    "mypy-type-checker.args": [
        "--config-file=pyproject.toml"
    ],
    "mypy-type-checker.importStrategy": "fromEnvironment"
}
```

---

## 일반 오류 및 해결

### 1. Missing imports

```
error: Cannot find implementation or library stub for module
```

**해결**:
```toml
[[tool.mypy.overrides]]
module = "problematic_module.*"
ignore_missing_imports = true
```

### 2. Incompatible types

```
error: Incompatible types in assignment
```

**해결**: 타입 힌트 수정 또는 캐스트
```python
from typing import cast
x: int = cast(int, some_value)
```

### 3. Argument type mismatch

```
error: Argument 1 has incompatible type
```

**해결**: 함수 시그니처 또는 호출부 수정

---

## Pydantic 통합

### 플러그인 설정

```toml
[tool.mypy]
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

### Pydantic v2 모델

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# mypy가 타입 검사 수행
user = User(name="Alice", age=30)
reveal_type(user.name)  # str
```

---

## 점진적 적용 전략

### 1단계: 기본 설정

```toml
[tool.mypy]
ignore_missing_imports = true
check_untyped_defs = true
```

### 2단계: 경고 활성화

```toml
[tool.mypy]
warn_return_any = true
warn_unused_configs = true
```

### 3단계: 핵심 모듈 strict

```toml
[[tool.mypy.overrides]]
module = "src.core.*"
disallow_untyped_defs = true
```

### 4단계: 전체 strict

```toml
[tool.mypy]
strict = true
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/quality-precommit/SKILL.md] | Pre-commit hook 설정 |
| [@skills/quality-ruff/SKILL.md] | Ruff 린터 설정 |
| [@skills/check-python-style/SKILL.md] | 코드 스타일 검증 |
| [@skills/convention-python/SKILL.md] | Python 코딩 컨벤션 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-21 | 1.0.0 | 초기 생성 - mypy 설정 관리 |

## Gotchas (실패 포인트)

- `--strict` 없이 실행 시 많은 오류 누락 — 반드시 `--strict` 사용
- `reveal_type(x)` 디버그 코드를 commit에 포함하지 않도록 주의
- 서드파티 라이브러리 stubs 없으면 `ignore-missing-imports = true` 설정 필요
- pyproject.toml의 mypy 설정이 CLI 플래그보다 우선 적용됨
