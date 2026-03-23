"""
ETA 확률적 Robustness 분석 CLI.

AW-010 Log-normal 분포(mu_log=4.015, sigma_log=1.363)로
MILP/ALNS/Benders 3개 솔버의 배정 결과를 Monte Carlo 평가하고
CVaR95 기반 robustness 순위를 산출한다.

사용법:
    uv run python scripts/run_robustness.py
    uv run python scripts/run_robustness.py --n-mc 200 --seed 0
    uv run python scripts/run_robustness.py --out results/robustness.csv
"""
from __future__ import annotations

import argparse
import logging
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from libs.evaluation import RealDataBacktester
from libs.evaluation.robustness import RobustnessAnalyzer, RobustnessResult
from libs.optimization import MinWaitObjective
from libs.solver import (
    ALNSSolver,
    BendersSolver,
    ConvergenceCriteria,
    MILPSolver,
)
from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec

logger = logging.getLogger(__name__)

DEFAULT_CSV = "data/raw/scheduling/data/2024-06_SchData.csv"

# 정계지 좌표 (인천항, 정계지 위치.csv)
BERTH_LOCATIONS: dict[str, tuple[float, float]] = {
    "연안부두정계지": (37.450647, 126.594899),
    "송도정계지": (37.350732, 126.662215),
    "내항정계지": (37.474525, 126.607523),
    "북항임시정계지": (37.496626, 126.624476),
}
DEPOT_LOC: tuple[float, float] = (37.450000, 126.610000)


def _berth_locs(windows: list[TimeWindowSpec]) -> dict[str, tuple[float, float]]:
    result: dict[str, tuple[float, float]] = {}
    for w in windows:
        bid = w.berth_id
        if bid:
            result[bid] = BERTH_LOCATIONS.get(bid, DEPOT_LOC)
    return result


