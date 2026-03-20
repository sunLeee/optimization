"""
항구 에이전트 기반 시뮬레이터 대시보드 (Streamlit).

실행: streamlit run scripts/harbor_dashboard.py
"""
import sys
sys.path.insert(0, '.')

import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(
    page_title="Harbor Optimization Simulator",
    page_icon="⚓",
    layout="wide",
)

st.title("⚓ 항구 선박 운영 최적화 시뮬레이터")
st.caption("Agent-Based Model | Rolling Horizon Optimization | 날씨 불확실성 ±2h")

# ── 사이드바 설정 ──────────────────────────────
with st.sidebar:
    st.header("시뮬레이션 설정")
    n_vessels = st.slider("선박 수 (n)", 5, 50, 18)
    n_berths = st.slider("선석 수 (k)", 2, 10, 3)
    horizon_h = st.slider("계획 수평선 (hours)", 12, 48, 24)
    delay_sigma = st.slider("날씨 지연 σ (hours)", 0.1, 2.0, 0.85)
    seed = st.number_input("시드", value=42, step=1)

    method = st.selectbox(
        "최적화 방법론",
        ["Rolling Horizon", "Deterministic", "Two-Stage SAA", "Robust"],
        index=0,
    )

    run_btn = st.button("▶ 시뮬레이션 실행", type="primary", use_container_width=True)

# ── 메인 영역 ──────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

if run_btn or 'sim_result' not in st.session_state:
    from libs.simulation.agents import VesselAgent, Position
    from libs.simulation.environment import PortSimulator, PortConfig

    with st.spinner("시뮬레이션 실행 중..."):
        config = PortConfig(name="부산항")
        sim = PortSimulator(config=config, seed=int(seed), delay_sigma_h=delay_sigma)

        rng = np.random.default_rng(int(seed))
        vessels = []
        for i in range(n_vessels):
            arrival = float(rng.uniform(0, horizon_h * 0.9))
            duration = float(rng.exponential(3.88))
            v = VesselAgent(
                vessel_id=i,
                name=f"V-{i:03d}",
                arrival_time=arrival,
                service_duration=max(1.0, duration),
                priority=int(rng.choice([1, 2, 3], p=[0.6, 0.3, 0.1])),
                draft_m=float(rng.uniform(8, 14)),
                length_m=float(rng.uniform(150, 300)),
                start_pos=Position(
                    35.05 + rng.uniform(0, 0.1),
                    129.0 + rng.uniform(0, 0.1),
                ),
            )
            vessels.append(v)

        # n_berths 맞게 선석 재초기화
        config.berth_positions = [
            Position(35.096 + i*0.003, 129.034 + i*0.004)
            for i in range(n_berths)
        ]
        sim = PortSimulator(config=config, seed=int(seed), delay_sigma_h=delay_sigma)
        sim.add_vessel_schedule(vessels, apply_weather_delay=True)
        sim.run(until_h=float(horizon_h))
        st.session_state['sim_result'] = sim

sim = st.session_state['sim_result']
summary = sim.summary()

# KPI 카드
with col1:
    st.metric("완료 선박", f"{summary['completed_vessels']}/{summary['total_vessels']}")
with col2:
    st.metric("평균 대기시간", f"{summary['avg_wait_h']:.2f}h")
with col3:
    st.metric("최대 대기시간", f"{summary['max_wait_h']:.2f}h")
with col4:
    st.metric("총 예인선 연료", f"{summary['total_tug_fuel']:.1f} MT")

st.divider()

# ── 지도 시각화 ────────────────────────────────
map_col, chart_col = st.columns([3, 2])

