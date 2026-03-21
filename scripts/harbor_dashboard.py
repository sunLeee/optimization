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
        ["Rolling Horizon (ALNS)", "Batch MILP (Step 1)", "ALNS (Step 2)", "Benders (Step 3)"],
        index=0,
    )

    run_btn = st.button("▶ 시뮬레이션 실행", type="primary", use_container_width=True)

    st.subheader("Phase 3 설정")
    max_required_tugs = st.slider("최대 예인선/선박", 1, 3, 1)

# ── 탭 구성 ────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["시뮬레이션", "최적화 비교", "Phase 3"])

# ── 시뮬레이션 탭 ──────────────────────────────
with tab1:
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

# ── 최적화 비교 탭 ─────────────────────────────
with tab2:
    st.subheader("Phase 2 구현 현황")
    status_data = {
        "Step": ["Step 1", "Step 2", "Step 3", "Step 4"],
        "방법론": ["TSP-T MILP (Pyomo+HiGHS)", "ALNS + EcoSpeedOptimizer (γ=2.5)",
                   "Benders Decomposition", "Rolling Horizon (MPC)"],
        "대상 규모": ["n<10 (Exact)", "n=10~50 (ALNS)", "n>50 (Decomp)", "실시간 (RHO)"],
        "toy_n5 결과": ["5/5, gap=0%, SC1~4 ✅", "5/5 배정 ✅", "5/5, 2회 수렴 ✅", "5/5, 0.48초 ✅"],
        "상태": ["완료", "완료", "완료", "완료"],
    }
    st.dataframe(pd.DataFrame(status_data), use_container_width=True)

    st.subheader("알고리즘 Big-O 복잡도")
    complexity = {
        "알고리즘": ["Greedy", "2-opt/3-opt", "ALNS", "MILP (B&B)", "Benders"],
        "시간복잡도": ["O(n²)", "O(n²)/O(n³)", "O(n·log n·iter)", "O(2ⁿ) worst", "O(iter·sub)"],
        "적용 규모": ["n<5", "n<20", "n=10~50", "n<10", "n>50"],
        "품질 보장": ["근사", "근사", "근사(BKS 5%)", "최적", "near-optimal"],
    }
    st.dataframe(pd.DataFrame(complexity), use_container_width=True)

# ── Phase 3 탭 ──────────────────────────────────
with tab3:
    st.subheader("Phase 3 구현 현황")

    phase3_data = {
        "항목": ["대규모 벤치마크", "멀티-예인선 배정", "AIS 데이터 처리", "대시보드 고도화"],
        "상태": ["✅ 완료", "✅ 완료", "✅ 완료", "🔄 진행 중"],
        "결과": ["n=50(11초), n=75(36초)", "Gang scheduling 구현", "Log-normal/KDE 피팅", "이 화면"],
        "테스트": ["—", "5/5 PASS", "5/5 PASS", "—"],
    }
    st.dataframe(pd.DataFrame(phase3_data), use_container_width=True)

    st.subheader("대규모 벤치마크 결과")
    benchmark_data = {
        "알고리즘": ["ALNS", "ALNS", "RHO"],
        "n (선박)": [50, 75, 50],
        "배정률": ["100%", "100%", "100%"],
        "소요시간": ["11.28s", "36.08s", "0.47s"],
        "수렴": ["✅", "✅", "✅"],
    }
    st.dataframe(pd.DataFrame(benchmark_data), use_container_width=True)

    st.subheader("AIS 편차 분포 시각화")
    try:
        import sys; sys.path.insert(0, '.')
        from libs.stochastic.ais_processor import generate_synthetic_ais, fit_eta_distribution
        import plotly.express as px

        weather = st.selectbox("날씨 조건", ["calm", "moderate", "rough"])
        data = generate_synthetic_ais(n_records=500, weather=weather)
        model = fit_eta_distribution(data)

        fig = px.histogram(x=data, nbins=50, title=f"ETA 편차 분포 ({weather}) — {model.distribution_type}",
                          labels={"x": "ETA 편차 (hours)", "y": "빈도"})
        st.plotly_chart(fig, use_container_width=True)
        st.metric("평균 편차", f"{model.mean_h:.2f}h")
        st.metric("표준편차", f"{model.std_h:.2f}h")
        st.metric("분포 타입", model.distribution_type)
    except ImportError:
        st.info("plotly 미설치: pip install plotly")
