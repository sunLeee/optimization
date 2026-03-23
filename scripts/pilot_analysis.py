"""
도선사(Pilot) 운영 최적화 분석.

역사적 배차 방식과 최적 배차 방식을 비교하여
도선사의 이동시간, 유휴시간, 최적 출발시각을 분석한다.

확률적 도착하에서 newsvendor 모델로 최적 버퍼를 계산한다.

사용법:
    uv run python scripts/pilot_analysis.py
"""

from __future__ import annotations

import json
import logging
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from libs.data import HarborDataLoader
from libs.data.loader import AIS_SUPPLEMENTARY_LOCATIONS
from libs.utils.geo import haversine_nm
from libs.utils.travel_time import TravelTimeMatrix

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

# 도선사 출발지: PAL (팔미 파일럿 스테이션)
PILOT_STATION = ("PAL", (37.463117, 126.596133))
PILOT_SPEED_KMH = 20.0  # 도선사 이동속도 (km/h)
NM_TO_KM = 1.852
MU_LOG = 4.015
SIGMA_LOG = 1.363
DELAY_PROB = 0.714


def travel_time_pilot(
    from_pos: tuple[float, float], to_pos: tuple[float, float]
) -> float:
    """도선사 이동시간 (분)."""
    dist_nm = haversine_nm(from_pos, to_pos)
    dist_km = dist_nm * NM_TO_KM
    return dist_km / PILOT_SPEED_KMH * 60.0


def newsvendor_buffer(
    w_v: float,
    w_p: float,
    mu_log: float,
    sigma_log: float,
    p_delay: float,
) -> float:
    """Newsvendor 모델 기반 최적 버퍼 계산.

    Args:
        w_v: 선박 대기 단위비용 (per minute)
        w_p: 도선사 대기 단위비용 (per minute)
        mu_log: 지연 분포 LogNormal mu 파라미터
        sigma_log: 지연 분포 LogNormal sigma 파라미터
        p_delay: 지연 발생 확률

    Returns:
        최적 버퍼 (분) — 도선사가 scheduled_start보다 얼마나 일찍 출발해야 하는가
    """
    from scipy import stats

    # Critical ratio
    cr = w_v / (w_v + w_p)
    # 지연 ~ LogNormal(mu, sigma)인 경우
    lognorm = stats.lognorm(s=sigma_log, scale=np.exp(mu_log))
    # p_delay 비율만큼만 지연 발생 → effective quantile
    effective_q = max(0.0, (cr - (1 - p_delay)) / p_delay)
    if effective_q <= 0:
        return 0.0
    if effective_q >= 1:
        return float(lognorm.ppf(0.999))
    return float(lognorm.ppf(effective_q))


