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
import time
import warnings
from collections import deque
from dataclasses import dataclass

import numpy as np
from scipy.optimize import differential_evolution

from libs.fuel.eco_speed import EcoSpeedOptimizer
from libs.utils.constants import DEPOT
from libs.utils.geo import haversine_nm
from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec

# ── 데이터 타입 ──────────────────────────────────────────────

@dataclass
class RouteResult:
    """ALNS 풀이 결과."""
    assignments: list[SchedulingToRoutingSpec]
    # tug_id → [DEPOT, job_id, ..., DEPOT]
    routes: dict[str, list[str]]
    arc_speeds: dict[tuple[str, str], float] # (from, to) → knots
    total_cost: float
    waiting_cost: float
    fuel_cost: float
    iterations: int
    converged: bool
    solve_time_sec: float = 0.0
    optimality_gap: float = 0.0              # ALNS heuristic → 0.0


@dataclass
class ALNSConfig:
    """ALNS 파라미터 설정 (config.yaml 오버라이드 가능)."""
    max_iter: int = 200          # 최대 내부 반복 수
    max_outer_iter: int = 20     # eco-speed alternating 최대 횟수
    tol: float = 0.001           # 수렴 임계값 (상대 오차)
    tol_window: int = 3          # oscillation 감지 window 크기
    temperature: float = 0.1     # SA 초기 온도 (acceptance)
    cooling: float = 0.995       # SA 냉각 비율
    destroy_fraction: float = 0.3  # 제거 비율 (Shaw 2019 권장)
    w1: float = 1.0              # 대기시간 가중치
    w2: float = 0.01             # 연료 가중치
    seed: int = 42               # 재현성 (AW-005)
    # Adaptive Weight (Ropke & Pisinger 2006)
    segment_size: int = 100      # 가중치 갱신 주기
    rho: float = 0.1             # 학습률
    # Shaw Destroy lambda (원논문 기본값; from_yaml() 또는 fit_shaw_lambdas()로 override)
    shaw_lambda_d: float = 0.5   # 거리 가중치 (Ropke & Pisinger 2006)
    shaw_lambda_t: float = 0.3   # 시간창 가중치
    shaw_lambda_p: float = 0.2   # 우선순위 가중치
    shaw_phi: float = 3.0        # randomness 지수

    @classmethod
    def from_yaml(
        cls,
        path: str = "configs/shaw_params.yaml",
        **kwargs,
    ) -> ALNSConfig:
        """YAML 파라미터 파일에서 Shaw lambda를 읽어 ALNSConfig 생성.

        YAML 파일 없으면 원논문 기본값(0.5, 0.3, 0.2) fallback.

        Args:
            path: shaw_params.yaml 경로 (scripts/fit_shaw_parameters.py 출력).
            **kwargs: 추가 필드 override (max_iter 등).

        Example:
            cfg = ALNSConfig.from_yaml()
            # configs/shaw_params.yaml 에서 lambda_d=0.0, lambda_t=1.0 등 로드
        """
        from libs.utils.param_loader import load_shaw_params

        p = load_shaw_params(path)
        return cls(
            shaw_lambda_d=p["lambda_d"],
            shaw_lambda_t=p["lambda_t"],
            shaw_lambda_p=p["lambda_p"],
            **kwargs,
        )


# Adaptive Weight 점수 상수 (Ropke & Pisinger 2006)
SCORE_NEW_BEST: int = 33     # σ1: 전체 최적해 갱신
SCORE_BETTER_CURR: int = 9   # σ2: 현재해 개선
SCORE_ACCEPTED: int = 3      # σ3: SA 수용 (개선 아님)
SCORE_REJECTED: int = 0      # 기각


@dataclass
class OperatorStats:
    """개별 연산자 성능 통계 (Adaptive Weight)."""
    weight: float = 1.0
    score_sum: float = 0.0
    usage_count: int = 0

    def record(self, score: int) -> None:
        """사용 횟수 및 점수 누적."""
        self.usage_count += 1
        self.score_sum += score

    def update_weight(self, rho: float) -> None:
        """세그먼트 종료 시 가중치 갱신 후 초기화.

        w ← (1-ρ)·w + ρ·(score_sum / usage_count)
        사용 없으면 weight 유지.
        """
        if self.usage_count > 0:
            self.weight = (
                (1 - rho) * self.weight
                + rho * (self.score_sum / self.usage_count)
            )
        self.score_sum = 0.0
        self.usage_count = 0


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


