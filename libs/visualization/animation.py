"""
예인선 이동 MP4 애니메이션 — matplotlib.animation 기반.

스케줄 배정 결과를 시간축으로 시각화.
AW-007: libs/utils/에만 의존.

사용 예:
    from libs.visualization.animation import animate_routes
    animate_routes(
        assignments=result.assignments,
        berth_locations=BERTH_LOCS,
        out_path="results/animation.mp4",
        speed_factor=30.0,  # 1초 = 30분
    )
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# 예인선 색상 (matplotlib named colors)
_TUG_COLORS: list[str] = [
    "#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
]

# 기본 depot (인천항 중심)
_DEFAULT_DEPOT: tuple[float, float] = (37.450000, 126.610000)


def animate_routes(
    assignments: list[Any],  # list[SchedulingToRoutingSpec]
    berth_locations: dict[str, tuple[float, float]] | None = None,
    depot_location: tuple[float, float] | None = None,
    out_path: str = "results/animation.mp4",
    fps: int = 10,
    speed_factor: float = 30.0,  # 분/초 (1초 = 30분)
    dpi: int = 100,
    figsize: tuple[int, int] = (10, 8),
) -> str | None:
    """예인선 배정 결과를 MP4 애니메이션으로 저장.

    각 프레임은 시뮬레이션 시각(분)의 한 스냅샷.
    예인선 마커가 현재 위치(이동 중 보간, 서비스 중 정지)를 반영.

    Args:
        assignments: SchedulingToRoutingSpec 리스트
        berth_locations: berth_id → (lat, lon) 매핑
        depot_location: depot (lat, lon)
        out_path: MP4 저장 경로
        fps: 프레임/초
        speed_factor: 분/초 (클수록 빠른 재생)
        dpi: 해상도
        figsize: 그림 크기 인치

    Returns:
        저장 경로 (성공 시), None (오류 시)
    """
    try:
        import matplotlib.animation as mpl_anim
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        logger.warning("matplotlib 미설치. `uv add matplotlib`")
        return None

    import pathlib

    if not assignments:
        logger.warning("assignments 비어 있음 — 애니메이션 생략")
        return None

    # ── 좌표 매핑 구성 ────────────────────────────────────────
    berths: dict[str, tuple[float, float]] = berth_locations or {}
    depot: tuple[float, float] = depot_location or _DEFAULT_DEPOT

    def _loc(spec: Any) -> tuple[float, float]:
        """SchedulingToRoutingSpec → (lat, lon)."""
        pickup = getattr(spec, "pickup_location", None)
        if pickup and len(pickup) == 2:
            return (float(pickup[0]), float(pickup[1]))
        tw = getattr(spec, "time_window", None)
        berth_id = getattr(tw, "berth_id", "") if tw else ""
        return berths.get(berth_id, depot)

    # ── 예인선별 이벤트 구성 ──────────────────────────────────
    tug_ids: list[str] = sorted({getattr(s, "tug_id", "T0") for s in assignments})
    color_map: dict[str, str] = {
        t: _TUG_COLORS[i % len(_TUG_COLORS)] for i, t in enumerate(tug_ids)
    }

    # 예인선별 세그먼트: (start_min, end_min, from_loc, to_loc, vessel_id)
    segments: dict[str, list[tuple[float, float, tuple, tuple, str]]] = {
        t: [] for t in tug_ids
    }
    for spec in sorted(assignments, key=lambda s: (
        getattr(s, "tug_id", ""), getattr(s, "scheduled_start", 0.0)
    )):
        tug = getattr(spec, "tug_id", "T0")
        sched = float(getattr(spec, "scheduled_start", 0.0))
        tw = getattr(spec, "time_window", None)
        svc = float(getattr(tw, "service_duration", 30.0)) if tw else 30.0
        vessel_id = getattr(spec, "vessel_id", "?")
        loc = _loc(spec)

        # 이전 세그먼트 끝 위치 → 현재 위치 이동 세그먼트
        prev_segs = segments[tug]
        if prev_segs:
            prev_end_t, _, _, prev_loc, _ = prev_segs[-1]
            # 이동 세그먼트 (이전 작업 종료 → 현재 작업 시작)
            if sched > prev_end_t:
                segments[tug].append((prev_end_t, sched, prev_loc, loc, "transit"))
        else:
            # depot → 첫 작업
            if sched > 0:
                segments[tug].append((0.0, sched, depot, loc, "transit"))

        # 서비스 세그먼트 (정지)
        segments[tug].append((sched, sched + svc, loc, loc, vessel_id))

    # ── 시간 범위 ──────────────────────────────────────────────
    all_times = [0.0]
    for segs in segments.values():
        for s in segs:
            all_times += [s[0], s[1]]
    t_min_global = min(all_times)
    t_max_global = max(all_times)

    n_frames = max(int((t_max_global - t_min_global) / speed_factor * fps), 30)
    frame_times = np.linspace(t_min_global, t_max_global, n_frames)

    # ── 현재 위치 보간 ────────────────────────────────────────
    def _tug_position(tug: str, t: float) -> tuple[float, float]:
        for (t0, t1, from_loc, to_loc, _) in segments[tug]:
            if t0 <= t <= t1:
                if t1 == t0 or from_loc == to_loc:
                    return to_loc
                alpha = (t - t0) / (t1 - t0)
                lat = from_loc[0] + alpha * (to_loc[0] - from_loc[0])
                lon = from_loc[1] + alpha * (to_loc[1] - from_loc[1])
                return (lat, lon)
        # 모든 세그먼트 종료 → depot 복귀
        return depot

    # ── 지도 범위 계산 ────────────────────────────────────────
    all_locs: list[tuple[float, float]] = [depot] + list(berths.values())
    lats = [pt[0] for pt in all_locs]
    lons = [pt[1] for pt in all_locs]
    lat_pad = max((max(lats) - min(lats)) * 0.2, 0.01)
    lon_pad = max((max(lons) - min(lons)) * 0.2, 0.01)
    lat_range = (min(lats) - lat_pad, max(lats) + lat_pad)
    lon_range = (min(lons) - lon_pad, max(lons) + lon_pad)

    # ── Figure 구성 ───────────────────────────────────────────
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.set_xlim(lon_range[0], lon_range[1])
    ax.set_ylim(lat_range[0], lat_range[1])
    ax.set_xlabel("경도 (Longitude)")
    ax.set_ylabel("위도 (Latitude)")
    ax.set_facecolor("#e8f4f8")
    ax.grid(True, alpha=0.3)

    # 정계지 마커 (고정)
    for berth_id, (lat, lon) in berths.items():
        ax.plot(lon, lat, "s", markersize=12, color="gray", zorder=5)
        ax.annotate(berth_id, (lon, lat), textcoords="offset points",
                    xytext=(5, 5), fontsize=7, color="black")

    # Depot 마커
    ax.plot(depot[1], depot[0], "^", markersize=14, color="black", zorder=6,
            label="Depot")

    # 예인선 마커 (이동용)
    tug_markers: dict[str, Any] = {}
    tug_label_texts: dict[str, Any] = {}
    for tug in tug_ids:
        pos = _tug_position(tug, t_min_global)
        marker, = ax.plot(
            pos[1], pos[0], "o",
            markersize=10, color=color_map[tug], zorder=7,
            label=f"예인선 {tug}",
        )
        txt = ax.text(
            pos[1], pos[0], tug, fontsize=7, ha="left", va="bottom",
            color=color_map[tug], zorder=8,
        )
        tug_markers[tug] = marker
        tug_label_texts[tug] = txt

    title_obj = ax.set_title(f"예인선 이동 시뮬레이션 — t={t_min_global:.0f}분")
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()

    # ── 애니메이션 업데이트 함수 ──────────────────────────────
    def _update(frame_idx: int) -> list[Any]:
        t = frame_times[frame_idx]
        updated: list[Any] = [title_obj]
        title_obj.set_text(f"예인선 이동 시뮬레이션 — t={t:.0f}분")
        for tug in tug_ids:
            pos = _tug_position(tug, t)
            tug_markers[tug].set_data([pos[1]], [pos[0]])
            tug_label_texts[tug].set_position((pos[1] + 0.001, pos[0] + 0.001))
            updated += [tug_markers[tug], tug_label_texts[tug]]
        return updated

    ani = mpl_anim.FuncAnimation(
        fig, _update,
        frames=n_frames,
        interval=int(1000 / fps),
        blit=True,
    )

    # ── 저장 ──────────────────────────────────────────────────
    out = pathlib.Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # MP4 시도, 실패 시 GIF fallback
    saved_path: str | None = None
    try:
        writer = mpl_anim.FFMpegWriter(fps=fps, bitrate=1000)
        ani.save(str(out), writer=writer, dpi=dpi)
        saved_path = str(out.resolve())
        logger.info("MP4 저장 완료: %s", saved_path)
    except Exception as e_mp4:
        logger.warning("FFmpeg 미설치 — GIF fallback: %s", e_mp4)
        gif_path = out.with_suffix(".gif")
        try:
            ani.save(str(gif_path), writer="pillow", fps=fps // 2)
            saved_path = str(gif_path.resolve())
            logger.info("GIF 저장 완료: %s", saved_path)
        except Exception as e_gif:
            logger.error("GIF 저장도 실패: %s", e_gif)

    plt.close(fig)
    return saved_path