def _run_solver(
    name: str,
    solver,
    windows: list[TimeWindowSpec],
    tug_fleet: list[str],
    criteria,
) -> tuple[list[SchedulingToRoutingSpec], list[TimeWindowSpec]]:
    """솔버 실행 후 (assignments, windows) 반환."""
    berth_locations = _berth_locs(windows)
    logger.info("  실행: %s (n=%d)...", name, len(windows))
    try:
        result = solver.solve(
            windows=windows,
            tug_fleet=tug_fleet,
            berth_locations=berth_locations,
            objective=MinWaitObjective(),
            criteria=criteria,
        )
        logger.info(
            "  완료: %s → %d건 배정 | gap=%.4f",
            name, len(result.assignments), result.optimality_gap,
        )
        return result.assignments, windows
    except Exception as e:
        logger.error("  오류: %s — %s", name, e)
        return [], windows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ETA 확률적 Robustness 분석: CVaR95 비교"
    )
    parser.add_argument("--data", default=DEFAULT_CSV)
    parser.add_argument("--out", default="results/robustness.csv")
    parser.add_argument("--n-mc", type=int, default=100, dest="n_mc")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--mu-log", type=float, default=4.015, dest="mu_log")
    parser.add_argument("--sigma-log", type=float, default=1.363, dest="sigma_log")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
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

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("=== ETA Robustness 분석 시작 ===")
    logger.info(
        "n_mc=%d, mu_log=%.3f, sigma_log=%.3f, seed=%d",
        args.n_mc, args.mu_log, args.sigma_log, args.seed,
    )

    # ── 실데이터 로드 ──────────────────────────────────────────
    backtester = RealDataBacktester(
        csv_path=str(data_path), tug_fleet=[], berth_locations={}
    )
    all_windows = backtester._windows
    tug_ids = sorted({s.tug_id for s in backtester._assignments})
    tug_fleet = tug_ids[:3] if tug_ids else ["T0", "T1", "T2"]

    logger.info("로드 완료: N=%d, tug_fleet=%s", len(all_windows), tug_fleet)

    # ── Tier별 솔버 + 슬라이스 설정 ──────────────────────────
    solver_cfgs: list[dict] = [
        {
            "name": "MILP-Tier1",
            "solver": MILPSolver(),
            "windows": all_windows[:8],
            "criteria": ConvergenceCriteria(time_limit_sec=30.0),
        },
        {
            "name": "ALNS-Tier2",
            "solver": ALNSSolver(),
            "windows": all_windows[:30],
            "criteria": ConvergenceCriteria(
                max_iter=200, improvement_threshold=0.001
            ),
        },
        {
            "name": "Benders-Tier3",
            "solver": BendersSolver(),
            "windows": all_windows[:80],
            "criteria": ConvergenceCriteria(
                time_limit_sec=60.0, max_iter=20,
                improvement_threshold=0.005,
            ),
        },
    ]

    # ── 솔버 실행 ─────────────────────────────────────────────
    logger.info("── 솔버 실행 ─────────────────────────────────")
    solver_results: dict[str, tuple[list, list]] = {}
    for cfg in solver_cfgs:
        assignments, windows = _run_solver(
            cfg["name"], cfg["solver"],
            cfg["windows"], tug_fleet, cfg["criteria"],
        )
        if assignments:
            solver_results[cfg["name"]] = (assignments, windows)

    if not solver_results:
        logger.error("모든 솔버 실패 — 종료")
        sys.exit(1)

    # ── Robustness 분석 ───────────────────────────────────────
    logger.info("── Monte Carlo Robustness 분석 ───────────────")
    analyzer = RobustnessAnalyzer(
        mu_log=args.mu_log,
        sigma_log=args.sigma_log,
        n_mc=args.n_mc,
        seed=args.seed,
    )
    rob_results: dict[str, RobustnessResult] = analyzer.compare(solver_results)

    # ── 결과 출력 ─────────────────────────────────────────────
    print("\n=== ETA Robustness 분석 결과 ===")
    print(
        f"{'솔버':<20} {'n':>5} {'mean_h':>8} {'std_h':>8} "
        f"{'p50_h':>8} {'p95_h':>8} {'CVaR95_h':>10}"
    )
    print("-" * 72)

    rows: list[dict] = []
    for name, rob in sorted(rob_results.items(), key=lambda x: x[1].cvar95):
        print(
            f"{name:<20} {rob.n_windows:>5} {rob.mean_cost:>8.3f} "
            f"{rob.std_cost:>8.3f} {rob.p50:>8.3f} {rob.p95:>8.3f} "
            f"{rob.cvar95:>10.3f}"
        )
        rows.append({
            "solver": name,
            "n_windows": rob.n_windows,
            "n_mc": rob.n_mc,
            "mean_cost_h": round(rob.mean_cost, 4),
            "std_cost_h": round(rob.std_cost, 4),
            "p50_h": round(rob.p50, 4),
            "p95_h": round(rob.p95, 4),
            "cvar95_h": round(rob.cvar95, 4),
            "worst_h": round(rob.worst_cost, 4),
            "best_h": round(rob.best_cost, 4),
            "mu_log": rob.mu_log,
            "sigma_log": rob.sigma_log,
            "delay_prob": rob.delay_prob,
        })

    # 최적 솔버
    best_name = min(rob_results, key=lambda n: rob_results[n].cvar95)
    best = rob_results[best_name]
    print(f"\n최강 Robustness: {best_name} (CVaR95={best.cvar95:.3f}h)")

    # ── CSV 저장 ──────────────────────────────────────────────
    try:
        import pandas as pd
        df = pd.DataFrame(rows)
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        logger.info("저장 완료: %s", out_path)
        print(f"\n결과 파일: {out_path}")
    except ImportError:
        # pandas 없으면 수동 CSV 작성
        import csv
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        logger.info("저장 완료 (csv): %s", out_path)

    # ── 지연 분포 요약 ────────────────────────────────────────
    n_sample = all_windows[:8]
    sample_delays = analyzer.sample_delays(len(n_sample))
    print(f"\n지연 분포 샘플 (n_mc={args.n_mc}, n_windows={len(n_sample)}):")
    print(f"  중앙값(전체): {float(np.median(sample_delays)):.1f}분")
    print(f"  P95(전체):    {float(np.percentile(sample_delays, 95)):.1f}분")
    print(f"  양수 비율:    {float(np.mean(sample_delays > 0) * 100):.1f}%")


if __name__ == "__main__":
    main()
