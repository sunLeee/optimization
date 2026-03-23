"""
전체 베이스라인 KPI 평가 — SchData 336건 전체 (인간 디스패처 성능).

사용법:
    uv run python scripts/evaluate_full_baseline.py
"""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from libs.data import HarborDataLoader

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="전체 베이스라인 KPI 평가")
    parser.add_argument("--data-dir", default="data/raw/scheduling/data")
    parser.add_argument("--out", default="results/full_baseline_kpi.json")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    loader = HarborDataLoader(args.data_dir)
    executed = loader.load_executed()
    requests = loader.load_requests()

    # n_matched: SchData 선박명이 FristAllSchData에도 존재하는 건수 (Fix 3)
    request_vessels = {r.vessel_name for r in requests}
    n_matched = sum(1 for e in executed if e.vessel_name in request_vessels)
    logger.info("n_matched: %d/%d", n_matched, len(executed))

    # 전체 KPI 계산
    total_wait_min = 0.0
    max_delay_min = 0.0
    delays = []

    for e in executed:
        delay = (e.actual_start - e.initial_schedule).total_seconds() / 60.0
        wait = max(0.0, delay)
        total_wait_min += wait
        delays.append(wait)
        if wait > max_delay_min:
            max_delay_min = wait

    wait_h = total_wait_min / 60.0
    avg_delay_min = total_wait_min / max(len(executed), 1)

    # 기준예선별 KPI
    by_tug: dict[str, dict] = {}
    for e in executed:
        tug = e.base_tug_code
        if tug not in by_tug:
            by_tug[tug] = {"n": 0, "total_wait_min": 0.0}
        by_tug[tug]["n"] += 1
        wait = max(0.0, (e.actual_start - e.initial_schedule).total_seconds() / 60.0)
        by_tug[tug]["total_wait_min"] += wait

    by_tug_out = {
        k: {
            "n": v["n"],
            "avg_delay_min": round(v["total_wait_min"] / max(v["n"], 1), 2),
            "total_wait_min": round(v["total_wait_min"], 2),
        }
        for k, v in sorted(by_tug.items(), key=lambda x: -x[1]["total_wait_min"])
    }

    result = {
        "n_executed": len(executed),
        "n_matched_in_requests": n_matched,
        "population_warning": (
            f"베이스라인({len(executed)}건)과 최적화({len(requests)}건) 모집단 다름. "
            f"교집합: {n_matched}건 (vessel_name 기준)"
        ),
        "kpi": {
            "wait_h": round(wait_h, 4),
            "avg_delay_min": round(avg_delay_min, 2),
            "max_delay_min": round(max_delay_min, 2),
        },
        "by_tug": by_tug_out,
        "formula": "wait_h = sum(max(0, actual_start - initial_schedule)) / 60",
    }

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n=== 전체 베이스라인 KPI (인간 디스패처, 336건) ===")
    print(f"wait_h:         {wait_h:.4f}h")
    print(f"avg_delay_min:  {avg_delay_min:.1f}분/건")
    print(f"max_delay_min:  {max_delay_min:.1f}분")
    print(f"n_matched:      {n_matched}/{len(executed)}건 (FristAllSchData 교집합)")
    print(f"결과 파일:       {out_path.resolve()}")


if __name__ == "__main__":
    main()
