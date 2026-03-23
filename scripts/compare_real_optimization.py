"""
최적화 vs 베이스라인 공정 비교.

results/real_optimization.json (build_real_problem.py 출력)과
results/baseline_kpi.json (evaluate_baseline.py 출력)을 로드하여
개선율을 계산하고 results/real_comparison.csv에 저장한다.

개선율 공식:
    improvement_pct = (baseline - optimized) / baseline * 100
    (baseline = 0이면 NaN)

사용법:
    uv run python scripts/compare_real_optimization.py
    uv run python scripts/compare_real_optimization.py --opt-result results/real_optimization.json
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


def _improvement_pct(baseline: float, optimized: float) -> float:
    if baseline == 0.0:
        return math.nan
    return (baseline - optimized) / baseline * 100.0


def main() -> None:
    parser = argparse.ArgumentParser(description="최적화 vs 베이스라인 비교")
    parser.add_argument(
        "--opt-result", default="results/real_optimization.json"
    )
    parser.add_argument(
        "--baseline-result", default="results/baseline_kpi.json"
    )
    parser.add_argument("--output", default="results/real_comparison.csv")
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

    # ── 결과 파일 로드 ───────────────────────────────────────
    opt_path = pathlib.Path(args.opt_result)
    baseline_path = pathlib.Path(args.baseline_result)

    if not opt_path.exists():
        logger.error(
            "최적화 결과 없음: %s\n→ 먼저 build_real_problem.py 실행", opt_path
        )
        sys.exit(1)
    if not baseline_path.exists():
        logger.error(
            "베이스라인 결과 없음: %s\n→ 먼저 evaluate_baseline.py 실행",
            baseline_path,
        )
        sys.exit(1)

    with open(opt_path, encoding="utf-8") as f:
        opt = json.load(f)
    with open(baseline_path, encoding="utf-8") as f:
        baseline = json.load(f)

    opt_kpi = opt["total_kpi"]
    bl_kpi = baseline["kpi"]

    # ── 비교 행 구성 ─────────────────────────────────────────
    metrics = [
        ("wait_h", "Priority-weighted wait time (h)"),
        ("idle_h", "Tug idle time (h)"),
        ("objective_value", "Objective value"),
    ]

    rows = []
    for key, label in metrics:
        bl_val = bl_kpi.get(key, math.nan)
        opt_val = opt_kpi.get(key, math.nan)
        pct = _improvement_pct(bl_val, opt_val)
        rows.append(
            {
                "metric": label,
                "baseline": round(bl_val, 4),
                "optimized": round(opt_val, 4),
                "improvement_pct": round(pct, 2)
                if not math.isnan(pct)
                else "NaN",
            }
        )

    # 메타 행
    rows.append(
        {
            "metric": "n_single_tug_baseline",
            "baseline": baseline.get("n_single_tug", "—"),
            "optimized": opt.get("single_tug_requests", "—"),
            "improvement_pct": "—",
        }
    )
    rows.append(
        {
            "metric": "solver_used",
            "baseline": "Human dispatch",
            "optimized": "MILP/ALNS per day",
            "improvement_pct": "—",
        }
    )
    rows.append(
        {
            "metric": "days_processed",
            "baseline": "—",
            "optimized": opt.get("days_processed", "—"),
            "improvement_pct": "—",
        }
    )

    # ── CSV 저장 ─────────────────────────────────────────────
    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["metric", "baseline", "optimized", "improvement_pct"]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # ── stdout 출력 ──────────────────────────────────────────
    print("\n=== 최적화 vs 베이스라인 (동일 objective 기준) ===")
    print(
        f"{'Metric':<40} {'Baseline':>12} {'Optimized':>12} {'Improvement':>14}"
    )
    print("-" * 82)
    for row in rows[:3]:
        pct_str = (
            f"{row['improvement_pct']:+.1f}%"
            if isinstance(row["improvement_pct"], float)
            else str(row["improvement_pct"])
        )
        print(
            f"{row['metric']:<40} {str(row['baseline']):>12}"
            f" {str(row['optimized']):>12} {pct_str:>14}"
        )
    print("-" * 82)
    print(f"\n결과 파일: {out_path.resolve()}")

    # 경고: 개선 없음
    wait_pct = rows[0]["improvement_pct"]
    if isinstance(wait_pct, float) and wait_pct < 0:
        logger.warning(
            "wait_h 개선율이 음수 (%.1f%%) — 모델링 또는 데이터 문제 점검 필요",
            wait_pct,
        )


if __name__ == "__main__":
    main()
