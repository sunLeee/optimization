"""
TravelTimeMatrix — 선석/정계지 간 이동시간 행렬.

haversine 거리 + AIS 실측 속도 기반으로 115개 노드
(111 선석 + 4 정계지) 간 이동시간(분)을 사전 계산한다.

AIS 속도 파생:
    AISLog/ 디렉토리의 _tug_ 파일에서 SOG > 0.5 kn 행만 사용하여
    각 파일의 중앙값을 구하고, 전체 중앙값을 fleet 속도로 사용한다.
    AIS 데이터 없으면 default_speed_kn(기본 8.0 kn) 사용.

미지 코드:
    알 수 없는 선석/정계지 코드는 경고 로그 후 fallback_min 반환.
    fallback_min 기본값 = 31.0분 (SchData 작업까지 이동 시간 중앙값).
"""
from __future__ import annotations

import logging
import os
import pathlib

import numpy as np

from libs.utils.geo import haversine_nm

logger = logging.getLogger(__name__)

DEFAULT_SPEED_KN: float = 8.0
DEFAULT_FALLBACK_MIN: float = 31.0
_MIN_SPEED_KN: float = 1.0
_MAX_SPEED_KN: float = 20.0
_SOG_UNDERWAY_THRESHOLD: float = 0.5  # kn


