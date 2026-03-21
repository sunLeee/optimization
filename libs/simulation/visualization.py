from __future__ import annotations
import json
from .agents import Position
from .environment import PortSimulator

try:
    import folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    import pydeck as pdk
    HAS_PYDECK = True
except ImportError:
    HAS_PYDECK = False


def render_port_map_folium(sim: PortSimulator) -> "folium.Map | None":
    """folium으로 항구 현황 지도 렌더링."""
    if not HAS_FOLIUM:
        return None
    import folium

    m = folium.Map(
        location=[sim.config.center.lat, sim.config.center.lon],
        zoom_start=14,
        tiles="OpenStreetMap",
    )

    # 선석 마커
    for b in sim.berths.values():
        color = "green" if b.state.name == "EMPTY" else "red"
        folium.CircleMarker(
            location=[b.position.lat, b.position.lon],
            radius=12,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=f"{b.name}<br>상태: {b.state.name}<br>선박: {b.current_vessel}",
            tooltip=b.name,
        ).add_to(m)

    # 예인선 마커
    for tug in sim.tugboats.values():
        folium.Marker(
            location=[tug.position.lat, tug.position.lon],
            icon=folium.Icon(color="blue", icon="ship", prefix="fa"),
            popup=f"{tug.name}<br>상태: {tug.state.name}<br>연료: {tug.total_fuel:.1f}MT",
            tooltip=tug.name,
        ).add_to(m)

    # 선박 마커
    state_colors = {
        "APPROACHING": "gray",
        "WAITING": "orange",
        "BERTHED": "darkgreen",
        "DEPARTING": "purple",
    }
    for v in sim.vessels.values():
        color = state_colors.get(v.state.name, "gray")
        folium.CircleMarker(
            location=[v.position.lat, v.position.lon],
            radius=8,
            color=color,
            fill=True,
            popup=f"{v.name}<br>상태: {v.state.name}<br>ETA: {v.eta:.1f}h",
        ).add_to(m)

    return m


def render_pydeck_layers(sim: PortSimulator) -> list:
    """pydeck 레이어 리스트 반환 (Streamlit 연동용)."""
    if not HAS_PYDECK:
        return []
    import pydeck as pdk

    berth_data = [
        {
            "lat": b.position.lat,
            "lon": b.position.lon,
            "name": b.name,
            "state": b.state.name,
            "color": [0, 200, 0] if b.state.name == "EMPTY" else [200, 0, 0],
        }
        for b in sim.berths.values()
    ]

    vessel_data = [
        {
            "lat": v.position.lat,
            "lon": v.position.lon,
            "name": v.name,
            "state": v.state.name,
        }
        for v in sim.vessels.values()
    ]

    tug_data = [
        {
            "lat": t.position.lat,
            "lon": t.position.lon,
            "name": t.name,
        }
        for t in sim.tugboats.values()
    ]

    berth_layer = pdk.Layer(
        "ScatterplotLayer",
        data=berth_data,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=50,
        pickable=True,
    )
    vessel_layer = pdk.Layer(
        "ScatterplotLayer",
        data=vessel_data,
        get_position=["lon", "lat"],
        get_color=[100, 100, 255],
        get_radius=30,
        pickable=True,
    )
    return [berth_layer, vessel_layer]
