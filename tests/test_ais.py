import numpy as np
import pytest
from libs.stochastic.ais_processor import (
    ETADeviationModel,
    fit_eta_distribution,
    generate_synthetic_ais,
)


def test_fit_no_data():
    """데이터 없음 → TruncatedNormal 기본값."""
    model = fit_eta_distribution(np.array([]))
    assert model.distribution_type == "truncated_normal"
    assert model.params["sigma"] == pytest.approx(0.85)
    assert model.n_samples == 0
    assert model.mean_h == pytest.approx(0.0)
    assert model.std_h == pytest.approx(0.85)


def test_fit_small_n():
    """N < 200 → Log-normal 피팅."""
    rng = np.random.default_rng(0)
    data = rng.lognormal(0.1, 0.6, 50) - np.exp(0.1 + 0.6**2 / 2)
    model = fit_eta_distribution(data, threshold_n=200)
    assert model.distribution_type == "lognormal"
    assert model.n_samples == 50
    assert "mu" in model.params
    assert "sigma" in model.params


def test_fit_large_n():
    """N >= 200 → KDE."""
    rng = np.random.default_rng(1)
    data = rng.normal(0.2, 0.5, 300)
    model = fit_eta_distribution(data, threshold_n=200)
    assert model.distribution_type == "kde"
    assert model.n_samples == 300
    assert "kde" in model.params


def test_sample_within_bounds():
    """샘플이 [-2, +2] 범위 내에 있는가."""
    rng = np.random.default_rng(2)
    data = rng.normal(0.0, 0.5, 100)
    for dist_type in ("truncated_normal", "lognormal", "kde"):
        if dist_type == "truncated_normal":
            model = fit_eta_distribution(np.array([]))
        elif dist_type == "lognormal":
            model = fit_eta_distribution(data[:50], threshold_n=200)
        else:
            model = fit_eta_distribution(rng.normal(0, 0.5, 300), threshold_n=200)
        samples = model.sample(200, seed=42)
        assert samples.min() >= -2.0, f"{dist_type}: min {samples.min()} < -2"
        assert samples.max() <= 2.0, f"{dist_type}: max {samples.max()} > 2"


def test_synthetic_ais_shape():
    """합성 데이터 형태 검증."""
    for weather in ("calm", "moderate", "rough"):
        data = generate_synthetic_ais(n_records=100, weather=weather, seed=7)
        assert data.shape == (100,), f"{weather}: shape {data.shape}"
        assert data.min() >= -2.0
        assert data.max() <= 2.0
