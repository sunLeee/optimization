"""
tests/test_backtester.py — RealDataBacktester 단위+통합 테스트.

검증 범위:
    DEFAULT_COLUMN_MAP 필수 키
    RealDataBacktester._load(): N=10 minimal CSV, 파싱 오류 행 드롭
    run_all(): BacktestResult 반환 형식
    to_dataframe(): 컬럼 구조
    통합: 실데이터 N=336 (실데이터 파일 존재 시만 실행)
"""
from __future__ import annotations

import pathlib

import pandas as pd
import pytest

from libs.evaluation import (
    DEFAULT_COLUMN_MAP,
    BacktestResult,
    RealDataBacktester,
)
from libs.optimization import MinIdleObjective, MinWaitObjective

REAL_DATA_PATH = "data/raw/scheduling/data/2024-06_SchData.csv"

_VALID_ROW: dict = {
    "선박명": "V001",
    "기준예선": "T1",
    "실제 스케줄 시작 시각": "2024-06-08T07:00:00.000Z",
    "실제 스케줄 종료 시각": "2024-06-08T08:00:00.000Z",
    "최초 스케줄 시각": "2024-06-08T06:30:00.000Z",
    "최종 스케줄 시각": "2024-06-08T07:30:00.000Z",
    "작업중 이동 시간(분)": 30,
    "작업까지 이동 거리(km)": 5.0,
    "작업중 이동 거리(km)": 3.0,
    "톤수": 20000,
    "작업 시작지": "B1",
    "작업 종료지": "B2",
}


def _make_csv(tmp_path: pathlib.Path, rows: list[dict]) -> str:
    path = str(tmp_path / "data.csv")
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")
    return path


# ── DEFAULT_COLUMN_MAP ─────────────────────────────────────────────

class TestDefaultColumnMap:
    def test_required_keys_present(self) -> None:
        required = {
            "vessel_id", "tug_id", "scheduled_start",
            "earliest_start", "latest_start",
            "service_duration_min", "tonnage",
        }
        assert required.issubset(DEFAULT_COLUMN_MAP.keys())

    def test_values_are_korean_strings(self) -> None:
        for v in DEFAULT_COLUMN_MAP.values():
            assert isinstance(v, str) and len(v) > 0


# ── RealDataBacktester ─────────────────────────────────────────────

class TestRealDataBacktester:
    def test_load_n10(self, tmp_path: pathlib.Path) -> None:
        rows = [{**_VALID_ROW, "선박명": f"V{i:03d}"} for i in range(10)]
        csv_path = _make_csv(tmp_path, rows)
        bt = RealDataBacktester(
            csv_path=csv_path, tug_fleet=[], berth_locations={}
        )
        assert bt.n_samples == 10

    def test_run_all_result_count(self, tmp_path: pathlib.Path) -> None:
        rows = [{**_VALID_ROW, "선박명": f"V{i:03d}"} for i in range(5)]
        csv_path = _make_csv(tmp_path, rows)
        bt = RealDataBacktester(
            csv_path=csv_path, tug_fleet=[], berth_locations={}
        )
        results = bt.run_all([MinWaitObjective(), MinIdleObjective()])
        assert len(results) == 2
        for r in results:
            assert isinstance(r, BacktestResult)
            assert r.n_samples == 5

    def test_to_dataframe_columns(self, tmp_path: pathlib.Path) -> None:
        rows = [{**_VALID_ROW}]
        csv_path = _make_csv(tmp_path, rows)
        bt = RealDataBacktester(
            csv_path=csv_path, tug_fleet=[], berth_locations={}
        )
        df = bt.to_dataframe(bt.run_all([MinWaitObjective()]))
        expected = {
            "objective", "dist_nm", "idle_h", "wait_h",
            "fuel_mt", "objective_value", "solve_time_sec", "n_samples",
        }
        assert expected.issubset(set(df.columns))

    def test_kpi_non_negative(self, tmp_path: pathlib.Path) -> None:
        rows = [{**_VALID_ROW, "선박명": f"V{i:03d}"} for i in range(5)]
        csv_path = _make_csv(tmp_path, rows)
        bt = RealDataBacktester(
            csv_path=csv_path, tug_fleet=[], berth_locations={}
        )
        kpi = bt.run_all([MinIdleObjective()])[0].kpi
        assert kpi.idle_h >= 0.0
        assert kpi.wait_h >= 0.0
        assert kpi.dist_nm >= 0.0

    def test_invalid_rows_skipped(self, tmp_path: pathlib.Path) -> None:
        invalid_row = {
            **_VALID_ROW,
            "선박명": "V_BAD",
            "실제 스케줄 시작 시각": "not-a-date",
        }
        csv_path = _make_csv(tmp_path, [_VALID_ROW, invalid_row])
        bt = RealDataBacktester(
            csv_path=csv_path, tug_fleet=[], berth_locations={}
        )
        assert bt.n_samples == 1

    def test_latest_earliest_fallback(self, tmp_path: pathlib.Path) -> None:
        # latest == earliest → fallback: latest = earliest + service_duration
        row = {
            **_VALID_ROW,
            "최초 스케줄 시각": "2024-06-08T07:00:00.000Z",
            "최종 스케줄 시각": "2024-06-08T07:00:00.000Z",  # same
            "작업중 이동 시간(분)": 30,
        }
        csv_path = _make_csv(tmp_path, [row])
        bt = RealDataBacktester(
            csv_path=csv_path, tug_fleet=[], berth_locations={}
        )
        assert bt.n_samples == 1  # 드롭되지 않음


# ── 통합 테스트 (실데이터) ─────────────────────────────────────────

@pytest.mark.skipif(
    not pathlib.Path(REAL_DATA_PATH).exists(),
    reason="실데이터 파일 없음 (data/raw/scheduling/data/2024-06_SchData.csv)",
)
class TestRealDataIntegration:
    def test_n_samples_336(self) -> None:
        bt = RealDataBacktester(
            csv_path=REAL_DATA_PATH, tug_fleet=[], berth_locations={}
        )
        assert bt.n_samples == 336

    def test_all_four_strategies(self) -> None:
        from libs.optimization import MinAllObjective, MinCompositeObjective

        bt = RealDataBacktester(
            csv_path=REAL_DATA_PATH, tug_fleet=[], berth_locations={}
        )
        strategies = [
            MinWaitObjective(),
            MinIdleObjective(),
            MinCompositeObjective(),
            MinAllObjective(),
        ]
        results = bt.run_all(strategies)
        assert len(results) == 4
        for r in results:
            assert r.kpi.idle_h >= 0.0
            assert r.kpi.wait_h >= 0.0
            assert r.n_samples == 336
