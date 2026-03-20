"""
AIS 데이터 처리 — Phase 3.

ATA(Actual Time of Arrival) - ETA(Estimated Time of Arrival) 편차 분포 추정.

참조:
  - Mou et al. (2019), Ocean Engineering: AIS ETA deviation analysis
  - multiobjective_ais.md: AIS 처리 파이프라인
  - eta_distributions.md: Log-normal 기본, N≥200 시 KDE

데이터 형식 (CSV):
  mmsi, vessel_name, eta_utc, ata_utc
  123456789, VESSEL-A, 2024-01-01 08:00:00, 2024-01-01 09:30:00
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass


@dataclass
class ETADeviationModel:
    """ETA 편차 분포 모델."""

    distribution_type: str  # "lognormal" | "kde" | "truncated_normal"
    params: dict  # 분포 파라미터
    n_samples: int  # 학습에 사용된 샘플 수
    mean_h: float  # 평균 편차 (hours)
    std_h: float  # 표준편차 (hours)

    def sample(self, n: int, seed: int = 42) -> np.ndarray:
        """편차 샘플 생성 (hours)."""
        rng = np.random.default_rng(seed)
        dist_type = self.distribution_type

        if dist_type == "truncated_normal":
            from scipy.stats import truncnorm

            sigma = self.params.get("sigma", 0.85)
            samples = truncnorm.rvs(
                -2 / sigma,
                2 / sigma,
                loc=0,
                scale=sigma,
                size=n,
                random_state=rng.integers(int(1e9)),
            )
        elif dist_type == "lognormal":
            mu = self.params.get("mu", 0.1)
            sigma = self.params.get("sigma", 0.6)
            raw = rng.lognormal(mu, sigma, n)
            # zero-mean shift
            shift = np.exp(mu + sigma**2 / 2)
            samples = raw - shift
        else:  # kde
            from scipy.stats import gaussian_kde

            kde = self.params.get("kde")
            if kde:
                samples = kde.resample(n, seed=rng.integers(int(1e9)))[0]
            else:
                samples = rng.normal(0, 0.85, n)

        return np.clip(samples, -2.0, 2.0)


def parse_ais_csv(
    csv_path: str,
    eta_col: str = "eta_utc",
    ata_col: str = "ata_utc",
) -> np.ndarray:
    """AIS CSV에서 ETA 편차 추출 (hours).

    Args:
        csv_path: AIS 데이터 CSV 파일 경로.
        eta_col: ETA 컬럼명.
        ata_col: ATA 컬럼명.

    Returns:
        deviation array (ATA - ETA, hours)
    """
    import pandas as pd

    df = pd.read_csv(csv_path, parse_dates=[eta_col, ata_col])
    deviations = (df[ata_col] - df[eta_col]).dt.total_seconds() / 3600.0
    return deviations.dropna().values


def fit_eta_distribution(
    deviations: np.ndarray,
    threshold_n: int = 200,
) -> ETADeviationModel:
    """ETA 편차 데이터에 분포 피팅.

    N >= threshold_n: KDE
    N < threshold_n: Log-normal (MLE)
    N == 0: TruncatedNormal 기본값 (sigma=0.85)

    Args:
        deviations: ATA-ETA 편차 배열 (hours)
        threshold_n: KDE 전환 임계값

    Returns:
        ETADeviationModel
    """
    n = len(deviations)
    mean_h = float(np.mean(deviations)) if n > 0 else 0.0
    std_h = float(np.std(deviations)) if n > 0 else 0.85

    if n == 0:
        return ETADeviationModel(
            distribution_type="truncated_normal",
            params={"sigma": 0.85},
            n_samples=0,
            mean_h=0.0,
            std_h=0.85,
        )

    if n >= threshold_n:
        from scipy.stats import gaussian_kde

        kde = gaussian_kde(deviations)
        return ETADeviationModel(
            distribution_type="kde",
            params={"kde": kde},
            n_samples=n,
            mean_h=mean_h,
            std_h=std_h,
        )

    # Log-normal MLE (비음수 지연만 피팅 후 zero-mean shift)
    pos = deviations[deviations > 0]
    if len(pos) > 10:
        from scipy.stats import lognorm

        shape, _loc, scale = lognorm.fit(pos, floc=0)
        mu = np.log(scale)
        sigma = shape
    else:
        mu, sigma = 0.1, 0.6

    return ETADeviationModel(
        distribution_type="lognormal",
        params={"mu": mu, "sigma": sigma},
        n_samples=n,
        mean_h=mean_h,
        std_h=std_h,
    )


def generate_synthetic_ais(
    n_records: int = 500,
    weather: str = "calm",
    seed: int = 42,
) -> np.ndarray:
    """실제 AIS 데이터 없을 때 합성 편차 데이터 생성.

    Args:
        n_records: 생성할 레코드 수.
        weather: 기상 조건 "calm" | "moderate" | "rough".
        seed: 난수 시드.

    Returns:
        ETA 편차 배열 (hours), [-2, +2] 범위로 클립됨.
    """
    rng = np.random.default_rng(seed)
    params = {
        "calm": (0.05, 0.4),
        "moderate": (0.15, 0.7),
        "rough": (0.40, 1.0),
    }
    mu, sigma = params.get(weather, params["calm"])
    raw = rng.lognormal(mu, sigma, n_records)
    shift = np.exp(mu + sigma**2 / 2)
    return np.clip(raw - shift, -2.0, 2.0)
