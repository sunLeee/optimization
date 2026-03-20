"""연료 소비 함수 모델."""
from __future__ import annotations
import numpy as np


def fuel_consumption(
    speed_kn: float,
    dist_nm: float,
    alpha: float = 1.0,
    gamma: float = 2.5,
) -> float:
    """선박 연료 소비량 계산.

    F(v, d) = alpha * v^gamma * d

    Args:
        speed_kn: 속도 (knots)
        dist_nm: 거리 (nautical miles)
        alpha: 연료 소비 계수 (vessel-specific, MT/nm·kn^gamma)
        gamma: 속도 지수 (2.5 고정, AW-006)

    Returns:
        fuel_mt: 연료 소비량 (metric tons)
    """
    return alpha * (speed_kn ** gamma) * dist_nm


def mccormick_linearize(
    v_lo: float,
    v_hi: float,
    x_lo: float = 0.0,
    x_hi: float = 1.0,
) -> dict[str, float]:
    """McCormick envelope for bilinear term w = v^2 * x.

    Returns lower/upper bound coefficients for MILP formulation.
    """
    return {
        "w_lb1": v_lo**2 * x_lo + 2 * v_lo * x_lo,  # McCormick lower 1
        "w_lb2": v_hi**2 * x_hi + 2 * v_hi * x_hi,  # McCormick lower 2 (placeholder)
        "v_lo": v_lo,
        "v_hi": v_hi,
    }
