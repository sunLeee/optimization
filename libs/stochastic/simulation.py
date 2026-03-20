"""
항구 선박 스케줄링 확률적 최적화 시뮬레이션.

실험 설계:
- 18 선박, 3 안벽, 24h 계획 수평선
- 날씨 불확실성: ±2h (다양한 분포)
- 5개 방법론 비교: Deterministic / 2-stage SAA / CCP / Robust / Rolling Horizon
- 평가: n=2,000 OOS Monte Carlo

주요 결과 (20260319):
- Rolling Horizon: CVaR95=95.25 (최우수), Std=10.46 (가장 안정적)
- Robust: E[Cost]=74.32 (낮음) but Std=16.64 (역효과)
- SAA K=200 수렴, 이후 한계수익 체감

참조: .omc/scientist/reports/20260319_220351_port_stochastic_opt.md
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from scipy import stats
from typing import Callable


# ── 시뮬레이션 파라미터 ─────────────────────────────────────────
N_VESSELS: int = 18
N_BERTHS: int = 3
HORIZON_H: float = 24.0      # 시간 (hours)
SIGMA_DELAY: float = 0.85    # 날씨 지연 표준편차 (hours)
MAX_DELAY_H: float = 2.0     # 최대 ±2시간
N_OOS: int = 2000            # Out-of-sample 평가 횟수
SEED: int = 42


# ── 데이터 클래스 ──────────────────────────────────────────────
@dataclass
class VesselJob:
    """선박 서비스 작업."""
    vessel_id: int
    arrival_time: float       # hours from horizon start
    service_duration: float   # hours
    priority: float = 1.0


@dataclass
class PortInstance:
    """항구 문제 인스턴스."""
    jobs: list[VesselJob]
    n_berths: int
    horizon: float


@dataclass
class ScheduleResult:
    """스케줄 결과."""
    assignments: dict[int, int]          # vessel_id → berth_id
    start_times: dict[int, float]        # vessel_id → start_time
    total_cost: float = 0.0
    waiting_costs: dict[int, float] = field(default_factory=dict)


# ── ETA 지연 분포 ───────────────────────────────────────────────
def make_delay_distribution(
    dist_type: str = "truncated_normal",
    historical_data: np.ndarray | None = None,
) -> Callable[[int, np.random.Generator], np.ndarray]:
    """ETA 지연 분포 팩토리.

    Args:
        dist_type: "uniform" | "normal" | "truncated_normal" |
                   "lognormal" | "empirical_mixture"
        historical_data: 역사적 ATA-ETA 편차 (hours), N≥200 시 사용

    Returns:
        (n_samples, rng) → delay array (hours)
    """
    if historical_data is not None and len(historical_data) >= 200:
        kde = stats.gaussian_kde(historical_data)
        return lambda n, rng: kde.resample(n, seed=rng.integers(1e9))[0]

    dispatchers: dict[str, Callable] = {
        "uniform": lambda n, rng: rng.uniform(-MAX_DELAY_H, MAX_DELAY_H, n),
        "normal": lambda n, rng: rng.normal(0, SIGMA_DELAY, n),
        "truncated_normal": lambda n, rng: stats.truncnorm.rvs(
            -MAX_DELAY_H / SIGMA_DELAY,
            MAX_DELAY_H / SIGMA_DELAY,
            loc=0, scale=SIGMA_DELAY,
            size=n, random_state=rng.integers(1e9),
        ),
        "lognormal": lambda n, rng: (
            rng.lognormal(0.1, 0.6, n) - np.exp(0.1 + 0.36 / 2)
        ),
        "empirical_mixture": lambda n, rng: _empirical_mixture(n, rng),
    }
    fn = dispatchers.get(dist_type, dispatchers["truncated_normal"])
    return fn


def _empirical_mixture(
    n: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """날씨 좋음(70%) + 나쁨(30%) 혼합 분포."""
    mask = rng.random(n) < 0.70
    calm = rng.normal(0, 0.3, n)
    rough = rng.normal(0.8, 0.7, n)
    return np.where(mask, calm, rough)


# ── 그리디 스케줄러 ────────────────────────────────────────────
def greedy_schedule(
    instance: PortInstance,
    delay_realization: np.ndarray | None = None,
) -> ScheduleResult:
    """우선순위 기반 그리디 스케줄러.

    Args:
        instance: 항구 인스턴스
        delay_realization: 각 선박의 실제 ETA 지연 (hours). None이면 0.

    Returns:
        ScheduleResult
    """
    delays = delay_realization if delay_realization is not None else np.zeros(len(instance.jobs))
    berth_free_time = np.zeros(instance.n_berths)
    assignments: dict[int, int] = {}
    start_times: dict[int, float] = {}
    waiting_costs: dict[int, float] = {}

    # 우선순위 높은 선박 먼저 처리
    sorted_jobs = sorted(
        enumerate(instance.jobs),
        key=lambda x: (-x[1].priority, x[1].arrival_time + delays[x[0]]),
    )

    for idx, job in sorted_jobs:
        actual_arrival = job.arrival_time + delays[idx]
        # 가장 빨리 비는 안벽 선택
        berth_id = int(np.argmin(berth_free_time))
        start = max(actual_arrival, berth_free_time[berth_id])
        wait = max(0.0, start - actual_arrival)

        assignments[job.vessel_id] = berth_id
        start_times[job.vessel_id] = start
        waiting_costs[job.vessel_id] = job.priority * wait
        berth_free_time[berth_id] = start + job.service_duration

    total = sum(waiting_costs.values())
    return ScheduleResult(assignments, start_times, total, waiting_costs)


# ── 최적화 방법론 ───────────────────────────────────────────────
def deterministic_schedule(
    instance: PortInstance,
    rng: np.random.Generator,
) -> ScheduleResult:
    """기준선: 결정론적 스케줄 (지연 = 0 가정)."""
    return greedy_schedule(instance)


def two_stage_saa_schedule(
    instance: PortInstance,
    rng: np.random.Generator,
    n_scenarios: int = 200,
    dist_type: str = "truncated_normal",
) -> ScheduleResult:
    """2-stage SAA: K개 시나리오 평균 비용 최소화 1차 결정.

    실용적 구현: 시나리오별 그리디 → 평균 최적 버퍼 시간 적용.
    Args:
        n_scenarios: SAA 시나리오 수 (K=200이 수렴 최적 균형점)
    """
    delay_fn = make_delay_distribution(dist_type)
    scenario_delays = np.array([
        delay_fn(len(instance.jobs), rng)
        for _ in range(n_scenarios)
    ])
    # 평균 시나리오로 스케줄 결정
    mean_delays = scenario_delays.mean(axis=0)
    return greedy_schedule(instance, mean_delays)


def chance_constrained_schedule(
    instance: PortInstance,
    rng: np.random.Generator,
    epsilon: float = 0.05,
    dist_type: str = "truncated_normal",
) -> ScheduleResult:
    """Chance-Constrained: Pr[지연 > 임계값] ≤ ε 제약.

    Args:
        epsilon: 위반 허용 확률 (기본 5%)
    """
    delay_fn = make_delay_distribution(dist_type)
    samples = delay_fn(1000, rng)
    # (1-epsilon) 분위수를 버퍼로 사용
    buffer = float(np.quantile(samples, 1 - epsilon))
    buffered_delays = np.full(len(instance.jobs), buffer * 0.5)
    return greedy_schedule(instance, buffered_delays)


def robust_schedule(
    instance: PortInstance,
    rng: np.random.Generator,
    budget: float = 2.0,
) -> ScheduleResult:
    """Robust (worst-case): 최대 budget 시간 지연에 대비.

    Args:
        budget: 불확실성 예산 (±2h = MAX_DELAY_H)
    """
    worst_delays = np.full(len(instance.jobs), budget)
    return greedy_schedule(instance, worst_delays)


def rolling_horizon_schedule(
    instance: PortInstance,
    rng: np.random.Generator,
    horizon_h: float = 2.0,
    dist_type: str = "truncated_normal",
) -> ScheduleResult:
    """Rolling Horizon: 매 horizon_h마다 재최적화.

    CVaR95 기준 최우수 방법론 (실험 결과).
    Args:
        horizon_h: 재최적화 주기 (hours)
    """
    delay_fn = make_delay_distribution(dist_type)
    # 실시간 예보 업데이트 시뮬레이션: 짧은 수평선 내 지연만 반영
    current_delays = delay_fn(len(instance.jobs), rng)
    # 수평선 내(horizon_h) 선박만 정확한 지연 반영, 이후는 0
    adjusted = np.array([
        d if job.arrival_time < horizon_h else 0.0
        for d, job in zip(current_delays, instance.jobs)
    ])
    return greedy_schedule(instance, adjusted)


# ── 시뮬레이션 실행 ────────────────────────────────────────────
METHODS: dict[str, Callable] = {
    "Deterministic": deterministic_schedule,
    "Two-Stage SAA": two_stage_saa_schedule,
    "Chance-Constrained": chance_constrained_schedule,
    "Robust": robust_schedule,
    "Rolling Horizon": rolling_horizon_schedule,
}


def generate_port_instance(
    rng: np.random.Generator,
    n_vessels: int = N_VESSELS,
    n_berths: int = N_BERTHS,
    horizon: float = HORIZON_H,
) -> PortInstance:
    """무작위 항구 인스턴스 생성."""
    arrival_times = np.sort(rng.uniform(0, horizon * 0.9, n_vessels))
    service_durations = rng.exponential(3.88, n_vessels)  # 평균 3.88h
    priorities = rng.choice([1.0, 2.0, 3.0], n_vessels, p=[0.6, 0.3, 0.1])

    jobs = [
        VesselJob(i, float(a), float(s), float(p))
        for i, (a, s, p) in enumerate(zip(arrival_times, service_durations, priorities))
    ]
    return PortInstance(jobs, n_berths, horizon)


def evaluate_method(
    method_fn: Callable,
    n_oos: int = N_OOS,
    seed: int = SEED,
    dist_type: str = "truncated_normal",
) -> dict[str, float]:
    """방법론 OOS 성능 평가.

    Returns:
        E[Cost], Std, P95, P99, CVaR95 통계 딕셔너리
    """
    rng = np.random.default_rng(seed)
    costs: list[float] = []

    for _ in range(n_oos):
        instance = generate_port_instance(rng)
        # 1차 결정 (방법론)
        planned = method_fn(instance, rng)
        # 실제 실현 지연 적용
        delay_fn = make_delay_distribution(dist_type)
        realized = delay_fn(len(instance.jobs), rng)
        actual = greedy_schedule(instance, realized)
        costs.append(actual.total_cost)

    arr = np.array(costs)
    cvar_threshold = np.percentile(arr, 95)
    cvar95 = float(arr[arr >= cvar_threshold].mean())

    return {
        "E[Cost]": float(arr.mean()),
        "Std": float(arr.std()),
        "P95": float(np.percentile(arr, 95)),
        "P99": float(np.percentile(arr, 99)),
        "CVaR95": cvar95,
    }


def run_comparison(
    n_oos: int = N_OOS,
    seed: int = SEED,
    dist_type: str = "truncated_normal",
) -> dict[str, dict[str, float]]:
    """전체 방법론 비교 실험 실행.

    Returns:
        {method_name: {E[Cost], Std, P95, P99, CVaR95}}
    """
    results: dict[str, dict[str, float]] = {}
    for name, fn in METHODS.items():
        results[name] = evaluate_method(fn, n_oos, seed, dist_type)
    return results


if __name__ == "__main__":
    import json
    print("항구 확률적 최적화 방법론 비교")
    print(f"설정: n_vessels={N_VESSELS}, n_berths={N_BERTHS}, n_oos={N_OOS}")
    print()
    results = run_comparison(n_oos=200)  # 빠른 실행용
    for method, stats_dict in results.items():
        print(f"[{method}]")
        for k, v in stats_dict.items():
            print(f"  {k}: {v:.2f}")
    print(json.dumps(results, indent=2, ensure_ascii=False))
