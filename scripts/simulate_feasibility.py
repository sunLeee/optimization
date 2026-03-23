"""
실행가능성 검증 시뮬레이션 + 애니메이션 생성.

2024-06-07 스케줄을 실시간으로 시뮬레이션하여 예선과 도선사의
이동이 물리적으로 실현 가능한지 검증하고 GIF 애니메이션을 생성한다.

사용법:
    uv run python scripts/simulate_feasibility.py
"""
from __future__ import annotations

import json
import logging
import pathlib
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from libs.data import HarborDataLoader
from libs.data.loader import AIS_SUPPLEMENTARY_LOCATIONS
from libs.scheduling.multi_tug import assign_multi_tug_greedy
from libs.utils.geo import haversine_nm
from libs.utils.time_window import TimeWindowSpec
from libs.utils.travel_time import TravelTimeMatrix

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

TARGET_DATE = "2024-06-07"
DEFAULT_ANCHORAGE = "연안부두정계지"
PILOT_STATION_POS = (37.463117, 126.596133)
TUG_SPEED_KN = 6.0
PILOT_SPEED_KMH = 20.0
NM_TO_KM = 1.852


def _priority(t: float) -> int:
    return 1 if t < 10_000 else 2 if t < 30_000 else 3


def interp_pos(
    pos1: tuple[float, float], pos2: tuple[float, float], frac: float
) -> tuple[float, float]:
    return (
        pos1[0] + (pos2[0] - pos1[0]) * frac,
        pos1[1] + (pos2[1] - pos1[1]) * frac,
    )


def travel_time_min(
    from_pos: tuple[float, float],
    to_pos: tuple[float, float],
    speed_kmh: float,
) -> float:
    dist_nm = haversine_nm(from_pos, to_pos)
    dist_km = dist_nm * NM_TO_KM
    return dist_km / speed_kmh * 60.0


