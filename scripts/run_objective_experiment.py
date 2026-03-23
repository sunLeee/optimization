"""
목적함수 실증 비교 실험 러너.

4종 ObjectiveStrategy를 2024-06 부산항 실데이터(N=336)에 대해 실행하고
결과를 CSV로 저장한다.

사용법:
    uv run python scripts/run_objective_experiment.py \\
        --data data/raw/scheduling/data/2024-06_SchData.csv \\
        --out results/objective_comparison.csv \\
        --seed 42
"""
from __future__ import annotations

import argparse
import logging
import pathlib
import sys

import pandas as pd

# libs/ 경로 보장
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from libs.evaluation import RealDataBacktester
from libs.optimization import (
    MinAllObjective,
    MinCompositeObjective,
    MinIdleObjective,
    MinWaitObjective,
    ObjectiveStrategy,
)


def build_strategies(
    w2: float = 0.5,
    w3: float = 0.5,
    lam: float = 1.0,
) -> list[ObjectiveStrategy]:
    """4종 ObjectiveStrategy 인스턴스 생성."""
    return [
        MinWaitObjective(),
        MinIdleObjective(),
        MinCompositeObjective(w2=w2, w3=w3),
        MinAllObjective(lam=lam),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="목적함수 실증 비교 실험: 4종 전략 × N=336 실데이터"
    )
    parser.add_argument(
        "--data",
        default="data/raw/scheduling/data/2024-06_SchData.csv",
        help="입력 CSV 경로 (default: %(default)s)",
    )
    parser.add_argument(
        "--out",
        default="results/objective_comparison.csv",
        help="출력 CSV 경로 (default: %(default)s)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="난수 시드 (현재 미사용, 향후 SAA 연동용)",
    )
    parser.add_argument(
        "--w2",
        type=float,
        default=0.5,
        help="OBJ-C idle 가중치 w2 (default: %(default)s)",
    )
    parser.add_argument(
        "--w3",
        type=float,
        default=0.5,
        help="OBJ-C wait 가중치 w3 (default: %(default)s)",
    )
    parser.add_argument(
        "--lam",
        type=float,
        default=1.0,
        help="OBJ-D dist 가중치 λ (default: %(default)s)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="로그 수준 (default: %(default)s)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("experiment")

    # 입력 파일 확인
    data_path = pathlib.Path(args.data)
    if not data_path.exists():
        logger.error("데이터 파일 없음: %s", data_path)
        sys.exit(1)

    # 출력 디렉토리 생성
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("=== 목적함수 실증 비교 실험 시작 ===")
    logger.info("데이터: %s", data_path)
    logger.info("출력: %s", out_path)

    # 백테스터 초기화
    backtester = RealDataBacktester(
        csv_path=str(data_path),
        tug_fleet=[],
        berth_locations={},
    )
    logger.info("n_samples=%d", backtester.n_samples)

    # 전략 생성
    strategies = build_strategies(w2=args.w2, w3=args.w3, lam=args.lam)
    logger.info("전략 수: %d", len(strategies))

    # 실행
    results = backtester.run_all(strategies)
    df: pd.DataFrame = backtester.to_dataframe(results)

    # CSV 저장
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    logger.info("결과 저장: %s (%d행)", out_path, len(df))

    # 요약 출력
    print("\n=== 실험 결과 요약 ===")
    summary = df[
        ["objective", "idle_h", "wait_h", "objective_value", "solve_time_sec"]
    ].copy()
    summary["idle_h"] = summary["idle_h"].round(2)
    summary["wait_h"] = summary["wait_h"].round(2)
    summary["objective_value"] = summary["objective_value"].round(4)
    summary["solve_time_sec"] = summary["solve_time_sec"].map(
        lambda x: f"{x*1000:.1f}ms"
    )
    print(summary.to_string(index=False))
    print(f"\n결과 파일: {out_path}")


if __name__ == "__main__":
    main()
