"""
항구 예선 스케줄링 실데이터 로더.

2024-06 인천항 데이터셋의 모든 CSV 파일을 파싱하여
타입이 지정된 파이썬 객체로 반환한다.

데이터 경로: data/raw/scheduling/data/
    - 2024-06_FristAllSchData.csv  (N=967, 최초 배정 요청)
    - 2024-06_SchData.csv          (N=336, 실제 수행 기록)
    - 선석 코드.csv                 (N=111, 선석 GPS 좌표)
    - 정계지 위치.csv               (N=4,   예선 대기지 GPS 좌표)
    - 예선 코드.csv                 (N=10,  예선 코드-이름 매핑)
"""
from __future__ import annotations

import logging
import pathlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import ClassVar

import pandas as pd

logger = logging.getLogger(__name__)

# AIS 로그 분석으로 추출한 보조 선석 GPS (선석 코드.csv 미등재 코드)
# n = AIS 샘플 수. PAL(n=205), NPPS(n=68) 등 고신뢰
AIS_SUPPLEMENTARY_LOCATIONS: dict[str, tuple[float, float]] = {
    "PAL":    (37.463117, 126.596133),  # 팔미 파일럿 스테이션 (n=205)
    "NPPS":   (37.336349, 126.619842),  # North Port Pilot Station (n=68)
    "SOD1":   (37.443767, 126.586033),  # 송도 1 (n=13)
    "BUKJ2":  (37.337511, 126.599780),  # 북쪽 구역 2 (n=4)
    "JANG":   (37.303900, 126.433582),  # 장봉도 근해 (n=3)
    "SAMPYO": (37.437083, 126.601473),  # 삼표 부두 (n=3)
    "W4":     (37.439650, 126.599817),  # 서쪽 4번 부두 (n=3)
    "LE":     (37.467902, 126.609423),  # LE 정박지 (n=2)
    "JAK":    (37.560717, 126.603700),  # 작업 구역 (n=1)
    "E4":     (37.454783, 126.590467),  # 동쪽 4번 부두 (n=1)
    # E2, E3, SICT1: AIS 샘플 없음 → 근접 선석 좌표 근사
    "E2":     (37.453500, 126.591000),  # E4 근사
    "E3":     (37.454000, 126.590700),  # E4 근사
    "SICT1":  (37.341517, 126.624203),  # HJIT1 근사 (송도 컨테이너)
    # 코드 별칭: 스케줄 데이터는 공백 있음("SKI 1"), 선석코드.csv는 공백 없음("SKI1")
    "SKI 1":  (37.505922, 126.602388),
    "SKI 2":  (37.508903, 126.601765),
    "SKI 3":  (37.502412, 126.602477),
    "SKI 4":  (37.511764, 126.601157),
    # 기타 자주 사용되는 미등재 코드
    "DONG":   (37.507000, 126.601500),  # 동측 부두 (SKI 근방 근사)
    "GSD":    (37.478154, 126.594861),  # 가스도 (GSD = libs/utils 기존값)
    "N-HOB":  (37.498992, 126.629899),  # 북항 외측 정박지
}

# 예선별 볼라드 풀 (tonnes) — 인천항 예선 추정값 (IMO Pull Test 기준)
# 볼라드 풀 = 예선이 발휘할 수 있는 최대 견인력 (정지 상태)
TUG_BOLLARD_PULL: dict[str, float] = {
    "뉴월미호": 42.0,
    "대한호": 50.0,
    "희양호": 36.0,
    "한창1호": 68.0,
    "쥬피터1호": 58.0,
    "뉴마스호": 38.0,
    "대창호": 42.0,
    "동보1호": 48.0,
    "뉴엔젤호": 38.0,
    "뉴약진호": 42.0,
    "대명호": 46.0,
    "대성호": 38.0,
}


def compute_bp_required(tonnage_mt: float) -> float:
    """톤수 기반 최소 요구 볼라드 풀 (tonnes) 계산.

    인천항 운영 기준 및 IMO 권고 수준 기반 추정값.
    최대 가용 fleet BP = 546t (12척 합계) 고려.

    Args:
        tonnage_mt: 선박 총톤수 (metric tons)

    Returns:
        최소 필요 볼라드 풀 (tonnes)
    """
    if tonnage_mt < 5_000:
        return 30.0
    if tonnage_mt < 30_000:
        return 80.0
    if tonnage_mt < 60_000:
        return 160.0
    if tonnage_mt < 100_000:
        return 250.0
    return 350.0  # 100K+ MT (VLCC 포함): 인천항 최대 가용 BP 범위 내


