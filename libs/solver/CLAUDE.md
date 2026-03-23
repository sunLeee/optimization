# libs/solver/ — SolverStrategy 추상화 패키지

## 역할

알고리즘(MILP/ALNS/Benders/Rolling)을 ObjectiveStrategy처럼 교체 가능한 인터페이스로 추상화.
AW-007 의존 방향 준수: `evaluation → solver → scheduling/routing/stochastic → utils`

## 공개 API

| 클래스 | Tier | 내부 솔버 |
|--------|------|----------|
| `MILPSolver` | Tier 1 (n<10) | `TugScheduleModel` |
| `ALNSSolver` | Tier 2 (n=10~50) | `ALNSWithSpeedOptimizer` |
| `BendersSolver` | Tier 3 (n>50) | `BendersDecomposition` |
| `RollingSolver` | MPC (24h) | `RollingHorizonOrchestrator` |

## 사용 예

```python
from libs.solver import MILPSolver, ALNSSolver, SolverStrategy
from libs.optimization import MinWaitObjective

# Protocol 검증
solver = MILPSolver()
assert isinstance(solver, SolverStrategy)  # @runtime_checkable

# 실행
result = solver.solve(
    windows=windows,
    tug_fleet=["T0", "T1"],
    berth_locations={"B0": (35.098, 129.037)},
    objective=MinWaitObjective(),
)
print(result.solver_name, result.converged, result.optimality_gap)
```

## ConvergenceCriteria 매핑

| 기준 | MILP | ALNS | Benders | Rolling |
|------|------|------|---------|---------|
| `time_limit_sec` | ✅ HiGHS | ❌ (iter 기반) | ✅ | ❌ |
| `max_iter` | ❌ | ✅ | ✅ | ❌ |
| `improvement_threshold` | ❌ | ✅ (tol) | ✅ (gap_tol) | ❌ |

## SolveResult.metadata 관례

```python
# MILP
{"total_cost": float, "waiting_cost": float, "fuel_cost": float, "solver_status": str}

# ALNS
{"iterations": int, "total_cost": float, "convergence_history": list}

# Benders
{"iterations": int, "n_cuts": int, "lower_bound": float, "upper_bound": float,
 "lb_history": list, "ub_history": list, "fallback_used": bool}

# Rolling
{"steps": int, "total_cost": float, "simulate_until_h": float}
```

## objective 파라미터 의미

각 래퍼는 `objective: ObjectiveStrategy`를 수신하지만 내부 솔버에 주입하지 않는다.
솔버는 자체 목적함수(w1·wait + w2·fuel)를 사용하며,
objective는 `SolveResult.assignments`로 KPI를 후처리하는 N×M 러너에서 활용된다.

```python
# N×M 러너 패턴
result = solver.solve(windows, tugs, berths, objective)
kpi = objective.compute(result.assignments, windows)
```

## 수렴 로깅 현황 (Phase 7 확장 예정)

- ALNS: `RouteResult.iterations` (outer loop 횟수), `converged` 제공. Per-iteration 비용 미제공.
- Benders: 최종 LB/UB만 `BendersResult`에 저장. Per-iteration 이력 미제공.
- Phase 7에서 각 솔버에 convergence callback 추가 예정.
- `libs/visualization/convergence.py`: `SolveResult.metadata`에서 수렴 곡선 생성.

## 의존 방향 (AW-007)

```
libs/solver/ → libs/scheduling/  (MILPSolver, BendersSolver)
             → libs/routing/     (ALNSSolver)
             → libs/stochastic/  (RollingSolver)
             → libs/utils/       (TimeWindowSpec, SchedulingToRoutingSpec)
libs/evaluation/ → libs/solver/  (역방향 금지)
```
