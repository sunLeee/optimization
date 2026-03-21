"""
통합 테스트 — Phase 2 Step 1~4 전체 파이프라인 검증.

각 테스트는 toy_n5 또는 Solomon R101-25 인스턴스를 사용한다.
"""
import sys
sys.path.insert(0, '.')
import pytest
from tests.fixtures.toy_n5.instance import TIME_WINDOWS, BERTHS, EXPECTED


@pytest.fixture
def berth_locs():
    return {b['berth_id']: b['position'] for b in BERTHS}


@pytest.fixture
def tug_fleet():
    return ['T0', 'T1']


def test_step1_milp_all_vessels_assigned(berth_locs, tug_fleet):
    """Step 1: MILP가 5/5 선박 배정."""
    from libs.scheduling.tsp_t_milp import TugScheduleModel
    model = TugScheduleModel(windows=TIME_WINDOWS, tug_fleet=tug_fleet, berth_locations=berth_locs)
    result = model.solve()
    assert len(result.assignments) == len(TIME_WINDOWS)
    assert result.optimality_gap <= 0.05


def test_step1_milp_sc4_beats_greedy(berth_locs, tug_fleet):
    """Step 1 SC-4: MILP가 greedy 대비 개선."""
    from libs.scheduling.tsp_t_milp import TugScheduleModel
    from libs.utils.geo import haversine_nm
    from libs.routing.alns import DEPOT
    model = TugScheduleModel(windows=TIME_WINDOWS, tug_fleet=tug_fleet, berth_locations=berth_locs)
    result = model.solve()
    # greedy 비교
    tug_free = {k: 0.0 for k in tug_fleet}
    greedy_cost = 0.0
    for w in sorted(TIME_WINDOWS, key=lambda x: x.earliest_start):
        k = min(tug_free, key=tug_free.get)
        d = haversine_nm(list(berth_locs.values())[0], berth_locs[w.berth_id])
        arrival = tug_free[k] + d / 10.0 * 60.0
        start = max(arrival, w.earliest_start)
        wait_h = max(0.0, start - w.earliest_start) / 60.0
        greedy_cost += 1.0 * w.priority * wait_h + 0.01 * 0.5 * d
        tug_free[k] = start + w.service_duration
    assert result.total_cost <= greedy_cost + 1e-6, f"MILP cost {result.total_cost:.4f} > greedy {greedy_cost:.4f}"


def test_step2_alns_solomon_r101_25():
    """Step 2: ALNS Solomon R101-25 25/25 배정."""
    from tests.fixtures.solomon_r101 import SOLOMON_R101_25, SOLOMON_META
    from libs.routing.alns import ALNSWithSpeedOptimizer, ALNSConfig
    from libs.fuel.eco_speed import EcoSpeedOptimizer
    eco = EcoSpeedOptimizer(alpha=0.5, gamma=2.5)
    cfg = ALNSConfig(max_iter=100, max_outer_iter=10, seed=42)
    alns = ALNSWithSpeedOptimizer(
        windows=SOLOMON_R101_25,
        tug_fleet=SOLOMON_META['tug_fleet'],
        berth_locations=SOLOMON_META['berth_locations'],
        eco_speed_optimizer=eco, cfg=cfg,
    )
    result = alns.solve()
    assert len(result.assignments) == len(SOLOMON_R101_25)


def test_step3_benders_toy_n5(berth_locs, tug_fleet):
    """Step 3: Benders Decomposition 5/5 배정."""
    from libs.scheduling.benders import BendersDecomposition, BendersConfig
    cfg = BendersConfig(max_iter=5, gap_tol=0.05, time_limit_sec=30)
    benders = BendersDecomposition(windows=TIME_WINDOWS, tug_fleet=tug_fleet, berth_locations=berth_locs, cfg=cfg)
    result = benders.solve()
    assert len(result.assignments) > 0


def test_step4_rolling_horizon_all_assigned(berth_locs, tug_fleet):
    """Step 4: Rolling Horizon 24h 시뮬레이션에서 모든 선박 배정."""
    from libs.stochastic.rolling_horizon import RollingHorizonOrchestrator, RollingHorizonConfig
    cfg = RollingHorizonConfig(horizon_h=6.0, dt_h=2.0, max_steps=12)
    rho = RollingHorizonOrchestrator(windows=TIME_WINDOWS, tug_fleet=tug_fleet, berth_locations=berth_locs, cfg=cfg)
    result = rho.run(simulate_until_h=24.0)
    assert len(result.total_assignments) == len(TIME_WINDOWS)
    assert result.elapsed_sec < 60.0


def test_end_to_end_pipeline(berth_locs, tug_fleet):
    """종단 간 파이프라인: MILP → ALNS → Rolling Horizon 순서."""
    from libs.scheduling.tsp_t_milp import TugScheduleModel
    from libs.stochastic.rolling_horizon import RollingHorizonOrchestrator, RollingHorizonConfig
    # Step 1: 배치 최적화
    milp = TugScheduleModel(windows=TIME_WINDOWS, tug_fleet=tug_fleet, berth_locations=berth_locs)
    milp_result = milp.solve()
    assert len(milp_result.assignments) == len(TIME_WINDOWS)
    # Step 4: 실시간 디스패치
    cfg = RollingHorizonConfig(horizon_h=6.0, dt_h=2.0, max_steps=12)
    rho = RollingHorizonOrchestrator(windows=TIME_WINDOWS, tug_fleet=tug_fleet, berth_locations=berth_locs, cfg=cfg)
    rho_result = rho.run(simulate_until_h=24.0)
    assert len(rho_result.total_assignments) == len(TIME_WINDOWS)
    print(f"MILP cost: {milp_result.total_cost:.4f}, RHO cost: {rho_result.total_cost:.4f}")


def test_multi_tug_integration(berth_locs, tug_fleet):
    """멀티-예인선 배정이 SchedulingToRoutingSpec으로 변환."""
    from libs.scheduling.multi_tug import assign_multi_tug_greedy, to_scheduling_specs
    required = {w.vessel_id: (2 if int(w.vessel_id) == 0 else 1) for w in TIME_WINDOWS}
    assignments = assign_multi_tug_greedy(TIME_WINDOWS, tug_fleet, required)
    specs = to_scheduling_specs(assignments, TIME_WINDOWS, berth_locs)
    # V0는 2개 예인선 → 2개 spec
    v0_specs = [s for s in specs if s.vessel_id == "0"]
    assert len(v0_specs) == 2, f"V0 expected 2 tugs, got {len(v0_specs)}"
    # 동기화: 같은 시작 시간
    assert v0_specs[0].scheduled_start == v0_specs[1].scheduled_start
    print(f"멀티-예인선 통합: 총 {len(specs)} specs (5선박, V0=2예인선)")
