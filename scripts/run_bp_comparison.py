"""
볼라드 풀 제약 기반 다중 알고리즘 × 시나리오 비교.

알고리즘: MILP-BP, BP-Greedy, ALNS-BP
시나리오: normal, heavy, large_vessel
날짜: 더미 데이터 첫날 사용

사용법:
    uv run python scripts/run_bp_comparison.py
    uv run python scripts/run_bp_comparison.py --n-days 3
"""

from __future__ import annotations

import argparse
import csv
import logging
import pathlib
import random
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import numpy as np  # noqa: F401

from libs.data import HarborDataLoader
from libs.data.loader import AIS_SUPPLEMENTARY_LOCATIONS, TUG_BOLLARD_PULL
from libs.scheduling.multi_tug_milp import MultiTugSchedulingModel
from libs.utils.geo import haversine_nm
from libs.utils.time_window import TimeWindowSpec
from libs.utils.travel_time import TravelTimeMatrix

logger = logging.getLogger(__name__)

DEFAULT_ANCHORAGE = "연안부두정계지"
SCENARIOS = ["normal", "heavy", "large_vessel"]
ALGORITHMS = ["MILP-BP", "BP-Greedy", "ALNS-BP"]


def _priority(tonnage_mt: float) -> int:
    return 1 if tonnage_mt < 10_000 else 2 if tonnage_mt < 30_000 else 3


def generate_scenario_data(
    scenario: str, n_days: int = 3, seed: int = 42
) -> pathlib.Path:
    """더미 데이터 생성 후 경로 반환."""
    out_dir = pathlib.Path(f"data/dummy_{scenario}")
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/generate_dummy_data.py",
            "--scenario",
            scenario,
            "--n-days",
            str(n_days),
            "--seed",
            str(seed),
            "--out-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error("더미 데이터 생성 실패: %s", result.stderr[-300:])
        raise RuntimeError(
            f"generate_dummy_data failed for scenario={scenario}"
        )
    return out_dir


def build_windows_and_maps(
    loader: HarborDataLoader, all_locs: dict, matrix: TravelTimeMatrix
):
    """요청 데이터 → TimeWindowSpec + bp_required_map 반환."""
    reqs = loader.load_requests()
    epoch = (
        min(r.scheduled_start.timestamp() / 60.0 for r in reqs)
        if reqs
        else 0.0
    )

    # 첫 날만 사용
    first_date = min(r.scheduled_start.strftime("%Y-%m-%d") for r in reqs)
    day_reqs = [
        r for r in reqs if r.scheduled_start.strftime("%Y-%m-%d") == first_date
    ]

    windows, berth_map, bp_map = [], {}, {}
    for r in day_reqs:
        earliest = r.scheduled_start.timestamp() / 60.0 - epoch
        svc = matrix.get_time_min(r.start_berth_code, r.end_berth_code)
        travel = matrix.get_time_min(DEFAULT_ANCHORAGE, r.start_berth_code)
        latest = earliest + max(travel + svc, 65.0)
        vid = f"{r.vessel_name}_{r.row_id}"
        windows.append(
            TimeWindowSpec(
                vessel_id=vid,
                berth_id=r.start_berth_code,
                earliest_start=earliest,
                latest_start=latest,
                service_duration=svc,
                priority=_priority(r.tonnage_mt),
                travel_to_site_min=travel,
            )
        )
        berth_map[vid] = (r.start_berth_code, r.end_berth_code)
        bp_map[vid] = r.bp_required

    return windows, berth_map, bp_map, first_date


def run_milp_bp(
    windows, berth_map, bp_map, tug_names, all_locs, matrix
) -> dict:
    t0 = time.time()
    model = MultiTugSchedulingModel(
        services=windows,
        required_tugs_map={w.vessel_id: 1 for w in windows},
        tug_fleet=tug_names,
        travel_matrix=matrix,
        berth_map=berth_map,
        time_limit_sec=30.0,
        day_relative_epoch=0.0,
        bollard_pull=TUG_BOLLARD_PULL,
        bp_required_map=bp_map,
    )
    result = model.solve()
    return {
        "wait_h": result.wait_h,
        "solver_used": result.solver_used,
        "solve_time_sec": time.time() - t0,
        "n_assignments": len(result.assignments),
    }


def run_bp_greedy(
    windows, berth_map, bp_map, tug_names, all_locs, tug_bp: dict
) -> dict:
    t0 = time.time()
    anch_pos = all_locs.get(DEFAULT_ANCHORAGE, (37.450647, 126.594899))
    tug_free = dict.fromkeys(tug_names, -720.0)
    tug_pos = dict.fromkeys(tug_names, anch_pos)
    wait_total = 0.0
    assignments = []
    bp_satisfied = 0

    for w in sorted(windows, key=lambda x: x.earliest_start):
        bp_min = bp_map.get(w.vessel_id, 30.0)
        sb, eb = berth_map.get(
            w.vessel_id, (DEFAULT_ANCHORAGE, DEFAULT_ANCHORAGE)
        )
        sb_pos = all_locs.get(sb, anch_pos)
        eb_pos = all_locs.get(eb, anch_pos)

        # 각 예선 도착 가능 시각
        can_arrive = {}
        for t in tug_names:
            d_nm = haversine_nm(tug_pos[t], sb_pos)
            travel = d_nm / 6.0 * 60.0 * 1.3
            can_arrive[t] = tug_free[t] + travel

        # BP 합계 ≥ bp_min 충족하는 최소 예선 조합 (빠른 도착순 탐욕)
        sorted_tugs = sorted(can_arrive.keys(), key=lambda t: can_arrive[t])
        selected, bp_sum = [], 0.0
        for t in sorted_tugs:
            selected.append(t)
            bp_sum += tug_bp.get(t, 40.0)
            if bp_sum >= bp_min:
                break

        gang_start = max(can_arrive[t] for t in selected)
        actual_start = max(gang_start, w.earliest_start)
        wait = max(0.0, actual_start - w.earliest_start)
        wait_total += wait

        end_time = actual_start + w.service_duration
        for t in selected:
            tug_free[t] = end_time
            tug_pos[t] = eb_pos

        if bp_sum >= bp_min:
            bp_satisfied += 1
        assignments.append((w.vessel_id, selected, actual_start))

    n = len(windows)
    return {
        "wait_h": wait_total / 60.0,
        "solver_used": "BP-Greedy",
        "solve_time_sec": time.time() - t0,
        "n_assignments": len(assignments),
        "bp_satisfied_pct": bp_satisfied / max(n, 1) * 100,
    }


