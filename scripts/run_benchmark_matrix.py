"""
N×M 벤치마크 매트릭스 러너.

4종 SolverStrategy × 4종 ObjectiveStrategy를 실데이터(N=336)에 대해 실행하고
KPI를 CSV로 저장한다.

Tier별 n 제한 (AW-005):
    MILP   (Tier 1): n=8    (n<10 정확해)
    ALNS   (Tier 2): n=30   (n=10~50 대상)
    Benders(Tier 3): n=80   (n>50 대상)
    Rolling(MPC)   : n<=240 (최초 스케줄 시각 기준 24h 이내 선박)

사용법:
    uv run python scripts/run_benchmark_matrix.py \\
        --data data/raw/scheduling/data/2024-06_SchData.csv \\
        --out results/benchmark_matrix.csv \\
        --log-level INFO
"""
from __future__ import annotations

import argparse
import logging
import pathlib
import sys
import time
import traceback

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from libs.evaluation import RealDataBacktester
from libs.optimization import (
    MinAllObjective,
    MinCompositeObjective,
    MinIdleObjective,
    MinWaitObjective,
    ObjectiveStrategy,
)
from libs.solver import (
    ALNSSolver,
    BendersSolver,
    ConvergenceCriteria,
    MILPSolver,
    RollingSolver,
    SolverStrategy,
)
from libs.utils.time_window import TimeWindowSpec

logger = logging.getLogger(__name__)

# ── 부산항 대표 좌표 (fallback) ─────────────────────────────────
BUSAN_DEFAULT_LOC: tuple[float, float] = (35.098, 129.037)

# 정계지 위치.csv 기반 (근사치)
KNOWN_BERTH_LOCATIONS: dict[str, tuple[float, float]] = {
    "연안부두정계지": (35.099, 129.037),
    "송도정계지": (35.082, 128.990),
    "내항정계지": (35.108, 129.038),
    "북항임시정계지": (35.115, 129.042),
}

# ── Tier별 솔버 + 데이터 슬라이스 설정 ──────────────────────────
SOLVER_CONFIGS: list[dict] = [
    {
        "name": "MILP-Tier1",
        "solver": MILPSolver(),
        "n_windows": 8,  # Tier 1: n < 10
        "criteria": ConvergenceCriteria(time_limit_sec=30.0),
    },
    {
        "name": "ALNS-Tier2",
        "solver": ALNSSolver(),
        "n_windows": 30,  # Tier 2: n = 10~50
        "criteria": ConvergenceCriteria(
            max_iter=200, improvement_threshold=0.001
        ),
    },
    {
        "name": "Benders-Tier3",
        "solver": BendersSolver(),
        "n_windows": 80,  # Tier 3: n > 50
        "criteria": ConvergenceCriteria(
            time_limit_sec=60.0,
            max_iter=20,
            improvement_threshold=0.005,
        ),
    },
    {
        "name": "RollingHorizon-MPC",
        "solver": RollingSolver(simulate_until_h=24.0),
        "n_windows": None,  # 24h 이내 선박 전체 (필터링 적용)
        "criteria": None,
    },
]

OBJECTIVES: list[ObjectiveStrategy] = [
    MinWaitObjective(),
    MinIdleObjective(),
    MinCompositeObjective(w2=0.5, w3=0.5),
    MinAllObjective(lam=1.0),
]


def _build_berth_locations(
    windows: list[TimeWindowSpec],
) -> dict[str, tuple[float, float]]:
    """TimeWindowSpec에 등장하는 모든 berth_id에 좌표를 매핑.

    KNOWN_BERTH_LOCATIONS에 없으면 BUSAN_DEFAULT_LOC 사용.
    """
    berth_ids = {w.berth_id for w in windows if w.berth_id}
    return {
        bid: KNOWN_BERTH_LOCATIONS.get(bid, BUSAN_DEFAULT_LOC)
        for bid in berth_ids
    }