def destroy_shaw(
    routes: dict[str, list[str]],
    windows: list[TimeWindowSpec],
    fraction: float,
    distances: dict[tuple[str, str], float],
    rng: random.Random,
    lambda_d: float = 0.5,
    lambda_t: float = 0.3,
    lambda_p: float = 0.2,
    phi: float = 3.0,
) -> tuple[dict[str, list[str]], list[str]]:
    """D3: Shaw relatedness destroy (Shaw 1998).

    relatedness(j*, j) =
      λ_d·(d_{j*,j}/d_max) + λ_t·(|e_{j*}-e_j|/T)
      + λ_p·(|p_{j*}-p_j|/P_max)
    선택 확률 ∝ relatedness^phi (유사한 job 우선 제거).
    O(n²).
    """
    wmap = {w.vessel_id: w for w in windows}
    all_jobs = [j for route in routes.values() for j in route if j != DEPOT]
    if not all_jobs:
        return routes, []

    n_remove = max(1, int(len(all_jobs) * fraction))

    # 정규화 기준값
    d_max = max(
        (distances.get((i, j), 0.0)
         for i in all_jobs for j in all_jobs if i != j),
        default=1.0,
    )
    d_max = max(d_max, 1e-9)  # ZeroDivisionError 방지 (동일 좌표 시)
    t_max = max((wmap[j].earliest_start for j in all_jobs), default=1.0) - \
            min((wmap[j].earliest_start for j in all_jobs), default=0.0)
    p_max = max((wmap[j].priority for j in all_jobs), default=1)
    t_max = max(t_max, 1.0)

    # seed job 무작위 선택
    seed_job = rng.choice(all_jobs)
    removed: list[str] = [seed_job]
    remaining = [j for j in all_jobs if j != seed_job]

    while len(removed) < n_remove and remaining:
        last = removed[-1]
        w_last = wmap[last]
        # relatedness 계산
        relatedness = []
        for j in remaining:
            w_j = wmap[j]
            d_norm = distances.get((last, j), 0.0) / d_max
            t_norm = abs(w_last.earliest_start - w_j.earliest_start) / t_max
            p_norm = abs(w_last.priority - w_j.priority) / max(p_max, 1)
            r = lambda_d * d_norm + lambda_t * t_norm + lambda_p * p_norm
            relatedness.append(r)

        # 확률적 선택: r^phi 가중
        weights = [r ** phi for r in relatedness]
        total_w = sum(weights)
        if total_w < 1e-12:
            chosen = rng.choice(remaining)
        else:
            cumulative = []
            s = 0.0
            for w in weights:
                s += w / total_w
                cumulative.append(s)
            rand = rng.random()
            chosen = remaining[-1]
            for idx, c in enumerate(cumulative):
                if rand <= c:
                    chosen = remaining[idx]
                    break

        removed.append(chosen)
        remaining.remove(chosen)

    # 경로에서 제거
    new_routes: dict[str, list[str]] = {}
    removed_set = set(removed)
    for tug_id, route in routes.items():
        new_routes[tug_id] = [n for n in route if n not in removed_set]
        if not new_routes[tug_id] or new_routes[tug_id][0] != DEPOT:
            new_routes[tug_id] = [DEPOT] + new_routes[tug_id]
        if new_routes[tug_id][-1] != DEPOT:
            new_routes[tug_id].append(DEPOT)

    return new_routes, removed


def destroy_time_window(
    routes: dict[str, list[str]],
    windows: list[TimeWindowSpec],
    fraction: float,
    rng: random.Random,
    window_width_min: float = 60.0,
) -> tuple[dict[str, list[str]], list[str]]:
    """D4: 혼잡 시간대 집중 제거.

    무작위 시각 t* 선정, [t*-w/2, t*+w/2] 내 job 제거. O(n).
    """
    wmap = {w.vessel_id: w for w in windows}
    all_jobs = [j for route in routes.values() for j in route if j != DEPOT]
    if not all_jobs:
        return routes, []

    t_min = min(wmap[j].earliest_start for j in all_jobs)
    t_max = max(wmap[j].latest_start for j in all_jobs)
    t_star = rng.uniform(t_min, t_max)
    half_w = window_width_min / 2.0

    candidates = [
        j for j in all_jobs
        if t_star - half_w <= wmap[j].earliest_start <= t_star + half_w
    ]
    n_remove = max(1, int(len(all_jobs) * fraction))
    removed = (
        candidates[:n_remove]
        if candidates
        else rng.sample(all_jobs, min(1, len(all_jobs)))
    )

    removed_set = set(removed)
    new_routes: dict[str, list[str]] = {}
    for tug_id, route in routes.items():
        new_routes[tug_id] = [n for n in route if n not in removed_set]
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
                cost = _estimate_route_cost(
                    candidate, wmap, distances, speeds, cfg
                )
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
            cost += (
                cfg.w1 * w.priority * wait_h
                + cfg.w2 * alpha * (v ** gamma) * d
            )
            current_time = start + w.service_duration
    return cost