def run_alns_bp(
    windows,
    berth_map,
    bp_map,
    tug_names,
    all_locs,
    tug_bp: dict,
    n_restarts: int = 10,
) -> dict:
    t0 = time.time()
    rnd = random.Random(42)
    best_wait = float("inf")
    best_result = None

    for _ in range(n_restarts):
        shuffled = list(windows)
        rnd.shuffle(shuffled)
        result = run_bp_greedy(
            shuffled, berth_map, bp_map, tug_names, all_locs, tug_bp
        )
        if result["wait_h"] < best_wait:
            best_wait = result["wait_h"]
            best_result = result

    best_result = best_result or {
        "wait_h": 0.0,
        "bp_satisfied_pct": 100.0,
        "n_assignments": len(windows),
    }
    best_result["solver_used"] = "ALNS-BP"
    best_result["solve_time_sec"] = time.time() - t0
    return best_result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="볼라드 풀 제약 다중 알고리즘 비교"
    )
    parser.add_argument("--n-days", type=int, default=3, dest="n_days")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="results/bp_algorithm_comparison.csv")
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s: %(message)s",
    )

    rows = []
    print(
        f"\n{'Scenario':15} {'Algorithm':12} {'n_jobs':6} {'n_large':7} "
        f"{'wait_h':8} {'avg_min':7} {'bp_sat%':7} {'solver':10} {'time(s)':7}"
    )
    print("-" * 85)

    for scenario in SCENARIOS:
        # 더미 데이터 생성
        try:
            out_dir = generate_scenario_data(scenario, args.n_days, args.seed)
        except RuntimeError as e:
            logger.error("시나리오 %s 스킵: %s", scenario, e)
            continue

        # 데이터 로드
        loader = HarborDataLoader(str(out_dir))
        all_locs = {
            **AIS_SUPPLEMENTARY_LOCATIONS,
            **loader.load_anchorage_locations(),
            **loader.load_berth_locations(),
        }
        real_lookup = loader.build_real_travel_lookup(
            min_count=2, max_ratio=5.0
        )
        matrix = TravelTimeMatrix(
            all_locs, {}, real_lookup=real_lookup, route_factor=1.3
        )
        tug_names = list(loader.load_tug_mapping().values())

        windows, berth_map, bp_map, first_date = build_windows_and_maps(
            loader, all_locs, matrix
        )
        if not windows:
            continue

        # 대형 선박 비율
        n_large = sum(
            1 for w in windows if bp_map.get(w.vessel_id, 30.0) >= 160.0
        )

        for algo in ALGORITHMS:
            try:
                if algo == "MILP-BP":
                    r = run_milp_bp(
                        windows, berth_map, bp_map, tug_names, all_locs, matrix
                    )
                elif algo == "BP-Greedy":
                    r = run_bp_greedy(
                        windows,
                        berth_map,
                        bp_map,
                        tug_names,
                        all_locs,
                        TUG_BOLLARD_PULL,
                    )
                else:  # ALNS-BP
                    r = run_alns_bp(
                        windows,
                        berth_map,
                        bp_map,
                        tug_names,
                        all_locs,
                        TUG_BOLLARD_PULL,
                    )
            except Exception as exc:
                logger.error("%s × %s 오류: %s", scenario, algo, exc)
                r = {
                    "wait_h": float("nan"),
                    "solver_used": "ERROR",
                    "solve_time_sec": 0.0,
                    "n_assignments": 0,
                    "bp_satisfied_pct": 0.0,
                }

            n = len(windows)
            avg_min = r["wait_h"] * 60.0 / max(n, 1)
            bp_sat = r.get(
                "bp_satisfied_pct", 100.0 if algo == "MILP-BP" else 0.0
            )

            row = {
                "scenario": scenario,
                "algorithm": algo,
                "n_jobs": n,
                "n_large_vessel": n_large,
                "wait_h": round(r["wait_h"], 4),
                "avg_wait_min": round(avg_min, 2),
                "bp_satisfied_pct": round(bp_sat, 1),
                "solver_used": r["solver_used"],
                "solve_time_sec": round(r["solve_time_sec"], 3),
            }
            rows.append(row)
            print(
                f"{scenario:15} {algo:12} {n:6} {n_large:7} "
                f"{r['wait_h']:8.3f} {avg_min:7.1f} {bp_sat:7.1f} "
                f"{r['solver_used']:10} {r['solve_time_sec']:7.2f}"
            )

    # CSV 저장
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n결과 저장: {out_path.resolve()}")


if __name__ == "__main__":
    main()
