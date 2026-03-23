"""
전체 967건 Multi-Resource Gang Scheduling 최적화.

FristAllSchData.csv의 모든 선박 서비스 요청을 날짜별로 그룹핑하여
MultiTugSchedulingModel(MILP + greedy fallback)로 최적 예선 배정을 수행한다.

사용법:
    uv run python scripts/build_full_problem.py
    uv run python scripts/build_full_problem.py --max-days 3 --log-level DEBUG
"""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from libs.data import HarborDataLoader
from libs.data.loader import AIS_SUPPLEMENTARY_LOCATIONS
from libs.scheduling.multi_tug_milp import MultiTugSchedulingModel
from libs.utils.time_window import TimeWindowSpec
from libs.utils.travel_time import TravelTimeMatrix

logger = logging.getLogger(__name__)

DEFAULT_ANCHORAGE = "연안부두정계지"


def _priority(tonnage_mt: float) -> int:
    if tonnage_mt < 10_000:
        return 1
    if tonnage_mt < 30_000:
        return 2
    return 3


def _build_epoch_windows(day_reqs, epoch_offset: float, matrix: TravelTimeMatrix, all_locs: dict):
    """ServiceRequest 목록 → TimeWindowSpec 목록 (day-relative 기준)."""
    windows = []
    for r in day_reqs:
        earliest = (r.scheduled_start.timestamp() / 60.0) - epoch_offset
        # 서비스 시간: 출발선석 → 도착선석 이동시간
        svc = matrix.get_time_min(r.start_berth_code, r.end_berth_code)
        travel = matrix.get_time_min(DEFAULT_ANCHORAGE, r.start_berth_code)
        latest = earliest + max(travel + svc, 65.0)
        windows.append(TimeWindowSpec(
            vessel_id=f"{r.vessel_name}_{r.row_id}",
            berth_id=r.start_berth_code,
            earliest_start=earliest,
            latest_start=latest,
            service_duration=svc,
            priority=_priority(r.tonnage_mt),
            travel_to_site_min=travel,
            return_to_base_min=matrix.get_time_min(r.end_berth_code, DEFAULT_ANCHORAGE),
            anchorage_id=DEFAULT_ANCHORAGE,
        ))
    return windows


def main() -> None:
    parser = argparse.ArgumentParser(description="전체 967건 Multi-Resource 최적화")
    parser.add_argument("--data-dir", default="data/raw/scheduling/data")
    parser.add_argument("--output", default="results/full_optimization.json")
    parser.add_argument("--max-days", type=int, default=None, help="처리할 최대 날짜 수")
    parser.add_argument("--time-limit", type=float, default=60.0, help="MILP 시간 제한(초)")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # ── 데이터 로드 ──────────────────────────────────────────
    loader = HarborDataLoader(args.data_dir)
    berths = loader.load_berth_locations()
    anchorages = loader.load_anchorage_locations()
    all_locs: dict[str, tuple[float, float]] = {
        **AIS_SUPPLEMENTARY_LOCATIONS,
        **anchorages,
        **berths,
    }
    tug_names = list(loader.load_tug_mapping().values())
    ais_dir = str(pathlib.Path(args.data_dir) / "AISLog")
    real_lookup = loader.build_real_travel_lookup(min_count=2, max_ratio=3.0)
    matrix = TravelTimeMatrix(
        all_locs, {}, ais_log_dir=ais_dir,
        real_lookup=real_lookup, route_factor=1.8,
    )

    all_requests = loader.load_requests()
    logger.info("전체 요청: %d건, 예선: %d척", len(all_requests), len(tug_names))

    # ── 날짜별 그룹핑 ────────────────────────────────────────
    by_date: dict[str, list] = defaultdict(list)
    for r in all_requests:
        date_str = r.scheduled_start.strftime("%Y-%m-%d")
        by_date[date_str].append(r)

    dates = sorted(by_date.keys())
    if args.max_days is not None:
        dates = dates[: args.max_days]

    # ── 날짜별 최적화 ────────────────────────────────────────
    by_day_results = []
    total_wait_h = 0.0
    total_obj = 0.0

    for date_str in dates:
        day_reqs = by_date[date_str]

        # day-relative epoch (UTC 분 기준)
        epoch_offset = min(r.scheduled_start.timestamp() / 60.0 for r in day_reqs)

        windows = _build_epoch_windows(day_reqs, epoch_offset, matrix, all_locs)

        required_tugs_map = {
            f"{r.vessel_name}_{r.row_id}": r.required_tugs
            for r in day_reqs
        }
        berth_map = {
            f"{r.vessel_name}_{r.row_id}": (r.start_berth_code, r.end_berth_code)
            for r in day_reqs
        }

        avg_r = sum(required_tugs_map.values()) / max(len(required_tugs_map), 1)
        logger.info(
            "날짜 %s: n=%d, avg_r=%.2f, total_slots=%d",
            date_str, len(day_reqs), avg_r, sum(required_tugs_map.values()),
        )

        model = MultiTugSchedulingModel(
            services=windows,
            required_tugs_map=required_tugs_map,
            tug_fleet=tug_names,
            travel_matrix=matrix,
            berth_map=berth_map,
            time_limit_sec=args.time_limit,
            day_relative_epoch=epoch_offset,
        )

        try:
            result = model.solve()
            day_result = {
                "date": date_str,
                "n_jobs": len(day_reqs),
                "avg_required_tugs": round(avg_r, 2),
                "total_tug_slots": sum(required_tugs_map.values()),
                "solver": result.solver_used,
                "optimality_gap": (
                    round(result.optimality_gap, 6)
                    if result.optimality_gap == result.optimality_gap  # not NaN
                    else None
                ),
                "solve_time_sec": round(result.solve_time_sec, 3),
                "kpi": {
                    "wait_h": round(result.wait_h, 4),
                    "objective_value": round(result.objective_value, 4),
                },
            }
            total_wait_h += result.wait_h
            total_obj += result.objective_value
        except Exception as exc:
            logger.error("날짜 %s 오류: %s", date_str, exc)
            day_result = {
                "date": date_str,
                "n_jobs": len(day_reqs),
                "error": str(exc)[:200],
            }

        by_day_results.append(day_result)
        logger.info(
            "  → %s wait_h=%.3f time=%.2fs",
            day_result.get("solver", "ERROR"),
            day_result.get("kpi", {}).get("wait_h", 0),
            day_result.get("solve_time_sec", 0),
        )

    # ── 결과 저장 ────────────────────────────────────────────
    output = {
        "total_requests": len(all_requests),
        "days_processed": len(by_day_results),
        "total_tug_slots": sum(
            d.get("total_tug_slots", 0) for d in by_day_results
        ),
        "by_day": by_day_results,
        "total_kpi": {
            "wait_h": round(total_wait_h, 4),
            "objective_value": round(total_obj, 4),
        },
        "note": "AW-005: n_jobs > 50이면 Greedy fallback 사용",
    }

    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n=== 전체 최적화 완료 ===")
    print(f"전체 요청: {len(all_requests)}건")
    print(f"처리 날짜: {len(by_day_results)}일")
    print(f"총 wait_h: {total_wait_h:.4f}h")
    print(f"결과 파일: {out_path.resolve()}")


if __name__ == "__main__":
    main()
