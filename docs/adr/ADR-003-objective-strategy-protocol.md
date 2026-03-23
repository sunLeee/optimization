# ADR-003: ObjectiveStrategy — Protocol vs ABC

**날짜**: 2026-03-22
**상태**: Accepted
**작성자**: harbor-real-data-opt ralplan 합의

---

## Decision

`typing.Protocol` (구조적 서브타이핑)을 채택하여 `ObjectiveStrategy`를 선언한다.

```python
from typing import Protocol, runtime_checkable
from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec
from libs.optimization.objective import KPIResult

@runtime_checkable
class ObjectiveStrategy(Protocol):
    def compute(
        self,
        assignments: list[SchedulingToRoutingSpec],
        windows: list[TimeWindowSpec],
    ) -> KPIResult: ...

    def name(self) -> str: ...
```

---

## Drivers

1. **기존 클래스 무수정 교체**: Protocol은 덕타이핑 기반 — 기존 `TugScheduleModel`, `BendersDecomposition` 등에 상속 강제 없이 어댑터 패턴 적용 가능
2. **런타임 isinstance 체크**: `@runtime_checkable` 데코레이터로 `isinstance(obj, ObjectiveStrategy)` 검증 가능 (테스트 용이)
3. **Python 3.11+ 지원**: `typing.Protocol`은 PEP 544 (Python 3.8+), 성능 오버헤드 없음
4. **명시적 계약**: 메서드 시그니처가 Protocol에 선언되어 IDE, mypy, ruff가 일관성 검증

---

## Alternatives

### Option A — `abc.ABC` (거부)

```python
from abc import ABC, abstractmethod

class ObjectiveStrategy(ABC):
    @abstractmethod
    def compute(self, assignments, windows) -> KPIResult: ...
    @abstractmethod
    def name(self) -> str: ...
```

**거부 이유**:
- 모든 구현체가 `ABC`를 상속해야 함 → 기존 클래스 시그니처 변경 불가 (AW-004 위반)
- 다중 상속 시 MRO 복잡성 증가
- Protocol 대비 유연성 저하

### Option B — Duck Typing (타입 힌트 없음) (거부)

**거부 이유**:
- mypy가 타입 오류 검출 불가
- `isinstance` 런타임 검증 불가 → 테스트 신뢰도 저하

---

## Consequences

### Positive
- 기존 코드 무수정으로 Strategy Pattern 도입 가능
- `isinstance(obj, ObjectiveStrategy)` 단위 테스트로 계약 검증
- 향후 전략 추가 시 `objective.py`에만 구현체 추가, 기존 코드 무변경

### Negative
- `@runtime_checkable` Protocol은 메서드 존재만 확인, 파라미터 타입까지는 런타임 검증 안 함
- mypy strict 모드에서 Protocol 일치 여부 별도 확인 필요

### Risks
- `compute()` 시그니처 변경 시 모든 구현체 동시 수정 필요 — Protocol을 단일 진실 소스로 유지할 것

---

## Follow-ups

- 향후 전략 추가 시 `libs/optimization/objective.py`에만 구현체 추가
- Protocol 변경 시 ADR-003 개정
- `tests/test_objective.py`에서 4종 구현체 모두 `isinstance` 검증
