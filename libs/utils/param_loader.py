"""
YAML 기반 파라미터 로더 (AW-007 준수).

피팅 스크립트(scripts/fit_*.py)가 생성한 YAML 파일을 읽어
TwoStageConfig / ALNSConfig에 주입한다.
YAML 파일 없으면 데이터-없음 기본값으로 fallback.

기본값 기준 (AW-010):
    데이터 없음 → TruncatedNormal(-2h, +2h), mu_log=0.1, sigma_log=0.5
    N≥200 → MLE 결과를 YAML에 저장 후 로드 (fitted values)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

# ── 기본값 (데이터-없음 시 fallback) ───────────────────────────

_DEFAULT_ETA: dict[str, Any] = {
    "mu_log": 0.1,
    "sigma_log": 0.5,
    "clip_min_h": -2.0,
    "clip_max_h": 2.0,
    "delay_ratio": 0.7,
    "n_samples": 0,
    "data_source": None,
    "fitted_at": None,
}

_DEFAULT_SHAW: dict[str, Any] = {
    "lambda_d": 0.5,
    "lambda_t": 0.3,
    "lambda_p": 0.2,
    "accuracy": None,
    "n_pairs": 0,
    "data_source": None,
    "fitted_at": None,
}

# ── 로더 ──────────────────────────────────────────────────────

def _load_yaml(path: str | Path) -> dict[str, Any]:
    """YAML 파일을 읽어 dict로 반환. 파일 없으면 빈 dict."""
    try:
        import yaml  # type: ignore[import]
    except ModuleNotFoundError as exc:
        raise ImportError(
            "pyyaml 필요: uv pip install pyyaml"
        ) from exc

    p = Path(path)
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_eta_params(
    path: str | Path = "configs/eta_params.yaml",
) -> dict[str, Any]:
    """ETA 분포 파라미터 로드.

    YAML 파일이 있으면 fitted values 반환.
    없으면 데이터-없음 기본값 반환 (AW-010).

    Returns:
        dict with keys: mu_log, sigma_log, clip_min_h, clip_max_h,
                        delay_ratio, n_samples, data_source, fitted_at
    """
    raw = _load_yaml(path)
    # YAML 최상위 키가 "eta:"로 묶여 있을 수도 있음
    data = raw.get("eta", raw)
    result = {**_DEFAULT_ETA, **data}
    return result


def load_shaw_params(
    path: str | Path = "configs/shaw_params.yaml",
) -> dict[str, Any]:
    """Shaw Destroy lambda 파라미터 로드.

    YAML 파일이 있으면 fitted values 반환.
    없으면 원논문 기본값 반환 (Ropke & Pisinger 2006).

    Returns:
        dict with keys: lambda_d, lambda_t, lambda_p,
                        accuracy, n_pairs, data_source, fitted_at
    """
    raw = _load_yaml(path)
    data = raw.get("shaw", raw)
    result = {**_DEFAULT_SHAW, **data}
    return result


def load_base_config(
    path: str | Path = "configs/base_config.yaml",
) -> dict[str, Any]:
    """base_config.yaml 전체를 dict로 반환.

    섹션 키: benders, alns, rolling_horizon, two_stage.
    파일 없으면 빈 dict 반환 (각 Config 기본값 사용).

    Returns:
        dict with section keys as top-level keys
    """
    return _load_yaml(path)


def load_benders_params(
    path: str | Path = "configs/base_config.yaml",
) -> dict[str, Any]:
    """BendersConfig용 파라미터 로드.

    Returns:
        dict with keys matching BendersConfig fields
    """
    raw = load_base_config(path)
    return raw.get("benders", {})


def load_alns_base_params(
    path: str | Path = "configs/base_config.yaml",
) -> dict[str, Any]:
    """ALNSConfig 기본 파라미터 로드 (Shaw lambda 제외).

    Shaw lambda는 load_shaw_params()로 별도 로드.

    Returns:
        dict with keys matching ALNSConfig fields (excluding shaw_lambda_*)
    """
    raw = load_base_config(path)
    return raw.get("alns", {})


def load_rolling_horizon_params(
    path: str | Path = "configs/base_config.yaml",
) -> dict[str, Any]:
    """RollingHorizonConfig용 파라미터 로드.

    Returns:
        dict with keys matching RollingHorizonConfig fields
    """
    raw = load_base_config(path)
    return raw.get("rolling_horizon", {})


def load_two_stage_base_params(
    path: str | Path = "configs/base_config.yaml",
) -> dict[str, Any]:
    """TwoStageConfig 기본 파라미터 로드 (ETA 분포 제외).

    ETA 분포 파라미터는 load_eta_params()로 별도 로드.

    Returns:
        dict with keys matching TwoStageConfig fields (excluding eta_*)
    """
    raw = load_base_config(path)
    return raw.get("two_stage", {})