def _extract_tug_fleet(backtester: RealDataBacktester) -> list[str]:
    """백테스터 assignments에서 고유 예인선 ID 추출."""
    tug_ids: list[str] = sorted(
        {spec.tug_id for spec in backtester._assignments}
    )
    return tug_ids if tug_ids else ["T0", "T1", "T2"]


def _filter_24h_windows(
    windows: list[TimeWindowSpec],
    horizon_h: float = 24.0,
) -> list[TimeWindowSpec]:
    """earliest_start < horizon_h * 60 인 TimeWindowSpec만 반환."""
    cutoff_min = horizon_h * 60.0
    return [w for w in windows if w.earliest_start < cutoff_min]


def run_single(
    solver_cfg: dict,
    objective: ObjectiveStrategy,
    all_windows: list[TimeWindowSpec],
    tug_fleet: list[str],
) -> dict:
    """단일 (solver, objective) 조합 실행 → 결과 dict 반환."""
    solver_name: str = solver_cfg["name"]
    solver: SolverStrategy = solver_cfg["solver"]
    n_windows: int | None = solver_cfg["n_windows"]
    criteria = solver_cfg["criteria"]
    obj_name: str = objective.name()

    # 데이터 슬라이스
    if solver_name == "RollingHorizon-MPC":
        windows = _filter_24h_windows(all_windows)
    elif n_windows is not None:
        windows = all_windows[:n_windows]
    else:
        windows = all_windows

    if not windows:
        logger.warning("%s × %s: windows 없음 — 스킵", solver_name, obj_name)
        return _error_row(solver_name, obj_name, 0, "windows_empty")

    berth_locations = _build_berth_locations(windows)
    n_samples = len(windows)

    logger.info(
        "  실행: %s × %s | n=%d",
        solver_name,
        obj_name,
        n_samples,
    )

    t0 = time.perf_counter()
    try:
        result = solver.solve(
            windows=windows,
            tug_fleet=tug_fleet,
            berth_locations=berth_locations,
            objective=objective,
            criteria=criteria,
        )
        elapsed = time.perf_counter() - t0

        if not result.assignments:
            logger.warning(
                "  %s × %s: assignments 비어 있음", solver_name, obj_name
            )
            return _error_row(
                solver_name, obj_name, n_samples, "no_assignments"
            )

        kpi = objective.compute(result.assignments, windows)

        logger.info(
            "  완료: idle=%.2fh wait=%.2fh obj=%.4f gap=%.4f (%.2fs)",
            kpi.idle_h,
            kpi.wait_h,
            kpi.objective_value,
            result.optimality_gap,
            elapsed,
        )

        return {
            "solver": solver_name,
            "objective": obj_name,
            "dist_nm": round(kpi.dist_nm, 4),
            "idle_h": round(kpi.idle_h, 4),
            "wait_h": round(kpi.wait_h, 4),
            "fuel_mt": round(kpi.fuel_mt, 4),
            "objective_value": round(kpi.objective_value, 6),
            "solve_time_sec": round(result.solve_time_sec, 4),
            "optimality_gap": round(result.optimality_gap, 6),
            "n_samples": n_samples,
            "error": "",
        }

    except Exception as e:
        elapsed = time.perf_counter() - t0
        logger.error(
            "  오류: %s × %s | %.2fs | %s",
            solver_name,
            obj_name,
            elapsed,
            e,
        )
        logger.debug(traceback.format_exc())
        return _error_row(solver_name, obj_name, n_samples, str(e)[:120])


