"""
Shaw Destroy lambda 파라미터 피팅 스크립트.

실행:
    uv run python scripts/fit_shaw_parameters.py
    uv run python scripts/fit_shaw_parameters.py --data data/raw/scheduling/data/2024-06_SchData.csv
    uv run python scripts/fit_shaw_parameters.py --out configs/shaw_params.yaml

출력:
    configs/shaw_params.yaml — ALNSConfig.from_yaml()이 읽는 파라미터 파일
"""
from __future__ import annotations

import argparse
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))


def _haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3440.065
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _compute_ais_dist(ais_dir: Path, filename: str) -> float | None:
    """AIS 파일에서 예선 총 이동거리(nm) 계산."""
    f = ais_dir / filename
    if not f.exists():
        return None
    try:
        df = pd.read_csv(f).sort_values("CreatedAt")
        lats, lons = df["Latitude(위도)"].values, df["Longitude(경도)"].values
        return sum(
            _haversine_nm(lats[i], lons[i], lats[i + 1], lons[i + 1])
            for i in range(len(lats) - 1)
        )
    except Exception:
        return None


def fit_shaw(data_path: str | Path) -> dict:
    """역사적 배정 데이터에서 Shaw lambda 피팅.

    Returns:
        dict with lambda_d, lambda_t, lambda_p, accuracy, n_pairs
    """
    from scipy.optimize import differential_evolution  # type: ignore[import]

    df = pd.read_csv(data_path)
    df["실제_시작"] = pd.to_datetime(df["실제 스케줄 시작 시각"])

    # AIS 실거리 추출
    base = Path(data_path).parent
    ais_dir = base / "AISLog"
    dist_map: dict[int, float] = {}
    if ais_dir.exists():
        for f in ais_dir.glob("*_tug_*.csv"):
            try:
                idx = int(f.stem.split("_")[-2])
                d = _compute_ais_dist(ais_dir, f.name)
                if d is not None:
                    dist_map[idx] = d
            except Exception:
                pass

    df["ais_dist_nm"] = df["AIS 파일명 tug"].apply(
        lambda fname: dist_map.get(
            int(str(fname).split("_")[-2]) if pd.notna(fname) else -1, np.nan
        )
        if pd.notna(fname)
        else np.nan
    )

    valid = df.dropna(subset=["ais_dist_nm"]).copy()
    if len(valid) < 10:
        print("[WARNING] 데이터 부족 → 원논문 기본값 반환")
        return {"lambda_d": 0.5, "lambda_t": 0.3, "lambda_p": 0.2,
                "accuracy": None, "n_pairs": 0}

    valid["start_min"] = (
        valid["실제_시작"] - valid["실제_시작"].min()
    ).dt.total_seconds() / 60
    valid["priority"] = valid["톤수"].rank(pct=True)

    # similar / dissimilar 쌍 구성
    rng = np.random.default_rng(42)
    pairs_same: list[tuple[float, float, float]] = []
    for _, grp in valid.groupby("기준예선"):
        grp_s = grp.sort_values("실제_시작").reset_index(drop=True)
        for i in range(len(grp_s) - 1):
            a, b = grp_s.iloc[i], grp_s.iloc[i + 1]
            pairs_same.append((
                abs(float(a["ais_dist_nm"]) - float(b["ais_dist_nm"])),
                abs(float(a["start_min"]) - float(b["start_min"])),
                abs(float(a["priority"]) - float(b["priority"])),
            ))

    tugs = valid["기준예선"].unique()
    pairs_diff: list[tuple[float, float, float]] = []
    for _ in range(len(pairs_same)):
        t1, t2 = rng.choice(tugs, 2, replace=False)
        a = valid[valid["기준예선"] == t1].sample(1, random_state=int(rng.integers(9999))).iloc[0]
        b = valid[valid["기준예선"] == t2].sample(1, random_state=int(rng.integers(9999))).iloc[0]
        pairs_diff.append((
            abs(float(a["ais_dist_nm"]) - float(b["ais_dist_nm"])),
            abs(float(a["start_min"]) - float(b["start_min"])),
            abs(float(a["priority"]) - float(b["priority"])),
        ))

    arr = np.array(pairs_same + pairs_diff, dtype=float)
    labels = np.array([1] * len(pairs_same) + [0] * len(pairs_diff))
    d_max = arr[:, 0].max() or 1.0
    t_max = arr[:, 1].max() or 1.0
    p_max = arr[:, 2].max() or 1.0
    arr_n = arr / np.array([d_max, t_max, p_max])

    def _loss(lam12: np.ndarray) -> float:
        l1, l2 = lam12
        l3 = 1.0 - l1 - l2
        if l3 < 0.0:
            return 1e9
        r = arr_n @ np.array([l1, l2, l3])
        return -(r[labels == 0].mean() - r[labels == 1].mean())

    res = differential_evolution(_loss, bounds=[(0.0, 1.0), (0.0, 1.0)], seed=42, maxiter=300)
    l1, l2 = float(res.x[0]), float(res.x[1])
    l3 = max(0.0, 1.0 - l1 - l2)
    total = l1 + l2 + l3 or 1.0
    l1, l2, l3 = l1 / total, l2 / total, l3 / total

    # 정확도 계산
    r_all = arr_n @ np.array([l1, l2, l3])
    thr = np.median(r_all)
    acc = float(((labels == 1) & (r_all < thr)).sum() + ((labels == 0) & (r_all >= thr)).sum()) / len(labels)

    print(f"=== Shaw lambda 피팅 결과 ===")
    print(f"  N similar    = {len(pairs_same)}, N dissimilar = {len(pairs_diff)}")
    print(f"  lambda_d     = {l1:.4f}")
    print(f"  lambda_t     = {l2:.4f}")
    print(f"  lambda_p     = {l3:.4f}")
    print(f"  분류 정확도   = {acc*100:.1f}%")
    print(f"  원논문 기본값: λd=0.500, λt=0.300, λp=0.200")

    return {
        "lambda_d": round(l1, 4),
        "lambda_t": round(l2, 4),
        "lambda_p": round(l3, 4),
        "accuracy": round(acc, 4),
        "n_pairs": len(pairs_same),
    }


def write_yaml(params: dict, out_path: str | Path, data_source: str) -> None:
    try:
        import yaml  # type: ignore[import]
    except ModuleNotFoundError:
        print("[ERROR] pyyaml 필요: uv pip install pyyaml")
        sys.exit(1)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    doc = {
        "shaw": {
            **params,
            "paper_defaults": {"lambda_d": 0.5, "lambda_t": 0.3, "lambda_p": 0.2},
            "data_source": str(data_source),
            "fitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "method": "differential_evolution on similar/dissimilar pair separation",
            "reference": "ADR-002: docs/adr/ADR-002-shaw-lambda-empirical-fitting.md",
        }
    }

    with out.open("w", encoding="utf-8") as f:
        yaml.dump(doc, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"\n  → 저장 완료: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Shaw lambda 파라미터 피팅")
    parser.add_argument(
        "--data",
        default="data/raw/scheduling/data/2024-06_SchData.csv",
        help="스케줄 CSV 파일 경로",
    )
    parser.add_argument(
        "--out",
        default="configs/shaw_params.yaml",
        help="출력 YAML 파일 경로",
    )
    args = parser.parse_args()

    params = fit_shaw(args.data)
    write_yaml(params, args.out, args.data)


if __name__ == "__main__":
    main()
