# libs/stochastic/ — 확률적 오케스트레이터

## 역할

Rolling Horizon MPC 실시간 dispatch + 2-Stage SAA 사전 계획.
최상위 Orchestrator. `libs/scheduling/`, `libs/routing/`, `libs/fuel/`을 조율.

## 파일 목록

| 파일 | 주요 클래스 | 역할 |
|------|-----------|------|
| `rolling_horizon.py` | `RollingHorizonOrchestrator`, `PortState` | MPC 실시간 dispatch |
| `two_stage.py` | `TwoStageScheduler`, `TwoStageConfig` | SAA 사전 계획 |
| `simulation.py` | `make_delay_distribution()` | ETA 지연 분포 팩토리 |

## Rolling Horizon (MPC)

```python
from libs.stochastic import RollingHorizonOrchestrator, RollingHorizonConfig

cfg = RollingHorizonConfig(
    horizon_h=2.0,    # 예측 수평선 (2시간)
    dt_h=0.5,         # 재최적화 주기 (30분)
)
rh = RollingHorizonOrchestrator(windows, tug_fleet, berth_locations, cfg=cfg)
result = rh.run(simulate_until_h=24.0)
```

**Tier 자동 선택**: n<10→MILP, n<50→ALNS, n≥50→Benders.

## 2-Stage SAA

```python
from libs.stochastic import TwoStageScheduler, TwoStageConfig, compute_cvar

cfg = TwoStageConfig(n_scenarios=50, seed=42)
ts = TwoStageScheduler(windows, tug_fleet, berth_locations, cfg=cfg)
result = ts.solve()
print(f"E[cost]={result.expected_cost:.2f}, CVaR95={result.cvar_95:.2f}")
```

## ETA 지연 분포 (AW-010)

| 조건 | 분포 |
|------|------|
| 데이터 N≥200 | KDE (`gaussian_kde`) |
| 데이터 N<200 | Log-normal (MLE 피팅) |
| 데이터 없음 | Log-normal(μ=0.1, σ=0.5) clamp [-2h,+2h] |

## SAA 병렬화

`ProcessPoolExecutor(max_workers=min(K, cpu_count()))` — GIL 우회.
Pyomo 모델은 각 프로세스에서 독립 생성 (thread-safety).

## CVaR 계산

```python
from libs.stochastic import compute_cvar
cvar_95 = compute_cvar(scenario_costs, alpha=0.95)
```

`CVaR_α = VaR_α + E[(cost - VaR_α)^+ | cost > VaR_α]`

## 확장 시 주의

- `libs/scheduling/`, `libs/routing/`에 역방향 의존 금지 (AW-007)
- `PortState.current_time`: minutes 단위 (hours와 혼동 주의)
- Tier 경계 근방(±5): 두 솔버 실행 후 비용 기준 선택
