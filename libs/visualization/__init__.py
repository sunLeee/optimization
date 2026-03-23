"""
libs/visualization/ — 시각화 패키지.

공개 API:
    plot_convergence     — SolveResult.metadata에서 수렴 곡선 생성
    HarborRouteMap       — Folium 지도 (Phase 3)
    animate_routes       — matplotlib MP4 애니메이션 (Phase 3)
"""
from __future__ import annotations

from libs.visualization.convergence import plot_convergence
from libs.visualization.route_map import HarborRouteMap
from libs.visualization.animation import animate_routes

__all__ = [
    "plot_convergence",
    "HarborRouteMap",
    "animate_routes",
]
