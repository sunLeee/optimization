"""멀티-예인선 배정 (Phase 3) 검증 테스트."""
from __future__ import annotations
import pytest
from libs.utils.time_window import TimeWindowSpec
from libs.scheduling.multi_tug import (
    assign_multi_tug_greedy,
    to_scheduling_specs,
    MultiTugAssignment,
)


def _make_window(
    vessel_id: str,
    berth_id: str = "B1",
    earliest_start: float = 0.0,
    latest_start: float = 60.0,
    service_duration: float = 30.0,
    priority: int = 1,
) -> TimeWindowSpec:
    return TimeWindowSpec(
        vessel_id=vessel_id,
        berth_id=berth_id,
        earliest_start=earliest_start,
        latest_start=latest_start,
        service_duration=service_duration,
        priority=priority,
    )


TUG_FLEET = ["T1", "T2", "T3", "T4", "T5"]
BERTH_LOCS: dict[str, tuple[float, float]] = {
    "B1": (37.5, 126.8),
    "B2": (37.6, 126.9),
}


def test_multi_tug_all_requirements_met() -> None:
    """r_j=[1,2,1,3,1] 설정 후 required_tugs 충족 확인."""
    windows = [
        _make_window("V1", earliest_start=0),
        _make_window("V2", earliest_start=5),
        _make_window("V3", earliest_start=10),
        _make_window("V4", earliest_start=15),
        _make_window("V5", earliest_start=20),
    ]
    required_tugs_map = {"V1": 1, "V2": 2, "V3": 1, "V4": 3, "V5": 1}

    results = assign_multi_tug_greedy(windows, TUG_FLEET, required_tugs_map)

    assert len(results) == 5
    by_vessel = {a.vessel_id: a for a in results}

    assert by_vessel["V1"].actual_tugs == 1
    assert by_vessel["V2"].actual_tugs == 2
    assert by_vessel["V3"].actual_tugs == 1
    assert by_vessel["V4"].actual_tugs == 3
    assert by_vessel["V5"].actual_tugs == 1

    for vessel_id, a in by_vessel.items():
        assert a.required_tugs == required_tugs_map[vessel_id]
        assert a.actual_tugs == a.required_tugs
        assert len(a.tug_ids) == a.actual_tugs


def test_multi_tug_synchronization() -> None:
    """r_j=2 선박의 두 예인선이 동일 시작 시간을 가지는지 확인."""
    # T1이 먼저 배정되어 busy 상태, T2는 free — r=2이면 둘 다 기다려야 함
    windows = [
        _make_window("V1", earliest_start=0, service_duration=20),   # T1, T2 각 1개씩 선점
        _make_window("V2", earliest_start=0, service_duration=20),   # T3, T4 각 1개씩 선점
        _make_window("BIG", earliest_start=0, service_duration=30),  # r=2 필요
    ]
    required_tugs_map = {"V1": 1, "V2": 1, "BIG": 2}
    fleet = ["T1", "T2", "T3"]

    results = assign_multi_tug_greedy(windows, fleet, required_tugs_map)

    big = next(a for a in results if a.vessel_id == "BIG")
    assert big.actual_tugs == 2
    # 두 예인선의 시작 시간은 동일해야 한다 (gang scheduling 동기화)
    # to_scheduling_specs를 거치면 각 spec의 scheduled_start가 동일
    specs = to_scheduling_specs(results, windows, BERTH_LOCS)
    big_specs = [s for s in specs if s.vessel_id == "BIG"]
    assert len(big_specs) == 2
    assert big_specs[0].scheduled_start == big_specs[1].scheduled_start


def test_multi_tug_synchronization_start_time_is_max_free() -> None:
    """동기화 시작 시간이 선택된 예인선 중 가장 늦게 가용한 시간임을 확인."""
    # V1이 T1을 t=0~30 점유, V2가 T2를 t=0~10 점유
    # BIG(r=2)은 T1(free@30)과 T2(free@10)를 선택 → start=max(0,30)=30
    windows = [
        _make_window("V1", earliest_start=0, service_duration=30),
        _make_window("V2", earliest_start=0, service_duration=10),
        _make_window("BIG", earliest_start=0, service_duration=20),
    ]
    required_tugs_map = {"V1": 1, "V2": 1, "BIG": 2}
    fleet = ["T1", "T2"]

    results = assign_multi_tug_greedy(windows, fleet, required_tugs_map)

    big = next(a for a in results if a.vessel_id == "BIG")
    # T1 free@30, T2 free@10 → start = max(earliest_start=0, max_free=30) = 30
    assert big.start_time == 30.0


def test_multi_tug_to_specs() -> None:
    """to_scheduling_specs() 변환 결과 검증."""
    windows = [
        _make_window("V1", berth_id="B1", earliest_start=0, service_duration=30),
        _make_window("V2", berth_id="B2", earliest_start=5, service_duration=20, priority=2),
    ]
    required_tugs_map = {"V1": 2, "V2": 1}
    fleet = ["T1", "T2", "T3"]

    assignments = assign_multi_tug_greedy(windows, fleet, required_tugs_map)
    specs = to_scheduling_specs(assignments, windows, BERTH_LOCS)

    # V1은 r=2이므로 spec 2개, V2는 r=1이므로 spec 1개 → 총 3개
    assert len(specs) == 3

    v1_specs = [s for s in specs if s.vessel_id == "V1"]
    v2_specs = [s for s in specs if s.vessel_id == "V2"]

    assert len(v1_specs) == 2
    assert len(v2_specs) == 1

    # 각 spec의 tug_id는 고유해야 한다
    v1_tug_ids = {s.tug_id for s in v1_specs}
    assert len(v1_tug_ids) == 2

    # pickup/dropoff 위치는 berth_locations에서 올바르게 매핑되어야 한다
    for s in v1_specs:
        assert s.pickup_location == BERTH_LOCS["B1"]
        assert s.dropoff_location == BERTH_LOCS["B1"]

    for s in v2_specs:
        assert s.pickup_location == BERTH_LOCS["B2"]
        assert s.dropoff_location == BERTH_LOCS["B2"]
        assert s.priority == 2

    # required_tugs 필드 전달 확인
    for s in v1_specs:
        assert s.required_tugs == 2
    for s in v2_specs:
        assert s.required_tugs == 1


def test_multi_tug_default_map_is_all_ones() -> None:
    """required_tugs_map 미지정 시 모든 선박 r=1 기본값 동작 확인."""
    windows = [
        _make_window("V1", earliest_start=0),
        _make_window("V2", earliest_start=5),
    ]
    fleet = ["T1", "T2"]

    results = assign_multi_tug_greedy(windows, fleet)

    for a in results:
        assert a.required_tugs == 1
        assert a.actual_tugs == 1
        assert len(a.tug_ids) == 1
