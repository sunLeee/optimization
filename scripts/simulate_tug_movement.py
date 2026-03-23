"""
예선 이동 시뮬레이션 — 물리적 타당성 검증.

MILP 최적 배정을 기반으로 각 예선의 실제 이동 경로를 추적하여
'수학적 wait_h=0'이 실제 이동 제약 하에서도 성립하는지 검증한다.

시뮬레이션 로직:
    1. 각 예선은 하루 시작 시 '연안부두정계지'에 위치
    2. 배정된 순서대로 이동:
       이전 작업 종료지 → [이동] → 다음 작업 시작지
    3. 도착 가능 시각 = max(이전 작업 완료, 현재 위치 출발 가능 시각) + 이동시간
    4. 실제 대기 = max(0, tug_arrival - vessel_earliest_start)

사용법:
    uv run python scripts/simulate_tug_movement.py
    uv run python scripts/simulate_tug_movement.py --date 2024-06-11
"""
from __future__ import annotations

import argparse
import logging
import pathlib
import sys
from dataclasses import dataclass
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from libs.data import HarborDataLoader
from libs.optimization import MinWaitObjective
from libs.solver import MILPSolver, ALNSSolver, ConvergenceCriteria
from libs.utils.time_window import TimeWindowSpec, SchedulingToRoutingSpec
from libs.utils.travel_time import TravelTimeMatrix

logger = logging.getLogger(__name__)

DEFAULT_ANCHORAGE = "연안부두정계지"


@dataclass
class SimJob:
    vessel_id: str
    tug_id: str
    start_berth: str
    end_berth: str
    earliest_start: float    # 선박이 원하는 최초 시작 (분, epoch 기준)
    latest_start: float
    service_duration: float
    scheduled_start: float   # MILP 결정 시작 시각
    travel_to_site: float    # 정계지 → 작업 시작지 (참고용)


def _priority(tonnage_mt: float) -> int:
    if tonnage_mt < 10_000:
        return 1
    if tonnage_mt < 30_000:
        return 2
    return 3


