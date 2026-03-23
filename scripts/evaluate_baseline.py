"""
역사적 베이스라인 KPI 평가 — 인간 디스패처 성능 측정.

SchData.csv의 실제 수행 기록(단일 예선, 66건)을 MinWaitObjective로 평가하여
results/baseline_kpi.json에 저장한다.

wait_h 정의 (최적화와 동일 공식):
    wait_h = Σ(priority × max(0, actual_start - initial_schedule) / 60)

여기서:
    actual_start    = 실제 스케줄 시작 시각  (scheduled_start in SchedulingToRoutingSpec)
    initial_schedule = 최초 스케줄 시각      (earliest_start in TimeWindowSpec)

사용법:
    uv run python scripts/evaluate_baseline.py
    uv run python scripts/evaluate_baseline.py --out results/baseline_kpi.json
"""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from libs.data import ExecutedService, HarborDataLoader
from libs.optimization import MinWaitObjective
from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec

logger = logging.getLogger(__name__)

DEFAULT_SLACK_MIN = 65.0


def _priority(tonnage_mt: float) -> int:
    if tonnage_mt < 10_000:
        return 1
    if tonnage_mt < 30_000:
        return 2
    return 3


def main() -> None:
    parser = argparse.ArgumentParser(description="역사적 베이스라인 KPI 평가")
    parser.add_argument("--data-dir", default="data/raw/scheduling/data")
    parser.add_argument("--out", default="results/baseline_kpi.json")
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
    berths = loader.load_berth_locations()
    executed = loader.load_executed()

    # Stage A: 단일 예선만
    single: list[ExecutedService] = [e for e in executed if e.is_single_tug]
    logger.info("단일예선 실행기록: %d건 / 전체: %d건", len(single), len(executed))

    if not single:
        logger.error("평가할 기록 없음")
        sys.exit(1)

    # ── epoch 계산 ──────────────────────────────────────────
    epoch = min(e.actual_start for e in single)
    logger.info("epoch = %s", epoch.isoformat())

    # ── TimeWindowSpec + SchedulingToRoutingSpec 변환 ────────
    windows: list[TimeWindowSpec] = []
    assignments: list[SchedulingToRoutingSpec] = []

    for e in single:
        prio = _priority(e.tonnage_mt)

        # earliest_start = 최초 스케줄 시각 (인간이 처음 계획한 시각)
        earliest = (e.initial_schedule - epoch).total_seconds() / 60.0
        # scheduled_start = 실제 스케줄 시작 시각 (실제로 시작된 시각)
        actual_min = (e.actual_start - epoch).total_seconds() / 60.0

        latest = earliest + max(
            e.travel_to_site_min + e.service_duration_min, DEFAULT_SLACK_MIN
        )

        pickup = berths.get(e.start_berth_code, (0.0, 0.0))
        dropoff = berths.get(e.end_berth_code, (0.0, 0.0))

        tw = TimeWindowSpec(
            vessel_id=f"{e.vessel_name}_{e.row_id}",
            berth_id=e.start_berth_code,
            earliest_start=earliest,
            latest_start=latest,
            service_duration=e.service_duration_min,
            priority=prio,
            travel_to_site_min=e.travel_to_site_min,
            return_to_base_min=0.0,
            anchorage_id=e.from_anchorage,
            pilot_code=e.pilot_code,
            tonnage_mt=e.tonnage_mt,
        )
        spec = SchedulingToRoutingSpec(
            vessel_id=tw.vessel_id,
            tug_id=e.assigned_tug_codes[0],
            pickup_location=pickup,
            dropoff_location=dropoff,
            time_window=tw,
            scheduled_start=actual_min,
            required_tugs=1,
            priority=prio,
        )
        windows.append(tw)
        assignments.append(spec)

    # ── KPI 계산 ─────────────────────────────────────────────
    objective = MinWaitObjective()
    kpi = objective.compute(assignments, windows)

    # 추가 통계 (선택적)
    delays = [
        max(0.0, a.scheduled_start - w.earliest_start)
        for a, w in zip(assignments, windows, strict=True)
    ]
    avg_delay_min = sum(delays) / len(delays) if delays else 0.0
    max_delay_min = max(delays) if delays else 0.0

    # ── 결과 저장 ────────────────────────────────────────────
    result = {
        "n_executed_total": len(executed),
        "n_single_tug": len(single),
        "epoch_utc": epoch.isoformat(),
        "kpi": {
            "wait_h": round(kpi.wait_h, 4),
            "idle_h": round(kpi.idle_h, 4),
            "objective_value": round(kpi.objective_value, 6),
        },
        "stats": {
            "avg_delay_min": round(avg_delay_min, 2),
            "max_delay_min": round(max_delay_min, 2),
        },
        "formula": (
            "wait_h = sum(priority * max(0, actual_start - initial_schedule) / 60)"
        ),
    }

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n=== 베이스라인 KPI (인간 디스패처) ===")
    print(f"단일예선 평가 건수: {len(single)}건")
    print(f"wait_h:   {kpi.wait_h:.4f}h  (priority-weighted)")
    print(f"idle_h:   {kpi.idle_h:.4f}h")
    print(f"평균 지연: {avg_delay_min:.1f}분/건")
    print(f"최대 지연: {max_delay_min:.1f}분")
    print(f"결과 파일: {out_path.resolve()}")


if __name__ == "__main__":
    main()
