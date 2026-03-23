"""
ETA 확률적 Robustness 분석 — Monte Carlo + CVaR95.

AW-010 기반 Log-normal 지연 분포를 사용하여 배정 결과의
확률적 강건성(robustness)을 평가한다.

참조:
    AW-010: mu_log=4.015, sigma_log=1.363, clip=[-6h, +6h]
    ADR-001: 2024-06 부산항 N=336 실측값

수식:
    delay_i ~ (1-p_d)*Truncated(-δ, 0)  +  p_d*LogNormal(mu, sigma)
    clip:    delay_i in [-360, +360] 분
    CVaR95 = E[cost | cost >= Q_95]

사용 예:
    from libs.evaluation.robustness import RobustnessAnalyzer
    analyzer = RobustnessAnalyzer(n_mc=100, seed=42)
    result = analyzer.evaluate(assignments, windows)
    print(f"CVaR95={result.cvar95:.2f}h  mean={result.mean_cost:.2f}h")
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RobustnessResult:
    """Monte Carlo Robustness 분석 결과."""

    # 비용 통계 (단위: priority-weighted hours)
    cvar95: float            # CVaR at 95th percentile
    mean_cost: float         # 평균 비용
    std_cost: float          # 표준 편차
    p95: float               # 95번째 백분위수
    p50: float               # 중앙값
    worst_cost: float        # 최악 비용 (max)
    best_cost: float         # 최선 비용 (min)

    # 세부 데이터
    costs_mc: list[float] = field(default_factory=list)   # 전체 MC 샘플 비용
    n_mc: int = 0
    n_windows: int = 0

    # 분포 파라미터 (재현성)
    mu_log: float = 4.015
    sigma_log: float = 1.363
    delay_prob: float = 0.714
    clip_min_min: float = -360.0
    clip_max_min: float = 360.0


class RobustnessAnalyzer:
    """Log-normal ETA 지연 분포 기반 Monte Carlo Robustness 분석기.

    Args:
        mu_log: Log-normal μ (자연로그 스케일). AW-010 기본: 4.015
        sigma_log: Log-normal σ. AW-010 기본: 1.363
        clip_min_min: 지연 하한 (분). 기본: -360 (6시간 조기 도착)
        clip_max_min: 지연 상한 (분). 기본: 360 (6시간 지연)
        delay_prob: 지연 발생 확률. AW-010 기본: 0.714 (71.4%)
        n_mc: Monte Carlo 샘플 수. 기본: 100
        seed: 난수 시드 (재현성). 기본: 42
        w1: 대기시간 비용 가중치. 기본: 1.0
    """

    def __init__(
        self,
        mu_log: float = 4.015,
        sigma_log: float = 1.363,
        clip_min_min: float = -360.0,
        clip_max_min: float = 360.0,
        delay_prob: float = 0.714,
        n_mc: int = 100,
        seed: int = 42,
        w1: float = 1.0,
    ) -> None:
        self.mu_log = mu_log
        self.sigma_log = sigma_log
        self.clip_min_min = clip_min_min
        self.clip_max_min = clip_max_min
        self.delay_prob = delay_prob
        self.n_mc = n_mc
        self.seed = seed
        self.w1 = w1

    # ── 지연 샘플링 ────────────────────────────────────────────
    def sample_delays(
        self,
        n_windows: int,
    ) -> np.ndarray:
        """ETA 지연 행렬 샘플링 (shape: n_mc × n_windows, 단위: 분).

        각 셀은 해당 시나리오(행)에서 선박 j(열)의 ETA 지연(분).
        양수 = 지연(늦음), 음수 = 조기 도착.

        분포:
            - delay_prob 확률로 Log-normal(mu_log, sigma_log) 지연
            - (1-delay_prob) 확률로 Uniform(-|clip_min|, 0) 조기 도착
            - 결과를 [clip_min, clip_max]로 클립

        Args:
            n_windows: 선박 수 (열 수)

        Returns:
            np.ndarray (n_mc, n_windows)
        """
        rng = np.random.default_rng(self.seed)

        # 지연/조기도착 마스크 (shape: n_mc × n_windows)
        is_delayed = rng.random((self.n_mc, n_windows)) < self.delay_prob

        # 지연: Log-normal (양수)
        delay_pos = rng.lognormal(
            mean=self.mu_log,
            sigma=self.sigma_log,
            size=(self.n_mc, n_windows),
        )

        # 조기 도착: Uniform(clip_min, 0) (음수)
        early_range = abs(self.clip_min_min)
        delay_neg = -rng.uniform(0, early_range, size=(self.n_mc, n_windows))

        # 합성 및 클립
        delays = np.where(is_delayed, delay_pos, delay_neg)
        delays = np.clip(delays, self.clip_min_min, self.clip_max_min)

        return delays.astype(np.float64)

    # ── 단일 시나리오 비용 평가 ────────────────────────────────
    def _compute_perturbed_cost(
        self,
        assignments: list,
        windows_map: dict,
        delays: np.ndarray,
        window_index: dict[str, int],
    ) -> np.ndarray:
        """n_mc × 1 배열 반환 — 각 시나리오별 perturbed cost.

        perturbed_wait_j = max(0, actual_arrival_j - scheduled_start_j)
        actual_arrival_j = earliest_start_j + delay_j

        cost = w1 * sum(priority_j * perturbed_wait_j / 60)

        Args:
            assignments: list[SchedulingToRoutingSpec]
            windows_map: vessel_id → TimeWindowSpec
            delays: (n_mc, n_windows) delay 행렬
            window_index: vessel_id → column index in delays

        Returns:
            np.ndarray shape (n_mc,) — 시나리오별 비용
        """
        costs = np.zeros(self.n_mc, dtype=np.float64)

        for spec in assignments:
            vessel_id = getattr(spec, "vessel_id", None)
            if vessel_id is None or vessel_id not in windows_map:
                continue

            tw = windows_map[vessel_id]
            earliest_start = float(getattr(tw, "earliest_start", 0.0))
            priority = float(getattr(tw, "priority", 1.0))
            scheduled_start = float(
                getattr(spec, "scheduled_start", earliest_start)
            )

            col = window_index.get(vessel_id)
            if col is None:
                continue

            # 지연 적용: actual_arrival = earliest_start + delay (n_mc 벡터)
            actual_arrival = earliest_start + delays[:, col]

            # 예인선이 먼저 도착한 경우: 예인선 대기 시간
            extra_wait_min = np.maximum(0.0, actual_arrival - scheduled_start)

            # priority-weighted hours
            costs += priority * extra_wait_min / 60.0

        return costs * self.w1

    # ── 메인 평가 API ──────────────────────────────────────────
    def evaluate(
        self,
        assignments: list,
        windows: list,
    ) -> RobustnessResult:
        """Monte Carlo ETA 지연 시뮬레이션으로 robustness 평가.

        Args:
            assignments: list[SchedulingToRoutingSpec] — 평가할 배정 결과
            windows: list[TimeWindowSpec] — 원본 시간창 목록

        Returns:
            RobustnessResult (CVaR95, mean, std, percentiles 포함)
        """
        if not assignments or not windows:
            logger.warning("배정 또는 시간창 비어 있음 — robustness 평가 불가")
            return RobustnessResult(
                cvar95=0.0, mean_cost=0.0, std_cost=0.0,
                p95=0.0, p50=0.0, worst_cost=0.0, best_cost=0.0,
                n_mc=self.n_mc, n_windows=0,
                mu_log=self.mu_log, sigma_log=self.sigma_log,
                delay_prob=self.delay_prob,
            )

        n_windows = len(windows)
        windows_map = {getattr(w, "vessel_id", ""): w for w in windows}
        vessel_ids = [getattr(w, "vessel_id", "") for w in windows]
        window_index = {vid: i for i, vid in enumerate(vessel_ids)}

        logger.info(
            "Monte Carlo 시작: n_mc=%d, n_windows=%d, "
            "mu_log=%.3f, sigma_log=%.3f",
            self.n_mc, n_windows, self.mu_log, self.sigma_log,
        )

        # 지연 행렬 샘플링
        delays = self.sample_delays(n_windows)

        # 비용 계산 (벡터화)
        costs = self._compute_perturbed_cost(
            assignments, windows_map, delays, window_index
        )

        # 통계 계산
        mean_cost = float(np.mean(costs))
        std_cost = float(np.std(costs))
        p50 = float(np.percentile(costs, 50))
        p95 = float(np.percentile(costs, 95))
        worst = float(np.max(costs))
        best = float(np.min(costs))

        # CVaR95 = E[cost | cost > VaR_95]  (strict greater-than)
        threshold = np.percentile(costs, 95)
        tail = costs[costs > threshold]
        cvar95 = float(np.mean(tail)) if len(tail) > 0 else p95

        logger.info(
            "Robustness 완료: mean=%.2fh std=%.2fh p95=%.2fh CVaR95=%.2fh",
            mean_cost, std_cost, p95, cvar95,
        )

        return RobustnessResult(
            cvar95=cvar95,
            mean_cost=mean_cost,
            std_cost=std_cost,
            p95=p95,
            p50=p50,
            worst_cost=worst,
            best_cost=best,
            costs_mc=costs.tolist(),
            n_mc=self.n_mc,
            n_windows=n_windows,
            mu_log=self.mu_log,
            sigma_log=self.sigma_log,
            delay_prob=self.delay_prob,
            clip_min_min=self.clip_min_min,
            clip_max_min=self.clip_max_min,
        )

    # ── 솔버간 비교 ───────────────────────────────────────────
    def compare(
        self,
        solver_results: dict[str, tuple[list, list]],
    ) -> dict[str, RobustnessResult]:
        """여러 솔버 결과를 동일 시드로 비교.

        Args:
            solver_results: {solver_name: (assignments, windows)} 딕셔너리

        Returns:
            {solver_name: RobustnessResult} 딕셔너리
        """
        return {
            name: self.evaluate(assignments, windows)
            for name, (assignments, windows) in solver_results.items()
        }
