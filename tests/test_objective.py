"""
tests/test_objective.py — ObjectiveStrategy 구현체 단위 테스트.

검증 범위:
    _compute_idle, _compute_wait (내부 함수)
    ObjectiveStrategy Protocol (runtime_checkable)
    MinWaitObjective, MinIdleObjective, MinCompositeObjective, MinAllObjective
"""
from __future__ import annotations

from libs.optimization import (
    KPIResult,
    MinAllObjective,
    MinCompositeObjective,
    MinIdleObjective,
    MinWaitObjective,
    ObjectiveStrategy,
)
from libs.optimization.objective import _compute_idle, _compute_wait
from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec

# ── 헬퍼 ──────────────────────────────────────────────────────────

def _make_window(
    vessel_id: str,
    earliest_start: float = 0.0,
    latest_start: float = 60.0,
    service_duration: float = 30.0,
    priority: int = 1,
) -> TimeWindowSpec:
    return TimeWindowSpec(
        vessel_id=vessel_id,
        berth_id="B1",
        earliest_start=earliest_start,
        latest_start=latest_start,
        service_duration=service_duration,
        priority=priority,
    )


def _make_spec(
    vessel_id: str,
    tug_id: str,
    scheduled_start: float,
    window: TimeWindowSpec,
) -> SchedulingToRoutingSpec:
    return SchedulingToRoutingSpec(
        vessel_id=vessel_id,
        tug_id=tug_id,
        pickup_location=(0.0, 0.0),
        dropoff_location=(0.0, 0.0),
        time_window=window,
        scheduled_start=scheduled_start,
        required_tugs=1,
        priority=window.priority,
    )


# ── _compute_idle ──────────────────────────────────────────────────

class TestComputeIdle:
    def test_empty_returns_zero(self) -> None:
        assert _compute_idle([], []) == 0.0

    def test_single_assignment_no_idle(self) -> None:
        w = _make_window("V1")
        s = _make_spec("V1", "T1", 0.0, w)
        assert _compute_idle([s], [w]) == 0.0

    def test_gap_between_two_assignments(self) -> None:
        # T1: V1 시작=0, 지속=30분 → 종료=30분
        # T1: V2 시작=60분 → gap=30분=0.5h
        w1 = _make_window("V1", service_duration=30.0)
        w2 = _make_window("V2", service_duration=30.0)
        s1 = _make_spec("V1", "T1", 0.0, w1)
        s2 = _make_spec("V2", "T1", 60.0, w2)
        result = _compute_idle([s1, s2], [w1, w2])
        assert abs(result - 0.5) < 1e-9

    def test_overlap_not_counted(self) -> None:
        # T1: V1 시작=0, 지속=60분 → 종료=60분
        # T1: V2 시작=30분 → gap<0 → 미집계
        w1 = _make_window("V1", service_duration=60.0)
        w2 = _make_window("V2", service_duration=30.0)
        s1 = _make_spec("V1", "T1", 0.0, w1)
        s2 = _make_spec("V2", "T1", 30.0, w2)
        assert _compute_idle([s1, s2], [w1, w2]) == 0.0

    def test_different_tugs_independent(self) -> None:
        # T1: gap=30분, T2: gap=30분 → 합계 1.0h
        w1 = _make_window("V1", service_duration=30.0)
        w2 = _make_window("V2", service_duration=30.0)
        w3 = _make_window("V3", service_duration=30.0)
        w4 = _make_window("V4", service_duration=30.0)
        s1 = _make_spec("V1", "T1", 0.0, w1)
        s2 = _make_spec("V2", "T1", 60.0, w2)
        s3 = _make_spec("V3", "T2", 0.0, w3)
        s4 = _make_spec("V4", "T2", 60.0, w4)
        result = _compute_idle([s1, s2, s3, s4], [w1, w2, w3, w4])
        assert abs(result - 1.0) < 1e-9

    def test_unsorted_input_sorted_internally(self) -> None:
        # 순서 역전 입력 → 내부 정렬 후 동일 결과
        w1 = _make_window("V1", service_duration=30.0)
        w2 = _make_window("V2", service_duration=30.0)
        s1 = _make_spec("V1", "T1", 0.0, w1)
        s2 = _make_spec("V2", "T1", 60.0, w2)
        result_fwd = _compute_idle([s1, s2], [w1, w2])
        result_rev = _compute_idle([s2, s1], [w1, w2])
        assert abs(result_fwd - result_rev) < 1e-9


# ── _compute_wait ──────────────────────────────────────────────────

class TestComputeWait:
    def test_empty_returns_zero(self) -> None:
        assert _compute_wait([], []) == 0.0

    def test_no_wait_when_on_time(self) -> None:
        w = _make_window("V1", earliest_start=0.0)
        s = _make_spec("V1", "T1", 0.0, w)
        assert _compute_wait([s], [w]) == 0.0

    def test_wait_calculation(self) -> None:
        # earliest=0, scheduled=60분, priority=1 → wait=1.0h
        w = _make_window("V1", earliest_start=0.0, priority=1)
        s = _make_spec("V1", "T1", 60.0, w)
        result = _compute_wait([s], [w])
        assert abs(result - 1.0) < 1e-9

    def test_priority_multiplier(self) -> None:
        # earliest=0, scheduled=60분, priority=3 → wait=3.0h
        w = _make_window("V1", earliest_start=0.0, priority=3)
        s = _make_spec("V1", "T1", 60.0, w)
        result = _compute_wait([s], [w])
        assert abs(result - 3.0) < 1e-9

    def test_early_arrival_no_wait(self) -> None:
        # scheduled < earliest: max(0, ...) = 0
        w = _make_window("V1", earliest_start=60.0)
        s = _make_spec("V1", "T1", 0.0, w)
        assert _compute_wait([s], [w]) == 0.0


