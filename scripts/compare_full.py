"""
전체 최적화 vs 베이스라인 공정 비교.

results/full_optimization.json (build_full_problem.py 출력)과
results/full_baseline_kpi.json (evaluate_full_baseline.py 출력)을 비교한다.

주의: 베이스라인(336건)과 최적화(967건)는 다른 모집단 — WARNING 출력.

사용법:
    uv run python scripts/compare_full.py
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


def _pct(baseline: float, optimized: float) -> float:
    if baseline == 0.0:
        return math.nan
    return (baseline - optimized) / baseline * 100.0


def main() -> None:
    parser = argparse.ArgumentParser(description="전체 최적화 vs 베이스라인 비교")
    parser.add_argument("--opt-result", default="results/full_optimization.json")
    parser.add_argument("--baseline-result", default="results/full_baseline_kpi.json")
    parser.add_argument("--output", default="results/full_comparison.csv")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # ── 결과 파일 로드 ───────────────────────────────────────
    for path in [args.opt_result, args.baseline_result]:
        if not pathlib.Path(path).exists():
            logger.error("파일 없음: %s", path)
            sys.exit(1)

    with open(args.opt_result, encoding="utf-8") as f:
        opt = json.load(f)
    with open(args.baseline_result, encoding="utf-8") as f:
        bl = json.load(f)

    n_opt = opt.get("total_requests", 0)
    n_bl = bl.get("n_executed", 0)
    n_matched = bl.get("n_matched_in_requests", 0)

    # Population mismatch WARNING (Critic Fix 3)
    if n_opt != n_bl:
        logger.warning(
            "모집단 불일치: 최적화=%d건, 베이스라인=%d건, 교집합=%d건 "
            "(vessel_name 기준). 개선율은 참고치로만 사용.",
            n_opt, n_bl, n_matched,
        )

    opt_kpi = opt.get("total_kpi", {})
    bl_kpi = bl.get("kpi", {})

    # ── 비교 행 구성 ─────────────────────────────────────────
    rows = []

    # wait_h 비교
    bl_wait = bl_kpi.get("wait_h", math.nan)
    opt_wait = opt_kpi.get("wait_h", math.nan)
    wait_pct = _pct(bl_wait, opt_wait)
    rows.append({
        "metric": "wait_h (total)",
        "baseline": round(bl_wait, 4),
        "optimized": round(opt_wait, 4),
        "improvement_pct": round(wait_pct, 2) if not math.isnan(wait_pct) else "NaN",
        "note": "",
    })

    # avg wait_h per vessel
    bl_avg = bl_kpi.get("avg_delay_min", math.nan)
    opt_avg_min = opt_wait * 60 / max(n_opt, 1)
    avg_pct = _pct(bl_avg, opt_avg_min)
    rows.append({
        "metric": "avg_wait_min per vessel",
        "baseline": round(bl_avg, 2),
        "optimized": round(opt_avg_min, 2),
        "improvement_pct": round(avg_pct, 2) if not math.isnan(avg_pct) else "NaN",
        "note": "",
    })

    # 메타 행
    rows.append({
        "metric": "n_requests",
        "baseline": n_bl,
        "optimized": n_opt,
        "improvement_pct": "—",
        "note": f"WARNING: 다른 모집단 (교집합={n_matched}건)" if n_opt != n_bl else "",
    })
    rows.append({
        "metric": "n_matched (vessel_name)",
        "baseline": n_matched,
        "optimized": "—",
        "improvement_pct": "—",
        "note": f"{n_matched}/{n_bl} = {n_matched/max(n_bl,1)*100:.1f}%",
    })
    rows.append({
        "metric": "days_processed",
        "baseline": "—",
        "optimized": opt.get("days_processed", "—"),
        "improvement_pct": "—",
        "note": "",
    })

    # ── CSV 저장 ─────────────────────────────────────────────
    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["metric", "baseline", "optimized", "improvement_pct", "note"]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # ── stdout 출력 ──────────────────────────────────────────
    print("\n=== 전체 최적화 vs 베이스라인 ===")
    if n_opt != n_bl:
        print(f"  ⚠ 모집단 불일치: 베이스라인={n_bl}건, 최적화={n_opt}건, 교집합={n_matched}건")
    print(f"\n{'Metric':<30} {'Baseline':>12} {'Optimized':>12} {'Improvement':>14}")
    print("-" * 72)
    for row in rows[:2]:
        pct = row["improvement_pct"]
        pct_str = f"{pct:+.1f}%" if isinstance(pct, float) else str(pct)
        print(f"{row['metric']:<30} {str(row['baseline']):>12} {str(row['optimized']):>12} {pct_str:>14}")
    print("-" * 72)
    print(f"\n결과 파일: {out_path.resolve()}")


if __name__ == "__main__":
    main()
