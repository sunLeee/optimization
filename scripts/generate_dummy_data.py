"""
인천항 예선 스케줄링 더미 데이터 생성기.

실데이터(SchData.csv)에서 분포 파라미터를 추출하여
파이프라인 호환 합성 CSV 파일을 생성한다.

출력 파일:
    {out_dir}/2024-06_SchData.csv          — SchData 형식 (24컬럼)
    {out_dir}/2024-06_FristAllSchData.csv  — 초기 요청 (7컬럼)
    {out_dir}/선석 코드.csv                 — 원본 복사
    {out_dir}/정계지 위치.csv               — 원본 복사
    {out_dir}/예선 코드.csv                 — 원본 복사
    {out_dir}/AISLog/                      — 빈 디렉토리 (TravelTimeMatrix 요구)
    {out_dir}/generation_report.json       — 생성 파라미터 및 통계

사용법:
    uv run python scripts/generate_dummy_data.py
    uv run python scripts/generate_dummy_data.py --n-days 7 --seed 123
    uv run python scripts/generate_dummy_data.py --run-pipeline
"""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import shutil
import subprocess
import sys
from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

REAL_DATA_DIR = pathlib.Path("data/raw/scheduling/data")

# SchData 24컬럼 (순서 유지)
SCH_COLS = [
    "기준예선", "배정예선", "선박명", "From", "작업 시작지", "작업 종료지", "To",
    "실제 스케줄 시작 시각", "실제 스케줄 종료 시각",
    "작업까지 이동 거리(km)", "작업까지 이동 시간(분)",
    "작업중 이동 거리(km)", "작업중 이동 시간(분)",
    "도선사", "톤수", "선종",
    "최종 스케줄 시각", "최초 스케줄 시각",
    "최초 작업시작지", "최초 작업종료지", "최초 예선", "최초 도선사",
    "AIS 파일명 target", "AIS 파일명 tug",
]

# FristAllSchData 7컬럼
FRIST_COLS = [
    "배정예선", "선박명", "작업 시작지", "작업 종료지",
    "스케줄 시작 시각", "도선사", "톤수",
]

# AW-010 ETA 지연 분포 파라미터
MU_LOG = 4.015
SIGMA_LOG = 1.363
DELAY_PROB = 0.714

# 국적 및 선종 더미 풀
NATIONALITIES = ["KOREAN", "CHINESE", "JAPANESE", "GREEK", "NORWEGIAN", "SINGAPOREAN"]
VESSEL_TYPES_KOR = [
    "풀컨테이너선", "일반화물선", "석유제품 운반선", "산물선(벌크선)",
    "자동차운반선", "국제카페리", "케미칼 운반선", "세미(혼재)컨테이너선",
    "시멘트운반선", "LPG 운반선",
]

# 시나리오별 설정
SCENARIO_CONFIG: dict[str, dict] = {
    "normal":       {"lambda_daily": 15.0, "large_pct": 0.10},
    "heavy":        {"lambda_daily": 25.0, "large_pct": 0.40},
    "large_vessel": {"lambda_daily": 10.0, "large_pct": 0.80},
    "stress":       {"lambda_daily": 35.0, "large_pct": 0.30},
}

# 대형 선박 클래스 (이름, 최소 톤수, 최대 톤수)
LARGE_VESSEL_CLASSES: list[tuple[str, int, int]] = [
    ("Handysize",    10_000,  35_000),
    ("Panamax",      60_000,  80_000),
    ("Aframax",      80_000, 120_000),
    ("Suezmax",     120_000, 200_000),
    ("VLCC",        200_000, 320_000),
    ("LNG_Carrier",  70_000, 180_000),
]


class FitParams:
    """실데이터에서 추출한 분포 파라미터."""

    def __init__(
        self,
        tonnage_lognorm: tuple[float, float, float],
        service_gamma: tuple[float, float, float],
        travel_gamma: tuple[float, float, float],
        berth_codes: list[str],
        berth_weights: list[float],
        vessel_types: list[str],
        vessel_type_weights: list[float],
        tug_codes: list[str],
        pilot_codes: list[str],
        anchorage_from: list[str],
        anchorage_to: list[str],
    ) -> None:
        self.tonnage_lognorm = tonnage_lognorm
        self.service_gamma = service_gamma
        self.travel_gamma = travel_gamma
        self.berth_codes = berth_codes
        self.berth_weights = berth_weights
        self.vessel_types = vessel_types
        self.vessel_type_weights = vessel_type_weights
        self.tug_codes = tug_codes
        self.pilot_codes = pilot_codes
        self.anchorage_from = anchorage_from
        self.anchorage_to = anchorage_to