# ── ObjectiveStrategy Protocol ──────────────────────────────────────

class TestObjectiveStrategyProtocol:
    def test_all_strategies_implement_protocol(self) -> None:
        strategies = [
            MinWaitObjective(),
            MinIdleObjective(),
            MinCompositeObjective(),
            MinAllObjective(),
        ]
        for s in strategies:
            assert isinstance(s, ObjectiveStrategy)

    def test_strategy_names(self) -> None:
        assert MinWaitObjective().name() == "OBJ-A MinWait"
        assert MinIdleObjective().name() == "OBJ-B MinIdle"
        assert "OBJ-C" in MinCompositeObjective().name()
        assert "OBJ-D" in MinAllObjective().name()


# ── MinWaitObjective ───────────────────────────────────────────────

class TestMinWaitObjective:
    def test_objective_value_equals_wait_h(self) -> None:
        w = _make_window("V1", earliest_start=0.0, priority=1)
        s = _make_spec("V1", "T1", 60.0, w)
        kpi = MinWaitObjective().compute([s], [w])
        assert abs(kpi.objective_value - kpi.wait_h) < 1e-9

    def test_kpi_shape(self) -> None:
        w = _make_window("V1")
        s = _make_spec("V1", "T1", 0.0, w)
        kpi = MinWaitObjective().compute([s], [w])
        assert isinstance(kpi, KPIResult)
        assert kpi.dist_nm == 0.0
        assert kpi.fuel_mt == 0.0


# ── MinIdleObjective ───────────────────────────────────────────────

class TestMinIdleObjective:
    def test_objective_value_equals_idle_h(self) -> None:
        w1 = _make_window("V1", service_duration=30.0)
        w2 = _make_window("V2", service_duration=30.0)
        s1 = _make_spec("V1", "T1", 0.0, w1)
        s2 = _make_spec("V2", "T1", 60.0, w2)
        kpi = MinIdleObjective().compute([s1, s2], [w1, w2])
        assert abs(kpi.objective_value - kpi.idle_h) < 1e-9
        assert abs(kpi.idle_h - 0.5) < 1e-9


# ── MinCompositeObjective ──────────────────────────────────────────

class TestMinCompositeObjective:
    def test_default_weights(self) -> None:
        obj = MinCompositeObjective(w2=0.5, w3=0.5)
        w = _make_window("V1", earliest_start=0.0, priority=1)
        s = _make_spec("V1", "T1", 60.0, w)
        kpi = obj.compute([s], [w])
        expected = 0.5 * kpi.idle_h + 0.5 * kpi.wait_h
        assert abs(kpi.objective_value - expected) < 1e-9

    def test_custom_weights(self) -> None:
        obj = MinCompositeObjective(w2=0.8, w3=0.2)
        w = _make_window("V1", earliest_start=0.0, priority=1)
        s = _make_spec("V1", "T1", 60.0, w)
        kpi = obj.compute([s], [w])
        expected = 0.8 * kpi.idle_h + 0.2 * kpi.wait_h
        assert abs(kpi.objective_value - expected) < 1e-9

    def test_w2_zero_only_wait(self) -> None:
        obj = MinCompositeObjective(w2=0.0, w3=1.0)
        w = _make_window("V1", earliest_start=0.0, priority=1)
        s = _make_spec("V1", "T1", 60.0, w)
        kpi = obj.compute([s], [w])
        assert abs(kpi.objective_value - kpi.wait_h) < 1e-9


# ── MinAllObjective ────────────────────────────────────────────────

class TestMinAllObjective:
    def test_dist_nm_zero_by_default(self) -> None:
        obj = MinAllObjective()
        w = _make_window("V1")
        s = _make_spec("V1", "T1", 0.0, w)
        kpi = obj.compute([s], [w])
        assert kpi.dist_nm == 0.0

    def test_inject_dist_nm(self) -> None:
        obj = MinAllObjective(lam=2.0)
        obj.inject_dist_nm(10.0)
        w = _make_window("V1", earliest_start=0.0, priority=1)
        s = _make_spec("V1", "T1", 0.0, w)
        kpi = obj.compute([s], [w])
        # idle=0, wait=0, dist=10 → obj = 2.0 * 10 = 20.0
        assert abs(kpi.objective_value - 20.0) < 1e-9
        assert kpi.dist_nm == 10.0

    def test_objective_sums_all_terms(self) -> None:
        obj = MinAllObjective(lam=1.0, w_idle=1.0, w_wait=1.0)
        w = _make_window("V1", earliest_start=0.0, priority=1)
        # 60분 대기 → wait_h=1.0
        s = _make_spec("V1", "T1", 60.0, w)
        kpi = obj.compute([s], [w])
        expected = kpi.idle_h + kpi.wait_h + 0.0  # dist_nm=0
        assert abs(kpi.objective_value - expected) < 1e-9
