"""
확률적 도착 분포 기반 강건성 분석 (n_mc=200).

선박 도착 지연을 Log-normal+Uniform 혼합 분포로 모델링하여
Greedy/MILP/ALNS 세 알고리즘의 CVaR95를 비교한다.

사용법:
    uv run python scripts/stochastic_robustness_full.py
"""
from __future__ import annotations

import json
import logging
import pathlib
import random
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from libs.data import HarborDataLoader
from libs.data.loader import AIS_SUPPLEMENTARY_LOCATIONS
from libs.scheduling.multi_tug import assign_multi_tug_greedy
from libs.scheduling.multi_tug_milp import MultiTugSchedulingModel
from libs.utils.time_window import TimeWindowSpec
from libs.utils.travel_time import TravelTimeMatrix

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

TARGET_DATE = "2024-06-07"
N_MC = 200
SEED = 42
MU_LOG = 4.015
SIGMA_LOG = 1.363
DELAY_PROB = 0.714
CLIP_MIN = -360.0
CLIP_MAX = 360.0
DEFAULT_ANCHORAGE = "연안부두정계지"


def _priority(t: float) -> int:
    return 1 if t < 10_000 else 2 if t < 30_000 else 3


def _wait_h(
    start_times: dict[str, float],
    windows: list[TimeWindowSpec],
    delays: np.ndarray,
    win_order: list[str],
) -> float:
    """perturbed 도착 하에서 실제 대기 계산."""
    total = 0.0
    for i, vid in enumerate(win_order):
        w = next((w for w in windows if w.vessel_id == vid), None)
        if w is None:
            continue
        perturbed_earliest = w.earliest_start + delays[i]
        sched = start_times.get(vid, w.earliest_start)
        actual_start = max(sched, perturbed_earliest)
        total += max(0.0, actual_start - w.earliest_start)
    return total / 60.0


def sample_delays(n_mc: int, n_vessels: int, rng: np.random.Generator) -> np.ndarray:
    is_delayed = rng.random((n_mc, n_vessels)) < DELAY_PROB
    delay_pos = rng.lognormal(MU_LOG, SIGMA_LOG, (n_mc, n_vessels))
    delay_neg = -rng.uniform(0, abs(CLIP_MIN), (n_mc, n_vessels))
    delays = np.where(is_delayed, delay_pos, delay_neg)
    return np.clip(delays, CLIP_MIN, CLIP_MAX)


def cvar95(costs: np.ndarray) -> float:
    threshold = np.percentile(costs, 95)
    tail = costs[costs > threshold]
    return float(np.mean(tail)) if len(tail) > 0 else float(threshold)


