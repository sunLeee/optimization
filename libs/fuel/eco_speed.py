"""
EcoSpeedOptimizer — 예인선 속도 최적화 모듈 (Step 2).

F(v, d) = alpha * v^gamma * d  (gamma=2.5, AW-006)

ALNS alternating loop에서 배정(x) 고정 후 속도(v)를 CVXPY GP로 최적화.
Tier 2(n=10~50) 전용. Step 1에서는 F=alpha*d (speed 고정) 사용.

참조:
  - Psaraftis & Kontovas (2013), TRC: speed models for maritime transportation
  - phase2-strategy-v3.md: eco-speed alternating 전략
"""
from __future__ import annotations

from dataclasses import dataclass

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

try:
    import cvxpy as cp
    _HAS_CVXPY = True
except ImportError:
    _HAS_CVXPY = False


@dataclass
class SpeedSolution:
    """속도 최적화 결과."""
    speeds: dict[tuple[str, str], float]  # (from_job, to_job) → speed (knots)
    total_fuel: float                     # 총 연료 소비 (metric tons)
    # "optimal" | "infeasible" | "solver_error"
    status: str


class EcoSpeedOptimizer:
    """예인선 구간별 eco-speed 최적화.

    ALNS outer loop에서 배정(x_ij)이 고정되면,
    각 구간의 속도 v_ij를 CVXPY GP로 최적화한다.

    목적함수: min Σ alpha * v_ij^2.5 * d_ij   (γ=2.5)
    제약:     v_min ≤ v_ij ≤ v_max
              d_ij / v_ij ≤ time_budget_ij     (시간창 내 이동 완료)

    d/v 항은 CVXPY DCP 규칙에 따라 d * cp.inv_pos(v) 로 변환.

    사용 예:
        eco = EcoSpeedOptimizer(alpha=0.5, gamma=2.5)
        speeds = eco.compute_initial(windows)
        # ALNS 후
        speeds = eco.optimize(routes, distances)
    """

    def __init__(
        self,
        alpha: float = 0.5,     # 연료 계수 (MT/nm, vessel-specific)
        gamma: float = 2.5,     # 속도 지수 (AW-006)
        v_min: float = 4.0,     # 최소 속도 (knots)
        v_max: float = 14.0,    # 최대 속도 (knots)
        v_eco: float = 10.0,    # eco-speed 기본값 (초기화용)
    ) -> None:
        self.alpha = alpha
        self.gamma = gamma
        self.v_min = v_min
        self.v_max = v_max
        self.v_eco = v_eco

        if not _HAS_NUMPY:
            raise ImportError("numpy가 필요합니다.")

    def compute_initial(
        self,
        routes: list[tuple[str, str]],  # (from_job_id, to_job_id) 순서쌍
    ) -> SpeedSolution:
        """초기 eco-speed: 모든 구간을 v_eco (고정값)으로 설정.

        ALNS alternating loop 첫 번째 반복에서 호출.

        Args:
            routes: 예인선 이동 구간 목록. DEPOT 포함 가능.

        Returns:
            SpeedSolution (speeds: 모든 구간 = v_eco)
        """
        speeds = {arc: self.v_eco for arc in routes}
        total_fuel = 0.0  # 거리 미반영 초기값
        return SpeedSolution(
            speeds=speeds, total_fuel=total_fuel, status="initial"
        )

    def optimize(
        self,
        routes: list[tuple[str, str]],        # 활성 구간 (from, to)
        distances: dict[tuple[str, str], float],  # (from, to) → 거리 (nm)
        # 이동 허용 시간 (hours)
        time_budgets: dict[tuple[str, str], float] | None = None,
    ) -> SpeedSolution:
        """CVXPY GP로 구간별 최적 속도 계산.

        F = alpha * v^gamma * d  (γ=2.5, posynomial → GP 가능)
        v_min ≤ v ≤ v_max
        d/v ≤ t_budget  (→ d * inv_pos(v) ≤ t_budget, DCP 변환)

        Args:
            routes: 활성 구간 (from_id, to_id)
            distances: 구간별 거리 (해리)
            time_budgets: 구간별 이동 허용 시간 (hours). None이면 제약 없음.

        Returns:
            SpeedSolution
        """
        if not _HAS_CVXPY:
            # CVXPY 미설치 시 eco-speed 고정으로 폴백
            return self._fallback_eco_speed(routes, distances)

        if not routes:
            return SpeedSolution(speeds={}, total_fuel=0.0, status="optimal")

        # 구간 목록 (거리 > 0인 구간만)
        active_arcs = [
            arc for arc in routes
            if distances.get(arc, 0.0) > 1e-6
        ]

        if not active_arcs:
            return SpeedSolution(speeds={arc: self.v_eco for arc in routes},
                                  total_fuel=0.0, status="optimal")

        n = len(active_arcs)
        arc_idx = {arc: i for i, arc in enumerate(active_arcs)}

        # CVXPY 변수: v[i] = 구간 i의 속도 (knots)
        v = cp.Variable(n, pos=True)  # GP requires pos=True

        # 목적함수: Σ alpha * v_i^gamma * d_i
        # = alpha * Σ d_i * v_i^gamma
        # gamma=2.5: posynomial (GP standard form)
        d_vals = np.array([distances[arc] for arc in active_arcs])
        fuel_terms = self.alpha * cp.sum(
            cp.multiply(d_vals, cp.power(v, self.gamma))
        )
        objective = cp.Minimize(fuel_terms)

        constraints = [
            v >= self.v_min,
            v <= self.v_max,
        ]

        # 시간창 제약: d_i / v_i ≤ t_i → d_i * inv_pos(v_i) ≤ t_i
        if time_budgets:
            for arc, i in arc_idx.items():
                t_budget = time_budgets.get(arc)
                if t_budget is not None and t_budget > 0:
                    d = distances[arc]
                    # d * cp.inv_pos(v[i]) ≤ t_budget
                    constraints.append(d * cp.inv_pos(v[i]) <= t_budget)

        problem = cp.Problem(objective, constraints)

        # GP 지원 솔버 우선 순서: ECOS → SCS → CLARABEL
        solved = False
        for solver_name in ["ECOS", "SCS", "CLARABEL"]:
            try:
                if solver_name in cp.installed_solvers():
                    problem.solve(gp=True, solver=getattr(cp, solver_name))
                    solved = True
                    break
            except Exception:
                continue

        if not solved:
            try:
                problem.solve(gp=True)  # default solver
            except Exception:
                return self._fallback_eco_speed(routes, distances)

        if problem.status not in ("optimal", "optimal_inaccurate"):
            return self._fallback_eco_speed(routes, distances)

        # 결과 추출
        v_opt = np.clip(v.value, self.v_min, self.v_max)
        speeds = {}
        for arc, i in arc_idx.items():
            speeds[arc] = float(v_opt[i])
        # 활성 아닌 구간은 eco-speed
        for arc in routes:
            if arc not in speeds:
                speeds[arc] = self.v_eco

        total_fuel = (
            float(fuel_terms.value)
            if fuel_terms.value is not None
            else 0.0
        )
        return SpeedSolution(
            speeds=speeds, total_fuel=total_fuel, status="optimal"
        )

    def _fallback_eco_speed(
        self,
        routes: list[tuple[str, str]],
        distances: dict[tuple[str, str], float],
    ) -> SpeedSolution:
        """CVXPY 실패 시 eco-speed 고정 폴백."""
        speeds = {arc: self.v_eco for arc in routes}
        total_fuel = sum(
            self.alpha * (self.v_eco ** self.gamma) * distances.get(arc, 0.0)
            for arc in routes
        )
        return SpeedSolution(
            speeds=speeds, total_fuel=total_fuel, status="fallback"
        )

    def fuel_for_route(
        self,
        route: list[str],
        distances: dict[tuple[str, str], float],
        speeds: dict[tuple[str, str], float] | None = None,
    ) -> float:
        """경로의 총 연료 소비 계산.

        Args:
            route: 노드 순서 (depot 포함 가능)
            distances: 구간별 거리 (nm)
            speeds: 구간별 속도 (knots). None이면 v_eco 사용.

        Returns:
            총 연료 (metric tons)
        """
        total = 0.0
        for i in range(len(route) - 1):
            arc = (route[i], route[i + 1])
            d = distances.get(arc, 0.0)
            v = (speeds or {}).get(arc, self.v_eco)
            total += self.alpha * (v ** self.gamma) * d
        return total
