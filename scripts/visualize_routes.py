"""
OSM 경로 시각화 CLI — Folium HTML + MP4 애니메이션 생성.

실데이터(2024-06_SchData.csv, N=336)를 로드 후 MILP 솔버(n=8)로
배정 결과를 생성하고 시각화한다.

사용법:
    uv run python scripts/visualize_routes.py
    uv run python scripts/visualize_routes.py --n 8 --out results/
    uv run python scripts/visualize_routes.py --no-animation
"""
from __future__ import annotations

import argparse
import logging
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from libs.evaluation import RealDataBacktester
from libs.optimization import MinWaitObjective
from libs.solver import ConvergenceCriteria, MILPSolver
from libs.visualization.animation import animate_routes
from libs.visualization.route_map import (
    DEFAULT_BERTH_LOCATIONS,
    HarborRouteMap,
)

logger = logging.getLogger(__name__)

# 정계지 실좌표 (정계지 위치.csv — 인천항)
BERTH_LOCATIONS: dict[str, tuple[float, float]] = DEFAULT_BERTH_LOCATIONS

# Depot: 인천항 중심 근사치
DEPOT_LOCATION: tuple[float, float] = (37.450000, 126.610000)

# 기본 데이터 경로
DEFAULT_CSV = "data/raw/scheduling/data/2024-06_SchData.csv"


def _build_berth_locations_from_spec(assignments: list) -> dict[str, tuple[float, float]]:
    """배정 결과에 등장하는 berth_id를 BERTH_LOCATIONS에서 매핑."""
    result: dict[str, tuple[float, float]] = {}
    for spec in assignments:
        pickup = getattr(spec, "pickup_location", None)
        if pickup and len(pickup) == 2:
            tw = getattr(spec, "time_window", None)
            berth_id = getattr(tw, "berth_id", "") if tw else ""
            if berth_id:
                result[berth_id] = (float(pickup[0]), float(pickup[1]))
    return result or BERTH_LOCATIONS


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OSM 경로 시각화: Folium HTML + MP4 애니메이션"
    )
    parser.add_argument(
        "--data",
        default=DEFAULT_CSV,
        help=f"입력 CSV 경로 (default: {DEFAULT_CSV})",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=8,
        help="슬라이스할 시간창 수 — MILP Tier 1 (default: 8)",
    )
    parser.add_argument(
        "--out",
        default="results",
        help="출력 디렉토리 (default: results)",
    )
    parser.add_argument(
        "--no-animation",
        action="store_true",
        help="MP4 애니메이션 생략 (FFmpeg 없을 때 사용)",
    )
    parser.add_argument(
        "--speed-factor",
        type=float,
        default=30.0,
        help="애니메이션 재생 속도 — 분/초 (default: 30)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=10,
        help="애니메이션 FPS (default: 10)",
    )
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

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=== 경로 시각화 시작 ===")
    logger.info("데이터: %s", data_path)
    logger.info("n_windows: %d", args.n)

    # ── 실데이터 로드 ──────────────────────────────────────────
    backtester = RealDataBacktester(
        csv_path=str(data_path),
        tug_fleet=[],
        berth_locations={},
    )
    all_windows = backtester._windows
    windows = all_windows[: args.n]

    if not windows:
        logger.error("시간창 없음 — 종료")
        sys.exit(1)

    # 예인선 fleet 추출
    tug_ids: list[str] = sorted(
        {spec.tug_id for spec in backtester._assignments}
    )
    tug_fleet = tug_ids[:3] if tug_ids else ["T0", "T1", "T2"]

    logger.info(
        "로드 완료: n_windows=%d, tug_fleet=%s",
        len(windows), tug_fleet,
    )

    # berth_locations 매핑 (정계지 실좌표)
    berth_ids = {w.berth_id for w in windows if w.berth_id}
    berth_locations: dict[str, tuple[float, float]] = {}
    for bid in berth_ids:
        if bid in BERTH_LOCATIONS:
            berth_locations[bid] = BERTH_LOCATIONS[bid]
        else:
            logger.warning("berth_id '%s' 좌표 없음 — depot 사용", bid)
            berth_locations[bid] = DEPOT_LOCATION

    # ── MILP 솔버 실행 ─────────────────────────────────────────
    logger.info("MILP 솔버 실행 중 (n=%d)...", len(windows))
    solver = MILPSolver()
    criteria = ConvergenceCriteria(time_limit_sec=30.0)
    objective = MinWaitObjective()

    result = solver.solve(
        windows=windows,
        tug_fleet=tug_fleet,
        berth_locations=berth_locations,
        objective=objective,
        criteria=criteria,
    )

    if not result.assignments:
        logger.warning("배정 결과 없음 — 그리디 폴백 데이터로 시각화 진행")
        # 폴백: backtester 배정 사용 (첫 n개)
        assignments = backtester._assignments[: args.n]
    else:
        assignments = result.assignments
        logger.info(
            "배정 완료: %d건 | gap=%.4f | time=%.2fs",
            len(assignments),
            result.optimality_gap,
            result.solve_time_sec,
        )

    # berth 좌표 실제 할당 (solver가 거리 계산에 사용한 위치로 업데이트)
    actual_berths = _build_berth_locations_from_spec(assignments)
    if actual_berths and actual_berths is not BERTH_LOCATIONS:
        berth_locations.update(actual_berths)

    # ── Folium HTML 지도 ───────────────────────────────────────
    html_path = str(out_dir / "route_map.html")
    logger.info("Folium 지도 생성 중...")
    try:
        route_map = HarborRouteMap(
            berth_locations=berth_locations,
            depot_location=DEPOT_LOCATION,
        )
        route_map.add_assignments(assignments, label=f"MILP-Tier1 (n={len(windows)})")
        saved_html = route_map.save(html_path)
        logger.info("HTML 저장 완료: %s", saved_html)
        print(f"\nFolium HTML: {saved_html}")
    except Exception as e:
        logger.error("Folium 지도 생성 실패: %s", e)

    # ── MP4 애니메이션 ─────────────────────────────────────────
    if not args.no_animation:
        mp4_path = str(out_dir / "route_animation.mp4")
        logger.info(
            "MP4 애니메이션 생성 중 (speed=%.0f분/초, fps=%d)...",
            args.speed_factor, args.fps,
        )
        try:
            saved_anim = animate_routes(
                assignments=assignments,
                berth_locations=berth_locations,
                depot_location=DEPOT_LOCATION,
                out_path=mp4_path,
                fps=args.fps,
                speed_factor=args.speed_factor,
            )
            if saved_anim:
                print(f"애니메이션: {saved_anim}")
            else:
                logger.warning("애니메이션 저장 실패 (FFmpeg 설치 권장)")
        except Exception as e:
            logger.error("애니메이션 생성 실패: %s", e)
    else:
        logger.info("애니메이션 생략 (--no-animation)")

    print("\n=== 시각화 완료 ===")


if __name__ == "__main__":
    main()