def main() -> None:
    """도선사 운영 분석 메인 함수."""
    # 데이터 로드
    loader = HarborDataLoader()
    all_locs = {
        **AIS_SUPPLEMENTARY_LOCATIONS,
        **loader.load_anchorage_locations(),
        **loader.load_berth_locations(),
    }
    # TravelTimeMatrix는 내부 캐시 목적으로 초기화만 (현재 분석에서 직접 사용 안 함)
    _matrix = TravelTimeMatrix(all_locs, {})

    df = pd.read_csv("data/raw/scheduling/data/2024-06_SchData.csv")
    df["actual_start"] = pd.to_datetime(df["실제 스케줄 시작 시각"], utc=True)
    df["actual_end"] = pd.to_datetime(df["실제 스케줄 종료 시각"], utc=True)
    df["initial_schedule"] = pd.to_datetime(df["최초 스케줄 시각"], utc=True)
    df["service_min"] = (
        df["actual_end"] - df["actual_start"]
    ).dt.total_seconds() / 60.0
    df_pilot = df[df["도선사"].notna()].copy()

    pilot_station_pos = PILOT_STATION[1]

    # 각 서비스에 대해 도선사 이동시간 계산
    pilot_stats: list[dict] = []
    for _, row in df_pilot.iterrows():
        start_berth = str(row["작업 시작지"]).strip()
        berth_pos = all_locs.get(start_berth, pilot_station_pos)
        travel_min = travel_time_pilot(pilot_station_pos, berth_pos)

        delay_sec = (
            row["actual_start"] - row["initial_schedule"]
        ).total_seconds()

        pilot_stats.append(
            {
                "pilot": row["도선사"],
                "vessel": row["선박명"],
                "start_berth": start_berth,
                "travel_min": travel_min,
                "service_min": row["service_min"],
                "actual_start": row["actual_start"].timestamp() / 60.0,
                "delay_min": max(0.0, delay_sec / 60.0),
            }
        )

    df_stats = pd.DataFrame(pilot_stats)

    # newsvendor 최적 버퍼
    try:
        opt_buffer = newsvendor_buffer(
            w_v=2.0,
            w_p=1.0,
            mu_log=MU_LOG,
            sigma_log=SIGMA_LOG,
            p_delay=DELAY_PROB,
        )
    except ImportError:
        opt_buffer = 55.0  # scipy 없으면 근사값 (분포 중앙값 근사)

    # 도선사별 통계
    by_pilot = (
        df_stats.groupby("pilot")
        .agg(
            n=("vessel", "count"),
            avg_travel_min=("travel_min", "mean"),
            avg_service_min=("service_min", "mean"),
            avg_delay_min=("delay_min", "mean"),
        )
        .round(2)
        .to_dict("index")
    )

    # 결과 저장
    result = {
        "n_services_with_pilot": len(df_pilot),
        "n_unique_pilots": int(df_pilot["도선사"].nunique()),
        "pilot_station": {
            "name": PILOT_STATION[0],
            "lat": PILOT_STATION[1][0],
            "lon": PILOT_STATION[1][1],
        },
        "pilot_speed_kmh": PILOT_SPEED_KMH,
        "avg_travel_min": round(float(df_stats["travel_min"].mean()), 2),
        "avg_service_min": round(float(df_stats["service_min"].mean()), 2),
        "newsvendor_optimal_buffer_min": round(opt_buffer, 2),
        "interpretation": (
            f"도선사는 선박 서비스 시작 기준 평균 {df_stats['travel_min'].mean():.1f}분 전에 PAL 출발 필요. "
            f"불확실 도착 하에서 newsvendor 최적 버퍼: {opt_buffer:.1f}분 추가 여유."
        ),
        "by_pilot": {k: dict(v) for k, v in by_pilot.items()},
    }

    out_json = pathlib.Path("results/pilot_analysis.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 타임라인 차트
    top_pilots = df_stats.groupby("pilot").size().nlargest(8).index.tolist()
    df_top = df_stats[df_stats["pilot"].isin(top_pilots)].copy()
    df_top = df_top.sort_values("actual_start")  # noqa: F841 (reserved for future use)

    fig, axes = plt.subplots(2, 1, figsize=(16, 10), dpi=120)

    # Panel 1: 이동시간 분포
    ax = axes[0]
    ax.hist(
        df_stats["travel_min"],
        bins=20,
        color="steelblue",
        alpha=0.7,
        edgecolor="white",
    )
    ax.axvline(
        df_stats["travel_min"].mean(),
        color="red",
        linestyle="--",
        label=f"Mean={df_stats['travel_min'].mean():.1f}min",
    )
    ax.axvline(
        opt_buffer,
        color="orange",
        linestyle="--",
        label=f"Optimal buffer={opt_buffer:.1f}min",
    )
    ax.set_xlabel("Travel Time (minutes)")
    ax.set_ylabel("Count")
    ax.set_title("Pilot Travel Time Distribution (PAL → Work Site)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Panel 2: 도선사별 평균 이동+서비스 시간
    ax2 = axes[1]
    pilot_summary = (
        df_stats.groupby("pilot")[["travel_min", "service_min"]]
        .mean()
        .sort_values("service_min", ascending=False)
        .head(15)
    )
    x = range(len(pilot_summary))
    ax2.bar(
        x,
        pilot_summary["travel_min"],
        label="Avg Travel (min)",
        color="steelblue",
        alpha=0.8,
    )
    ax2.bar(
        x,
        pilot_summary["service_min"],
        bottom=pilot_summary["travel_min"],
        label="Avg Service (min)",
        color="mediumseagreen",
        alpha=0.8,
    )
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(pilot_summary.index, rotation=45)
    ax2.set_ylabel("Minutes")
    ax2.set_title("Pilot Time Breakdown: Travel + Service")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("results/pilot_timeline.png", bbox_inches="tight")
    plt.close()

    print("\n=== 도선사 운영 분석 ===")
    print(
        f"파일럿 서비스: {len(df_pilot)}건, 도선사: {df_pilot['도선사'].nunique()}명"
    )
    print(f"평균 이동시간 (PAL→작업지): {df_stats['travel_min'].mean():.1f}분")
    print(f"평균 서비스시간: {df_stats['service_min'].mean():.1f}분")
    print(f"newsvendor 최적 버퍼: {opt_buffer:.1f}분")
    print(f"결과: {out_json.resolve()}")


if __name__ == "__main__":
    main()