def repair_regret2_insert(
    routes: dict[str, list[str]],
    removed_jobs: list[str],
    windows: list[TimeWindowSpec],
    distances: dict[tuple[str, str], float],
    speeds: dict[tuple[str, str], float],
    cfg: ALNSConfig,
    rng: random.Random,
) -> dict[str, list[str]]:
    """R2: Regret-2 삽입 (Potvin & Rousseau 1993).

    regret[j] = c2[j] - c1[j]  (2등 삽입비용 - 1등 삽입비용)
    regret 큰 순서로 삽입 → 기회비용 높은 job 우선 배치.
    O(n²·m·log n).
    """
    result = {k: list(v) for k, v in routes.items()}
    remaining = list(removed_jobs)

    while remaining:
        best_job = None
        best_insert: tuple[str, int] | None = None
        best_regret = -float("inf")

        for job in remaining:
            # 모든 (tug, position) 조합의 비용 계산
            insertion_costs: list[tuple[float, str, int]] = []
            for tug_id, route in result.items():
                for pos in range(1, len(route)):
                    candidate = route[:pos] + [job] + route[pos:]
                    cost = _estimate_route_cost(
                        candidate, {w.vessel_id: w for w in windows},
                        distances, speeds, cfg
                    )
                    insertion_costs.append((cost, tug_id, pos))

            if not insertion_costs:
                continue

            insertion_costs.sort(key=lambda x: x[0])
            c1 = insertion_costs[0][0]
            c2 = insertion_costs[1][0] if len(insertion_costs) > 1 else c1
            regret = c2 - c1

            if regret > best_regret:
                best_regret = regret
                best_job = job
                _, best_tug, best_pos = insertion_costs[0]
                best_insert = (best_tug, best_pos)

        if best_job is None or best_insert is None:
            # fallback: 무작위 삽입
            job = rng.choice(remaining)
            tug_id = rng.choice(list(result.keys()))
            result[tug_id].insert(1, job)
            remaining.remove(job)
        else:
            tug_id, pos = best_insert
            result[tug_id].insert(pos, best_job)
            remaining.remove(best_job)

    return result


# ── 초기해 생성 ───────────────────────────────────────────────

def greedy_initial_solution(
    windows: list[TimeWindowSpec],
    tug_fleet: list[str],
    distances: dict[tuple[str, str], float],
) -> dict[str, list[str]]:
    """earliest_start 오름차순으로 예인선에 순차 배정 (초기해)."""
    routes: dict[str, list[str]] = {k: [DEPOT] for k in tug_fleet}
    tug_free_at = dict.fromkeys(tug_fleet, 0.0)

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