with map_col:
    st.subheader("실시간 항구 현황")

    # pydeck 지도
    try:
        import pydeck as pdk

        berth_data = [
            {
                "lon": b.position.lon,
                "lat": b.position.lat,
                "name": b.name,
                "state": b.state.name,
                "color": [0, 200, 0, 180] if b.state.name == "EMPTY" else [200, 50, 50, 180],
                "radius": 60,
            }
            for b in sim.berths.values()
        ]

        vessel_data = [
            {
                "lon": v.position.lon,
                "lat": v.position.lat,
                "name": v.name,
                "state": v.state.name,
                "color": {
                    "APPROACHING": [150, 150, 150, 200],
                    "WAITING": [255, 165, 0, 220],
                    "BERTHED": [0, 150, 80, 220],
                    "DEPARTING": [120, 0, 200, 200],
                }.get(v.state.name, [100, 100, 200, 200]),
                "radius": 40,
            }
            for v in sim.vessels.values()
        ]

        tug_data = [
            {
                "lon": t.position.lon,
                "lat": t.position.lat,
                "name": t.name,
                "state": t.state.name,
                "color": [30, 100, 255, 220],
                "radius": 30,
            }
            for t in sim.tugboats.values()
        ]

        center = sim.config.center
        view = pdk.ViewState(
            latitude=center.lat,
            longitude=center.lon,
            zoom=13,
            pitch=30,
        )

        berth_layer = pdk.Layer(
            "ScatterplotLayer",
            data=berth_data,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius="radius",
            pickable=True,
            tooltip=True,
        )
        vessel_layer = pdk.Layer(
            "ScatterplotLayer",
            data=vessel_data,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius="radius",
            pickable=True,
        )
        tug_layer = pdk.Layer(
            "ScatterplotLayer",
            data=tug_data,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius="radius",
            pickable=True,
        )

        deck = pdk.Deck(
            layers=[berth_layer, vessel_layer, tug_layer],
            initial_view_state=view,
            map_style="mapbox://styles/mapbox/light-v9",
            tooltip={"text": "{name}\n상태: {state}"},
        )
        st.pydeck_chart(deck)

        # 범례
        st.caption("🟢 선석(빈) 🔴 선석(점유) 🟠 대기 선박 🟡 접안중 ⚫ 접근중 🔵 예인선")

    except ImportError:
        st.warning("pydeck 미설치. `pip install pydeck`으로 설치하세요.")
        # 폴백: 간단 scatter
        df = pd.DataFrame([
            {"lat": b.position.lat, "lon": b.position.lon}
            for b in sim.berths.values()
        ])
        st.map(df)

with chart_col:
    st.subheader("스케줄 간트 차트")

    gantt_data = []
    for v in sim.vessels.values():
        if v.actual_arrival is not None:
            gantt_data.append({
                "선박": v.name,
                "도착": v.actual_arrival,
                "접안 시작": v.berth_start or v.actual_arrival,
                "접안 완료": (v.berth_start or v.actual_arrival) + v.service_duration,
                "대기": (v.berth_start or v.actual_arrival) - v.actual_arrival,
                "우선순위": v.priority,
            })

    if gantt_data:
        df_gantt = pd.DataFrame(gantt_data)

        try:
            import plotly.express as px
            fig = px.bar(
                df_gantt,
                x="대기",
                y="선박",
                orientation="h",
                color="우선순위",
                title="선박별 대기 시간",
                labels={"대기": "대기 시간 (h)"},
                color_continuous_scale="RdYlGn_r",
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.dataframe(df_gantt[["선박", "도착", "대기"]].round(2))

# ── 이벤트 로그 ────────────────────────────────
st.subheader("이벤트 로그")
if sim.event_log:
    df_log = pd.DataFrame(sim.event_log).round(3)
    st.dataframe(df_log, use_container_width=True, height=200)

# ── 방법론 비교 ────────────────────────────────
with st.expander("확률적 최적화 방법론 비교 (실험 결과)"):
    comparison_data = {
        "방법론": ["Deterministic", "Two-Stage SAA", "Chance-Constrained", "Robust", "Rolling Horizon"],
        "E[Cost]": [76.45, 76.67, 76.20, 74.32, 74.21],
        "Std": [13.98, 13.97, 14.12, 16.64, 10.46],
        "CVaR95": [107.26, 107.14, 106.18, 111.30, 95.25],
        "CVaR/E 비율": ["1.40x", "1.40x", "1.39x", "1.50x", "1.28x"],
        "권장": ["기준선", "사전 계획", "규제 준수", "극단 기상", "✅ 운영 최적화"],
    }
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)
    st.caption("참조: .omc/scientist/reports/20260319_220351_port_stochastic_opt.md")
