# ADR-006: 4종 목적함수 수식 정의 + OBJ-D 사후집계 확정

**날짜**: 2026-03-22
**상태**: Accepted
**작성자**: harbor-real-data-opt ralplan 합의

---

## Decision

Phase 1 목적함수를 Strategy Pattern으로 4종 구현한다. OBJ-D의 `λ·dist_nm` 항은 **사후집계 방식**으로 처리한다 (MILP 목적함수에 통합하지 않음).

### 4종 목적함수 정의

| ID | 클래스명 | Phase | 수식 | 비고 |
|----|---------|-------|------|------|
| OBJ-A | `MinWaitObjective` | 1 | `min Σ(priority × wait_h)` | 선박 대기 최소화 (기존 TwoStageResult.waiting_cost_h 기반) |
| OBJ-B | `MinIdleObjective` | 1 | `min Σ idle_h` | 예인선 유휴 최소화 (신규 `_compute_idle()` 기반) |
| OBJ-C | `MinCompositeObjective` | 1 | `min w2·idle_h + w3·priority×wait_h` | 유휴+대기 가중합, 기본값 w2=w3=0.5 |
| OBJ-D | `MinAllObjective` | 1+2(사후) | `idle_h + priority×wait_h + λ·dist_nm` | 사후집계, λ=1.0 기본값 |

### OBJ-D 사후집계 방식 확정

```python
class MinAllObjective:
    """OBJ-D: 사후집계 — Phase 1 풀이 후 dist_nm을 RouteResult에서 읽어 합산."""

    def compute(
        self,
        assignments: list[SchedulingToRoutingSpec],
        windows: list[TimeWindowSpec],
    ) -> KPIResult:
        idle_h = _compute_idle(assignments, windows)
        wait_h = _compute_wait(assignments, windows)
        # dist_nm: RouteResult에서 주입되지 않으면 0.0 fallback
        # 백테스터 컨텍스트에서는 dist_nm = 0.0 (RouteResult 없음)
        dist_nm = self._dist_nm_cache or 0.0
        obj_val = idle_h + wait_h + self.lam * dist_nm
        return KPIResult(
            dist_nm=dist_nm,
            idle_h=idle_h,
            wait_h=wait_h,
            fuel_mt=0.0,  # Phase 2 연료는 별도 계산
            objective_value=obj_val,
        )
```

**주의**: 백테스터(`RealDataBacktester`) 컨텍스트에서는 `RouteResult`가 없으므로 `dist_nm = 0.0`이다. 이 경우 OBJ-D의 `objective_value`는 OBJ-C와 실질적으로 동치가 된다. 이는 알려진 제약이며 실험 결과 해석 시 명시해야 한다.

### `_compute_idle()` 알고리즘

```python
def _compute_idle(
    assignments: list[SchedulingToRoutingSpec],
    windows: list[TimeWindowSpec],
) -> float:
    """예인선별 유휴시간 합산.

    알고리즘:
    1. tug_id별로 assignments를 scheduled_start 기준 정렬
    2. 연속 assignment 간:
       prev_end = prev.scheduled_start + prev.time_window.service_duration
       gap = next.scheduled_start - prev_end
       gap > 0이면 유휴시간
    3. 모든 tug의 gap 합산 → idle_h (hours, /60 변환)

    참조 패턴: libs/routing/alns.py 내 tug_free_at[k] = start + w.service_duration
    """
    from collections import defaultdict
    tug_assignments: dict[str, list] = defaultdict(list)
    for spec in assignments:
        tug_assignments[spec.tug_id].append(spec)

    total_idle_min = 0.0
    for tug_id, specs in tug_assignments.items():
        specs_sorted = sorted(specs, key=lambda s: s.scheduled_start)
        for i in range(1, len(specs_sorted)):
            prev = specs_sorted[i - 1]
            curr = specs_sorted[i]
            prev_end = prev.scheduled_start + prev.time_window.service_duration
            gap = curr.scheduled_start - prev_end
            if gap > 0:
                total_idle_min += gap

    return total_idle_min / 60.0  # minutes → hours
```

---

## Drivers

1. **4대 KPI 커버**: 각 단일 최적화(OBJ-A, B)와 조합(OBJ-C, D)으로 실증 비교 가능
2. **Phase 1 MILP 구조 무변경**: OBJ-D를 MILP에 통합 시 `λ·dist_nm` 선형화 필요 (dist_nm은 비선형 경로 합산) — 복잡도 과다
3. **기존 `TugScheduleModel.solve()` 재사용**: MILP 목적함수 교체 없이 사후집계로 처리

---

## Alternatives

### Option A — OBJ-D를 MILP 목적함수에 λ·dist_nm 항 추가 (거부)

```python
# tsp_t_milp.py 내 목적함수 수정
model.obj = Objective(
    expr=w1 * sum(wait) + w2 * sum(fuel) + lam * sum(dist),
    sense=minimize
)
```

**거부 이유**:
- `dist_nm`은 berth-to-berth 거리 합산 → 배정에 따라 달라지는 비선형 항
- Pyomo에서 선형화 시 McCormick 근사 또는 추가 바이너리 변수 필요 → 모델 복잡도 급증
- 기존 `TugScheduleModel` 시그니처 변경 필요 (AW 위반)

### Option B — Phase 2(ALNS)에서 dist_nm 최소화 후 OBJ-D 사후집계 (채택 방식과 동일)

Phase 2 RouteResult.total_cost에 dist_nm이 포함되어 있으므로, Phase 2 완료 후 OBJ-D를 집계하는 것도 동일한 사후집계 방식이다. 현재 채택 방식.

---

## Consequences

### Positive
- Phase 1 MILP 구조 무변경 (기존 24개 테스트 Green 유지)
- 백테스터에서 4종 모두 동일 파이프라인으로 실행 가능
- OBJ-D의 λ 값은 실험 후 조정 가능 (ADR 개정 대상)

### Negative
- 백테스터 컨텍스트에서 OBJ-D `dist_nm = 0.0` → OBJ-D와 OBJ-C가 실질적으로 동치
- RouteResult 없는 환경에서 OBJ-D 실험 차별성 제한

### Risks
- 향후 dist_nm 추정값(haversine_nm 기반)을 백테스터에 추가하면 OBJ-D 차별성 복원 가능 — ADR-006 개정 대상

---

## Follow-ups

- 실증 결과에 따라 λ 범위 조정 후 ADR-006 개정
- 백테스터에 berth-to-berth haversine 거리 추정 추가 고려 (ADR-006 v2)
- OBJ-B/OBJ-C 순서 확정 근거: Spec 기준 — OBJ-B=MinIdle(유휴), OBJ-C=MinComposite(유휴+대기)
