---
name: check-design-doc
triggers:
  - "check design doc"
description: 코드와 설계문서(CLAUDE.md, docs/design/) 일치 여부 검증.
user-invocable: true
---

# check-design-doc

PR 제출 전 코드와 설계문서의 일치 여부를 확인한다.

## 검증 항목

1. **Function signature**: 설계문서에 명시된 파라미터/반환값과 일치하는가
2. **File path pattern**: AW-006 패턴 준수 (cli_runner/config.py 정의, tool_context.state 사용)
3. **Import style**: 절대 import, sys.path 조작 없음
4. **Type hints**: 모든 파라미터/반환값 type hint 존재
5. **Docstring**: Google style, 한국어, Logics 섹션 존재

## 실행 방법

```bash
# 변경된 Python 파일 목록 확인
git diff --name-only HEAD | grep '\.py$'

# 각 파일에 대해
# 1. type hint 누락 확인
grep -n "def " {file} | grep -v "->"

# 2. 절대 import 확인
grep -n "from \.\." {file}

# 3. sys.path 조작 확인
grep -n "sys.path" {file}
```

## 판정 기준

| 항목 | 통과 | 실패 |
|------|------|------|
| Type hints | 모든 def에 `->` 존재 | `def func(x):` 형태 |
| Import | `from utils.x import Y` | `from ..utils import Y` |
| sys.path | 없음 | `sys.path.insert` 존재 |
| Docstring | Logics 섹션 있음 | 없거나 영어 |

**상황 1**: PR 제출 전 자동 실행 → 위반 발견 시 수정 후 재제출
**상황 2**: Stop hook이 이 skill 실행 안내 메시지 출력 → 수동 실행

## Gotchas (실패 포인트)

- 설계문서와 코드가 다르면 코드 기준이 정답 — 설계문서 업데이트 필요
- ADR 없이 설계 변경 시 나중에 '왜 이렇게 됐지?' 추적 불가
- 설계문서 링크가 PR에 없으면 AW-006 위반 — PR 차단 가능