class TravelTimeMatrix:
    """선석/정계지 간 이동시간 사전 계산 행렬.

    Args:
        berth_locations: {선석코드: (위도, 경도)} — 111개
        anchorage_locations: {정계지명: (위도, 경도)} — 4개
        default_speed_kn: AIS 데이터 없을 때 사용할 기본 속도 (kn).
        ais_log_dir: AISLog 디렉토리 경로. None이면 기본 속도만 사용.
        fallback_min: 미지 코드용 폴백 이동시간 (분).

    Example:
        matrix = TravelTimeMatrix(berth_locs, anchorage_locs,
                                  ais_log_dir="data/raw/scheduling/data/AISLog")
        t = matrix.get_time_min("연안부두정계지", "KICT")  # 분 단위 float
    """

    def __init__(
        self,
        berth_locations: dict[str, tuple[float, float]],
        anchorage_locations: dict[str, tuple[float, float]],
        default_speed_kn: float = DEFAULT_SPEED_KN,
        ais_log_dir: str | None = None,
        fallback_min: float = DEFAULT_FALLBACK_MIN,
        real_lookup: dict[tuple[str, str], float] | None = None,
        route_factor: float = 1.8,
    ) -> None:
        """
        Args:
            real_lookup: SchData 실측 이동시간 {(출발지, 도착지): 분}.
                제공 시 haversine 추정보다 우선 사용 (유효범위 0.3~3.0× 이내만).
            route_factor: 항만 항로 보정 계수. haversine 직선거리 × route_factor
                = 실제 항만 항로 이동시간 추정. 기본값 1.8.
                (실측 데이터 분석: 신뢰 경로 중앙 비율 ≈ 1.6~2.0×)
        """
        self._fallback_min = fallback_min
        self._route_factor = route_factor
        self._real_lookup: dict[tuple[str, str], float] = real_lookup or {}

        # 속도 파생
        if ais_log_dir is not None:
            self._speed_kn = self.derive_speed_from_ais(ais_log_dir, default_speed_kn)
        else:
            self._speed_kn = default_speed_kn

        logger.info(
            "TravelTimeMatrix 초기화: speed=%.2f kn, route_factor=%.1f, "
            "real_lookup=%d쌍, fallback=%.1f min",
            self._speed_kn, route_factor, len(self._real_lookup), fallback_min,
        )

        # 전체 노드 집합 (berths + anchorages)
        all_nodes: dict[str, tuple[float, float]] = {}
        all_nodes.update(berth_locations)
        all_nodes.update(anchorage_locations)
        self._nodes = all_nodes

        # 이동시간 캐시 (분) — 실측 우선, 없으면 haversine × route_factor
        self._cache: dict[tuple[str, str], float] = {}
        node_list = list(all_nodes.items())
        for _i, (code_a, pos_a) in enumerate(node_list):
            for code_b, pos_b in node_list:
                if code_a == code_b:
                    self._cache[(code_a, code_b)] = 0.0
                    continue
                dist_nm = haversine_nm(pos_a, pos_b)
                haversine_min = dist_nm / self._speed_kn * 60.0
                real_val = self._real_lookup.get((code_a, code_b))
                if real_val is not None:
                    # real_lookup 값은 build_real_travel_lookup()에서 이미 검증됨 → 직접 사용
                    self._cache[(code_a, code_b)] = real_val
                else:
                    # 실측값 없으면 haversine × route_factor
                    self._cache[(code_a, code_b)] = haversine_min * route_factor

        n_real_used = sum(
            1 for k, v in self._cache.items()
            if k in self._real_lookup and v == self._real_lookup[k]
        )
        logger.info(
            "TravelTimeMatrix 캐시 완료: %d 노드, %d 쌍 (실측 적용: %d쌍)",
            len(all_nodes), len(self._cache), n_real_used,
        )

    def get_time_min(self, from_code: str, to_code: str) -> float:
        """두 노드 간 이동시간 (분) 반환.

        Args:
            from_code: 출발지 선석코드 또는 정계지명.
            to_code: 도착지 선석코드 또는 정계지명.

        Returns:
            이동시간 (분, >= 0.0). 미지 코드이면 fallback_min 반환.
        """
        if from_code == to_code:
            return 0.0

        key = (from_code, to_code)
        if key in self._cache:
            return self._cache[key]

        # 미지 코드 처리
        unknown = [c for c in (from_code, to_code) if c not in self._nodes]
        logger.warning(
            "미지 코드 %s → fallback %.1f분 사용", unknown, self._fallback_min
        )
        return self._fallback_min

    @property
    def speed_kn(self) -> float:
        """파생된 fleet 평균 속도 (kn)."""
        return self._speed_kn

    @property
    def known_codes(self) -> set[str]:
        """알려진 모든 노드 코드 집합."""
        return set(self._nodes.keys())

    def derive_speed_from_ais(
        self,
        ais_log_dir: str,
        default_speed_kn: float = DEFAULT_SPEED_KN,
    ) -> float:
        """AIS 로그에서 fleet 평균 속도를 파생한다.

        _tug_ 패턴의 AIS 파일에서 SOG > 0.5 kn 행만 사용하여
        각 파일의 중앙값을 구하고 전체 중앙값을 반환한다.

        Args:
            ais_log_dir: AISLog 디렉토리 경로.
            default_speed_kn: AIS 데이터 없거나 오류 시 반환할 기본값.

        Returns:
            Fleet 평균 속도 (kn), 범위 [1.0, 20.0] 내로 클립.
        """
        import pandas as pd

        ais_path = pathlib.Path(ais_log_dir)
        if not ais_path.is_dir():
            logger.warning("AIS 디렉토리 없음: %s → 기본 속도 %.1f kn 사용",
                           ais_log_dir, default_speed_kn)
            return default_speed_kn

        tug_files = [
            f for f in os.listdir(ais_path)
            if "_tug_" in f and f.endswith(".csv")
        ]
        if not tug_files:
            logger.warning("AIS _tug_ 파일 없음 → 기본 속도 %.1f kn 사용", default_speed_kn)
            return default_speed_kn

        file_medians: list[float] = []
        for fname in tug_files:
            try:
                df = pd.read_csv(ais_path / fname, usecols=["Sog(속도)"])
                underway = df["Sog(속도)"][df["Sog(속도)"] > _SOG_UNDERWAY_THRESHOLD]
                if len(underway) > 0:
                    file_medians.append(float(underway.median()))
            except Exception as exc:
                logger.debug("AIS 파일 스킵 (%s): %s", fname, exc)

        if not file_medians:
            logger.warning("유효한 AIS SOG 없음 → 기본 속도 %.1f kn 사용", default_speed_kn)
            return default_speed_kn

        fleet_speed = float(np.median(file_medians))
        fleet_speed = float(np.clip(fleet_speed, _MIN_SPEED_KN, _MAX_SPEED_KN))
        logger.info(
            "AIS 속도 파생 완료: %d 파일 → fleet 중앙값 %.2f kn",
            len(file_medians), fleet_speed,
        )
        return fleet_speed
