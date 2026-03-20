import pytest
from libs.utils.time_window import TimeWindowSpec, SchedulingToRoutingSpec
from libs.utils.geo import haversine_nm
from libs.fuel.consumption import fuel_consumption
from libs.scheduling.tsp_t_milp import _compute_big_m
from libs.routing.alns import greedy_initial_solution
from libs.fuel.eco_speed import EcoSpeedOptimizer
from tests.fixtures.toy_n5.instance import TIME_WINDOWS

def test_time_window_spec():
    # verify priority default=1
    tw = TimeWindowSpec(
        vessel_id="V1",
        berth_id="B1",
        earliest_start=10.0,
        latest_start=20.0,
        service_duration=5.0
    )
    assert tw.priority == 1

def test_scheduling_to_routing_spec():
    # verify scheduled_start=0.0
    tw = TimeWindowSpec(
        vessel_id="V1",
        berth_id="B1",
        earliest_start=10.0,
        latest_start=20.0,
        service_duration=5.0
    )
    spec = SchedulingToRoutingSpec(
        vessel_id="V1",
        tug_id="T1",
        pickup_location=(35.1, 129.0),
        dropoff_location=(35.2, 129.1),
        time_window=tw
    )
    assert spec.scheduled_start == 0.0

def test_haversine_nm():
    # verify distance calculation (Busan area)
    pos1 = (35.1, 129.0)
    pos2 = (35.2, 129.1)
    dist = haversine_nm(pos1, pos2)
    assert dist > 0
    # Add a sanity check for distance in nautical miles. 1 degree latitude is approx 60 nm.
    # 0.1 degree is roughly 6 nm. So distance should be > 6.
    assert dist > 5.0

def test_fuel_consumption():
    # verify F=α·v^γ·d with γ=2.5
    v = 10.0
    d = 50.0
    alpha = 1.0
    expected = alpha * (v ** 2.5) * d
    actual = fuel_consumption(speed_kn=v, dist_nm=d, alpha=alpha, gamma=2.5)
    assert actual == pytest.approx(expected)

def test_big_m_calculation():
    # verify M=1020 for toy_n5
    m = _compute_big_m(TIME_WINDOWS)
    assert m == 1020.0

def test_greedy_initial_solution():
    # verify all vessels assigned
    tug_fleet = ["T1", "T2"]
    # We need dummy distances
    vessel_ids = [w.vessel_id for w in TIME_WINDOWS]
    nodes = ["__depot__"] + vessel_ids
    distances = {}
    for i in nodes:
        for j in nodes:
            distances[(i, j)] = 10.0

    routes = greedy_initial_solution(
        windows=TIME_WINDOWS,
        tug_fleet=tug_fleet,
        distances=distances
    )
    
    assigned_vessels = []
    for t_id, t_route in routes.items():
        assert t_route[0] == "__depot__"
        assert t_route[-1] == "__depot__"
        assigned_vessels.extend(t_route[1:-1])
    
    assert set(assigned_vessels) == set(vessel_ids)
    assert len(assigned_vessels) == len(vessel_ids)

def test_eco_speed_compute_initial():
    # verify speeds all = v_eco
    eco = EcoSpeedOptimizer(v_eco=10.0)
    routes = [("__depot__", "0"), ("0", "2"), ("2", "4"), ("__depot__", "1"), ("1", "3")]
    solution = eco.compute_initial(routes)
    for arc, speed in solution.speeds.items():
        assert speed == 10.0
    assert solution.status == "initial"
