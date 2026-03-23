"""
N×M 벤치마크 — 3 목적함수 × 3 알고리즘 × 실데이터.

목적함수: MinWait, MinIdle, MinComposite
알고리즘: Greedy, MILP, ALNS(random restart)
데이터: 2024-06-07 (n=18건)

사용법:
    uv run python scripts/run_nm_benchmark_full.py
"""
from __future__ import annotations

import csv
import logging
import pathlib
import random
import sys
import time
from collections import defaultdict

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from libs.data import HarborDataLoader
from libs.data.loader import AIS_SUPPLEMENTARY_LOCATIONS
from libs.scheduling.multi_tug import (
    MultiTugAssignment,
    assign_multi_tug_greedy,
)
from libs.scheduling.multi_tug_milp import MultiTugSchedulingModel
from libs.utils.time_window import TimeWindowSpec
from libs.utils.travel_time import TravelTimeMatrix

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s: %(message)s")

DEFAULT_ANCHORAGE = "연안부두정계지"
TARGET_DATE = "2024-06-07"


def _priority(tonnage_mt: float) -> int:
    if tonnage_mt < 10_000:
        return 1
    if tonnage_mt < 30_000:
        return 2
    return 3


def _compute_idle_h(assignments: list[MultiTugAssignment], windows: list[TimeWindowSpec]) -> float:
    """예선별 유휴시간 합계 (시간)."""
    win_map = {w.vessel_id: w for w in windows}
    tug_timeline: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for a in assignments:
        w = win_map.get(a.vessel_id)
        if w is None:
            continue
        end = a.start_time + w.service_duration
        for tug in a.tug_ids:
            tug_timeline[tug].append((a.start_time, end))

    idle_min = 0.0
    for _tug, slots in tug_timeline.items():
        slots.sort()
        for i in range(len(slots) - 1):
            gap = slots[i + 1][0] - slots[i][1]
            if gap > 0:
                idle_min += gap
    return idle_min / 60.0


def _compute_wait_h(assignments: list[MultiTugAssignment], windows: list[TimeWindowSpec]) -> float:
    win_map = {w.vessel_id: w for w in windows}
    total = 0.0
    for a in assignments:
        w = win_map.get(a.vessel_id)
        if w:
            total += max(0.0, a.start_time - w.earliest_start)
    return total / 60.0


def run_greedy(windows, tug_fleet, required_tugs_map, objective: str) -> dict:
    t0 = time.time()
    assignments = assign_multi_tug_greedy(windows, tug_fleet, required_tugs_map)
    elapsed = time.time() - t0
    wait_h = _compute_wait_h(assignments, windows)
    idle_h = _compute_idle_h(assignments, windows)
    composite = 0.5 * wait_h + 0.5 * idle_h
    obj_val = {"MinWait": wait_h, "MinIdle": idle_h, "MinComposite": composite}[objective]
    return {
        "algorithm": "Greedy",
        "wait_h": wait_h,
        "idle_h": idle_h,
        "composite": composite,
        "objective_value": obj_val,
        "solve_time_sec": elapsed,
        "optimality_gap": float("nan"),
    }


def run_milp(windows, tug_fleet, required_tugs_map, berth_map, matrix, objective: str) -> dict:
    model = MultiTugSchedulingModel(
        services=windows,
        required_tugs_map=required_tugs_map,
        tug_fleet=tug_fleet,
        travel_matrix=matrix,
        berth_map=berth_map,
        time_limit_sec=30.0,
        day_relative_epoch=0.0,
    )
    result = model.solve()
    wait_h = result.wait_h
    idle_h = _compute_idle_h(result.assignments, windows)
    composite = 0.5 * wait_h + 0.5 * idle_h
    obj_val = {"MinWait": wait_h, "MinIdle": idle_h, "MinComposite": composite}[objective]
    return {
        "algorithm": "MILP",
        "wait_h": wait_h,
        "idle_h": idle_h,
        "composite": composite,
        "objective_value": obj_val,
        "solve_time_sec": result.solve_time_sec,
        "optimality_gap": result.optimality_gap,
    }


