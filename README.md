# Harbor Optimization

항구 예인선(Tugboat) · 대형선박(Vessel) · 선석(Berth) 스케줄·경로·연료 최적화 시스템.

## 개요

| 문제 | 수식 클래스 | 알고리즘 |
|------|------------|---------|
| 선석 배분 (BAP) | MILP | Pyomo + HiGHS |
| 예인선 스케줄 (TSP-T) | MILP | Pyomo + HiGHS |
| 경로 최적화 (VRPTW) | NP-Hard | ALNS + eco-speed GP |
| 대규모 통합 | Benders | Master HiGHS + Sub CVXPY/IPOPT |
| 실시간 dispatch | MPC | Rolling Horizon Orchestrator |
| 불확실성 계획 | 2-stage SP | SAA K=50, ProcessPoolExecutor |

## 빠른 시작

```bash
# 환경 설정
uv sync

# 벤치마크 실행 (Phase 3a vs 3b 비교)
uv run python scripts/benchmark_benders.py --n 12 --tugs 4 --berths 2 --compare-gamma

# 품질 게이트
bash .claude/check-criteria.sh --score   # ≥ 90 목표
```

## 설치

```bash
# uv 설치 (https://docs.astral.sh/uv/)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync

# 선택적: IPOPT (Phase 3b 속도 최적화)
brew install ipopt
uv pip install cyipopt
```

**핵심 의존성**: `pyomo>=6.7`, `highspy>=1.7`, `numpy>=1.26`, `scipy>=1.11`, `cvxpy>=1.4`

## 프로젝트 구조

```
harbor-optimization/
├── libs/                     # 최적화 라이브러리
│   ├── utils/                # 공통 유틸 (geo, constants, 인터페이스)
│   ├── fuel/                 # 연료 모델 F(v,d)=α·v^2.5·d
│   ├── scheduling/           # BAP, TSP-T MILP, Benders
│   ├── routing/              # ALNS + eco-speed alternating
│   ├── stochastic/           # Rolling Horizon, 2-stage SAA
│   └── simulation/           # 에이전트 시뮬레이션 환경
├── scripts/                  # 실행 스크립트
│   └── benchmark_benders.py  # Phase 3a/3b 비교 벤치마크
├── docs/research/            # 수학적 formulation, 알고리즘 선택 가이드
└── tests/                    # 단위·통합 테스트
```

## Tier별 알고리즘 (AW-005)

| 규모 | 알고리즘 | 솔버 | 연료 모델 |
|------|----------|------|---------|
| n < 10 | Exact MILP | Pyomo + HiGHS | F=α·d (선형) |
| n = 10~50 | ALNS + eco-speed | CVXPY GP | F=α·v^2.5·d |
| n > 50 | Benders Decomposition | HiGHS + CVXPY | F=α·v^2.5·d |

## 연료 모델 (AW-006)

```python
from libs.fuel.consumption import fuel_consumption

# F(v, d) = α · v^γ · d,  γ=2.5 고정
fuel_mt = fuel_consumption(speed_kn=12.0, dist_nm=10.0, alpha=0.5)
# → 2494.15 MT
```

## BAP → TSP-T 파이프라인

```python
from libs.scheduling.bap import BAPInput, BerthAllocationModel
from libs.scheduling.tsp_t_milp import TugScheduleModel

bap = BerthAllocationModel(bap_input)
bap_result = bap.solve()                         # 선석 배분

tug = TugScheduleModel(
    windows=bap_result.time_windows,             # [I1] 인터페이스
    tug_fleet=["T0", "T1"],
    berth_locations=bap_result.berth_positions,
)
tug_result = tug.solve()
```

## Rolling Horizon + SAA

```python
from libs.stochastic import RollingHorizonOrchestrator, TwoStageScheduler

# 실시간 dispatch (MPC)
rh = RollingHorizonOrchestrator(windows, tug_fleet, berth_locations)
result = rh.run(simulate_until_h=24.0)

# 사전 계획 (SAA K=50)
ts = TwoStageScheduler(windows, tug_fleet, berth_locations)
ts_result = ts.solve()
print(f"E[cost]={ts_result.expected_cost:.2f}, CVaR95={ts_result.cvar_95:.2f}")
```

## 모듈 의존 방향 (AW-007)

```
libs/stochastic → libs/scheduling → libs/utils
libs/stochastic → libs/routing   → libs/utils
libs/stochastic → libs/fuel      → libs/utils
```

역방향 의존 금지.

## 워크플로우 규칙 (AW-001 ~ AW-010)

전체 규칙은 `CLAUDE.md` 참조.

## 연구 문서

| 파일 | 내용 |
|------|------|
| `docs/research/mathematical_formulation.md` | TSP-T/VRPTW/BAP 수식 |
| `docs/research/algorithm_selection.md` | Tier별 알고리즘 가이드 |
| `docs/research/stochastic_scheduling.md` | 2-stage SP, Rolling Horizon |
| `docs/research/eta_distributions.md` | ETA 지연 분포 선택 가이드 |
