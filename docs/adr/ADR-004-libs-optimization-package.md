# ADR-004: libs/optimization/ 패키지 위치 결정

**날짜**: 2026-03-22
**상태**: Accepted
**작성자**: harbor-real-data-opt ralplan 합의

---

## Decision

`libs/optimization/` 신규 패키지를 생성하여 `ObjectiveStrategy` Protocol과 4개 전략 구현체를 배치한다.

```
libs/optimization/
├── __init__.py      # KPIResult, ObjectiveStrategy, 4개 구현체 export
└── objective.py     # Protocol + _compute_idle + 4개 구현체
```

---

## Drivers

1. **AW-007 계층 분리**: `libs/utils/`는 "공통 타입, 상수, 지리 계산" 계층 — 전략 구현체 혼입 시 계층 오염
2. **단일 책임**: 목적함수 전략 로직은 유틸리티가 아닌 도메인 로직 → 별도 패키지로 격리
3. **테스트 독립성**: `libs/optimization/`의 테스트가 `libs/utils/` 변경에 의존하지 않음
4. **선택적 주입**: `libs/stochastic/`에서 `from libs.optimization import MinIdleObjective`로 교체 가능

---

## Alternatives

### Option A — `libs/utils/objective.py` 단일 파일 (거부)

```python
# libs/utils/objective.py  ← 계층 오염
class MinIdleObjective:
    def compute(self, ...) -> KPIResult: ...
```

**거부 이유**:
- `libs/utils/`는 순수 인터페이스·상수·지리 계산 계층 (AW-007 주석)
- 전략 구현체가 혼입되면 `utils → fuel`, `utils → scheduling` 역방향 의존이 생길 수 있음
- `libs/CLAUDE.md` 체크리스트 항목 1 위반

### Option B — `libs/stochastic/objective.py` (거부)

**거부 이유**:
- `libs/stochastic/`은 오케스트레이터 계층 — 목적함수 전략 구현체 혼입 시 SRP 위반
- `libs/evaluation/`이 `libs/stochastic/`에 의존하게 되어 AW-007 의존 방향 위반 가능

---

## Consequences

### Positive
- 의존 그래프: `stochastic → optimization → utils` (단방향)
- `libs/evaluation/` → `libs/optimization/` 의존 허용 (같은 방향)
- 전략 추가/교체 시 `libs/optimization/objective.py` 만 수정

### Negative
- 새 패키지 init 필요 (`__init__.py` export 관리)
- `pyproject.toml`에 패키지 경로 추가 필요 여부 확인

### New Dependency Graph

```
libs/stochastic   → libs/optimization → libs/utils
libs/stochastic   → libs/optimization → libs/fuel
libs/evaluation   → libs/optimization → libs/utils
libs/evaluation   → libs/fuel         → libs/utils
```

---

## Follow-ups

- `libs/CLAUDE.md` 의존 그래프에 `optimization`, `evaluation` 노드 추가 (Step 1 완료 기준)
- `libs/optimization/CLAUDE.md` 생성 권장 (신규 패키지 자체 문서화)
