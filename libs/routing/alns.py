"""
ALNS (Adaptive Large Neighborhood Search) — Phase 2 Step 2.

Ropke & Pisinger (2006) 기반 ALNS with eco-speed alternating loop.

알고리즘:
1. Greedy 초기해 생성
2. ALNS 내부 루프 (destroy → repair → accept)
3. EcoSpeedOptimizer.optimize()로 속도 재최적화 (outer loop)
4. 수렴 조건: |Δobjective| < tol (상대 오차)

참조:
  - Ropke & Pisinger (2006), Transportation Science: ALNS for PDPTW
  - phase2-strategy-v3.md: ALNSWithSpeedOptimizer pseudocode

Tier 2 적용: n=10~50 선박, m=5~20 예인선
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable

from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec
from libs.fuel.eco_speed import EcoSpeedOptimizer, SpeedSolution

# Depot 노드 ID
DEPOT = "__depot__"


# ── 데이터 타입 ──────────────────────────────────────────────

@dataclass
class RouteResult:
    """ALNS 풀이 결과."""
    assignments: list[SchedulingToRoutingSpec]
    routes: dict[str, list[str]]             # tug_id → [DEPOT, job_id, ..., DEPOT]
    arc_speeds: dict[tuple[str, str], float] # (from, to) → knots
    total_cost: float
    waiting_cost: float
    fuel_cost: float
    iterations: int
    converged: bool


@dataclass
class ALNSConfig:
    """ALNS 파라미터 설정 (config.yaml 오버라이드 가능)."""
    max_iter: int = 200          # 최대 내부 반복 수
    max_outer_iter: int = 20     # eco-speed alternating 최대 횟수
    tol: float = 0.001           # 수렴 임계값 (상대 오차)
    temperature: float = 0.1     # SA 초기 온도 (acceptance)
    cooling: float = 0.995       # SA 냉각 비율
    destroy_fraction: float = 0.3  # 제거 비율 (Shaw 2019 권장)
    w1: float = 1.0              # 대기시간 가중치
    w2: float = 0.01             # 연료 가중치
    seed: int = 42               # 재현성 (AW-005)


# ── 비용 함수 ─────────────────────────────────────────────────

def compute_cost(
    routes: dict[str, list[str]],
    windows: list[TimeWindowSpec],
    distances: dict[tuple[str, str], float],
    speeds: dict[tuple[str, str], float],
    cfg: ALNSConfig,
    alpha: float = 0.5,
    gamma: float = 2.5,
) -> tuple[float, float, float]:
    """총 비용 = w1·대기 + w2·연료를 반환.

    Returns:
        (total_cost, waiting_cost, fuel_cost)
    """
    wmap = {w.vessel_id: w for w in windows}
    waiting_cost = 0.0
    fuel_cost = 0.0

    for tug_id, route in routes.items():
        current_time = 0.0
        for i in range(len(route) - 1):
            from_node = route[i]
            to_node = route[i + 1]
            if to_node == DEPOT:
                continue
            arc = (from_node, to_node)
            d = distances.get(arc, 0.0)
            v = speeds.get(arc, 10.0)
            travel_min = (d / v * 60.0) if v > 0 else 0.0

            if from_node == DEPOT:
                arrival = travel_min
            else:
                arrival = current_time + travel_min

            w = wmap.get(to_node)
            if w:
                start = max(arrival, w.earliest_start)
                wait_h = max(0.0, start - w.earliest_start) / 60.0
                waiting_cost += w.priority * wait_h
                fuel_cost += alpha * (v ** gamma) * d
                current_time = start + w.service_duration

    total = cfg.w1 * waiting_cost + cfg.w2 * fuel_cost
    return total, waiting_cost, fuel_cost


# ── Destroy 연산자 ────────────────────────────────────────────

def destroy_random(
    routes: dict[str, list[str]],
    windows: list[TimeWindowSpec],
    fraction: float,
    rng: random.Random,
) -> tuple[dict[str, list[str]], list[str]]:
    """무작위 job 제거."""
    all_jobs = [j for jobs in routes.values() for j in jobs if j != DEPOT]
    n_remove = max(1, int(len(all_jobs) * fraction))
    removed = rng.sample(all_jobs, min(n_remove, len(all_jobs)))

    new_routes: dict[str, list[str]] = {}
    for tug_id, route in routes.items():
        new_routes[tug_id] = [n for n in route if n not in removed]
        # depot 보장
        if not new_routes[tug_id] or new_routes[tug_id][0] != DEPOT:
            new_routes[tug_id] = [DEPOT] + new_routes[tug_id]
        if new_routes[tug_id][-1] != DEPOT:
            new_routes[tug_id].append(DEPOT)

    return new_routes, removed


def destroy_worst(
    routes: dict[str, list[str]],
    windows: list[TimeWindowSpec],
    fraction: float,
    distances: dict[tuple[str, str], float],
    speeds: dict[tuple[str, str], float],
    cfg: ALNSConfig,
    rng: random.Random,
) -> tuple[dict[str, list[str]], list[str]]:
    """가장 높은 대기시간을 유발하는 job 제거."""
    wmap = {w.vessel_id: w for w in windows}
    job_costs: list[tuple[str, float]] = []

    for tug_id, route in routes.items():
        current_time = 0.0
        for i in range(len(route) - 1):
            to_node = route[i + 1]
            if to_node == DEPOT:
                continue
            from_node = route[i]
            arc = (from_node, to_node)
            d = distances.get(arc, 0.0)
            v = speeds.get(arc, 10.0)
            travel_min = (d / v * 60.0) if v > 0 else 0.0
            arrival = (travel_min if from_node == DEPOT
                       else current_time + travel_min)
            w = wmap.get(to_node)
            if w:
                start = max(arrival, w.earliest_start)
                wait_h = max(0.0, start - w.earliest_start) / 60.0
                job_costs.append((to_node, w.priority * wait_h))
                current_time = start + w.service_duration

    job_costs.sort(key=lambda x: -x[1])
    n_remove = max(1, int(len(job_costs) * fraction))
    removed = [j for j, _ in job_costs[:n_remove]]

    new_routes: dict[str, list[str]] = {}
    for tug_id, route in routes.items():
        new_routes[tug_id] = [n for n in route if n not in removed]
        if not new_routes[tug_id] or new_routes[tug_id][0] != DEPOT:
            new_routes[tug_id] = [DEPOT] + new_routes[tug_id]
        if new_routes[tug_id][-1] != DEPOT:
            new_routes[tug_id].append(DEPOT)

    return new_routes, removed


# ── Repair 연산자 ─────────────────────────────────────────────

def repair_greedy_insert(
    routes: dict[str, list[str]],
    removed_jobs: list[str],
    windows: list[TimeWindowSpec],
    distances: dict[tuple[str, str], float],
    speeds: dict[tuple[str, str], float],
    cfg: ALNSConfig,
    rng: random.Random,
) -> dict[str, list[str]]:
    """그리디 삽입: 각 제거된 job을 비용이 최소인 위치에 삽입."""
    wmap = {w.vessel_id: w for w in windows}
    result = {k: list(v) for k, v in routes.items()}

    # 무작위 순서로 삽입
    shuffled = list(removed_jobs)
    rng.shuffle(shuffled)

    for job in shuffled:
        best_cost = float("inf")
        best_tug = None
        best_pos = None

        for tug_id, route in result.items():
            for pos in range(1, len(route)):  # depot 이후 위치
                # 삽입 후 비용 추정 (해당 tug 경로만)
                candidate = route[:pos] + [job] + route[pos:]
                cost = _estimate_route_cost(candidate, wmap, distances, speeds, cfg)
                if cost < best_cost:
                    best_cost = cost
                    best_tug = tug_id
                    best_pos = pos

        if best_tug is not None:
            result[best_tug].insert(best_pos, job)

    return result


def _estimate_route_cost(
    route: list[str],
    wmap: dict[str, TimeWindowSpec],
    distances: dict[tuple[str, str], float],
    speeds: dict[tuple[str, str], float],
    cfg: ALNSConfig,
    alpha: float = 0.5,
    gamma: float = 2.5,
) -> float:
    """단일 경로의 비용 추정."""
    cost = 0.0
    current_time = 0.0
    for i in range(len(route) - 1):
        from_node, to_node = route[i], route[i + 1]
        if to_node == DEPOT:
            continue
        arc = (from_node, to_node)
        d = distances.get(arc, 0.0)
        v = speeds.get(arc, 10.0)
        travel_min = (d / v * 60.0) if v > 0 else 0.0
        arrival = (travel_min if from_node == DEPOT
                   else current_time + travel_min)
        w = wmap.get(to_node)
        if w:
            start = max(arrival, w.earliest_start)
            wait_h = max(0.0, start - w.earliest_start) / 60.0
            cost += cfg.w1 * w.priority * wait_h + cfg.w2 * alpha * (v ** gamma) * d
            current_time = start + w.service_duration
    return cost


# ── 초기해 생성 ───────────────────────────────────────────────

def greedy_initial_solution(
    windows: list[TimeWindowSpec],
    tug_fleet: list[str],
    distances: dict[tuple[str, str], float],
) -> dict[str, list[str]]:
    """earliest_start 오름차순으로 예인선에 순차 배정 (초기해)."""
    routes: dict[str, list[str]] = {k: [DEPOT] for k in tug_fleet}
    tug_free_at = {k: 0.0 for k in tug_fleet}

    sorted_jobs = sorted(windows, key=lambda w: w.earliest_start)
    for w in sorted_jobs:
        # 가장 빨리 가용한 예인선
        k = min(tug_free_at, key=tug_free_at.get)  # type: ignore
        routes[k].append(w.vessel_id)
        prev = routes[k][-2]  # 이전 노드
        arc = (prev, w.vessel_id)
        d = distances.get(arc, 0.0)
        travel_min = d / 10.0 * 60.0  # eco-speed 10kn
        arrival = tug_free_at[k] + travel_min
        start = max(arrival, w.earliest_start)
        tug_free_at[k] = start + w.service_duration

    for k in tug_fleet:
        routes[k].append(DEPOT)

    return routes


# ── 메인 ALNS 클래스 ──────────────────────────────────────────

class ALNSWithSpeedOptimizer:
    """ALNS + EcoSpeedOptimizer alternating loop.

    Phase 2 Step 2 (Tier 2, n=10~50).

    알고리즘 (phase2-strategy-v3.md pseudocode):
        speeds = EcoSpeedOptimizer.compute_initial(routes)
        for outer_iter in range(max_outer_iter):
            routes = ALNS_inner(instance, fixed_speeds=speeds, max_iter)
            new_speeds = EcoSpeedOptimizer.optimize(routes)
            if |Δobjective| / objective < tol:
                break
            speeds = new_speeds
        return RouteResult(routes, speeds)

    성공 기준:
        - Solomon R101(25 node) BKS 대비 5% 이내
        - n=30 인스턴스 5분 이내 수렴
        - max_outer_iter=20 이내 수렴 (tol=0.001)
    """

    def __init__(
        self,
        windows: list[TimeWindowSpec],
        tug_fleet: list[str],
        berth_locations: dict[str, tuple[float, float]],
        eco_speed_optimizer: EcoSpeedOptimizer | None = None,
        cfg: ALNSConfig | None = None,
    ) -> None:
        self.windows = windows
        self.tug_fleet = tug_fleet
        self.berth_locations = berth_locations
        self.cfg = cfg or ALNSConfig()
        self.eco = eco_speed_optimizer or EcoSpeedOptimizer()
        self._wmap = {w.vessel_id: w for w in windows}
        self._rng = random.Random(self.cfg.seed)
        self._distances = self._build_distances()

    def _build_distances(self) -> dict[tuple[str, str], float]:
        """구간별 거리 행렬 (해리, Haversine)."""
        from libs.scheduling.tsp_t_milp import _haversine_nm

        locs: dict[str, tuple[float, float]] = {DEPOT: list(self.berth_locations.values())[0]}
        for w in self.windows:
            locs[w.vessel_id] = self.berth_locations[w.berth_id]

        nodes = [DEPOT] + [w.vessel_id for w in self.windows]
        dist: dict[tuple[str, str], float] = {}
        for i in nodes:
            for j in nodes:
                dist[(i, j)] = 0.0 if i == j else _haversine_nm(locs[i], locs[j])
        return dist

    def _all_arcs(self, routes: dict[str, list[str]]) -> list[tuple[str, str]]:
        """경로에서 모든 아크를 추출."""
        arcs = []
        for route in routes.values():
            for i in range(len(route) - 1):
                arcs.append((route[i], route[i + 1]))
        return arcs

    def _inner_alns(
        self,
        routes: dict[str, list[str]],
        speeds: dict[tuple[str, str], float],
    ) -> dict[str, list[str]]:
        """ALNS 내부 루프: Destroy → Repair → Accept (SA)."""
        cfg = self.cfg
        current = {k: list(v) for k, v in routes.items()}
        current_cost, _, _ = compute_cost(
            current, self.windows, self._distances, speeds, cfg
        )
        best = {k: list(v) for k, v in current.items()}
        best_cost = current_cost

        temperature = cfg.temperature

        for _ in range(cfg.max_iter):
            # Destroy (adaptive: 50% random, 50% worst)
            if self._rng.random() < 0.5:
                destroyed, removed = destroy_random(
                    current, self.windows, cfg.destroy_fraction, self._rng
                )
            else:
                destroyed, removed = destroy_worst(
                    current, self.windows, cfg.destroy_fraction,
                    self._distances, speeds, cfg, self._rng
                )

            # Repair
            repaired = repair_greedy_insert(
                destroyed, removed, self.windows,
                self._distances, speeds, cfg, self._rng
            )

            new_cost, _, _ = compute_cost(
                repaired, self.windows, self._distances, speeds, cfg
            )

            # Simulated Annealing 수용
            delta = new_cost - current_cost
            if delta < 0 or self._rng.random() < math.exp(-delta / max(temperature, 1e-10)):
                current = repaired
                current_cost = new_cost

                if current_cost < best_cost:
                    best = {k: list(v) for k, v in current.items()}
                    best_cost = current_cost

            temperature *= cfg.cooling

        return best

    def solve(self) -> RouteResult:
        """ALNS + eco-speed alternating loop 실행.

        Returns:
            RouteResult (배정, 경로, 속도, 비용)
        """
        cfg = self.cfg

        # 초기해
        routes = greedy_initial_solution(
            self.windows, self.tug_fleet, self._distances
        )
        arcs = self._all_arcs(routes)
        speed_sol = self.eco.compute_initial(arcs)
        speeds = speed_sol.speeds

        prev_cost, _, _ = compute_cost(
            routes, self.windows, self._distances, speeds, cfg
        )

        converged = False
        for outer_iter in range(cfg.max_outer_iter):
            # ALNS 내부 루프 (speed 고정)
            routes = self._inner_alns(routes, speeds)

            # 속도 재최적화 (배정 고정)
            arcs = self._all_arcs(routes)
            time_budgets = self._compute_time_budgets(routes, speeds)
            speed_sol = self.eco.optimize(arcs, self._distances, time_budgets)
            speeds = speed_sol.speeds

            new_cost, _, _ = compute_cost(
                routes, self.windows, self._distances, speeds, cfg
            )

            # 수렴 체크 (상대 오차)
            rel_change = abs(new_cost - prev_cost) / max(abs(prev_cost), 1e-10)
            if rel_change < cfg.tol:
                converged = True
                break

            prev_cost = new_cost

        # 최종 비용 계산
        total_cost, waiting_cost, fuel_cost = compute_cost(
            routes, self.windows, self._distances, speeds, cfg
        )

        # SchedulingToRoutingSpec 생성
        assignments = self._build_assignments(routes, speeds)

        return RouteResult(
            assignments=assignments,
            routes=routes,
            arc_speeds=speeds,
            total_cost=total_cost,
            waiting_cost=waiting_cost,
            fuel_cost=fuel_cost,
            iterations=outer_iter + 1,
            converged=converged,
        )

    def _compute_time_budgets(
        self,
        routes: dict[str, list[str]],
        speeds: dict[tuple[str, str], float],
    ) -> dict[tuple[str, str], float]:
        """시간창 기반 이동 허용 시간 계산 (eco-speed 최적화용)."""
        budgets: dict[tuple[str, str], float] = {}
        for tug_id, route in routes.items():
            current_time = 0.0
            for i in range(len(route) - 1):
                from_node, to_node = route[i], route[i + 1]
                if to_node == DEPOT:
                    continue
                arc = (from_node, to_node)
                d = self._distances.get(arc, 0.0)
                v = speeds.get(arc, self.eco.v_eco)
                travel_min = (d / v * 60.0) if v > 0 else 0.0
                arrival = (travel_min if from_node == DEPOT
                           else current_time + travel_min)
                w = self._wmap.get(to_node)
                if w:
                    # 허용 이동시간 = latest_start - current_time (hours)
                    budget_h = max(0.1, (w.latest_start - current_time) / 60.0)
                    budgets[arc] = budget_h
                    start = max(arrival, w.earliest_start)
                    current_time = start + w.service_duration
        return budgets

    def _build_assignments(
        self,
        routes: dict[str, list[str]],
        speeds: dict[tuple[str, str], float],
    ) -> list[SchedulingToRoutingSpec]:
        """RouteResult → SchedulingToRoutingSpec 리스트 변환."""
        assignments = []
        for tug_id, route in routes.items():
            current_time = 0.0
            for i in range(len(route) - 1):
                from_node, to_node = route[i], route[i + 1]
                if to_node == DEPOT:
                    continue
                arc = (from_node, to_node)
                d = self._distances.get(arc, 0.0)
                v = speeds.get(arc, self.eco.v_eco)
                travel_min = (d / v * 60.0) if v > 0 else 0.0
                arrival = (travel_min if from_node == DEPOT
                           else current_time + travel_min)
                w = self._wmap.get(to_node)
                if w:
                    start = max(arrival, w.earliest_start)
                    spec = SchedulingToRoutingSpec(
                        vessel_id=to_node,
                        tug_id=tug_id,
                        pickup_location=self.berth_locations[w.berth_id],
                        dropoff_location=self.berth_locations[w.berth_id],
                        time_window=w,
                        scheduled_start=start,
                        required_tugs=1,
                        priority=w.priority,
                    )
                    assignments.append(spec)
                    current_time = start + w.service_duration
        return assignments
