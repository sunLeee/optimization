"""
OSM 기반 예인선 경로 지도 — Folium HTML 생성.

실제 정계지 좌표를 기반으로 예인선 배정 경로를 OpenStreetMap 위에 시각화.
AW-007: libs/utils/에만 의존.

사용 예:
    from libs.visualization.route_map import HarborRouteMap
    m = HarborRouteMap(berth_locations=BERTH_LOCS)
    m.add_assignments(assignments)
    m.save("results/route_map.html")
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# 정계지 좌표 (정계지 위치.csv 기반 — 인천항)
DEFAULT_BERTH_LOCATIONS: dict[str, tuple[float, float]] = {
    "연안부두정계지": (37.450647, 126.594899),
    "송도정계지": (37.350732, 126.662215),
    "내항정계지": (37.474525, 126.607523),
    "북항임시정계지": (37.496626, 126.624476),
}

# 기본 depot (인천항 중심)
DEFAULT_DEPOT: tuple[float, float] = (37.450000, 126.610000)

# 예인선별 색상 팔레트
TUG_COLORS: list[str] = [
    "blue", "red", "green", "purple", "orange",
    "darkblue", "darkred", "darkgreen", "cadetblue", "pink",
]


class HarborRouteMap:
    """Folium 기반 항구 경로 시각화 지도.

    Args:
        berth_locations: berth_id → (lat, lon) 매핑
        depot_location: depot (lat, lon). None이면 베르스 중심 사용
        zoom_start: 초기 줌 레벨 (기본 13)
    """

    def __init__(
        self,
        berth_locations: dict[str, tuple[float, float]] | None = None,
        depot_location: tuple[float, float] | None = None,
        zoom_start: int = 13,
    ) -> None:
        try:
            import folium  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "folium 미설치. `uv add folium`으로 설치하세요."
            ) from e

        self._berths: dict[str, tuple[float, float]] = (
            berth_locations if berth_locations is not None
            else DEFAULT_BERTH_LOCATIONS.copy()
        )
        self._depot: tuple[float, float] = (
            depot_location if depot_location is not None
            else self._compute_center()
        )
        self._zoom = zoom_start
        self._assignments_by_tug: dict[str, list[Any]] = {}
        self._tug_color: dict[str, str] = {}

    # ── 내부 헬퍼 ──────────────────────────────────────────────
    def _compute_center(self) -> tuple[float, float]:
        if not self._berths:
            return DEFAULT_DEPOT
        lats = [lat for lat, _ in self._berths.values()]
        lons = [lon for _, lon in self._berths.values()]
        return (sum(lats) / len(lats), sum(lons) / len(lons))

    def _get_tug_color(self, tug_id: str) -> str:
        if tug_id not in self._tug_color:
            idx = len(self._tug_color) % len(TUG_COLORS)
            self._tug_color[tug_id] = TUG_COLORS[idx]
        return self._tug_color[tug_id]

    def _berth_location(self, berth_id: str) -> tuple[float, float]:
        return self._berths.get(berth_id, self._depot)

    # ── 배정 추가 ──────────────────────────────────────────────
    def add_assignments(
        self,
        assignments: list[Any],  # list[SchedulingToRoutingSpec]
        label: str = "",
    ) -> HarborRouteMap:
        """SchedulingToRoutingSpec 리스트를 지도에 추가.

        Args:
            assignments: SchedulingToRoutingSpec 인스턴스 리스트
            label: 레이어 레이블 (범례 표시)

        Returns:
            self (메서드 체인 지원)
        """
        for spec in assignments:
            tug_id = getattr(spec, "tug_id", "T0")
            if tug_id not in self._assignments_by_tug:
                self._assignments_by_tug[tug_id] = []
            self._assignments_by_tug[tug_id].append((spec, label))
        return self

    # ── 지도 빌드 및 저장 ──────────────────────────────────────
    def build(self) -> Any:
        """Folium Map 객체 생성 후 반환."""
        import folium
        from folium.plugins import MiniMap

        center = self._compute_center()
        m = folium.Map(location=list(center), zoom_start=self._zoom, tiles="OpenStreetMap")

        # 미니맵
        import contextlib
        with contextlib.suppress(Exception):
            MiniMap().add_to(m)

        # ── 정계지 마커 ──
        for berth_id, (lat, lon) in self._berths.items():
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(berth_id, max_width=200),
                tooltip=berth_id,
                icon=folium.Icon(color="gray", icon="anchor", prefix="fa"),
            ).add_to(m)

        # ── 예인선 경로 ──
        for tug_id, spec_list in self._assignments_by_tug.items():
            color = self._get_tug_color(tug_id)
            # 예인선별 레이어 그룹
            tug_group = folium.FeatureGroup(name=f"예인선 {tug_id}", show=True)

            # 배정 순서 정렬 (scheduled_start 기준)
            sorted_specs = sorted(
                spec_list,
                key=lambda x: getattr(x[0], "scheduled_start", 0.0),
            )

            route_points: list[tuple[float, float]] = [self._depot]
            for spec, label in sorted_specs:
                pickup = getattr(spec, "pickup_location", None)
                vessel_id = getattr(spec, "vessel_id", "?")
                priority = getattr(spec, "priority", 1)
                tw = getattr(spec, "time_window", None)
                sched = getattr(spec, "scheduled_start", 0.0)
                svc = getattr(tw, "service_duration", 0.0) if tw else 0.0

                # 픽업 위치 (pickup_location 또는 berth_id로부터)
                if pickup and len(pickup) == 2:
                    plat, plon = float(pickup[0]), float(pickup[1])
                else:
                    berth_id = getattr(tw, "berth_id", "") if tw else ""
                    plat, plon = self._berth_location(berth_id)

                route_points.append((plat, plon))

                # 선박 마커
                popup_html = (
                    f"<b>선박</b>: {vessel_id}<br>"
                    f"<b>예인선</b>: {tug_id}<br>"
                    f"<b>시작</b>: {sched:.0f}분<br>"
                    f"<b>서비스</b>: {svc:.0f}분<br>"
                    f"<b>우선순위</b>: {priority}"
                )
                if label:
                    popup_html += f"<br><b>시나리오</b>: {label}"

                folium.CircleMarker(
                    location=[plat, plon],
                    radius=8,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{vessel_id} ({tug_id})",
                ).add_to(tug_group)

            route_points.append(self._depot)

            # 경로 선
            if len(route_points) > 1:
                folium.PolyLine(
                    locations=[[p[0], p[1]] for p in route_points],
                    color=color,
                    weight=2.5,
                    opacity=0.8,
                    tooltip=f"예인선 {tug_id} 경로",
                    dash_array="5 5",
                ).add_to(tug_group)

            tug_group.add_to(m)

        # ── Depot 마커 ──
        folium.Marker(
            location=list(self._depot),
            popup="Depot (출발지)",
            tooltip="Depot",
            icon=folium.Icon(color="black", icon="home", prefix="fa"),
        ).add_to(m)

        # 레이어 컨트롤
        folium.LayerControl(collapsed=False).add_to(m)

        return m

    def save(self, path: str = "results/route_map.html") -> str:
        """Folium 지도를 HTML 파일로 저장.

        Args:
            path: 저장 경로 (기본: results/route_map.html)

        Returns:
            저장된 파일 절대 경로
        """
        import pathlib
        out = pathlib.Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)

        m = self.build()
        m.save(str(out))
        logger.info("경로 지도 저장 완료: %s", out)
        return str(out.resolve())
