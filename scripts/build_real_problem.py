"""
실데이터 기반 최적화 실행 — Stage A (단일 예선 요청).

2024-06_FristAllSchData.csv에서 단일 예선 요청(291건)을 추출하고,
날짜별로 MILP (n≤30) 또는 ALNS (n>30) 솔버를 실행하여
results/real_optimization.json에 결과를 저장한다.

사용법:
    uv run python scripts/build_real_problem.py
    uv run python scripts/build_real_problem.py --max-n 20 --log-level DEBUG
"""
from __future__ import annotations

import argparse
import datetime
import json
import logging
import pathlib
import sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from libs.data import HarborDataLoader, ServiceRequest
from libs.optimization import MinWaitObjective
from libs.solver import ALNSSolver, ConvergenceCriteria, MILPSolver
from libs.utils.time_window import TimeWindowSpec
from libs.utils.travel_time import TravelTimeMatrix

logger = logging.getLogger(__name__)

DEFAULT_ANCHORAGE = "연안부두정계지"
DEFAULT_SLACK_MIN = 65.0   # 최소 time window 폭 (분)


def _priority(tonnage_mt: float) -> int:
    if tonnage_mt < 10_000:
        return 1
    if tonnage_mt < 30_000:
        return 2
    return 3


def _build_windows(
    requests: list[ServiceRequest],
    matrix: TravelTimeMatrix,
    epoch,
) -> list[TimeWindowSpec]:
    windows = []
    for r in requests:
        earliest = (r.scheduled_start - epoch).total_seconds() / 60.0
        svc = matrix.get_time_min(r.start_berth_code, r.end_berth_code)
        travel = matrix.get_time_min(DEFAULT_ANCHORAGE, r.start_berth_code)
        latest = earliest + max(travel + svc, DEFAULT_SLACK_MIN)
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
            pilot_code=r.pilot_code,
            tonnage_mt=r.tonnage_mt,
        ))
    return windows


def main() -> None:
    parser = argparse.ArgumentParser(description="실데이터 기반 최적화 실행")
    parser.add_argument("--data-dir", default="data/raw/scheduling/data")
    parser.add_argument("--output", default="results/real_optimization.json")
    parser.add_argument("--max-n", type=int, default=None, help="단일예선 요청 최대 처리 수")
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

    # ── 데이터 로드 ─────────────────────────────────────────
    loader = HarborDataLoader(args.data_dir)
    all_locs = loader.load_all_locations()   # 선석 111 + 정계지 4 + AIS 보조 13

    ais_dir = str(pathlib.Path(args.data_dir) / "AISLog")
    matrix = TravelTimeMatrix(all_locs, {}, ais_log_dir=ais_dir)

    all_requests = loader.load_requests()
    single = [r for r in all_requests if r.is_single_tug]
    # 미지 berth 코드 필터링
    single_valid = [
        r for r in single
        if r.start_berth_code in all_locs and r.end_berth_code in all_locs
    ]
    skipped_multi = len(all_requests) - len(single)
    skipped_unknown = len(single) - len(single_valid)
    single = single_valid

    if args.max_n is not None:
        single = single[: args.max_n]

    logger.info(
        "단일예선 요청: %d건 (멀티예선 스킵: %d건, 미지선석 스킵: %d건)",
        len(single), skipped_multi, skipped_unknown,
    )

    if not single:
        logger.error("처리할 요청 없음")
        sys.exit(1)

    # ── epoch 계산 ──────────────────────────────────────────
    epoch = min(r.scheduled_start for r in single)
    logger.info("epoch = %s", epoch.isoformat())

    # ── tug fleet ───────────────────────────────────────────
    tug_mapping = loader.load_tug_mapping()
    tug_fleet = list(tug_mapping.values())

    # ── 날짜별 그룹핑 (AW-005) ──────────────────────────────
    by_date: dict[str, list[ServiceRequest]] = defaultdict(list)
    for r in single:
        date_str = r.scheduled_start.astimezone(datetime.UTC).strftime("%Y-%m-%d")
        by_date[date_str].append(r)

    berth_locs: dict[str, tuple[float, float]] = all_locs

    # ── 날짜별 솔버 실행 ─────────────────────────────────────
    by_day_results = []
    total_wait_h = 0.0
    total_idle_h = 0.0
    total_obj = 0.0
    objective = MinWaitObjective()

    for date_str in sorted(by_date.keys()):
        day_reqs = by_date[date_str]
        n = len(day_reqs)
        windows = _build_windows(day_reqs, matrix, epoch)

        # AW-005 Tier 선택
        if n <= 30:
            solver = MILPSolver()
            solver_name = "MILP-Tier1"
            criteria = ConvergenceCriteria(time_limit_sec=30.0)
        else:
            solver = ALNSSolver()
            solver_name = "ALNS-Tier2"
            criteria = ConvergenceCriteria(max_iter=200, improvement_threshold=0.001)

        logger.info("날짜 %s: n=%d → %s", date_str, n, solver_name)

        try:
            result = solver.solve(
                windows=windows,
                tug_fleet=tug_fleet,
                berth_locations=berth_locs,
                objective=objective,
                criteria=criteria,
            )
            kpi = objective.compute(result.assignments, windows)
            day_result = {
                "date": date_str,
                "n": n,
                "solver": solver_name,
                "solve_time_sec": round(result.solve_time_sec, 4),
                "optimality_gap": round(result.optimality_gap, 6),
                "kpi": {
                    "wait_h": round(kpi.wait_h, 4),
                    "idle_h": round(kpi.idle_h, 4),
                    "objective_value": round(kpi.objective_value, 6),
                },
            }
            total_wait_h += kpi.wait_h
            total_idle_h += kpi.idle_h
            total_obj += kpi.objective_value
        except Exception as exc:
            logger.error("솔버 오류 (%s, %s): %s", date_str, solver_name, exc)
            day_result = {
                "date": date_str,
                "n": n,
                "solver": solver_name,
                "error": str(exc)[:200],
            }

        by_day_results.append(day_result)
        logger.info(
            "  완료: wait_h=%.3f idle_h=%.3f",
            day_result.get("kpi", {}).get("wait_h", 0),
            day_result.get("kpi", {}).get("idle_h", 0),
        )

    # ── 결과 저장 ────────────────────────────────────────────
    output = {
        "epoch_utc": epoch.isoformat(),
        "total_requests": len(all_requests),
        "single_tug_requests": len(single),
        "skipped_multi_tug": skipped_multi,
        "skipped_unknown_berth": skipped_unknown,
        "days_processed": len(by_day_results),
        "by_day": by_day_results,
        "total_kpi": {
            "wait_h": round(total_wait_h, 4),
            "idle_h": round(total_idle_h, 4),
            "objective_value": round(total_obj, 6),
        },
    }

    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n=== 최적화 결과 ===")
    print(f"단일예선 요청: {len(single)}건 / 전체: {len(all_requests)}건")
    print(f"처리 날짜: {len(by_day_results)}일")
    print(f"총 wait_h:  {total_wait_h:.4f}h")
    print(f"총 idle_h:  {total_idle_h:.4f}h")
    print(f"결과 파일: {out_path.resolve()}")


if __name__ == "__main__":
    main()