def main() -> None:
    loader = HarborDataLoader()
    all_locs = {
        **AIS_SUPPLEMENTARY_LOCATIONS,
        **loader.load_anchorage_locations(),
        **loader.load_berth_locations(),
    }
    tug_names = list(loader.load_tug_mapping().values())
    matrix = TravelTimeMatrix(
        all_locs, {}, ais_log_dir="data/raw/scheduling/data/AISLog"
    )

    all_reqs = loader.load_requests()
    day_reqs = [
        r
        for r in all_reqs
        if r.scheduled_start.strftime("%Y-%m-%d") == TARGET_DATE
    ]
    epoch = min(r.scheduled_start.timestamp() / 60.0 for r in day_reqs)

    windows: list[TimeWindowSpec] = []
    required_tugs_map: dict[str, int] = {}
    berth_map: dict[str, tuple[str, str]] = {}
    for r in day_reqs:
        earliest = r.scheduled_start.timestamp() / 60.0 - epoch
        svc = matrix.get_time_min(r.start_berth_code, r.end_berth_code)
        travel = matrix.get_time_min(DEFAULT_ANCHORAGE, r.start_berth_code)
        latest = earliest + max(travel + svc, 65.0)
        vid = f"{r.vessel_name}_{r.row_id}"
        w = TimeWindowSpec(
            vessel_id=vid,
            berth_id=r.start_berth_code,
            earliest_start=earliest,
            latest_start=latest,
            service_duration=svc,
            priority=_priority(r.tonnage_mt),
        )
        windows.append(w)
        required_tugs_map[vid] = r.required_tugs
        berth_map[vid] = (r.start_berth_code, r.end_berth_code)

    win_order = [w.vessel_id for w in windows]
    n_vessels = len(windows)

    print(f"스케줄 생성 중 ({TARGET_DATE}, n={n_vessels})...")

    # Greedy
    greedy_assign = assign_multi_tug_greedy(windows, tug_names, required_tugs_map)
    greedy_times = {a.vessel_id: a.start_time for a in greedy_assign}

    # MILP
    milp_model = MultiTugSchedulingModel(
        services=windows,
        required_tugs_map=required_tugs_map,
        tug_fleet=tug_names,
        travel_matrix=matrix,
        berth_map=berth_map,
        time_limit_sec=30.0,
        day_relative_epoch=0.0,
    )
    milp_result = milp_model.solve()
    milp_times = milp_result.start_times

    # ALNS (random restart x 10)
    rnd = random.Random(42)
    best_alns: dict[str, float] | None = None
    best_alns_wait = float("inf")
    for _ in range(10):
        shuffled = list(windows)
        rnd.shuffle(shuffled)
        assign = assign_multi_tug_greedy(shuffled, tug_names, required_tugs_map)
        w_h = sum(
            max(
                0,
                a.start_time
                - next(
                    ww for ww in windows if ww.vessel_id == a.vessel_id
                ).earliest_start,
            )
            for a in assign
        ) / 60.0
        if w_h < best_alns_wait:
            best_alns_wait = w_h
            best_alns = {a.vessel_id: a.start_time for a in assign}
    alns_times = best_alns or greedy_times

    algo_schedules = {"Greedy": greedy_times, "MILP": milp_times, "ALNS": alns_times}

    print(f"Monte Carlo 시뮬레이션 (n_mc={N_MC})...")
    rng = np.random.default_rng(SEED)
    delay_matrix = sample_delays(N_MC, n_vessels, rng)

    algo_costs: dict[str, np.ndarray] = {}
    for algo_name, sched_times in algo_schedules.items():
        costs = np.zeros(N_MC)
        for mc_idx in range(N_MC):
            delays = delay_matrix[mc_idx]
            costs[mc_idx] = _wait_h(sched_times, windows, delays, win_order)
        algo_costs[algo_name] = costs

    algo_stats: dict[str, dict[str, float]] = {}
    for algo_name, costs in algo_costs.items():
        algo_stats[algo_name] = {
            "mean_wait_h": round(float(np.mean(costs)), 4),
            "std_wait_h": round(float(np.std(costs)), 4),
            "p50_wait_h": round(float(np.percentile(costs, 50)), 4),
            "p95_wait_h": round(float(np.percentile(costs, 95)), 4),
            "cvar95_wait_h": round(cvar95(costs), 4),
            "max_wait_h": round(float(np.max(costs)), 4),
        }

    most_robust = min(algo_stats, key=lambda a: algo_stats[a]["cvar95_wait_h"])

    result = {
        "date": TARGET_DATE,
        "n_vessels": n_vessels,
        "n_mc": N_MC,
        "distribution": {
            "mu_log": MU_LOG,
            "sigma_log": SIGMA_LOG,
            "delay_prob": DELAY_PROB,
        },
        "algorithms": algo_stats,
        "most_robust": most_robust,
        "most_robust_cvar95": algo_stats[most_robust]["cvar95_wait_h"],
    }

    out_json = pathlib.Path("results/stochastic_robustness_full.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=120)

    names = list(algo_stats.keys())
    means = [algo_stats[n]["mean_wait_h"] for n in names]
    p95s = [algo_stats[n]["p95_wait_h"] for n in names]
    cvar95s = [algo_stats[n]["cvar95_wait_h"] for n in names]

    x = np.arange(len(names))
    w = 0.28
    ax = axes[0]
    ax.bar(x - w, means, w, label="Mean", color="#4c9be8", alpha=0.85)
    ax.bar(x, p95s, w, label="P95", color="#e8a24c", alpha=0.85)
    ax.bar(x + w, cvar95s, w, label="CVaR95", color="#e84c4c", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Wait Time (hours)")
    ax.set_title(
        f"Robustness: Mean/P95/CVaR95 by Algorithm\n(n_mc={N_MC}, {TARGET_DATE})"
    )
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    ax2 = axes[1]
    for algo_name, costs in algo_costs.items():
        ax2.hist(costs, bins=30, alpha=0.5, label=algo_name, density=True)
    ax2.set_xlabel("Wait Time (hours)")
    ax2.set_ylabel("Density")
    ax2.set_title("Wait Time Distribution under Stochastic Arrivals")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("results/robustness_chart.png", bbox_inches="tight")
    plt.close()

    print("\n=== 강건성 분석 결과 ===")
    for algo_name, stats in algo_stats.items():
        print(
            f"{algo_name:8}: mean={stats['mean_wait_h']:.3f}h"
            f" p95={stats['p95_wait_h']:.3f}h"
            f" CVaR95={stats['cvar95_wait_h']:.3f}h"
        )
    print(
        f"\n가장 강건한 알고리즘: {most_robust}"
        f" (CVaR95={algo_stats[most_robust]['cvar95_wait_h']:.3f}h)"
    )
    print(f"결과: {out_json.resolve()}")


if __name__ == "__main__":
    main()
