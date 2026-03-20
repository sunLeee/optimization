"""
Rolling Horizon Orchestrator — Phase 2 Step 4.

실시간 예인선 dispatch 최적화 (D-0 당일 운영 기본).
사전 계획은 2-stage SAA로 별도 처리.

알고리즘:
1. 현재 PortState에서 미배정 선박 목록 추출
2. 지평선(horizon_h) 내 도착 선박에만 초점
3. Tier별 솔버 선택:
   - Tier 1 (n<10): TugScheduleModel (Pyomo MILP)
   - Tier 2 (n=10~50): ALNSWithSpeedOptimizer
   - Tier 3 (n>50): BendersDecomposition
4. 첫 번째 결정만 적용 (MPC 원칙)
5. horizon_h 시간 후 재최적화

참조:
  - Petris et al. (2024): Bi-objective dynamic tugboat scheduling
  - Rodriguez-Molins et al. (2014): Rolling horizon for bulk ports
  - phase2-strategy-v3.md: RollingHorizonOrchestrator 설계
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec
from libs.stochastic import PortState


@dataclass
class RollingHorizonConfig:
    """Rolling Horizon 파라미터."""
    horizon_h: float = 2.0          # 재최적화 수평선 (hours)
    dt_h: float = 0.5               # 재최적화 주기 (hours)
    tier1_threshold: int = 10       # n < 10: MILP
    tier2_threshold: int = 50       # n < 50: ALNS
    w1: float = 1.0                 # 대기시간 가중치
    w2: float = 0.01                # 연료 가중치
    alpha: float = 0.5              # 연료 계수
    max_steps: int = 48             # 최대 타임스텝 (48 × 0.5h = 24h)


@dataclass
class DispatchDecision:
    """단일 타임스텝의 dispatch 결정."""
    timestamp_h: float
    assignments: list[SchedulingToRoutingSpec]
    solver_tier: int
    solve_time_sec: float
    n_vessels: int


@dataclass
class RollingHorizonResult:
    """전체 시뮬레이션 결과."""
    decisions: list[DispatchDecision]
    total_assignments: list[SchedulingToRoutingSpec]
    total_waiting_cost: float
    total_fuel_cost: float
    total_cost: float
    steps: int
    elapsed_sec: float


class RollingHorizonOrchestrator:
    """Rolling Horizon 최적화 오케스트레이터.

    libs/stochastic의 최상위 Orchestrator.
    libs/scheduling (TugScheduleModel, Benders) 과
    libs/routing (ALNSWithSpeedOptimizer) 을 조율.

    MPC 원칙: 매 dt_h마다 horizon_h 내 선박만 최적화,
               첫 번째 결정만 실행, 나머지 반복.

    사용 예:
        orchestrator = RollingHorizonOrchestrator(
            windows=ALL_WINDOWS,
            tug_fleet=["T0","T1","T2"],
            berth_locations=berth_locs,
        )
        result = orchestrator.run(initial_state=port_state)
    """

    def __init__(
        self,
        windows: list[TimeWindowSpec],
        tug_fleet: list[str],
        berth_locations: dict[str, tuple[float, float]],
        cfg: RollingHorizonConfig | None = None,
    ) -> None:
        self.windows = windows
        self.tug_fleet = tug_fleet
        self.berth_locations = berth_locations
        self.cfg = cfg or RollingHorizonConfig()
        self._wmap = {w.vessel_id: w for w in windows}

    def _select_tier(self, n: int) -> int:
        """선박 수 n에 따라 Tier 결정."""
        if n < self.cfg.tier1_threshold:
            return 1
        elif n < self.cfg.tier2_threshold:
            return 2
        else:
            return 3

    def _get_horizon_windows(
        self,
        current_time_h: float,
        assigned_ids: set[str],
    ) -> list[TimeWindowSpec]:
        """현재 시간 + horizon 내 미배정 선박 필터링."""
        horizon_end = current_time_h + self.cfg.horizon_h
        # current_time 단위: hours, TimeWindowSpec은 minutes
        t_min = current_time_h * 60.0
        h_min = horizon_end * 60.0

        return [
            w for w in self.windows
            if w.vessel_id not in assigned_ids
            and w.earliest_start <= h_min
            and w.latest_start >= t_min
        ]

    def _solve_step(
        self,
        horizon_windows: list[TimeWindowSpec],
        tier: int,
    ) -> tuple[list[SchedulingToRoutingSpec], float]:
        """Tier별 솔버로 한 타임스텝 최적화.

        Returns:
            (assignments, solve_time_sec)
        """
        t0 = time.time()
        cfg = self.cfg

        # Rolling Horizon에서는 모든 Tier에 ALNS 사용
        # (MILP Tier 1은 Pyomo appsi_highs의 서브인스턴스 변수 미로드 이슈 회피)
        # MILP 배치 최적화는 TugScheduleModel.solve()를 직접 호출해 사용
        if tier in (1, 2):
            from libs.routing.alns import ALNSWithSpeedOptimizer, ALNSConfig
            from libs.fuel.eco_speed import EcoSpeedOptimizer
            alns_cfg = ALNSConfig(
                max_iter=100, max_outer_iter=10,
                w1=cfg.w1, w2=cfg.w2,
            )
            eco = EcoSpeedOptimizer(alpha=cfg.alpha, gamma=2.5)
            alns = ALNSWithSpeedOptimizer(
                windows=horizon_windows,
                tug_fleet=self.tug_fleet,
                berth_locations=self.berth_locations,
                eco_speed_optimizer=eco,
                cfg=alns_cfg,
            )
            route_result = alns.solve()
            assignments = route_result.assignments

        else:  # tier == 3
            from libs.scheduling.benders import BendersDecomposition, BendersConfig
            b_cfg = BendersConfig(
                max_iter=20, gap_tol=0.05,
                w1=cfg.w1, w2=cfg.w2, alpha=cfg.alpha,
            )
            benders = BendersDecomposition(
                windows=horizon_windows,
                tug_fleet=self.tug_fleet,
                berth_locations=self.berth_locations,
                cfg=b_cfg,
            )
            b_result = benders.solve()
            assignments = b_result.assignments

        return assignments, time.time() - t0

    def run(
        self,
        initial_state: PortState | None = None,
        simulate_until_h: float = 24.0,
    ) -> RollingHorizonResult:
        """Rolling Horizon 시뮬레이션 실행.

        Args:
            initial_state: 초기 PortState (None이면 빈 상태)
            simulate_until_h: 시뮬레이션 종료 시간 (hours)

        Returns:
            RollingHorizonResult
        """
        cfg = self.cfg
        t_global = time.time()

        current_time_h = 0.0
        assigned_ids: set[str] = set()
        all_assignments: list[SchedulingToRoutingSpec] = []
        decisions: list[DispatchDecision] = []

        step = 0
        while current_time_h <= simulate_until_h and step < cfg.max_steps:
            # 현재 horizon 내 미배정 선박
            horizon_windows = self._get_horizon_windows(current_time_h, assigned_ids)

            if horizon_windows:
                tier = self._select_tier(len(horizon_windows))
                assignments, solve_time = self._solve_step(horizon_windows, tier)

                # MPC: 첫 번째 결정만 적용
                # (여기서는 전체 horizon 결정을 적용 — 실시간 시스템에서는 첫 결정만)
                new_assigned = 0
                for spec in assignments:
                    if spec.vessel_id not in assigned_ids:
                        assigned_ids.add(spec.vessel_id)
                        all_assignments.append(spec)
                        new_assigned += 1

                decisions.append(DispatchDecision(
                    timestamp_h=current_time_h,
                    assignments=[a for a in assignments if a.vessel_id in assigned_ids],
                    solver_tier=tier,
                    solve_time_sec=solve_time,
                    n_vessels=len(horizon_windows),
                ))

            current_time_h += cfg.dt_h
            step += 1

            # 모든 선박 배정 완료 시 종료
            if len(assigned_ids) >= len(self.windows):
                break

        # 비용 집계
        waiting_cost = sum(
            spec.priority * max(0.0, spec.scheduled_start - spec.time_window.earliest_start) / 60.0
            for spec in all_assignments
        )
        fuel_cost = 0.0  # Tier 2/3에서는 별도 추적 필요

        total_cost = cfg.w1 * waiting_cost + cfg.w2 * fuel_cost
        elapsed = time.time() - t_global

        return RollingHorizonResult(
            decisions=decisions,
            total_assignments=all_assignments,
            total_waiting_cost=waiting_cost,
            total_fuel_cost=fuel_cost,
            total_cost=total_cost,
            steps=step,
            elapsed_sec=elapsed,
        )

    def step(
        self,
        current_state: PortState,
        assigned_ids: set[str],
    ) -> tuple[list[SchedulingToRoutingSpec], int]:
        """단일 타임스텝 실행 (MPC 인터페이스).

        Args:
            current_state: 현재 PortState
            assigned_ids: 이미 배정된 vessel_id 집합

        Returns:
            (new_assignments, tier)
        """
        current_time_h = current_state.current_time / 60.0
        horizon_windows = self._get_horizon_windows(current_time_h, assigned_ids)

        if not horizon_windows:
            return [], 0

        tier = self._select_tier(len(horizon_windows))
        assignments, _ = self._solve_step(horizon_windows, tier)
        return assignments, tier