def _error_row(
    solver_name: str,
    obj_name: str,
    n_samples: int,
    error_msg: str,
) -> dict:
    """오류 발생 시 NaN 채운 행 반환."""
    return {
        "solver": solver_name,
        "objective": obj_name,
        "dist_nm": float("nan"),
        "idle_h": float("nan"),
        "wait_h": float("nan"),
        "fuel_mt": float("nan"),
        "objective_value": float("nan"),
        "solve_time_sec": float("nan"),
        "optimality_gap": float("nan"),
        "n_samples": n_samples,
        "error": error_msg,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="N×M 벤치마크 매트릭스: 4 솔버 × 4 목적함수 × 실데이터"
    )
    parser.add_argument(
        "--data",
        default="data/raw/scheduling/data/2024-06_SchData.csv",
        help="입력 CSV 경로 (default: %(default)s)",
    )
    parser.add_argument(
        "--out",
        default="results/benchmark_matrix.csv",
        help="출력 CSV 경로 (default: %(default)s)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    parser.add_argument(
        "--skip-rolling",
        action="store_true",
        help="RollingHorizon-MPC 스킵 (긴 시뮬레이션 시간 회피)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    data_path = pathlib.Path(args.data)
    if not data_path.exists():
        logger.error("데이터 파일 없음: %s", data_path)
        sys.exit(1)

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("=== N×M 벤치마크 매트릭스 시작 ===")
    logger.info("데이터: %s", data_path)
    logger.info("출력:   %s", out_path)

    # 실데이터 로드
    backtester = RealDataBacktester(
        csv_path=str(data_path),
        tug_fleet=[],
        berth_locations={},
    )
    all_windows: list[TimeWindowSpec] = backtester._windows
    tug_fleet: list[str] = _extract_tug_fleet(backtester)

    logger.info(
        "로드 완료: n_samples=%d, tug_fleet=%s",
        backtester.n_samples,
        tug_fleet,
    )

    # 솔버 필터
    solver_configs = SOLVER_CONFIGS
    if args.skip_rolling:
        solver_configs = [
            cfg
            for cfg in solver_configs
            if cfg["name"] != "RollingHorizon-MPC"
        ]
        logger.info("RollingHorizon-MPC 스킵 (--skip-rolling 플래그)")

    # N×M 실험
    rows: list[dict] = []
    total = len(solver_configs) * len(OBJECTIVES)
    idx = 0

    for solver_cfg in solver_configs:
        logger.info("── 솔버: %s ──────────────────", solver_cfg["name"])
        for objective in OBJECTIVES:
            idx += 1
            logger.info("[%d/%d]", idx, total)
            row = run_single(solver_cfg, objective, all_windows, tug_fleet)
            rows.append(row)

    # 결과 저장
    df = pd.DataFrame(rows)
    col_order = [
        "solver",
        "objective",
        "dist_nm",
        "idle_h",
        "wait_h",
        "fuel_mt",
        "objective_value",
        "solve_time_sec",
        "optimality_gap",
        "n_samples",
        "error",
    ]
    df = df[col_order]
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    logger.info("저장 완료: %s (%d행)", out_path, len(df))

    # 요약 출력
    print("\n=== N×M 벤치마크 결과 요약 ===")
    summary = df[
        [
            "solver",
            "objective",
            "idle_h",
            "wait_h",
            "objective_value",
            "solve_time_sec",
            "n_samples",
            "error",
        ]
    ].copy()
    summary["idle_h"] = summary["idle_h"].round(2)
    summary["wait_h"] = summary["wait_h"].round(2)
    summary["objective_value"] = summary["objective_value"].round(4)
    summary["solve_time_sec"] = summary["solve_time_sec"].map(
        lambda x: f"{x:.2f}s" if not pd.isna(x) else "ERR"
    )
    print(summary.to_string(index=False))

    # 오류 요약
    errors = df[df["error"] != ""]
    if not errors.empty:
        print(f"\n오류 발생: {len(errors)}건")
        for _, r in errors.iterrows():
            print(f"  [{r['solver']} × {r['objective']}] {r['error']}")

    # 최우수 조합 (objective_value 기준)
    valid = df[df["error"] == ""].copy()
    if not valid.empty:
        print("\n=== 목적함수별 최우수 솔버 ===")
        for obj_name in valid["objective"].unique():
            subset = valid[valid["objective"] == obj_name]
            best = subset.loc[subset["objective_value"].idxmin()]
            print(
                f"  {obj_name}: {best['solver']}"
                f" (obj={best['objective_value']:.4f},"
                f" n={best['n_samples']})"
            )

    print(f"\n결과 파일: {out_path}")


if __name__ == "__main__":
    main()