@dataclass
class ServiceRequest:
    """FristAllSchData.csv 한 행 (최초 배정 요청).

    Attributes:
        row_id: CSV 행 인덱스 (0-based)
        tug_codes: 배정예선 콤마 분리 목록 (예: ["미", "W"], ["I"])
        is_single_tug: len(tug_codes) == 1
        vessel_name: 선박명
        start_berth_code: 작업 시작지 (선석코드)
        end_berth_code: 작업 종료지 (선석코드)
        scheduled_start: 스케줄 시작 시각 (UTC datetime)
        pilot_code: 도선사 코드
        tonnage_mt: 톤수 (metric tons)
    """

    row_id: int
    tug_codes: list[str]
    is_single_tug: bool
    vessel_name: str
    start_berth_code: str
    end_berth_code: str
    scheduled_start: datetime
    pilot_code: str
    tonnage_mt: float
    required_tugs: int = 1
    bp_required: float = 30.0   # 최소 요구 볼라드 풀 (tonnes)


@dataclass
class ExecutedService:
    """SchData.csv 한 행 (실제 수행 기록).

    Attributes:
        row_id: CSV 행 인덱스 (0-based)
        base_tug_code: 기준예선 코드
        assigned_tug_codes: 배정예선 콤마 분리 목록
        is_single_tug: len(assigned_tug_codes) == 1
        vessel_name: 선박명
        from_anchorage: 출발 정계지 (빈 문자열이면 미기록)
        start_berth_code: 작업 시작지
        end_berth_code: 작업 종료지
        to_anchorage: 귀환 정계지 (빈 문자열이면 미기록)
        actual_start: 실제 스케줄 시작 시각 (UTC)
        actual_end: 실제 스케줄 종료 시각 (UTC)
        travel_to_site_km: 작업까지 이동 거리 (km)
        travel_to_site_min: 작업까지 이동 시간 (분)
        service_dist_km: 작업중 이동 거리 (km)
        service_duration_min: 작업중 이동 시간 (분)
        pilot_code: 도선사 코드
        tonnage_mt: 톤수
        initial_schedule: 최초 스케줄 시각 (UTC)
        initial_tug_code: 최초 예선 코드
        ais_file_target: AIS 파일명 target (없으면 빈 문자열)
        ais_file_tug: AIS 파일명 tug (없으면 빈 문자열)
    """

    row_id: int
    base_tug_code: str
    assigned_tug_codes: list[str]
    is_single_tug: bool
    vessel_name: str
    from_anchorage: str
    start_berth_code: str
    end_berth_code: str
    to_anchorage: str
    actual_start: datetime
    actual_end: datetime
    travel_to_site_km: float
    travel_to_site_min: float
    service_dist_km: float
    service_duration_min: float
    pilot_code: str
    tonnage_mt: float
    initial_schedule: datetime
    initial_tug_code: str
    ais_file_target: str
    ais_file_tug: str


