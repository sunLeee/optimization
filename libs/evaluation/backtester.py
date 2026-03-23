"""
RealDataBacktester — 실제 항구 데이터 기반 목적함수 백테스팅.

2024-06 부산항 실측 데이터(N=336)를 로드하여 4종 ObjectiveStrategy를
동일 조건으로 실행하고 KPI를 비교한다.

참조:
  - ADR-005: RealDataBacktester 위치 + CSV column_map 설계
  - ADR-006: 4종 목적함수 수식 정의
  - data/raw/scheduling/data/2024-06_SchData.csv (N=336)
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import pandas as pd

from libs.optimization.objective import KPIResult, ObjectiveStrategy
from libs.utils.time_window import SchedulingToRoutingSpec, TimeWindowSpec

logger = logging.getLogger(__name__)

# 확정 컬럼 매핑 (Step 3 CSV 확인 기반, ADR-005)
DEFAULT_COLUMN_MAP: dict[str, str] = {
    "vessel_id": "선박명",
    "tug_id": "기준예선",
    "scheduled_start": "실제 스케줄 시작 시각",  # ISO8601 UTC
    "scheduled_end": "실제 스케줄 종료 시각",     # ISO8601 UTC
    "earliest_start": "최초 스케줄 시각",
    "latest_start": "최종 스케줄 시각",
    "service_duration_min": "작업중 이동 시간(분)",
    "dist_to_work_km": "작업까지 이동 거리(km)",
    "dist_work_km": "작업중 이동 거리(km)",
    "tonnage": "톤수",
    "from_loc": "작업 시작지",
    "to_loc": "작업 종료지",
}


@dataclass
class BacktestResult:
    """단일 ObjectiveStrategy 백테스팅 결과."""

    objective_name: str
    kpi: KPIResult
    solve_time_sec: float
    n_samples: int


def _parse_iso_to_minutes_from_midnight(iso_str: str) -> float:
    """ISO8601 UTC 문자열 → 자정 기준 분 수.

    예: "2024-06-08T07:32:18.000Z" → 452.3 (분)

    Args:
        iso_str: ISO8601 UTC 형식 문자열

    Returns:
        자정(00:00)으로부터의 경과 시간 (minutes)
    """
    ts = pd.Timestamp(iso_str, tz="UTC")
    midnight = ts.normalize()  # 자정
    delta_min = (ts - midnight).total_seconds() / 60.0
    return delta_min


class RealDataBacktester:
    """실데이터 기반 ObjectiveStrategy 비교 백테스터.

    2024-06_SchData.csv를 로드하여 SchedulingToRoutingSpec + TimeWindowSpec을
    생성한 뒤, 각 전략의 compute()를 호출하고 KPI를 비교한다.

    사용 예:
        backtester = RealDataBacktester(
            csv_path="data/raw/scheduling/data/2024-06_SchData.csv",
            tug_fleet=["I", "M", "F1", ...],
            berth_locations={},
        )
        results = backtester.run_all([MinIdleObjective(), MinWaitObjective()])
        df = backtester.to_dataframe(results)
    """

    def __init__(
        self,
        csv_path: str,
        tug_fleet: list[str],
        berth_locations: dict[str, tuple[float, float]],
        column_map: dict[str, str] | None = None,
    ) -> None:
        """
        Args:
            csv_path: 실데이터 CSV 경로
            tug_fleet: 예인선 ID 목록 (필터링에 사용)
            berth_locations: {berth_id: (lat, lon)} (현재 미사용, 향후 확장용)
            column_map: CSV 컬럼명 → 표준 컬럼명 매핑.
                None이면 DEFAULT_COLUMN_MAP 사용.
        """
        self.csv_path = csv_path
        self.tug_fleet = tug_fleet
        self.berth_locations = berth_locations
        self.column_map = column_map or DEFAULT_COLUMN_MAP

        self._assignments: list[SchedulingToRoutingSpec] = []
        self._windows: list[TimeWindowSpec] = []
        self._load()

    def _load(self) -> None:
        """CSV 로드 → SchedulingToRoutingSpec + TimeWindowSpec 변환."""
        df = pd.read_csv(self.csv_path)
        n_raw = len(df)
        logger.info("CSV 로드: %d 행", n_raw)

        col = self.column_map
        dropped = 0

        for idx, row in df.iterrows():
            try:
                vessel_id: str = str(row[col["vessel_id"]])
                tug_id: str = str(row[col["tug_id"]]).strip()
                service_duration_min: float = float(
                    row[col["service_duration_min"]]
                )
                tonnage: int = int(row[col["tonnage"]])

                # 시간 파싱 (ISO8601 UTC → 자정 기준 분)
                scheduled_start_min = _parse_iso_to_minutes_from_midnight(
                    row[col["scheduled_start"]]
                )
                earliest_min = _parse_iso_to_minutes_from_midnight(
                    row[col["earliest_start"]]
                )
                latest_min = _parse_iso_to_minutes_from_midnight(
                    row[col["latest_start"]]
                )

                # latest < earliest 방지 (슬랙 = service_duration)
                if latest_min <= earliest_min:
                    latest_min = earliest_min + service_duration_min

                # priority: 톤수 기반 (1~5 스케일)
                priority = max(1, min(5, int(tonnage // 10_000) + 1))

                # from_loc 컬럼명 (column_map에 없으면 기본값)
                from_loc_col = col.get("from_loc", "작업 시작지")
                berth_id = str(row.get(from_loc_col, ""))

                # TimeWindowSpec 생성
                window = TimeWindowSpec(
                    vessel_id=vessel_id,
                    berth_id=berth_id,
                    earliest_start=earliest_min,
                    latest_start=latest_min,
                    service_duration=service_duration_min,
                    priority=priority,
                )

                # SchedulingToRoutingSpec 생성
                # 좌표 미제공 → (0,0) fallback (향후 berth_locations 연동)
                spec = SchedulingToRoutingSpec(
                    vessel_id=vessel_id,
                    tug_id=tug_id,
                    pickup_location=(0.0, 0.0),
                    dropoff_location=(0.0, 0.0),
                    time_window=window,
                    scheduled_start=scheduled_start_min,
                    required_tugs=1,
                    priority=priority,
                )

                self._assignments.append(spec)
                self._windows.append(window)

            except (KeyError, ValueError, TypeError) as e:
                dropped += 1
                logger.warning("행 %d 스킵 — %s", idx, e)

        n_loaded = len(self._assignments)
        if dropped > 0:
            logger.warning(
                "필터링: %d행 드롭 (사유: 파싱 오류). 최종 %d행 사용",
                dropped,
                n_loaded,
            )
        logger.info(
            "로드 완료: %d/%d 행 사용 (%.1f%%)",
            n_loaded,
            n_raw,
            100.0 * n_loaded / n_raw if n_raw > 0 else 0,
        )

    @property
    def n_samples(self) -> int:
        """로드된 유효 샘플 수."""
        return len(self._assignments)

    def run_all(
        self, strategies: list[ObjectiveStrategy]
    ) -> list[BacktestResult]:
        """모든 전략에 대해 백테스팅 실행.

        Args:
            strategies: ObjectiveStrategy 구현체 목록.
                MinAllObjective 사용 시 주의: 백테스터 컨텍스트에서 dist_nm=0.0
                (RouteResult 미제공). 실제 거리 반영 필요 시 run_all 호출 전에
                inject_dist_nm(dist_nm)을 호출할 것.

        Returns:
            전략별 BacktestResult 목록
        """
        from libs.optimization.objective import MinAllObjective

        for strategy in strategies:
            if (
                isinstance(strategy, MinAllObjective)
                and strategy._dist_nm_cache == 0.0
            ):
                logger.warning(
                    "%s: dist_nm=0.0 (inject_dist_nm 미호출). "
                    "objective_value가 OBJ-C와 실질적으로 동치가 됩니다.",
                    strategy.name(),
                )

        results: list[BacktestResult] = []
        for strategy in strategies:
            t0 = time.time()
            kpi = strategy.compute(self._assignments, self._windows)
            elapsed = time.time() - t0
            logger.info(
                "%s | idle=%.2fh wait=%.2fh fuel=%.2fMT obj=%.4f (%.3fs)",
                strategy.name(),
                kpi.idle_h,
                kpi.wait_h,
                kpi.fuel_mt,
                kpi.objective_value,
                elapsed,
            )
            results.append(
                BacktestResult(
                    objective_name=strategy.name(),
                    kpi=kpi,
                    solve_time_sec=elapsed,
                    n_samples=self.n_samples,
                )
            )
        return results

    def to_dataframe(self, results: list[BacktestResult]) -> pd.DataFrame:
        """BacktestResult 목록을 DataFrame으로 변환.

        컬럼: objective, dist_nm, idle_h, wait_h, fuel_mt,
               objective_value, solve_time_sec, n_samples

        Args:
            results: run_all() 반환값

        Returns:
            pd.DataFrame
        """
        rows = []
        for r in results:
            rows.append(
                {
                    "objective": r.objective_name,
                    "dist_nm": r.kpi.dist_nm,
                    "idle_h": r.kpi.idle_h,
                    "wait_h": r.kpi.wait_h,
                    "fuel_mt": r.kpi.fuel_mt,
                    "objective_value": r.kpi.objective_value,
                    "solve_time_sec": r.solve_time_sec,
                    "n_samples": r.n_samples,
                }
            )
        return pd.DataFrame(rows)