def main() -> None:
    loader = HarborDataLoader()
    all_locs = {
        **AIS_SUPPLEMENTARY_LOCATIONS,
        **loader.load_anchorage_locations(),
        **loader.load_berth_locations(),
    }
    tug_names = list(loader.load_tug_mapping().values())
    tug_speed_kmh = TUG_SPEED_KN * NM_TO_KM
    real_lookup = loader.build_real_travel_lookup(min_count=2, max_ratio=3.0)
    matrix = TravelTimeMatrix(
        all_locs, {}, ais_log_dir="data/raw/scheduling/data/AISLog",
        real_lookup=real_lookup, route_factor=1.8,
    )

    all_reqs = loader.load_requests()
    day_reqs = [
        r
        for r in all_reqs
        if r.scheduled_start.strftime("%Y-%m-%d") == TARGET_DATE
    ]
    epoch = min(r.scheduled_start.timestamp() / 60.0 for r in day_reqs)

    windows = []
    req_map = {}
    required_tugs_map = {}
    berth_map = {}
    for r in day_reqs:
        earliest = r.scheduled_start.timestamp() / 60.0 - epoch
        svc = matrix.get_time_min(r.start_berth_code, r.end_berth_code)
        travel = matrix.get_time_min(DEFAULT_ANCHORAGE, r.start_berth_code)
        latest = earliest + max(travel + svc, 65.0)
        vid = f"{r.vessel_name}_{r.row_id}"
        w = TimeWindowSpec(
            vessel_id=vid,
            berth_id=r.start_berth_code,
            earliest_start=earliest,
            latest_start=latest,
            service_duration=svc,
            priority=_priority(r.tonnage_mt),
            travel_to_site_min=travel,
        )
        windows.append(w)
        required_tugs_map[vid] = r.required_tugs
        berth_map[vid] = (r.start_berth_code, r.end_berth_code)
        req_map[vid] = r

    # Greedy 배정
    assignments = assign_multi_tug_greedy(windows, tug_names, required_tugs_map)
    win_map = {w.vessel_id: w for w in windows}

    # 시뮬레이션: 예선별 타임라인
    tug_timeline: dict[str, list[dict]] = defaultdict(list)
    for a in assignments:
        w = win_map[a.vessel_id]
        sb, eb = berth_map.get(a.vessel_id, (DEFAULT_ANCHORAGE, DEFAULT_ANCHORAGE))
        sb_pos = all_locs.get(sb, all_locs[DEFAULT_ANCHORAGE])
        eb_pos = all_locs.get(eb, all_locs[DEFAULT_ANCHORAGE])
        for tug in a.tug_ids:
            tug_timeline[tug].append(
                {
                    "vessel_id": a.vessel_id,
                    "start": a.start_time,
                    "end": a.start_time + w.service_duration,
                    "start_berth": sb,
                    "end_berth": eb,
                    "start_pos": sb_pos,
                    "end_pos": eb_pos,
                }
            )

    # 정렬
    for tug in tug_timeline:
        tug_timeline[tug].sort(key=lambda x: x["start"])

    # 실행가능성 검증
    feasibility_results = []
    anchorage_pos = all_locs[DEFAULT_ANCHORAGE]

    for tug, jobs in tug_timeline.items():
        prev_end = -720.0  # 예선은 당일 epoch 12시간 전부터 정계지에서 대기
        prev_pos = anchorage_pos
        for job in jobs:
            travel_t = travel_time_min(prev_pos, job["start_pos"], tug_speed_kmh)
            earliest_arrival = prev_end + travel_t
            feasible = earliest_arrival <= job["start"] + 1.0  # 1분 허용오차
            feasibility_results.append(
                {
                    "tug": tug,
                    "vessel": job["vessel_id"],
                    "scheduled_start": round(job["start"], 2),
                    "earliest_arrival": round(earliest_arrival, 2),
                    "travel_from": str(prev_pos),
                    "travel_to": job["start_berth"],
                    "travel_min": round(travel_t, 1),
                    "gap_min": round(job["start"] - prev_end, 1),
                    "feasible": feasible,
                }
            )
            prev_end = job["end"]
            prev_pos = job["end_pos"]

    n_total = len(feasibility_results)
    n_feasible = sum(1 for r in feasibility_results if r["feasible"])
    overall_feasible = n_feasible == n_total

    result = {
        "date": TARGET_DATE,
        "n_assignments": len(assignments),
        "feasibility": {
            "overall": "FEASIBLE" if overall_feasible else "INFEASIBLE",
            "n_total_checks": n_total,
            "n_feasible": n_feasible,
            "n_infeasible": n_total - n_feasible,
        },
        "details": feasibility_results[:20],  # 처음 20개만
    }

    out_json = pathlib.Path("results/feasibility_report.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n=== 실행가능성 검증 ({TARGET_DATE}) ===")
    print(f"전체 판정: {result['feasibility']['overall']}")
    print(f"총 {n_total}건 중 {n_feasible}건 실행가능, {n_total - n_feasible}건 불가능")

    # 애니메이션 생성
    print("애니메이션 생성 중...")
    min_time = min(a.start_time for a in assignments)
    max_time = max(
        a.start_time + win_map[a.vessel_id].service_duration for a in assignments
    )
    time_frames = np.arange(min_time, max_time + 10, 10)  # 10분 단위

    lats = [pos[0] for pos in all_locs.values()]
    lons = [pos[1] for pos in all_locs.values()]
    lat_min, lat_max = min(lats) - 0.02, max(lats) + 0.02
    lon_min, lon_max = min(lons) - 0.02, max(lons) + 0.02

    colors = plt.cm.tab10(np.linspace(0, 1, min(len(tug_names), 10)))
    tug_color = {tug: colors[i % 10] for i, tug in enumerate(tug_names)}

    fig, ax = plt.subplots(figsize=(12, 10), dpi=80)

    def get_tug_pos(
        tug: str, t: float
    ) -> tuple[float, float] | None:
        jobs = tug_timeline.get(tug, [])
        cur_pos = anchorage_pos
        cur_end = 0.0
        for job in jobs:
            # transit to job start
            if cur_end <= t < job["start"]:
                travel_t = travel_time_min(cur_pos, job["start_pos"], tug_speed_kmh)
                if travel_t > 0:
                    depart = max(cur_end, job["start"] - travel_t)
                    if depart <= t <= job["start"]:
                        frac = (t - depart) / max(travel_t, 0.01)
                        return interp_pos(cur_pos, job["start_pos"], min(1.0, frac))
                return cur_pos
            if job["start"] <= t < job["end"]:
                # during service
                frac = (t - job["start"]) / max(job["end"] - job["start"], 0.01)
                return interp_pos(job["start_pos"], job["end_pos"], min(1.0, frac))
            cur_pos = job["end_pos"]
            cur_end = job["end"]
        if t >= cur_end:
            return cur_pos  # back to last position
        return None

    def animate(frame_idx: int) -> None:
        ax.clear()
        t = time_frames[frame_idx]
        ax.set_xlim(lon_min, lon_max)
        ax.set_ylim(lat_min, lat_max)
        ax.set_title(
            f"Harbor Operations Simulation — t={t:.0f}min ({TARGET_DATE})",
            fontsize=11,
        )
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(alpha=0.2)

        # berths (small dots)
        for pos in all_locs.values():
            ax.scatter(pos[1], pos[0], c="lightgray", s=8, alpha=0.4)

        # anchorage (star)
        anch_pos = all_locs[DEFAULT_ANCHORAGE]
        ax.scatter(
            anch_pos[1],
            anch_pos[0],
            c="blue",
            s=100,
            marker="*",
            zorder=5,
            label="Anchorage",
        )

        # pilot station
        ax.scatter(
            PILOT_STATION_POS[1],
            PILOT_STATION_POS[0],
            c="purple",
            s=100,
            marker="D",
            zorder=5,
            label="Pilot Stn",
        )

        # active vessels
        for a in assignments:
            w = win_map[a.vessel_id]
            if a.start_time <= t < a.start_time + w.service_duration:
                sb, eb = berth_map[a.vessel_id]
                sb_pos = all_locs.get(sb, anchorage_pos)
                eb_pos = all_locs.get(eb, anchorage_pos)
                frac = (t - a.start_time) / max(w.service_duration, 0.01)
                pos = interp_pos(sb_pos, eb_pos, min(1.0, frac))
                ax.scatter(
                    pos[1], pos[0], c="black", s=80, marker="s", zorder=6, alpha=0.8
                )

        # tugs
        for tug in tug_timeline:
            pos = get_tug_pos(tug, t)
            if pos:
                color = tug_color.get(tug, "gray")
                ax.scatter(
                    pos[1], pos[0], c=[color], s=60, marker="o", zorder=7, alpha=0.9
                )
                ax.annotate(tug[:3], (pos[1], pos[0]), fontsize=6, ha="center", va="bottom")

        legend_elements = [
            Line2D(
                [0], [0], marker="*", color="blue", markersize=8,
                label="Anchorage", linestyle="None",
            ),
            Line2D(
                [0], [0], marker="D", color="purple", markersize=6,
                label="Pilot Stn", linestyle="None",
            ),
            Line2D(
                [0], [0], marker="s", color="black", markersize=6,
                label="Vessel (active)", linestyle="None",
            ),
            Line2D(
                [0], [0], marker="o", color="tab:blue", markersize=6,
                label="Tug", linestyle="None",
            ),
        ]
        ax.legend(handles=legend_elements, loc="upper right", fontsize=7)

    n_frames = min(len(time_frames), 24)
    frame_indices = np.linspace(0, len(time_frames) - 1, n_frames, dtype=int)

    ani = animation.FuncAnimation(fig, animate, frames=frame_indices, interval=500)
    gif_path = pathlib.Path("results/operations_animation.gif")
    ani.save(str(gif_path), writer="pillow", fps=2)
    plt.close()
    print(f"애니메이션 저장: {gif_path.resolve()}")
    print(f"보고서: {out_json.resolve()}")


if __name__ == "__main__":
    main()
