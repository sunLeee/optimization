---
name: convention-python
triggers:
  - "convention python"
description: Python 코드 작성 중 PEP8, 타입 힌트, 네이밍 규칙, Docstring 규칙이 필요할 때. 검증이 아닌 참조용 — 검증은 check-python-style 사용. "Python 코딩 규칙", "PEP 8 스타일", "타입 힌트 어떻게?", "Docstring 작성법" 요청 시.
argument-hint: "[섹션] - pep8, naming, types, docstring, headers, pandas, all"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: Python 코드 작성 시 참조해야 할 팀 코딩 컨벤션. 검증(check)이 아닌 참조(reference) 목적. 79자, 한국어 73자 docstring, pandas vectorization 등 팀 특화 규칙 포함.
agent: Python 코딩 스타일 가이드 전문가. 팀 표준(79자, 한국어 docstring, ADK 패턴)에 맞는 일관된 코드 작성 방법을 안내한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references:
  - "@skills/quality/check/python-style/SKILL.md"
referenced-by:
  - "@skills/quality/check/python-style/SKILL.md"
  - "@skills/quality/review/adversarial-review/SKILL.md"
---

# convention-python

팀 Python 코딩 컨벤션. 검증은 `/quality/check/python-style` 사용.

## Supersedes

`python-patterns`(외부 skill, 88자 Black 기준) — 팀 기준은 **79자**.

---

## 네이밍 규칙

| 대상 | 규칙 | 예시 |
|------|------|------|
| 변수/함수 | `snake_case` | `zone_id`, `load_data()` |
| class | `PascalCase` | `DataProcessor` |
| 상수 | `UPPER_SNAKE_CASE` | `MAX_RETRY` |
| 모듈/파일 | `snake_case` | `demand_analysis.py` |

**상황 1**: class 이름을 `dataProcessor`로 작성 → `DataProcessor`로 수정
**상황 2**: 상수를 `maxRetry = 3`으로 정의 → `MAX_RETRY = 3`으로 수정

---

## 줄 길이: 79자 (팀 표준)

```toml
[tool.ruff]
line-length = 79
```

- ruff pre-commit hook이 79자 초과 시 commit 차단
- 탭 없음, 스페이스 4개 들여쓰기

---

## Type Hint (필수)

모든 function 파라미터 + 반환값에 type hint 필수. `mypy --strict` 통과 기준.

```python
# CORRECT
def load_data(file_path: str, encoding: str = "utf-8") -> pd.DataFrame: ...

# VIOLATION (금지)
def load_data(file_path, encoding="utf-8"): ...
```

---

## Google Style Docstring (한국어, 73자 이하, Logics 섹션 필수)

```python
def load_zone_data(zone_id: int) -> pd.DataFrame:
    """zone_id에 해당하는 데이터를 로드한다.

    Args:
        zone_id: 분석 대상 zone의 고유 식별자.

    Returns:
        zone 데이터가 담긴 DataFrame.

    Raises:
        FileNotFoundError: 데이터 파일이 없을 때.

    Logics:
        1. config에서 파일 경로를 가져온다.
        2. CSV를 읽어 DataFrame으로 반환한다.
    """
```

규칙:
- docstring은 **한국어** 작성
- 한 줄 설명: **73자 이하**
- `Logics` 섹션 **필수**
- 모든 public 모듈/함수/class에 작성

---

## Import 순서

표준 라이브러리 → 서드파티 → 로컬. **절대 경로**. 상대 import, sys.path 조작 금지.

```python
import os
import pandas as pd
from utils.prompt_loader import PromptLoader  # 절대 경로
```

---

## Pandas 최적화 (AW-011 Rob Pike Rule)

- `iterrows()` **금지** → vectorized 연산
- Query는 **ANSI SQL** (DB engine 독립성)

```python
# VIOLATION
for idx, row in df.iterrows():
    result = row["value"] * 2

# CORRECT
result = df["value"] * 2
```

---

## Gotchas (실패 포인트)

- **79자 vs 88자**: VSCode 기본 Black은 88자 → `.vscode/settings.json`에서 `"editor.rulers": [79]`
- **Logics 섹션**: mypy 통과해도 Logics 없으면 pre-commit에서 탐지
- **한국어 docstring**: 영문+한국어 혼용 금지, 한국어 통일
- **pandas chained assignment**: `.loc` 또는 `.copy()` 사용

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-010 | team-operations.md | pre-commit ruff + mypy 실제 강제 |
| @AW-011 | team-operations.md | pandas vectorization — Rob Pike |
| 코드 스타일 | CLAUDE.md § 코드 스타일 | 79자, type hint, Google docstring |

## 참조

- `/quality/check/python-style` — 규칙 준수 검증
- `docs/adr/ADR-004-line-length-79.md` — 79자 채택 이유
- [team-operations.md](../../docs/design/ref/team-operations.md) § AW-010