class HarborDataLoader:
    """항구 실데이터 통합 로더.

    인천항 2024-06 데이터셋의 모든 CSV 파일을 파싱한다.

    Args:
        data_dir: CSV 파일들이 위치한 디렉토리 경로.
            None이면 "data/raw/scheduling/data" 사용.

    Example:
        loader = HarborDataLoader()
        berths = loader.load_berth_locations()   # 111개
        requests = loader.load_requests()         # 967개
        executed = loader.load_executed()         # 336개
    """

    DEFAULT_DATA_DIR: ClassVar[str] = "data/raw/scheduling/data"

    def __init__(self, data_dir: str | None = None) -> None:
        self._dir = pathlib.Path(data_dir or self.DEFAULT_DATA_DIR)

    # ── 참조 데이터 로더 ──────────────────────────────────────

    def load_berth_locations(self) -> dict[str, tuple[float, float]]:
        """선석 코드.csv → {선석코드: (위도, 경도)}.

        Returns:
            111개 선석의 {코드: (위도float, 경도float)} 딕셔너리.

        Raises:
            FileNotFoundError: 파일이 없을 경우.
        """
        path = self._dir / "선석 코드.csv"
        df = pd.read_csv(path)
        result: dict[str, tuple[float, float]] = {}
        for _, row in df.iterrows():
            code = str(row["선석코드"]).strip()
            result[code] = (float(row["위도"]), float(row["경도"]))
        logger.info("선석 로드: %d개", len(result))
        return result

    def load_anchorage_locations(self) -> dict[str, tuple[float, float]]:
        """정계지 위치.csv → {정계지명: (위도, 경도)}.

        Returns:
            4개 정계지의 {이름: (위도float, 경도float)} 딕셔너리.
        """
        path = self._dir / "정계지 위치.csv"
        df = pd.read_csv(path)
        result: dict[str, tuple[float, float]] = {}
        for _, row in df.iterrows():
            name = str(row["정계지"]).strip()
            result[name] = (float(row["위도"]), float(row["경도"]))
        logger.info("정계지 로드: %d개", len(result))
        return result

    def load_all_locations(self) -> dict[str, tuple[float, float]]:
        """선석 + 정계지 + AIS 보조 좌표를 통합한 위치 딕셔너리 반환.

        Returns:
            {코드/이름: (위도, 경도)} — 선석 111개 + 정계지 4개 + AIS 보조 13개.
        """
        result: dict[str, tuple[float, float]] = {}
        result.update(AIS_SUPPLEMENTARY_LOCATIONS)   # 낮은 신뢰도 먼저 (덮어쓰기 대비)
        result.update(self.load_anchorage_locations())
        result.update(self.load_berth_locations())    # 공식 데이터 최우선
        return result

    def build_real_travel_lookup(
        self,
        min_count: int = 2,
        max_ratio: float = 3.0,
    ) -> dict[tuple[str, str], float]:
        """SchData 실측 이동시간에서 신뢰할 수 있는 경로별 중앙값 반환.

        유효성 검증: haversine 추정값의 0.3~max_ratio배 이내만 포함
        (대기시간이 섞인 이상값 자동 제외).

        Args:
            min_count: 최소 관측 건수. 기본 2.
            max_ratio: haversine 대비 최대 허용 비율. 기본 3.0.

        Returns:
            {(출발지, 도착지): 중앙값_분} 딕셔너리.
        """
        from libs.utils.geo import haversine_nm

        all_locs = self.load_all_locations()
        speed_kn = 6.0  # AIS 실측 fleet 속도

        path = self._dir / "2024-06_SchData.csv"
        df = pd.read_csv(path)
        df_from = df[df["From"].notna()].copy()

        lookup: dict[tuple[str, str], float] = {}
        dropped = 0

        def _is_valid(frm: str, to: str, median_val: float) -> bool:
            p1, p2 = all_locs.get(frm), all_locs.get(to)
            if p1 and p2:
                dist_nm = haversine_nm(p1, p2)
                h_min = dist_nm / speed_kn * 60.0
                if h_min > 0:
                    ratio = median_val / h_min
                    return 0.3 <= ratio <= max_ratio
            return True  # GPS 없으면 검증 불가 → 포함

        # 정계지 → 작업시작지
        for (frm, start), grp in df_from.groupby(["From", "작업 시작지"]):
            if len(grp) < min_count:
                continue
            med = float(grp["작업까지 이동 시간(분)"].median())
            if _is_valid(frm, start, med):
                lookup[(frm, start)] = med
            else:
                dropped += 1

        # 작업시작지 → 작업종료지
        for (start, end), grp in df.groupby(["작업 시작지", "작업 종료지"]):
            if len(grp) < min_count:
                continue
            med = float(grp["작업중 이동 시간(분)"].median())
            if _is_valid(start, end, med):
                lookup[(start, end)] = med
            else:
                dropped += 1

        logger.info(
            "실측 이동시간 lookup: %d쌍 구축 (이상값 제외: %d쌍)", len(lookup), dropped
        )
        return lookup

    def load_tug_mapping(self) -> dict[str, str]:
        """예선 코드.csv → {예선코드: 예선명}.

        Returns:
            10개 예선의 {코드: 이름} 딕셔너리.
        """
        path = self._dir / "예선 코드.csv"
        df = pd.read_csv(path)
        result: dict[str, str] = {}
        for _, row in df.iterrows():
            code = str(row["예선코드"]).strip()
            name = str(row["예선명"]).strip()
            result[code] = name
        logger.info("예선 매핑 로드: %d개", len(result))
        return result

    # ── 스케줄 데이터 로더 ────────────────────────────────────

    @staticmethod
    def compute_required_tugs(tonnage_mt: float) -> int:
        """톤수 기반 필요 예선 수 추정.

        실측 데이터 (SchData 2024-06) 기반 구간 규칙:
            < 5,000 MT  → 1척
            5,000~15,000 → 2척
            15,000~30,000 → 2척
            30,000~60,000 → 3척
            > 60,000 MT → 4척

        Args:
            tonnage_mt: 선박 총톤수 (metric tons)

        Returns:
            필요 예선 수 (1~4)
        """
        if tonnage_mt < 5_000:
            return 1
        if tonnage_mt < 30_000:
            return 2
        if tonnage_mt < 60_000:
            return 3
        return 4

    def load_requests(self) -> list[ServiceRequest]:
        """FristAllSchData.csv 전체를 ServiceRequest 목록으로 반환.

        Returns:
            967개 ServiceRequest 목록. is_single_tug 필드 자동 계산.

        Notes:
            - 배정예선이 "미,W" 형태이면 tug_codes=["미","W"], is_single_tug=False
            - 파싱 실패 행은 경고 로그 후 스킵
        """
        path = self._dir / "2024-06_FristAllSchData.csv"
        df = pd.read_csv(path)
        result: list[ServiceRequest] = []
        dropped = 0

        for idx, row in df.iterrows():
            try:
                raw_tug = str(row["배정예선"]).strip()
                tug_codes = [t.strip() for t in raw_tug.split(",") if t.strip()]

                result.append(
                    ServiceRequest(
                        row_id=int(idx),
                        tug_codes=tug_codes,
                        is_single_tug=len(tug_codes) == 1,
                        vessel_name=str(row["선박명"]).strip(),
                        start_berth_code=str(row["작업 시작지"]).strip(),
                        end_berth_code=str(row["작업 종료지"]).strip(),
                        scheduled_start=_parse_iso_utc(str(row["스케줄 시작 시각"])),
                        pilot_code=str(row["도선사"]).strip(),
                        tonnage_mt=float(row["톤수"]),
                        required_tugs=self.compute_required_tugs(float(row["톤수"])),
                        bp_required=compute_bp_required(float(row["톤수"])),
                    )
                )
            except Exception as exc:
                dropped += 1
                logger.warning("FristAllSchData 행 %d 스킵: %s", idx, exc)

        if dropped:
            logger.warning("%d행 드롭됨 (파싱 오류)", dropped)
        logger.info(
            "요청 로드: %d건 (단일예선=%d건)",
            len(result),
            sum(1 for r in result if r.is_single_tug),
        )
        return result

    def load_executed(self) -> list[ExecutedService]:
        """SchData.csv 전체를 ExecutedService 목록으로 반환.

        Returns:
            336개 ExecutedService 목록.

        Notes:
            - From/To 컬럼 NaN → 빈 문자열
            - AIS 파일명 NaN → 빈 문자열
        """
        path = self._dir / "2024-06_SchData.csv"
        df = pd.read_csv(path)
        result: list[ExecutedService] = []
        dropped = 0

        for idx, row in df.iterrows():
            try:
                raw_assigned = str(row["배정예선"]).strip()
                assigned_codes = [t.strip() for t in raw_assigned.split(",") if t.strip()]

                result.append(
                    ExecutedService(
                        row_id=int(idx),
                        base_tug_code=str(row["기준예선"]).strip(),
                        assigned_tug_codes=assigned_codes,
                        is_single_tug=len(assigned_codes) == 1,
                        vessel_name=str(row["선박명"]).strip(),
                        from_anchorage=_clean_str(row.get("From", "")),
                        start_berth_code=str(row["작업 시작지"]).strip(),
                        end_berth_code=str(row["작업 종료지"]).strip(),
                        to_anchorage=_clean_str(row.get("To", "")),
                        actual_start=_parse_iso_utc(str(row["실제 스케줄 시작 시각"])),
                        actual_end=_parse_iso_utc(str(row["실제 스케줄 종료 시각"])),
                        travel_to_site_km=float(row["작업까지 이동 거리(km)"]),
                        travel_to_site_min=float(row["작업까지 이동 시간(분)"]),
                        service_dist_km=float(row["작업중 이동 거리(km)"]),
                        service_duration_min=float(row["작업중 이동 시간(분)"]),
                        pilot_code=str(row["도선사"]).strip(),
                        tonnage_mt=float(row["톤수"]),
                        initial_schedule=_parse_iso_utc(str(row["최초 스케줄 시각"])),
                        initial_tug_code=str(row["최초 예선"]).strip(),
                        ais_file_target=_clean_str(row.get("AIS 파일명 target", "")),
                        ais_file_tug=_clean_str(row.get("AIS 파일명 tug", "")),
                    )
                )
            except Exception as exc:
                dropped += 1
                logger.warning("SchData 행 %d 스킵: %s", idx, exc)

        if dropped:
            logger.warning("%d행 드롭됨 (파싱 오류)", dropped)
        logger.info(
            "실행기록 로드: %d건 (단일예선=%d건)",
            len(result),
            sum(1 for e in result if e.is_single_tug),
        )
        return result


# ── 내부 헬퍼 ────────────────────────────────────────────────

def _parse_iso_utc(s: str) -> datetime:
    """ISO-8601 UTC 문자열 → timezone-aware datetime (UTC).

    Args:
        s: ISO-8601 문자열 (예: "2024-06-08T07:32:18.000Z")

    Returns:
        UTC timezone-aware datetime 객체.

    Raises:
        ValueError: 파싱 불가 시.
    """
    s = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def _clean_str(val: object) -> str:
    """NaN / None / 빈 값을 빈 문자열로 변환.

    Args:
        val: 임의 값.

    Returns:
        문자열 또는 빈 문자열.
    """
    if val is None:
        return ""
    s = str(val).strip()
    return "" if s.lower() in ("nan", "none", "") else s
