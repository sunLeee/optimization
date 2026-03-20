"""
Toy instance n=5 — Step 1 TSP-T MILP 검증용 픽스처.

5개 선박, 2개 예인선, 2개 선석.
논문 결과와 ±1% 이내 검증에 사용.
"""
from __future__ import annotations
from libs.simulation.agents import VesselAgent, Position
from libs.utils.time_window import TimeWindowSpec


# ── 선박 스케줄 (단위: hours) ─────────────────────────────────
VESSELS = [
    {"vessel_id": 0, "name": "V-000", "arrival_time": 1.0, "service_duration": 3.0, "priority": 2},
    {"vessel_id": 1, "name": "V-001", "arrival_time": 2.5, "service_duration": 4.0, "priority": 1},
    {"vessel_id": 2, "name": "V-002", "arrival_time": 4.0, "service_duration": 2.5, "priority": 3},
    {"vessel_id": 3, "name": "V-003", "arrival_time": 6.0, "service_duration": 3.5, "priority": 1},
    {"vessel_id": 4, "name": "V-004", "arrival_time": 7.5, "service_duration": 2.0, "priority": 2},
]

# ── 선석 정보 ─────────────────────────────────────────────────
BERTHS = [
    {"berth_id": "B0", "position": (35.098, 129.037), "length_m": 300, "depth_m": 15},
    {"berth_id": "B1", "position": (35.101, 129.041), "length_m": 280, "depth_m": 14},
]

# ── 예인선 정보 ───────────────────────────────────────────────
TUGBOATS = [
    {"tug_id": "T0", "speed_kn": 12.0, "fuel_coeff": 0.5},
    {"tug_id": "T1", "speed_kn": 10.0, "fuel_coeff": 0.6},
]

# ── TimeWindowSpec (BAP → TSP-T 인터페이스) ──────────────────
# 이 픽스처에서는 BAP를 사전 결정 (간단 배정):
# 선박 0,2,4 → B0 / 선박 1,3 → B1
TIME_WINDOWS = [
    TimeWindowSpec("0", "B0", earliest_start=1.0*60, latest_start=3.0*60, service_duration=3.0*60),
    TimeWindowSpec("1", "B1", earliest_start=2.5*60, latest_start=5.0*60, service_duration=4.0*60),
    TimeWindowSpec("2", "B0", earliest_start=7.0*60, latest_start=9.0*60, service_duration=2.5*60),
    TimeWindowSpec("3", "B1", earliest_start=11.0*60, latest_start=13.0*60, service_duration=3.5*60),
    TimeWindowSpec("4", "B0", earliest_start=14.0*60, latest_start=16.0*60, service_duration=2.0*60),
]

# ── 기대 결과 (논문 벤치마크 ±1% 허용) ───────────────────────
EXPECTED = {
    "total_waiting_cost": None,  # Step 1 구현 후 채움
    "solver": "HiGHS",
    "gamma": 2.5,
    "n_vessels": 5,
    "n_berths": 2,
    "n_tugs": 2,
}
