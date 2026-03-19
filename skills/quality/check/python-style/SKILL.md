---
name: check-python-style
triggers:
  - "check python style"
description: Python 코드 작성 후 PEP8, 타입 힌트, Docstring 규칙 준수 여부를 검증하고 싶을 때. ruff/mypy 실행 전 빠른 체크리스트가 필요할 때.
argument-hint: "[파일 경로] - 검증할 Python 파일 또는 디렉토리 (기본: .)"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
model: claude-sonnet-4-6[1m]
context: Python 코드 스타일 검증 스킬. convention-python 스킬의 규칙을 기반으로 실제 코드에 적용하여 위반 사항을 탐지한다.
agent: Python 스타일 검증 전문가. ruff와 mypy 기준으로 코드 품질을 검증하고 구체적인 수정 방법을 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 코드 검증
skill-type: Atomic
references:
  - "@skills/reference/python/SKILL.md"
referenced-by:
  - "@skills/quality/review/adversarial-review/SKILL.md"
---

# check-python-style

Python 코드가 팀 컨벤션을 준수하는지 검증한다.

## 실행 순서

```bash
# 1. ruff 검사 (79자 + PEP8)
uv run ruff check . --select E,W,F,I,N --max-line-length 79

# 2. type hint 검사 (mypy strict)
uv run mypy . --strict --ignore-missing-imports

# 3. docstring 검사 (Google style, 한국어, 73자 이하)
# — 수동 확인: Logics 섹션 존재 여부
grep -rn "def " --include="*.py" . | head -20
```

## 체크리스트

- [ ] 줄 길이 79자 이하 (ruff로 자동 검출)
- [ ] 모든 function: 파라미터 + 반환값 type hint 있음
- [ ] Docstring: Google style, 한국어, 73자 이하
- [ ] Docstring: `Logics:` 섹션 포함
- [ ] import: 절대 경로 사용 (상대 import 없음)
- [ ] 한국어 블록 주석: 모든 기능 단위에 작성
- [ ] pandas: iterrows() 없음 (vectorized 연산 사용)

## 자동 수정

```bash
# ruff 자동 수정
uv run ruff check . --fix
uv run ruff format .
```

## Gotchas (실패 포인트)

- **79자 vs 88자**: 전역 Black 설정은 88자일 수 있음 — 우리 프로젝트는 **79자** 강제
- **mypy strict vs basic**: `--strict` 옵션 없으면 많은 오류 놓침
- **Logics 섹션 누락**: mypy/ruff 통과해도 docstring에 Logics가 없으면 위반
- **Korean docstring**: 영어로 작성된 기존 docstring → 한국어로 변환 필요
- **ADK ToolContext type**: `ToolContext`를 `Any`로 처리하면 mypy 통과 — 실제 타입 명시 필요

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-010 | team-operations.md | pre-commit ruff + mypy 실제 강제 |
| 코드 스타일 | CLAUDE.md § 코드 스타일 | 79자, type hint, Google docstring |

## 참조

- `/reference/python` — Python 컨벤션 전체
- `docs/adr/ADR-004-line-length-79.md` — 79자 채택 이유
- [team-operations.md](../../../docs/design/ref/team-operations.md) § AW-010
