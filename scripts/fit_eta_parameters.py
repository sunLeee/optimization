"""
ETA 지연 분포 파라미터 MLE 피팅 스크립트.

실행:
    uv run python scripts/fit_eta_parameters.py
    uv run python scripts/fit_eta_parameters.py --data data/raw/scheduling/data/2024-06_SchData.csv
    uv run python scripts/fit_eta_parameters.py --out configs/eta_params.yaml

출력:
    configs/eta_params.yaml — TwoStageConfig.from_yaml()이 읽는 파라미터 파일
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))


def fit_eta(data_path: str | Path) -> dict:
    """실데이터에서 ETA 분포 파라미터 MLE 피팅.

    AW-010: N≥200 → MLE 적용.

    Returns:
        dict with mu_log, sigma_log, clip_min_h, clip_max_h, delay_ratio, n_samples
    """
    df = pd.read_csv(data_path)
    df["실제_시작"] = pd.to_datetime(df["실제 스케줄 시작 시각"])
    df["최초_시각"] = pd.to_datetime(df["최초 스케줄 시각"])
    ev_min = (df["실제_시작"] - df["최초_시각"]).dt.total_seconds() / 60

    n = len(ev_min.dropna())
    delay_ratio = float((ev_min > 0).mean())

    if n < 200:
        print(f"[WARNING] N={n} < 200 — AW-010 기준 미충족. 기본값 사용 권장.")

    pos = ev_min[ev_min > 0].dropna()
    mu_log = float(np.log(pos).mean())
    sigma_log = float(np.log(pos).std())

    # clip 범위: 실측 분포의 ±6h 커버율 기준
    cover_2h = float(((ev_min >= -120) & (ev_min <= 120)).mean())
    cover_6h = float(((ev_min >= -360) & (ev_min <= 360)).mean())
    # 커버율 89% 이상 달성하는 clip 선택 (6h 기본)
    clip_h = 6.0 if cover_6h >= 0.89 else 4.0

    print(f"=== ETA MLE 피팅 결과 ===")
    print(f"  N            = {n}")
    print(f"  mu_log       = {mu_log:.4f}")
    print(f"  sigma_log    = {sigma_log:.4f}")
    print(f"  delay_ratio  = {delay_ratio:.4f} ({delay_ratio*100:.1f}%)")
    print(f"  clip_h       = ±{clip_h}h  (±2h 커버 {cover_2h*100:.1f}%, ±6h 커버 {cover_6h*100:.1f}%)")

    return {
        "mu_log": round(mu_log, 4),
        "sigma_log": round(sigma_log, 4),
        "clip_min_h": -clip_h,
        "clip_max_h": clip_h,
        "delay_ratio": round(delay_ratio, 4),
        "n_samples": n,
    }


def write_yaml(params: dict, out_path: str | Path, data_source: str) -> None:
    """파라미터를 YAML 파일로 저장."""
    try:
        import yaml  # type: ignore[import]
    except ModuleNotFoundError:
        print("[ERROR] pyyaml 필요: uv pip install pyyaml")
        sys.exit(1)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    doc = {
        "eta": {
            **params,
            "data_source": str(data_source),
            "fitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "method": "Log-normal MLE on positive delays (AW-010)",
            "reference": "ADR-001: docs/adr/ADR-001-eta-distribution-parameters.md",
        }
    }

    with out.open("w", encoding="utf-8") as f:
        yaml.dump(doc, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"\n  → 저장 완료: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="ETA 분포 파라미터 MLE 피팅")
    parser.add_argument(
        "--data",
        default="data/raw/scheduling/data/2024-06_SchData.csv",
        help="스케줄 CSV 파일 경로",
    )
    parser.add_argument(
        "--out",
        default="configs/eta_params.yaml",
        help="출력 YAML 파일 경로",
    )
    args = parser.parse_args()

    params = fit_eta(args.data)
    write_yaml(params, args.out, args.data)


if __name__ == "__main__":
    main()
