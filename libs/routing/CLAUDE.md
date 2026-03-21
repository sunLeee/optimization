# libs/routing/ — ALNS + eco-speed 경로 최적화

## 역할

Tier 2 (n=10~50) 예인선 경로 최적화.
ALNS + EcoSpeedOptimizer alternating loop.
의존: `libs/utils/`, `libs/fuel/` (단방향).

## 주요 API

```python
from libs.routing.alns import ALNSWithSpeedOptimizer, ALNSConfig

cfg = ALNSConfig(max_iter=200, max_outer_iter=20, seed=42)
solver = ALNSWithSpeedOptimizer(windows, tug_fleet, berth_locations, cfg=cfg)
result = solver.solve()
# result.assignments, result.total_cost, result.converged
```

## 연산자 목록

### Destroy (D1~D4)
| ID | 함수 | 설명 | 복잡도 |
|----|------|------|--------|
| D1 | `destroy_random()` | 무작위 제거 | O(n) |
| D2 | `destroy_worst()` | 최고 비용 제거 | O(n log n) |
| D3 | `destroy_shaw()` | Shaw relatedness | O(n²) |
| D4 | `destroy_time_window()` | 혼잡 시간대 제거 | O(n) |

### Repair (R1~R2)
| ID | 함수 | 설명 | 복잡도 |
|----|------|------|--------|
| R1 | `repair_greedy_insert()` | 최소 비용 삽입 | O(n²·m) |
| R2 | `repair_regret2_insert()` | Regret-2 삽입 | O(n²·m·log n) |

## Shaw Destroy Lambda (D3)

기본값 (Ropke & Pisinger 2006): `λ_d=0.5, λ_t=0.3, λ_p=0.2`

실제 항구 데이터 피팅:
```python
from libs.routing.alns import fit_shaw_lambdas
lambda_d, lambda_t, lambda_p = fit_shaw_lambdas(historical_data, distances, windows)
cfg = ALNSConfig(shaw_lambda_d=lambda_d, ...)
```

## Adaptive Weight (Ropke & Pisinger 2006)

- `σ1=33` (최적해 갱신), `σ2=9` (현재해 개선), `σ3=3` (SA 수용)
- `ρ=0.1` (학습률), `segment_size=100` (갱신 주기)
- `OperatorStats.update_weight()`: `w ← (1-ρ)·w + ρ·(score/usage)`

## 수렴 조건

Outer loop (alternating): window 평균 수렴 판단 (oscillation 완화)
- `|Δcost_avg| / cost < tol=0.001` (최근 `tol_window=3`회 평균)
- 미수렴 시 `RouteResult.converged=False` + `ConvergenceWarning`

ALNS (이론적 수렴 보장 없음) → SA 수용 기준으로 실용적 수렴.

## 확장 시 주의

- 새 Destroy/Repair 연산자: `OperatorStats` 리스트에 추가 후 `_roulette_select()` 자동 적용
- `DEPOT`, `haversine_nm`은 `libs/utils/`에서 import (AW-007)
- `fit_shaw_lambdas()`: 데이터 없으면 원논문 기본값 사용