def simulate_day(
    jobs: list[SimJob],
    matrix: TravelTimeMatrix,
    anchorage: str = DEFAULT_ANCHORAGE,
) -> list[dict]:
    """예선별 순차 이동 시뮬레이션.

    Args:
        jobs: 하루의 배정 목록 (MILP 결과)
        matrix: 이동시간 행렬
        anchorage: 예선 출발/귀환 정계지

    Returns:
        각 배정의 시뮬레이션 결과 딕셔너리 목록.
    """
    # 예선별 jobs 그룹핑 후 scheduled_start 순 정렬
    by_tug: dict[str, list[SimJob]] = defaultdict(list)
    for j in jobs:
        by_tug[j.tug_id].append(j)
    for tug_jobs in by_tug.values():
        tug_jobs.sort(key=lambda x: x.scheduled_start)

    results = []

    for tug_id, tug_jobs in sorted(by_tug.items()):
        # 예선 초기 상태: 정계지 위치, 준비 시각 = 0
        cur_loc = anchorage
        cur_free_at = 0.0   # 예선이 다음 이동 가능한 시각 (분, epoch 기준)

        for job in tug_jobs:
            # 이동 시간: 현재 위치 → 작업 시작지
            travel = matrix.get_time_min(cur_loc, job.start_berth)

            # 예선 도착 가능 시각 = 자유로워진 시각 + 이동시간
            tug_arrival = cur_free_at + travel

            # 실제 서비스 시작 = max(예선 도착, 선박 earliest_start)
            actual_start = max(tug_arrival, job.earliest_start)

            # 대기 = 선박 관점: 예선이 latest_start 이후 도착하면 과도 대기
            # wait = 선박이 original 요청 시각보다 얼마나 늦게 시작하는가
            vessel_wait = max(0.0, actual_start - job.earliest_start)

            # 예선 대기: 예선이 선박보다 먼저 도착해서 기다리는 시간
            tug_wait = max(0.0, job.earliest_start - tug_arrival)

            # 서비스 종료 시각
            service_end = actual_start + job.service_duration

            # MILP scheduled_start와 실제 actual_start 비교
            milp_vs_sim = actual_start - job.scheduled_start

            feasible = actual_start <= job.latest_start

            results.append({
                "tug_id": tug_id,
                "vessel_id": job.vessel_id,
                "start_berth": job.start_berth,
                "end_berth": job.end_berth,
                "from_loc": cur_loc,
                "travel_min": round(travel, 1),
                "tug_arrival": round(tug_arrival, 1),
                "earliest_start": round(job.earliest_start, 1),
                "actual_start_sim": round(actual_start, 1),
                "milp_scheduled": round(job.scheduled_start, 1),
                "vessel_wait_min": round(vessel_wait, 1),
                "tug_wait_min": round(tug_wait, 1),
                "service_end": round(service_end, 1),
                "feasible": feasible,
                "milp_vs_sim_diff": round(milp_vs_sim, 1),
            })

            # 예선 상태 업데이트
            cur_loc = job.end_berth
            cur_free_at = service_end

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="예선 이동 시뮬레이션")
    parser.add_argument("--data-dir", default="data/raw/scheduling/data")
    parser.add_argument("--date", default=None, help="특정 날짜 (YYYY-MM-DD), 없으면 최대 부하일")
    parser.add_argument("--log-level", default="WARNING",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # ── 데이터 로드 ────────────────────────────────────────
    loader = HarborDataLoader(args.data_dir)
    all_locs = loader.load_all_locations()
    ais_dir = str(pathlib.Path(args.data_dir) / "AISLog")
    matrix = TravelTimeMatrix(all_locs, {}, ais_log_dir=ais_dir)
    tug_names = list(loader.load_tug_mapping().values())

    all_reqs = [
        r for r in loader.load_requests()
        if r.is_single_tug
        and r.start_berth_code in all_locs
        and r.end_berth_code in all_locs
    ]

    epoch = min(r.scheduled_start for r in all_reqs)

    # 날짜별 그룹
    from collections import defaultdict as dd2
    by_date: dict[str, list] = dd2(list)
    for r in all_reqs:
        by_date[r.scheduled_start.strftime("%Y-%m-%d")].append(r)

    # 특정 날짜 또는 최대 부하 날짜 선택
    if args.date:
        target_date = args.date
    else:
        target_date = max(by_date, key=lambda d: len(by_date[d]))

    day_reqs = by_date[target_date]
    print(f"\n=== 시뮬레이션 날짜: {target_date} (n={len(day_reqs)}건, 예선 {len(tug_names)}척) ===\n")

    # ── MILP 실행 ──────────────────────────────────────────
    def mk_window(r):
        earliest = (r.scheduled_start - epoch).total_seconds() / 60.0
        svc = matrix.get_time_min(r.start_berth_code, r.end_berth_code)
        travel = matrix.get_time_min(DEFAULT_ANCHORAGE, r.start_berth_code)
        latest = earliest + max(travel + svc, 65.0)
        pri = _priority(r.tonnage_mt)
        return TimeWindowSpec(
            vessel_id=f"{r.vessel_name}_{r.row_id}",
            berth_id=r.start_berth_code,
            earliest_start=earliest,
            latest_start=latest,
            service_duration=svc,
            priority=pri,
            travel_to_site_min=travel,
            return_to_base_min=matrix.get_time_min(r.end_berth_code, DEFAULT_ANCHORAGE),
            anchorage_id=DEFAULT_ANCHORAGE,
        )

    windows = [mk_window(r) for r in day_reqs]
    req_map = {f"{r.vessel_name}_{r.row_id}": r for r in day_reqs}
    win_map = {w.vessel_id: w for w in windows}

    n = len(windows)
    if n <= 30:
        solver = MILPSolver()
        criteria = ConvergenceCriteria(time_limit_sec=30.0)
    else:
        solver = ALNSSolver()
        criteria = ConvergenceCriteria(max_iter=200, improvement_threshold=0.001)

    result = solver.solve(
        windows=windows, tug_fleet=tug_names, berth_locations=all_locs,
        objective=MinWaitObjective(), criteria=criteria,
    )

    # ── SimJob 구성 ────────────────────────────────────────
    sim_jobs = []
    for a in result.assignments:
        w = win_map[a.vessel_id]
        r = req_map[a.vessel_id]
        sim_jobs.append(SimJob(
            vessel_id=a.vessel_id,
            tug_id=a.tug_id,
            start_berth=r.start_berth_code,
            end_berth=r.end_berth_code,
            earliest_start=w.earliest_start,
            latest_start=w.latest_start,
            service_duration=w.service_duration,
            scheduled_start=a.scheduled_start,
            travel_to_site=w.travel_to_site_min,
        ))

    # ── 시뮬레이션 실행 ────────────────────────────────────
    sim_results = simulate_day(sim_jobs, matrix)

    # ── 결과 출력 ──────────────────────────────────────────
    total_vessel_wait = 0.0
    infeasible_count = 0

    print(f"{'예선':10} {'선박':22} {'이전위치':8} {'이동':5} {'예선도착':8} {'earliest':8} {'실제시작':8} {'선박대기':6} {'예선대기':6} {'가능':4} {'MILP차이':6}")
    print("-" * 110)

    for r in sorted(sim_results, key=lambda x: x["actual_start_sim"]):
        total_vessel_wait += r["vessel_wait_min"]
        if not r["feasible"]:
            infeasible_count += 1
        flag = "" if r["feasible"] else "❌"
        milp_diff = f"{r['milp_vs_sim_diff']:+.1f}"
        print(
            f"{r['tug_id']:10} {r['vessel_id'][:22]:22} "
            f"{r['from_loc'][:8]:8} {r['travel_min']:5.1f} "
            f"{r['tug_arrival']:8.1f} {r['earliest_start']:8.1f} "
            f"{r['actual_start_sim']:8.1f} {r['vessel_wait_min']:6.1f} "
            f"{r['tug_wait_min']:6.1f} {flag+'O':4} {milp_diff:6}"
        )

    print("-" * 110)
    print(f"\n=== 시뮬레이션 요약 ===")
    print(f"총 배정 건수:  {len(sim_results)}건")
    print(f"선박 총 대기:  {total_vessel_wait:.1f}분  ({total_vessel_wait/60:.3f}h)")
    print(f"불가능 배정:   {infeasible_count}건")
    print(f"평균 선박대기: {total_vessel_wait/len(sim_results):.1f}분/건")

    print(f"\n[해석]")
    print(f"  선박 대기 = 선박의 earliest_start 이후 실제로 서비스가 시작되기까지 대기")
    print(f"  예선 대기 = 예선이 earliest_start 전에 도착해서 선박을 기다리는 시간")
    print(f"  MILP 차이 = 시뮬레이션 actual_start - MILP scheduled_start (음수=예선 늦게 도착)")

    if infeasible_count == 0 and total_vessel_wait == 0:
        print(f"\n  결론: 실제 이동 제약 하에서도 wait=0 유지 가능")
        print(f"  이유: 예선 대기 시간(tug_wait)이 발생 — 예선이 선박보다 먼저 도착해서 대기")
    elif total_vessel_wait > 0:
        print(f"\n  결론: 실제 이동 제약 하에서 선박 대기 발생 ({total_vessel_wait:.1f}분)")
        print(f"  원인: 예선 이동시간이 배정 간 여유보다 큼")


if __name__ == "__main__":
    main()
