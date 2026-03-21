# libs/fuel/ — 연료 소비 모델

## 역할

예인선 연료 소비량 계산 및 eco-speed 최적화. `libs/utils/`에만 의존.

## 핵심 규칙 (AW-006)

**γ=2.5 고정**: `F(v, d) = α · v^2.5 · d`

- Tier 1: `F = α · d` (선형 근사, 속도 고정)
- Tier 2+: `F = α · v^2.5 · d` (비선형, CVXPY GP)

## 주요 API

```python
from libs.fuel.consumption import fuel_consumption
from libs.fuel.eco_speed import EcoSpeedOptimizer

# 단일 구간 연료
fuel_mt = fuel_consumption(speed_kn=12.0, dist_nm=10.0, alpha=0.5)

# 구간별 eco-speed 최적화 (CVXPY GP, v^2.5)
eco = EcoSpeedOptimizer(alpha=0.5, gamma=2.5)
sol = eco.optimize(arcs, distances, time_budgets)
# sol.speeds: {(from,to): speed_kn}, sol.total_fuel: float
```

## 파일 목록

| 파일 | 클래스/함수 | 역할 |
|------|-----------|------|
| `consumption.py` | `fuel_consumption()`, `mccormick_linearize()` | 기본 연료 계산 |
| `eco_speed.py` | `EcoSpeedOptimizer`, `SpeedSolution` | CVXPY GP 속도 최적화 |

## EcoSpeedOptimizer 수렴성

CVXPY GP (posynomial): 전역 최적 보장.
`v_min=4kn`, `v_max=14kn` 범위에서 항상 수렴.

## 확장 시 주의

- `gamma` 변경 시 반드시 AW-006 검토
- `mccormick_linearize()`: Tier 1 MILP용 v² 선형화 (v^2.5 아님)
- Tier 2 ALNS outer loop에서 `eco.optimize()` 호출 → 배정 고정 후 속도 최적화