def fit_shaw_lambdas(
    windows: list[TimeWindowSpec],
    assignments: dict[str, list[str]],
    distances: dict[tuple[str, str], float],
    seed: int = 42,
) -> tuple[float, float, float]:
    """Shaw Destroy 가중치 (λ_d, λ_t, λ_p)를 역사적 데이터로 피팅.

    같은 예인선에 순차 배정된 작업 쌍(similar)과 다른 예인선 쌍(dissimilar)의
    relatedness 분리도를 최대화하도록 λ를 최적화한다.

    피팅 데이터가 부족(N<10)하면 원논문 기본값 (0.5, 0.3, 0.2) 반환.

    부산항 실측값 (2024-06, N=336, ADR-002):
        λ_d=0.000, λ_t=1.000, λ_p=0.000 (시간창이 지배적)

    Args:
        windows: 작업 time window 목록.
        assignments: 예인선별 배정 vessel_id 리스트 (DEPOT 포함 무방).
        distances: (vessel_i, vessel_j) → 거리(nm) 딕셔너리.
        seed: 재현성 시드.

    Returns:
        (lambda_d, lambda_t, lambda_p) — 합계 = 1.0.
    """
    _DEFAULTS = (0.5, 0.3, 0.2)  # 원논문 Ropke & Pisinger 2006

    # 인덱스 맵
    win_map = {w.vessel_id: w for w in windows}
    T_max = max((w.latest_start for w in windows), default=1.0) or 1.0
    P_max = max((w.priority for w in windows), default=1) or 1

    # similar 쌍: 같은 예인선 내 순차 작업
    pairs_same: list[tuple[float, float, float]] = []
    for tug_id, route in assignments.items():
        jobs = [v for v in route if v != DEPOT and v in win_map]
        for i in range(len(jobs) - 1):
            a, b = win_map[jobs[i]], win_map[jobs[i + 1]]
            d = distances.get((a.vessel_id, b.vessel_id),
                              distances.get((b.vessel_id, a.vessel_id), 0.0))
            t = abs(a.earliest_start - b.earliest_start)
            p = abs(a.priority - b.priority)
            pairs_same.append((d, t, float(p)))

    if len(pairs_same) < 5:
        return _DEFAULTS

    # dissimilar 쌍: 다른 예인선 작업 (동수 샘플링)
    rng = np.random.default_rng(seed)
    all_routes = [
        [v for v in route if v != DEPOT and v in win_map]
        for route in assignments.values()
        if len([v for v in route if v != DEPOT and v in win_map]) > 0
    ]
    pairs_diff: list[tuple[float, float, float]] = []
    for _ in range(len(pairs_same)):
        if len(all_routes) < 2:
            break
        r1_idx, r2_idx = rng.choice(len(all_routes), 2, replace=False)
        a = win_map[all_routes[r1_idx][rng.integers(len(all_routes[r1_idx]))]]
        b = win_map[all_routes[r2_idx][rng.integers(len(all_routes[r2_idx]))]]
        d = distances.get((a.vessel_id, b.vessel_id),
                          distances.get((b.vessel_id, a.vessel_id), 0.0))
        t = abs(a.earliest_start - b.earliest_start)
        p = abs(a.priority - b.priority)
        pairs_diff.append((d, t, float(p)))

    if not pairs_diff:
        return _DEFAULTS

    arr = np.array(pairs_same + pairs_diff, dtype=float)
    labels = np.array([1] * len(pairs_same) + [0] * len(pairs_diff))

    d_max = arr[:, 0].max() or 1.0
    t_max = arr[:, 1].max() or T_max
    p_max = arr[:, 2].max() or float(P_max)
    arr_n = arr / np.array([d_max, t_max, p_max])

    def _loss(lam12: np.ndarray) -> float:
        l1, l2 = lam12
        l3 = 1.0 - l1 - l2
        if l3 < 0.0:
            return 1e9
        r = arr_n @ np.array([l1, l2, l3])
        return -(r[labels == 0].mean() - r[labels == 1].mean())

    result = differential_evolution(
        _loss, bounds=[(0.0, 1.0), (0.0, 1.0)], seed=int(seed), maxiter=300
    )
    l1, l2 = float(result.x[0]), float(result.x[1])
    l3 = max(0.0, 1.0 - l1 - l2)
    # 정규화
    total = l1 + l2 + l3 or 1.0
    return round(l1 / total, 4), round(l2 / total, 4), round(l3 / total, 4)


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
        locs: dict[str, tuple[float, float]] = {
            DEPOT: list(self.berth_locations.values())[0]
        }
        for w in self.windows:
            locs[w.vessel_id] = self.berth_locations[w.berth_id]

        nodes = [DEPOT] + [w.vessel_id for w in self.windows]
        dist: dict[tuple[str, str], float] = {}
        for i in nodes:
            for j in nodes:
                dist[(i, j)] = (
                    0.0 if i == j
                    else haversine_nm(locs[i], locs[j])
                )
        return dist

    def _all_arcs(self, routes: dict[str, list[str]]) -> list[tuple[str, str]]:
        """경로에서 모든 아크를 추출."""
        arcs = []
        for route in routes.values():
            for i in range(len(route) - 1):
                arcs.append((route[i], route[i + 1]))
        return arcs

    def _roulette_select(
        self, stats: list[OperatorStats]
    ) -> int:
        """가중치 기반 roulette wheel 선택 → 인덱스 반환."""
        total = sum(s.weight for s in stats)
        if total < 1e-12:
            return self._rng.randrange(len(stats))
        rand = self._rng.random() * total
        cumulative = 0.0
        for idx, s in enumerate(stats):
            cumulative += s.weight
            if rand <= cumulative:
                return idx
        return len(stats) - 1

    def _inner_alns(
        self,
        routes: dict[str, list[str]],
        speeds: dict[tuple[str, str], float],
    ) -> dict[str, list[str]]:
        """ALNS 내부 루프: Destroy → Repair → Accept (SA) + Adaptive Weight.

        Destroy 연산자: D1(random), D2(worst), D3(shaw), D4(time_window)
        Repair 연산자:  R1(greedy), R2(regret2)
        선택: Roulette wheel (segment_size마다 가중치 갱신)
        """
        cfg = self.cfg
        current = {k: list(v) for k, v in routes.items()}
        current_cost, _, _ = compute_cost(
            current, self.windows, self._distances, speeds, cfg
        )
        best = {k: list(v) for k, v in current.items()}
        best_cost = current_cost

        temperature = cfg.temperature

        # Adaptive Weight 통계 초기화 (D1~D4, R1~R2)
        d_stats = [OperatorStats() for _ in range(4)]
        r_stats = [OperatorStats() for _ in range(2)]

        for iteration in range(cfg.max_iter):
            # ── Destroy 선택 (roulette) ──
            d_idx = self._roulette_select(d_stats)
            if d_idx == 0:
                destroyed, removed = destroy_random(
                    current, self.windows, cfg.destroy_fraction, self._rng
                )
            elif d_idx == 1:
                destroyed, removed = destroy_worst(
                    current, self.windows, cfg.destroy_fraction,
                    self._distances, speeds, cfg, self._rng
                )
            elif d_idx == 2:
                destroyed, removed = destroy_shaw(
                    current, self.windows, cfg.destroy_fraction,
                    self._distances, self._rng,
                    lambda_d=cfg.shaw_lambda_d,
                    lambda_t=cfg.shaw_lambda_t,
                    lambda_p=cfg.shaw_lambda_p,
                    phi=cfg.shaw_phi,
                )
            else:
                destroyed, removed = destroy_time_window(
                    current, self.windows, cfg.destroy_fraction, self._rng
                )

            # ── Repair 선택 (roulette) ──
            r_idx = self._roulette_select(r_stats)
            if r_idx == 0:
                repaired = repair_greedy_insert(
                    destroyed, removed, self.windows,
                    self._distances, speeds, cfg, self._rng
                )
            else:
                repaired = repair_regret2_insert(
                    destroyed, removed, self.windows,
                    self._distances, speeds, cfg, self._rng
                )

            new_cost, _, _ = compute_cost(
                repaired, self.windows, self._distances, speeds, cfg
            )

            # ── SA 수용 및 점수 결정 ──
            delta = new_cost - current_cost
            accepted = (
                delta < 0
                or self._rng.random()
                < math.exp(-delta / max(temperature, 1e-10))
            )

            if new_cost < best_cost:
                score = SCORE_NEW_BEST
                best = {k: list(v) for k, v in repaired.items()}
                best_cost = new_cost
            elif accepted and new_cost < current_cost:
                score = SCORE_BETTER_CURR
            elif accepted:
                score = SCORE_ACCEPTED
            else:
                score = SCORE_REJECTED

            if accepted:
                current = repaired
                current_cost = new_cost

            d_stats[d_idx].record(score)
            r_stats[r_idx].record(score)
            temperature *= cfg.cooling

            # ── 세그먼트 종료: 가중치 갱신 ──
            if (iteration + 1) % cfg.segment_size == 0:
                for s in d_stats:
                    s.update_weight(cfg.rho)
                for s in r_stats:
                    s.update_weight(cfg.rho)

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
        _t0 = time.perf_counter()
        # window 평균 수렴 판단 (oscillation 완화)
        cost_window: deque[float] = deque(maxlen=cfg.tol_window)
        cost_window.append(prev_cost)

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
            cost_window.append(new_cost)

            # window 평균 수렴 체크
            # (단일 비교 대신 window 평균으로 oscillation 완화)
            if len(cost_window) >= cfg.tol_window:
                avg_prev = sum(list(cost_window)[:-1]) / (len(cost_window) - 1)
                rel_change = (
                    abs(new_cost - avg_prev) / max(abs(avg_prev), 1e-10)
                )
                if rel_change < cfg.tol:
                    converged = True
                    break

            prev_cost = new_cost

        _solve_time = time.perf_counter() - _t0
        if not converged:
            warnings.warn(
                f"ALNSWithSpeedOptimizer: "
                f"{cfg.max_outer_iter}회 outer iteration 후 "
                f"수렴 미달 (마지막 cost={prev_cost:.4f}). "
                "converged=False로 RouteResult 반환.",
                stacklevel=2,
            )

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
            solve_time_sec=_solve_time,
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
