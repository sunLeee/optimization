"""
목적함수 Strategy Pattern — 플러거블 목적함수 설계.

OBJ-A: MinWaitObjective   — min Σ(priority × wait_h)
OBJ-B: MinIdleObjective   — min Σ idle_h
OBJ-C: MinCompositeObjective — min w2·idle_h + w3·priority×wait_h
OBJ-D: MinAllObjective    — 사후집계: idle_h + priority×wait_h + λ·dist_nm

참조:
  - ADR-003: Protocol vs ABC 선택 근거
  - ADR-006: 4종 목적함수 수식 + OBJ-D 사후집계 확정
  - libs/routing/alns.py: tug_free_at 계산 패턴 (service_duration 사용)
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec


@dataclass
class KPIResult:
    """4대 KPI + 목적함수 값을 담는 결과 타입.

    단위:
        dist_nm: 해리 (nautical miles)
        idle_h:  시간 (hours)
        wait_h:  시간 (hours)
        fuel_mt: 메트릭 톤 (metric tons)
    """

    dist_nm: float           # 총 이동거리 (해리)
    idle_h: float            # 총 예인선 유휴시간 (시간)
    wait_h: float            # Σ(priority × raw_wait_h) — 우선순위 가중 (시간)
    fuel_mt: float           # 총 연료소비 (메트릭 톤)
    objective_value: float   # 목적함수 값 (최소화 방향)


def _compute_idle(
    assignments: list[SchedulingToRoutingSpec],
    windows: list[TimeWindowSpec],  # noqa: ARG001 — 향후 horizon 계산에 활용
) -> float:
    """예인선별 유휴시간 합산 (hours).

    알고리즘:
    1. tug_id별로 assignments를 scheduled_start 기준 정렬
    2. 연속 assignment 간 gap 계산:
       prev_end = prev.scheduled_start + prev.time_window.service_duration
       gap = curr.scheduled_start - prev_end
    3. gap > 0인 경우만 유휴시간으로 집계 (음수 = 겹침, 무시)
    4. 모든 tug의 gap 합산 → minutes → hours 변환

    참조 패턴:
        libs/routing/alns.py: tug_free_at[k] = start + w.service_duration

    Args:
        assignments: 솔버 출력 배정 목록 (SchedulingToRoutingSpec)
        windows: 전체 TimeWindowSpec (현재 미사용, 향후 horizon 계산용)

    Returns:
        총 예인선 유휴시간 (hours)
    """
    if not assignments:
        return 0.0

    tug_groups: dict[str, list[SchedulingToRoutingSpec]] = defaultdict(list)
    for spec in assignments:
        tug_groups[spec.tug_id].append(spec)

    total_idle_min = 0.0
    for specs in tug_groups.values():
        specs_sorted = sorted(specs, key=lambda s: s.scheduled_start)
        for i in range(1, len(specs_sorted)):
            prev = specs_sorted[i - 1]
            curr = specs_sorted[i]
            prev_end = prev.scheduled_start + prev.time_window.service_duration
            gap = curr.scheduled_start - prev_end
            if gap > 0:
                total_idle_min += gap

    return total_idle_min / 60.0  # minutes → hours


def _compute_wait(
    assignments: list[SchedulingToRoutingSpec],
    windows: list[TimeWindowSpec],
) -> float:
    """선박별 대기시간 합산 (hours, priority 가중 포함).

    대기시간 = max(0, scheduled_start - earliest_start)

    Args:
        assignments: 솔버 출력 배정 목록
        windows: 전체 TimeWindowSpec (earliest_start 참조)

    Returns:
        Σ(priority × wait_h)
    """
    if not assignments:
        return 0.0

    window_map = {w.vessel_id: w for w in windows}
    total_wait = 0.0
    for spec in assignments:
        w = window_map.get(spec.vessel_id)
        if w is None:
            continue
        wait_min = max(0.0, spec.scheduled_start - w.earliest_start)
        total_wait += spec.priority * (wait_min / 60.0)

    return total_wait


@runtime_checkable
class ObjectiveStrategy(Protocol):
    """목적함수 Strategy Protocol (ADR-003).

    구현 의무:
        compute(assignments, windows) -> KPIResult
        name() -> str

    런타임 검증:
        isinstance(obj, ObjectiveStrategy)  # @runtime_checkable
    """

    def compute(
        self,
        assignments: list[SchedulingToRoutingSpec],
        windows: list[TimeWindowSpec],
    ) -> KPIResult:
        """4대 KPI 계산 + 목적함수 값 반환.

        Args:
            assignments: TugScheduleModel.solve() 또는 동등 솔버 출력
            windows: 전체 TimeWindowSpec (모든 선박 포함)

        Returns:
            KPIResult (dist_nm, idle_h, wait_h, fuel_mt, objective_value)
        """
        ...

    def name(self) -> str:
        """목적함수 식별자 (예: 'OBJ-A MinWait')."""
        ...


class MinWaitObjective:
    """OBJ-A: 선박 대기시간 최소화.

    목적함수: min Σ(priority × wait_h)
    """

    def name(self) -> str:
        return "OBJ-A MinWait"

    def compute(
        self,
        assignments: list[SchedulingToRoutingSpec],
        windows: list[TimeWindowSpec],
    ) -> KPIResult:
        idle_h = _compute_idle(assignments, windows)
        wait_h = _compute_wait(assignments, windows)
        return KPIResult(
            dist_nm=0.0,
            idle_h=idle_h,
            wait_h=wait_h,
            fuel_mt=0.0,
            objective_value=wait_h,
        )


class MinIdleObjective:
    """OBJ-B: 예인선 유휴시간 최소화.

    목적함수: min Σ idle_h
    """

    def name(self) -> str:
        return "OBJ-B MinIdle"

    def compute(
        self,
        assignments: list[SchedulingToRoutingSpec],
        windows: list[TimeWindowSpec],
    ) -> KPIResult:
        idle_h = _compute_idle(assignments, windows)
        wait_h = _compute_wait(assignments, windows)
        return KPIResult(
            dist_nm=0.0,
            idle_h=idle_h,
            wait_h=wait_h,
            fuel_mt=0.0,
            objective_value=idle_h,
        )


class MinCompositeObjective:
    """OBJ-C: 유휴시간 + 대기시간 가중합.

    목적함수: min w2·idle_h + w3·priority×wait_h
    기본값: w2=w3=0.5
    """

    def __init__(self, w2: float = 0.5, w3: float = 0.5) -> None:
        self.w2 = w2
        self.w3 = w3

    def name(self) -> str:
        return f"OBJ-C MinComposite(w2={self.w2},w3={self.w3})"

    def compute(
        self,
        assignments: list[SchedulingToRoutingSpec],
        windows: list[TimeWindowSpec],
    ) -> KPIResult:
        idle_h = _compute_idle(assignments, windows)
        wait_h = _compute_wait(assignments, windows)
        obj_val = self.w2 * idle_h + self.w3 * wait_h
        return KPIResult(
            dist_nm=0.0,
            idle_h=idle_h,
            wait_h=wait_h,
            fuel_mt=0.0,
            objective_value=obj_val,
        )


class MinAllObjective:
    """OBJ-D: 유휴+대기+이동거리 사후집계 (ADR-006).

    목적함수: idle_h + priority×wait_h + λ·dist_nm
    λ=1.0 기본값. dist_nm은 RouteResult 주입 없으면 0.0 fallback.

    주의 (재사용 의미론):
        `inject_dist_nm(dist_nm)` 로 주입한 값은 인스턴스에 유지된다.
        동일 인스턴스를 복수의 run_all() 호출에 재사용할 경우 의도치 않은 값
        블리드가 발생할 수 있다. 새로운 라우팅 컨텍스트마다 inject_dist_nm()을
        재호출하거나 신규 인스턴스를 생성할 것.

        백테스터(RealDataBacktester) 컨텍스트에서는 RouteResult가 없으므로
        dist_nm = 0.0이 되어 OBJ-C와 실질적으로 동치가 된다.
        이는 알려진 제약 (ADR-006 Consequences 참조).
    """

    def __init__(
        self,
        lam: float = 1.0,
        w_idle: float = 1.0,
        w_wait: float = 1.0,
    ) -> None:
        self.lam = lam
        self.w_idle = w_idle
        self.w_wait = w_wait
        self._dist_nm_cache: float = 0.0

    def inject_dist_nm(self, dist_nm: float) -> None:
        """RouteResult에서 추출한 dist_nm을 주입.

        백테스터 컨텍스트 외에서 사용 시 Phase 2 완료 후 주입.
        """
        self._dist_nm_cache = dist_nm

    def name(self) -> str:
        return f"OBJ-D MinAll(λ={self.lam})"

    def compute(
        self,
        assignments: list[SchedulingToRoutingSpec],
        windows: list[TimeWindowSpec],
    ) -> KPIResult:
        idle_h = _compute_idle(assignments, windows)
        wait_h = _compute_wait(assignments, windows)
        dist_nm = self._dist_nm_cache
        obj_val = (
            self.w_idle * idle_h + self.w_wait * wait_h + self.lam * dist_nm
        )
        return KPIResult(
            dist_nm=dist_nm,
            idle_h=idle_h,
            wait_h=wait_h,
            fuel_mt=0.0,
            objective_value=obj_val,
        )