def _load_tug_mapping() -> dict[str, str]:
    """예선 코드.csv -> {코드: 이름} (standalone wrapper)."""
    df = pd.read_csv(REAL_DATA_DIR / "예선 코드.csv")
    return {str(r["예선코드"]).strip(): str(r["예선명"]).strip() for _, r in df.iterrows()}


def _load_known_berths() -> list[str]:
    """선석 코드.csv의 선석코드 목록 (standalone wrapper)."""
    df = pd.read_csv(REAL_DATA_DIR / "선석 코드.csv")
    return [str(c).strip() for c in df["선석코드"]]


def fit_distributions(real_sch_path: pathlib.Path) -> FitParams:
    """실데이터에서 분포 파라미터를 추출한다.

    Args:
        real_sch_path: 실데이터 SchData.csv 경로.

    Returns:
        FitParams 객체.
    """
    df = pd.read_csv(real_sch_path)

    # 톤수 Log-normal 피팅
    tonnage = df["톤수"].dropna().clip(lower=1)
    t_params = stats.lognorm.fit(tonnage, floc=0)

    # 서비스 시간 Gamma 피팅
    svc = df["작업중 이동 시간(분)"].dropna().clip(lower=1)
    s_params = stats.gamma.fit(svc, floc=0)

    # 이동 시간 Gamma 피팅
    trav = df["작업까지 이동 시간(분)"].dropna().clip(lower=1)
    tr_params = stats.gamma.fit(trav, floc=0)

    # 선석 빈도
    berth_counts = df["작업 시작지"].value_counts()
    top_berths = berth_counts.head(20)
    b_codes = top_berths.index.tolist()
    b_weights = (top_berths.values / top_berths.values.sum()).tolist()

    # 선종 빈도
    vt_counts = df["선종"].value_counts()
    v_types = vt_counts.index.tolist()
    v_weights = (vt_counts.values / vt_counts.values.sum()).tolist()

    # 예선/도선사 코드
    tug_map = _load_tug_mapping()
    tug_codes = list(tug_map.keys())
    pilot_codes = sorted(df["도선사"].dropna().unique().tolist())

    # 정계지
    anch_from = df["From"].dropna().unique().tolist()
    anch_to = df["To"].dropna().unique().tolist()
    if not anch_from:
        anch_from = ["연안부두정계지", "송도정계지"]
    if not anch_to:
        anch_to = ["연안부두정계지", "송도정계지"]

    logger.info(
        "분포 피팅 완료: 선석=%d, 선종=%d, 예선=%d, 도선사=%d",
        len(b_codes), len(v_types), len(tug_codes), len(pilot_codes),
    )
    return FitParams(
        tonnage_lognorm=t_params,
        service_gamma=s_params,
        travel_gamma=tr_params,
        berth_codes=b_codes,
        berth_weights=b_weights,
        vessel_types=v_types,
        vessel_type_weights=v_weights,
        tug_codes=tug_codes,
        pilot_codes=pilot_codes,
        anchorage_from=anch_from,
        anchorage_to=anch_to,
    )


def _sample_delay_min(rng: np.random.Generator) -> float:
    """AW-010 기반 ETA 지연 샘플링 (분)."""
    if rng.random() < DELAY_PROB:
        delay = float(rng.lognormal(MU_LOG, SIGMA_LOG))
        return float(np.clip(delay, 0, 360))
    return float(-rng.uniform(0, 60))


