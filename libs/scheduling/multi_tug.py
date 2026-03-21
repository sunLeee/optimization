"""
멀티-예인선 배정 모듈 — Phase 3.

대형 선박(required_tugs > 1)에 다수 예인선을 동시 배정.
수식 참조: Viana et al. (2020), Computers & Operations Research

Gang scheduling 동기화 제약 (TSP-T Multi-Tug):
  Σ_{k∈K} y_jk = r_j          (필요 예인선 수 r_j 충족)
  s_jk = S_j ∀k: y_jk=1      (동시 작업 시작)
  S_j ≥ e_j                   (시간창 하한)
  S_j ≤ l_j                   (시간창 상한)

bollard pull 기반 확장:
  Σ_{k∈K} bp_k * y_jk ≥ BP_j_min  (총 견인력 충족)
"""
from __future__ import annotations
from dataclasses import dataclass
from libs.utils.time_window import TimeWindowSpec, SchedulingToRoutingSpec


@dataclass
class MultiTugAssignment:
    """멀티-예인선 배정 결과 (단일 선박)."""
    vessel_id: str
    tug_ids: list[str]          # 배정된 예인선 목록
    start_time: float           # 동기화된 시작 시간
    required_tugs: int
    actual_tugs: int


def assign_multi_tug_greedy(
    windows: list[TimeWindowSpec],
    tug_fleet: list[str],
    required_tugs_map: dict[str, int] | None = None,
) -> list[MultiTugAssignment]:
    """그리디 멀티-예인선 배정.

    required_tugs_map: vessel_id → 필요 예인선 수
    기본값: 모든 선박 r_j=1
    """
    if required_tugs_map is None:
        required_tugs_map = {w.vessel_id: 1 for w in windows}

    results = []
    tug_free_at = {k: 0.0 for k in tug_fleet}

    for w in sorted(windows, key=lambda x: x.earliest_start):
        r = required_tugs_map.get(w.vessel_id, 1)
        # r개의 가장 빨리 가용한 예인선 선택
        sorted_tugs = sorted(tug_free_at, key=tug_free_at.get)
        selected = sorted_tugs[:r]
        # 동기화: 가장 늦게 가용한 예인선 기준
        max_free = max(tug_free_at[k] for k in selected)
        start = max(w.earliest_start, max_free)
        # 모든 선택 예인선 업데이트
        for k in selected:
            tug_free_at[k] = start + w.service_duration
        results.append(MultiTugAssignment(
            vessel_id=w.vessel_id,
            tug_ids=selected,
            start_time=start,
            required_tugs=r,
            actual_tugs=len(selected),
        ))
    return results


def to_scheduling_specs(
    assignments: list[MultiTugAssignment],
    windows: list[TimeWindowSpec],
    berth_locations: dict[str, tuple[float, float]],
) -> list[SchedulingToRoutingSpec]:
    """MultiTugAssignment → SchedulingToRoutingSpec 변환.

    멀티-예인선의 경우 각 예인선마다 별도 spec 생성.
    """
    wmap = {w.vessel_id: w for w in windows}
    specs = []
    for a in assignments:
        w = wmap[a.vessel_id]
        for tug_id in a.tug_ids:
            specs.append(SchedulingToRoutingSpec(
                vessel_id=a.vessel_id,
                tug_id=tug_id,
                pickup_location=berth_locations[w.berth_id],
                dropoff_location=berth_locations[w.berth_id],
                time_window=w,
                scheduled_start=a.start_time,
                required_tugs=a.required_tugs,
                priority=w.priority,
            ))
    return specs
