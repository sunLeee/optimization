---
name: convention-brooks-law
description: Brooks' Law. 늦은 프로젝트에 인력을 추가하면 더 늦어진다. 온보딩 비용과 커뮤니케이션 오버헤드.
user-invocable: true
triggers:
  - "Brooks' Law"
  - "브룩스의 법칙"
  - "인력 추가"
  - "늦은 프로젝트"
---

# convention-brooks-law

**@AW-028** | @docs/design/ref/team-operations.md § AW-028

Brooks' Law: "늦은 소프트웨어 프로젝트에 인력을 추가하면 더 늦어진다." (Fred Brooks, The Mythical Man-Month)

핵심: 에이전트/개발자 추가는 온보딩 비용 + 커뮤니케이션 오버헤드를 만들어낸다.

## VIOLATION 1: 늦은 에이전트에 서브에이전트 추가

```python
# 상황: demand_analyst 에이전트 구현이 2주 지연
# VIOLATION: 서브에이전트를 추가해서 해결하려 함

# 기존 에이전트가 절반만 구현된 상태에서:
# - 새 서브에이전트에 컨텍스트 전달 비용
# - 인터페이스 합의 필요
# - 기존 구현과 충돌 가능성
# → 결과: 통합 작업으로 더 늦어짐

# CORRECT: 인력 추가 대신 범위 축소
# 1. 완성된 부분만 먼저 배포
# 2. 미완성 부분은 다음 sprint로 이동
# 3. 기존 에이전트에 집중

class DemandAnalystV1:
    """핵심 기능만 구현 — 완성 가능한 범위로 축소."""

    def analyze_basic_demand(self, tool_context: ToolContext) -> dict:
        """기본 수요 분석 (V1 — 완성 가능한 범위)."""
        df = pd.read_csv(tool_context.state["app:demand_file"])
        return {"total": float(df["demand"].sum())}

    # V2로 미룬 기능:
    # - 지역별 분석 → 다음 sprint
    # - 시계열 예측 → 다음 sprint
```

## VIOLATION 2: 병렬 에이전트로 해결하려는 착각

```python
# VIOLATION: 하나의 복잡한 task를 병렬로 나눠 빠르게 하려 함
# 문제: 에이전트 간 의존성이 있으면 병렬화 효과 없음

# 의존성이 있는 작업:
# Agent A: 데이터 로딩 → Agent B: 전처리 → Agent C: 분석
# B는 A 완료 후 시작 가능 → 병렬 불가

# 의존성 분석 없이 병렬화하면 더 복잡해짐

# CORRECT: 의존성이 없는 작업만 병렬화
# 독립적인 작업:
# Agent A: demand 데이터 처리 (독립)
# Agent B: supply 데이터 처리 (독립)
# → 실제로 병렬 가능
```

## Brooks' Law 적용 체크리스트

| 상황 | 권장 행동 |
|------|----------|
| 에이전트 구현 지연 | 범위 축소 후 완성 |
| 복잡한 로직 | 단계별 분해 |
| 병렬화 고려 | 의존성 분석 먼저 |
| 새 에이전트 추가 | 온보딩 비용 계산 |

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-028 | @docs/design/ref/team-operations.md § AW-028 | Brooks' Law |
| @AW-019 | @docs/design/ref/team-operations.md § AW-019 | YAGNI — 범위 축소 |
| @AW-023 | @docs/design/ref/team-operations.md § AW-023 | Gall's Law — 단순부터 |

## 참조

- @docs/design/ref/team-operations.md § AW-028
- @.claude/skills/convention-yagni/SKILL.md
- @.claude/skills/convention-galls-law/SKILL.md
