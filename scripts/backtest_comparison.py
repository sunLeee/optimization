"""
올바른 베이스라인 vs 최적화 비교 — 동일 objective 기준.

핵심 원칙:
    베이스라인과 최적화 결과 모두 동일한 objective.compute()를 사용하여
    wait_h = Σ(priority × max(0, scheduled_start - earliest_start) / 60)
    를 계산한다. 이로써 apples-to-apples 비교가 보장된다.

사용법:
    uv run python scripts/backtest_comparison.py
    uv run python scripts/backtest_comparison.py --out results/backtest_comparison.csv
"""
from __future__ import annotations

import argparse
import csv
import logging
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from libs.evaluation import RealDataBacktester
from libs.optimization import MinWaitObjective
from libs.solver import ALNSSolver, BendersSolver, ConvergenceCriteria, MILPSolver
from libs.utils.time_window import TimeWindowSpec

logger = logging.getLogger(__name__)

DEFAULT_CSV = "data/raw/scheduling/data/2024-06_SchData.csv"

BERTH_LOCATIONS: dict[str, tuple[float, float]] = {
    "연안부두정계지": (37.450647, 126.594899),
    "송도정계지": (37.350732, 126.662215),
    "내항정계지": (37.474525, 126.607523),
    "북항임시정계지": (37.496626, 126.624476),
}
DEPOT_LOC: tuple[float, float] = (37.450000, 126.610000)

TIER_CONFIGS = [
    {"name": "MILP-Tier1",    "n": 8,  "solver_cls": MILPSolver,
     "solver_kwargs": {},
     "criteria": ConvergenceCriteria(time_limit_sec=30.0)},
    {"name": "ALNS-Tier2",   "n": 30, "solver_cls": ALNSSolver,
     "solver_kwargs": {},
     "criteria": ConvergenceCriteria(max_iter=200, improvement_threshold=0.001)},
    {"name": "Benders-Tier3","n": 80, "solver_cls": BendersSolver,
     "solver_kwargs": {},
     "criteria": ConvergenceCriteria(time_limit_sec=60.0, max_iter=20,
                                     improvement_threshold=0.005)},
]


def _berth_map(windows: list[TimeWindowSpec]) -> dict[str, tuple[float, float]]:
    return {w.berth_id: BERTH_LOCATIONS.get(w.berth_id, DEPOT_LOC)
            for w in windows if w.berth_id}


def main() -> None:
    parser = argparse.ArgumentParser(description="베이스라인 vs 최적화 공정 비교")
    parser.add_argument("--data", default=DEFAULT_CSV)
    parser.add_argument("--out", default="results/backtest_comparison.csv")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    data_path = pathlib.Path(args.data)
    if not data_path.exists():
        logger.error("데이터 파일 없음: %s", data_path)
        sys.exit(1)

    # 전체 데이터 로드
    backtester = RealDataBacktester(
        csv_path=str(data_path), tug_fleet=[], berth_locations={}
    )
    all_assignments = backtester._assignments
    all_windows = backtester._windows
    tug_ids = sorted({s.tug_id for s in all_assignments})
    tug_fleet = tug_ids[:3] if tug_ids else ["T0", "T1", "T2"]

    logger.info("로드 완료: N=%d assignments, tug_fleet=%s", len(all_assignments), tug_fleet)

    objective = MinWaitObjective()
    rows: list[dict] = []

    print("\n=== 공정 비교: 동일 objective 기준 (wait_h = Σ priority×max(0,start-earliest)/60) ===")
    print(f"{'Solver':<18} {'n':>4} "
          f"{'Historical wait_h':>18} {'Optimized wait_h':>17} "
          f"{'Reduction':>10} {'avg_wait_min(H)':>16} {'avg_wait_min(O)':>16}")
    print("-" * 105)

    for cfg in TIER_CONFIGS:
        n = cfg["n"]
        solver_name = cfg["name"]

        # ── 1. 역사적 베이스라인: 동일 objective 적용 ──────────────────
        hist_assignments = all_assignments[:n]
        hist_windows = all_windows[:n]

        hist_kpi = objective.compute(hist_assignments, hist_windows)
        hist_wait_h = hist_kpi.wait_h
        # 비가중 평균 (사람이 이해하기 쉬운 단위)
        hist_raw_wait_min = sum(
            max(0.0, s.scheduled_start - s.time_window.earliest_start)
            for s in hist_assignments
        ) / max(n, 1)

        # ── 2. 최적화: 솔버 실행 → 동일 objective 적용 ────────────────
        solver = cfg["solver_cls"](**cfg["solver_kwargs"])
        berth_locs = _berth_map(hist_windows)

        try:
            result = solver.solve(
                windows=hist_windows,
                tug_fleet=tug_fleet,
                berth_locations=berth_locs,
                objective=objective,
                criteria=cfg["criteria"],
            )
            opt_assignments = result.assignments
            opt_kpi = objective.compute(opt_assignments, hist_windows)
            opt_wait_h = opt_kpi.wait_h
            opt_gap = result.optimality_gap
            opt_time = result.solve_time_sec
            opt_raw_wait_min = sum(
                max(0.0, s.scheduled_start - s.time_window.earliest_start)
                for s in opt_assignments
            ) / max(len(opt_assignments), 1)
        except Exception as e:
            logger.error("솔버 오류 (%s): %s", solver_name, e)
            opt_wait_h = float("nan")
            opt_kpi = hist_kpi  # fallback
            opt_gap = float("nan")
            opt_time = 0.0
            opt_raw_wait_min = float("nan")

        # ── 3. 개선율 계산 ────────────────────────────────────────────
        if hist_wait_h > 0 and not (opt_wait_h != opt_wait_h):  # not NaN
            reduction_pct = (hist_wait_h - opt_wait_h) / hist_wait_h * 100
        else:
            reduction_pct = 0.0

        print(f"{solver_name:<18} {n:>4} "
              f"{hist_wait_h:>18.4f} {opt_wait_h:>17.4f} "
              f"{reduction_pct:>+9.1f}% {hist_raw_wait_min:>15.1f}m {opt_raw_wait_min:>15.1f}m")

        rows.append({
            "solver": solver_name,
            "n": n,
            "hist_wait_h": round(hist_wait_h, 4),
            "opt_wait_h": round(opt_wait_h, 4) if opt_wait_h == opt_wait_h else "",
            "reduction_pct": round(reduction_pct, 2),
            "hist_raw_wait_min_per_vessel": round(hist_raw_wait_min, 2),
            "opt_raw_wait_min_per_vessel": round(opt_raw_wait_min, 2)
                if opt_raw_wait_min == opt_raw_wait_min else "",
            "hist_idle_h": round(hist_kpi.idle_h, 4),
            "opt_idle_h": round(opt_kpi.idle_h, 4),
            "optimality_gap": round(opt_gap, 6) if opt_gap == opt_gap else "",
            "solve_time_sec": round(opt_time, 4),
        })

    # ── CSV 저장 ──────────────────────────────────────────────────
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n결과 저장: {out_path}")
    print("\n[참고] hist_wait_h와 opt_wait_h 모두 동일 공식 사용:")
    print("  wait_h = Σ(priority × max(0, scheduled_start - earliest_start)) / 60")
    print("  → 역사적 스케줄(실제 배정)과 최적화 스케줄을 동일 기준으로 평가")


if __name__ == "__main__":
    main()
