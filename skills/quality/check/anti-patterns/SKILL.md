---
name: check-anti-patterns
triggers:
  - "check anti patterns"
description: Python 코드를 작성하거나 리뷰할 때 God Class, Long Method, Feature Envy, Circular Dependency 등 설계 안티패턴이 있는지 확인하고 싶을 때. 특히 ADK tool에서 중복 검증, 파일 경로 직접 접근 패턴을 탐지할 때.
argument-hint: "[path] - 검사 대상 경로 (기본: 현재 디렉토리)"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
model: claude-sonnet-4-6[1m]
context: Python 코드의 안티패턴을 탐지하는 검증 스킬. AST 분석과 휴리스틱을 조합하여 설계 문제를 식별한다. ADK 프로젝트의 도메인 특화 패턴도 포함한다.
agent: 코드 품질 분석가. SOLID, DRY, KISS 원칙과 ADK 패턴에 정통하며 안티패턴을 식별하고 개선 방향을 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 코드 검증
skill-type: Atomic
references:
  - "@skills/quality/review/adversarial-review/SKILL.md"
  - "@skills/reference/philosophy/solid/srp/SKILL.md"
referenced-by:
  - "@skills/quality/review/adversarial-review/SKILL.md"
---

# check-anti-patterns

코드에서 설계 안티패턴을 탐지하고 개선 방향을 제시한다.

## 탐지 규칙

| 안티패턴 | 조건 | 심각도 |
|----------|------|--------|
| **God Class** | 메서드 > 10 또는 줄 수 > 200 | Major |
| **Long Method** | 줄 수 > 50 | Major |
| **Long Parameter List** | 파라미터 > 5 | Minor |
| **Feature Envy** | 외부 클래스 접근 > 50% | Major |
| **Circular Dependency** | 순환 import | Major |
| **Magic Number** | 리터럴 숫자 (0, 1, -1 제외) | Minor |
| **중복 검증** (ADK) | tool 내부 os.path.exists | Major |

## 사용법

```
/check-anti-patterns                     # 전체 코드베이스
/check-anti-patterns agents/             # 특정 경로
/check-anti-patterns src/ --god-class 15 # 임계값 조정
```

## 탐지 스크립트

### God Class / Long Method

```bash
# 200줄 초과 class 탐지
grep -n "^class " --include="*.py" -r . | while read f; do
  file=$(echo $f | cut -d: -f1)
  wc -l "$file"
done | awk '$1 > 200 {print "God Class 의심:", $2}'

# 50줄 초과 function 탐지
python3 -c "
import ast, sys
for path in sys.argv[1:]:
    tree = ast.parse(open(path).read())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            lines = node.end_lineno - node.lineno
            if lines > 50:
                print(f'{path}:{node.lineno} {node.name}() — {lines}줄')
" \$(find . -name '*.py' -not -path '*/.venv/*')
```

### ADK 전용: 중복 검증 탐지

```bash
# tool 내부에서 파일 존재 재확인 탐지 (금지 패턴)
grep -n "Path.*exists\|os.path.exists" agents/**/tools/*.py 2>/dev/null
# → agent __init__에서만 검증해야 함
```

### Circular Dependency

```bash
# 순환 import 탐지
python3 -m py_compile $(find . -name "*.py") 2>&1 | grep "circular"
```

## Gotchas (실패 포인트)

- **임계값이 컨텍스트에 따라 다름**: ADK tool 함수는 30줄도 Long Method일 수 있음
- **false positive 주의**: `__init__`의 파일 존재 확인은 정상 패턴 (금지 아님)
- **Feature Envy 수동 식별**: 자동 탐지 어려움 — 메서드가 자기 클래스 데이터보다 다른 클래스 데이터를 더 많이 쓰는지 확인
- **ADK state 접근**: `tool_context.state.get()`은 정상, `os.path.exists()` 재확인은 금지

## 예시 출력

```
=== Anti-Pattern Check: agents/ ===

[MAJOR] God Class
  agents/demand_analyst/src/demand_analyst/agent.py:10 - DemandAgent
  - Methods: 12 (limit: 10)
  - 개선: load_data(), analyze(), report()를 별도 클래스로 분리

[MAJOR] 중복 검증 (ADK)
  agents/demand_analyst/tools.py:45
  > if Path(file_path).exists():  # 금지
  - 개선: agent __init__에서만 파일 존재 확인

요약: Major 2개, Minor 0개
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| 구현 시 필수 스킬 | CLAUDE.md | 안티패턴 탐지는 구현 체인 3번째 |
| Simplicity First | CLAUDE.md § LLM 행동지침 | 200줄→50줄 다시 써라 |
| @AW-012 | team-operations.md | SRP — 단일 변경 이유 |

## 참조

- `/quality/review/adversarial-review` — 검증 후 셀프 리뷰
- `/reference/philosophy/solid/srp` — SRP 원칙
- [team-operations.md](../../../docs/design/ref/team-operations.md) § AW-012