def _fmt_dt(dt: datetime) -> str:
    """datetime -> ISO-8601 UTC 문자열."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _required_tugs(tonnage: float) -> int:
    if tonnage < 5_000:
        return 1
    if tonnage < 30_000:
        return 2
    if tonnage < 60_000:
        return 3
    return 4


def sample_service(
    row_id: int,
    date: datetime,
    fits: FitParams,
    rng: np.random.Generator,
    large_pct: float = 0.10,
) -> dict:
    """SchData 형식의 서비스 1건을 샘플링한다.

    Args:
        row_id: 행 인덱스 (선박명 생성에 사용).
        date: 서비스 날짜.
        fits: 분포 파라미터.
        rng: 랜덤 생성기.

    Returns:
        24컬럼 딕셔너리.
    """
    # 톤수 샘플링: large_pct 확률로 대형 선박 클래스 선택
    if large_pct > 0 and rng.random() < large_pct:
        # 대형 선박 클래스에서 균등 선택
        cls_name, cls_min, cls_max = LARGE_VESSEL_CLASSES[
            int(rng.integers(0, len(LARGE_VESSEL_CLASSES)))
        ]
        tonnage = float(rng.uniform(cls_min, cls_max))
    else:
        tonnage = max(500.0, float(stats.lognorm.rvs(*fits.tonnage_lognorm, random_state=rng.integers(0, 2**31))))
    tonnage = min(tonnage, 320_000.0)
    r_j = _required_tugs(tonnage)

    # 선석
    start_berth = str(rng.choice(fits.berth_codes, p=fits.berth_weights))
    end_berth = str(rng.choice(fits.berth_codes, p=fits.berth_weights))

    # 이동거리/시간
    travel_t = max(2.0, float(stats.gamma.rvs(*fits.travel_gamma, random_state=rng.integers(0, 2**31))))
    service_t = max(5.0, float(stats.gamma.rvs(*fits.service_gamma, random_state=rng.integers(0, 2**31))))
    travel_km = travel_t / 60.0 * 6.0 * 1.852   # 6 kn x time -> km
    service_km = service_t / 60.0 * 6.0 * 1.852

    # 최초 스케줄 시각 (하루 8:00~23:00 균등)
    hour_offset = float(rng.uniform(8, 23))
    initial_dt = date + timedelta(hours=hour_offset)

    # 지연 적용
    delay_min = _sample_delay_min(rng)
    actual_start_dt = initial_dt + timedelta(minutes=delay_min)
    actual_end_dt = actual_start_dt + timedelta(minutes=travel_t + service_t)
    final_dt = initial_dt + timedelta(minutes=float(rng.uniform(0, max(delay_min, 0) + 10)))

    # 예선 배정
    tug_codes = fits.tug_codes
    base_tug = str(rng.choice(tug_codes))
    other_tugs = [t for t in tug_codes if t != base_tug]
    if r_j > 1:
        extra = list(rng.choice(other_tugs, size=min(r_j - 1, len(other_tugs)), replace=False))
        assigned = [base_tug] + extra
    else:
        assigned = [base_tug]
    assigned_str = ",".join(assigned)

    # 최초 예선 (85% 확률로 다름)
    if rng.random() < 0.85 and len(tug_codes) > 1:
        initial_tug_codes = [t for t in tug_codes if t not in assigned]
        initial_tug = str(rng.choice(initial_tug_codes)) if initial_tug_codes else base_tug
    else:
        initial_tug = assigned_str

    # 도선사
    pilot = str(rng.choice(fits.pilot_codes)) if fits.pilot_codes else "KU"
    initial_pilot = str(rng.choice(fits.pilot_codes)) if fits.pilot_codes else pilot

    # 선종
    vessel_type = str(rng.choice(fits.vessel_types, p=fits.vessel_type_weights))

    # 선박명
    nation = str(rng.choice(NATIONALITIES))
    vtype_short = vessel_type.split("(")[0][:6].upper().replace(" ", "_")
    vessel_name = f"{nation}_{vtype_short}_{row_id:04d}"

    # 정계지 (Architect fix: np.nan, not "")
    from_anch = str(rng.choice(fits.anchorage_from)) if rng.random() < 0.65 else np.nan
    to_anch = str(rng.choice(fits.anchorage_to)) if rng.random() < 0.55 else np.nan

    return {
        "기준예선": base_tug,
        "배정예선": assigned_str,
        "선박명": vessel_name,
        "From": from_anch,
        "작업 시작지": start_berth,
        "작업 종료지": end_berth,
        "To": to_anch,
        "실제 스케줄 시작 시각": _fmt_dt(actual_start_dt),
        "실제 스케줄 종료 시각": _fmt_dt(actual_end_dt),
        "작업까지 이동 거리(km)": round(travel_km, 3),
        "작업까지 이동 시간(분)": round(travel_t, 3),
        "작업중 이동 거리(km)": round(service_km, 3),
        "작업중 이동 시간(분)": round(service_t, 3),
        "도선사": pilot,
        "톤수": int(tonnage),
        "선종": vessel_type,
        "최종 스케줄 시각": _fmt_dt(final_dt),
        "최초 스케줄 시각": _fmt_dt(initial_dt),
        "최초 작업시작지": start_berth,
        "최초 작업종료지": end_berth,
        "최초 예선": initial_tug,
        "최초 도선사": initial_pilot,
        "AIS 파일명 target": "",
        "AIS 파일명 tug": "",
    }


def generate_sch_data(
    fits: FitParams,
    n_days: int,
    lambda_daily: float,
    start_date: datetime,
    rng: np.random.Generator,
    large_pct: float = 0.10,
) -> pd.DataFrame:
    """SchData 형식 더미 DataFrame 생성.

    Args:
        fits: 분포 파라미터.
        n_days: 생성할 날짜 수.
        lambda_daily: 일일 평균 서비스 건수.
        start_date: 시작 날짜 (UTC).
        rng: 랜덤 생성기.
        large_pct: 대형 선박 비율 (0.0~1.0).

    Returns:
        24컬럼 DataFrame.
    """
    rows = []
    row_id = 0
    for day_idx in range(n_days):
        date = start_date + timedelta(days=day_idx)
        n_services = max(1, int(rng.poisson(lambda_daily)))
        for _ in range(n_services):
            row = sample_service(row_id, date, fits, rng, large_pct=large_pct)
            rows.append(row)
            row_id += 1
    df = pd.DataFrame(rows, columns=SCH_COLS)
    logger.info("SchData 생성: %d건 / %d일", len(df), n_days)
    return df


def generate_frist_all_sch_data(
    sch_df: pd.DataFrame,
    fits: FitParams,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """FristAllSchData 형식 더미 DataFrame 생성.

    SchData에서 1.8~2.5배 리샘플링하고 시각을 앞당겨 초기 요청처럼 만든다.

    Args:
        sch_df: 생성된 SchData DataFrame.
        fits: 분포 파라미터 (예선 코드).
        rng: 랜덤 생성기.

    Returns:
        7컬럼 DataFrame.
    """
    multiplier = rng.uniform(1.8, 2.5)
    n_frist = int(len(sch_df) * multiplier)
    sampled = sch_df.sample(n=n_frist, replace=True, random_state=int(rng.integers(0, 2**31)))

    frist_rows = []
    for _, base in sampled.iterrows():
        # 스케줄 시작 시각: 실제보다 평균 103분 빨리
        actual_dt = datetime.fromisoformat(base["실제 스케줄 시작 시각"].replace("Z", "+00:00"))
        early_min = float(rng.lognormal(mean=4.5, sigma=0.8))
        sched_dt = actual_dt - timedelta(minutes=early_min)

        # 85% 확률로 배정 예선 다름
        if rng.random() < 0.85 and fits.tug_codes:
            assigned_codes = base["배정예선"].split(",")
            other = [t for t in fits.tug_codes if t not in assigned_codes]
            r_j = len(assigned_codes)
            if other:
                new_assigned = list(rng.choice(other, size=min(r_j, len(other)), replace=False))
                assigned_str = ",".join(new_assigned)
            else:
                assigned_str = base["배정예선"]
        else:
            assigned_str = base["배정예선"]

        frist_rows.append({
            "배정예선": assigned_str,
            "선박명": base["선박명"],
            "작업 시작지": base["작업 시작지"],
            "작업 종료지": base["작업 종료지"],
            "스케줄 시작 시각": _fmt_dt(sched_dt.replace(tzinfo=None).replace(tzinfo=UTC)),
            "도선사": base["도선사"],
            "톤수": base["톤수"],
        })

    df = pd.DataFrame(frist_rows, columns=FRIST_COLS)
    logger.info("FristAllSchData 생성: %d건 (배율 %.2f×)", len(df), multiplier)
    return df


def write_outputs(
    sch_df: pd.DataFrame,
    frist_df: pd.DataFrame,
    out_dir: pathlib.Path,
    params: dict,
) -> None:
    """생성된 DataFrame과 참조 파일을 저장한다.

    Args:
        sch_df: SchData DataFrame.
        frist_df: FristAllSchData DataFrame.
        out_dir: 출력 디렉토리.
        params: 생성 파라미터 딕셔너리 (report용).
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. SchData — 로더 하드코딩 파일명 사용
    sch_path = out_dir / "2024-06_SchData.csv"
    sch_df.to_csv(sch_path, index=False, encoding="utf-8-sig")
    logger.info("저장: %s (%d건)", sch_path, len(sch_df))

    # 2. FristAllSchData
    frist_path = out_dir / "2024-06_FristAllSchData.csv"
    frist_df.to_csv(frist_path, index=False, encoding="utf-8-sig")
    logger.info("저장: %s (%d건)", frist_path, len(frist_df))

    # 3. 참조 파일 복사 (선석/정계지/예선 코드)
    for ref_file in ["선석 코드.csv", "정계지 위치.csv", "예선 코드.csv"]:
        src = REAL_DATA_DIR / ref_file
        dst = out_dir / ref_file
        if src.exists():
            shutil.copy2(src, dst)
            logger.info("복사: %s", dst)

    # 4. 빈 AISLog/ 디렉토리 (TravelTimeMatrix 요구)
    ais_dir = out_dir / "AISLog"
    ais_dir.mkdir(exist_ok=True)

    # 5. 생성 보고서
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "parameters": params,
        "statistics": {
            "n_sch_rows": len(sch_df),
            "n_frist_rows": len(frist_df),
            "frist_ratio": round(len(frist_df) / max(len(sch_df), 1), 2),
            "avg_tonnage": round(float(sch_df["톤수"].mean()), 0),
            "avg_service_min": round(float(sch_df["작업중 이동 시간(분)"].mean()), 1),
            "avg_delay_min": round(
                float(
                    (
                        pd.to_datetime(sch_df["실제 스케줄 시작 시각"], utc=True)
                        - pd.to_datetime(sch_df["최초 스케줄 시각"], utc=True)
                    ).dt.total_seconds().mean() / 60.0
                ),
                1,
            ),
        },
    }
    report_path = out_dir / "generation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info("보고서: %s", report_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="인천항 예선 스케줄링 더미 데이터 생성")
    parser.add_argument("--n-days", type=int, default=30, dest="n_days",
                        help="생성할 날짜 수 (기본 30)")
    parser.add_argument("--lambda-daily", type=float, default=15.0, dest="lambda_daily",
                        help="일일 평균 서비스 건수 (기본 15.0)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-dir", default="data/dummy", dest="out_dir",
                        help="출력 디렉토리 (기본 data/dummy/)")
    parser.add_argument("--start-date", default="2024-07-01", dest="start_date",
                        help="시작 날짜 YYYY-MM-DD (기본 2024-07-01)")
    parser.add_argument("--run-pipeline", action="store_true", dest="run_pipeline",
                        help="생성 후 build_full_problem.py 실행 검증")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument(
        "--scenario",
        default="normal",
        choices=["normal", "heavy", "large_vessel", "stress"],
        help="시나리오 선택 (기본 normal)",
    )
    args = parser.parse_args()

    scenario_cfg = SCENARIO_CONFIG[args.scenario]
    # --lambda-daily 명시 시 시나리오 기본값 override
    effective_lambda = args.lambda_daily if args.lambda_daily != 15.0 else scenario_cfg["lambda_daily"]
    large_pct = scenario_cfg["large_pct"]

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    rng = np.random.default_rng(args.seed)
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d").replace(tzinfo=UTC)
    out_dir = pathlib.Path(args.out_dir)

    real_sch = REAL_DATA_DIR / "2024-06_SchData.csv"
    if not real_sch.exists():
        logger.error("실데이터 없음: %s", real_sch)
        sys.exit(1)

    logger.info("=== 더미 데이터 생성 시작 ===")
    logger.info("scenario=%s, n_days=%d, lambda_daily=%.1f, large_pct=%.0f%%, seed=%d, out_dir=%s",
                args.scenario, args.n_days, effective_lambda, large_pct * 100, args.seed, out_dir)

    # 분포 파라미터 추출
    fits = fit_distributions(real_sch)

    # SchData 생성
    sch_df = generate_sch_data(fits, args.n_days, effective_lambda, start_date, rng, large_pct=large_pct)

    # FristAllSchData 생성
    frist_df = generate_frist_all_sch_data(sch_df, fits, rng)

    # 파일 저장
    params = {
        "n_days": args.n_days,
        "lambda_daily": effective_lambda,
        "scenario": args.scenario,
        "large_pct": large_pct,
        "seed": args.seed,
        "start_date": args.start_date,
        "out_dir": str(out_dir),
    }
    write_outputs(sch_df, frist_df, out_dir, params)

    print("\n=== 더미 데이터 생성 완료 ===")
    print(f"시나리오:        {args.scenario} (대형선 {large_pct*100:.0f}%, lambda={effective_lambda})")
    print(f"SchData:         {len(sch_df)}건 -> {out_dir}/2024-06_SchData.csv")
    print(f"FristAllSchData: {len(frist_df)}건 -> {out_dir}/2024-06_FristAllSchData.csv")
    print(f"기간:            {args.start_date} ~ {(start_date + timedelta(days=args.n_days-1)).strftime('%Y-%m-%d')}")
    print(f"시드:            {args.seed} (동일 시드로 동일 데이터 재생성 가능)")

    # 파이프라인 검증
    if args.run_pipeline:
        print("\n파이프라인 검증 중...")
        result = subprocess.run(
            ["uv", "run", "python", "scripts/build_full_problem.py",
             "--data-dir", str(out_dir), "--max-days", "2", "--log-level", "WARNING"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print("파이프라인 검증: SUCCESS")
        else:
            print("파이프라인 검증: FAILED")
            print(result.stderr[-500:] if result.stderr else "(no output)")


if __name__ == "__main__":
    main()