def run_alns(windows, tug_fleet, required_tugs_map, objective: str, n_restarts: int = 20) -> dict:
    """ALNS 근사: random restart greedy + best solution selection."""
    t0 = time.time()
    best_assignments = None
    best_obj = float("inf")

    def obj_fn(assignments):
        w = _compute_wait_h(assignments, windows)
        i = _compute_idle_h(assignments, windows)
        return {"MinWait": w, "MinIdle": i, "MinComposite": 0.5 * w + 0.5 * i}[objective]

    # 기본 실행
    base = assign_multi_tug_greedy(windows, tug_fleet, required_tugs_map)
    best_obj = obj_fn(base)
    best_assignments = base

    rng = random.Random(42)
    for _ in range(n_restarts):
        shuffled = list(windows)
        rng.shuffle(shuffled)
        assignments = assign_multi_tug_greedy(shuffled, tug_fleet, required_tugs_map)
        val = obj_fn(assignments)
        if val < best_obj:
            best_obj = val
            best_assignments = assignments

    elapsed = time.time() - t0
    wait_h = _compute_wait_h(best_assignments, windows)
    idle_h = _compute_idle_h(best_assignments, windows)
    composite = 0.5 * wait_h + 0.5 * idle_h
    obj_val = {"MinWait": wait_h, "MinIdle": idle_h, "MinComposite": composite}[objective]
    return {
        "algorithm": "ALNS",
        "wait_h": wait_h,
        "idle_h": idle_h,
        "composite": composite,
        "objective_value": obj_val,
        "solve_time_sec": elapsed,
        "optimality_gap": float("nan"),
    }


def main() -> None:
    loader = HarborDataLoader()
    all_locs = {
        **AIS_SUPPLEMENTARY_LOCATIONS,
        **loader.load_anchorage_locations(),
        **loader.load_berth_locations(),
    }
    tug_names = list(loader.load_tug_mapping().values())
    matrix = TravelTimeMatrix(all_locs, {}, ais_log_dir="data/raw/scheduling/data/AISLog")

    all_reqs = loader.load_requests()
    day_reqs = [r for r in all_reqs if r.scheduled_start.strftime("%Y-%m-%d") == TARGET_DATE]
    print(f"데이터: {TARGET_DATE}, n={len(day_reqs)}건")

    epoch = min(r.scheduled_start.timestamp() / 60.0 for r in day_reqs)

    windows = []
    required_tugs_map = {}
    berth_map = {}
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
            travel_to_site_min=travel,
            anchorage_id=DEFAULT_ANCHORAGE,
        )
        windows.append(w)
        required_tugs_map[vid] = r.required_tugs
        berth_map[vid] = (r.start_berth_code, r.end_berth_code)

    objectives = ["MinWait", "MinIdle", "MinComposite"]
    algorithms = ["Greedy", "MILP", "ALNS"]

    rows = []
    results_grid: dict[tuple, float] = {}

    for obj in objectives:
        for alg in algorithms:
            print(f"  {obj} × {alg}...", end=" ", flush=True)
            try:
                if alg == "Greedy":
                    r = run_greedy(windows, tug_names, required_tugs_map, obj)
                elif alg == "MILP":
                    r = run_milp(windows, tug_names, required_tugs_map, berth_map, matrix, obj)
                else:
                    r = run_alns(windows, tug_names, required_tugs_map, obj)
                print(f"obj={r['objective_value']:.4f} t={r['solve_time_sec']:.2f}s")
            except Exception as e:
                print(f"ERROR: {e}")
                r = {
                    "algorithm": alg,
                    "wait_h": float("nan"),
                    "idle_h": float("nan"),
                    "composite": float("nan"),
                    "objective_value": float("nan"),
                    "solve_time_sec": 0.0,
                    "optimality_gap": float("nan"),
                }
            row = {"objective": obj, "algorithm": alg, "n_jobs": len(day_reqs), **r}
            rows.append(row)
            results_grid[(obj, alg)] = r["objective_value"]

    # CSV 저장
    out_csv = pathlib.Path("results/nm_benchmark_full.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "objective",
        "algorithm",
        "n_jobs",
        "wait_h",
        "idle_h",
        "composite",
        "objective_value",
        "solve_time_sec",
        "optimality_gap",
    ]
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    # 히트맵
    data = np.array(
        [
            [results_grid.get((obj, alg), float("nan")) for alg in algorithms]
            for obj in objectives
        ]
    )
    fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
    im = ax.imshow(data, cmap="YlOrRd", aspect="auto")
    plt.colorbar(im, ax=ax, label="Objective Value")
    ax.set_xticks(range(len(algorithms)))
    ax.set_xticklabels(algorithms)
    ax.set_yticks(range(len(objectives)))
    ax.set_yticklabels(objectives)
    ax.set_title(f"N×M Benchmark: Objective × Algorithm ({TARGET_DATE}, n={len(day_reqs)})")
    for i, _obj in enumerate(objectives):
        for j, _alg in enumerate(algorithms):
            val = data[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.3f}", ha="center", va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig("results/nm_heatmap_full.png", bbox_inches="tight")
    plt.close()

    print(f"\n결과: {out_csv.resolve()}")
    print("히트맵: results/nm_heatmap_full.png")


if __name__ == "__main__":
    main()
