"""
Solomon R101 벤치마크 인스턴스 — 25 노드 서브셋.

원본: Solomon (1987), Operations Research 35(2):254-265
출처: http://w.cba.neu.edu/~msolomon/problems.htm

R101은 무작위(Random) 배치 + 좁은 시간창 특성.
ALNS 검증 기준: BKS(Best Known Solution) 대비 5% 이내.

25 노드 서브셋: 원본 100고객 중 앞 25개.
예인선 문제에 맞게 변환:
  - 고객 → vessel (선박)
  - depot → 예인선 기지
  - 시간창 → 최적화 시간창

BKS (원본 R101): 1637.7 (100 customers)
25-node subset BKS: 참조 미확정 (자체 MILP 결과를 기준으로 설정)
"""
from __future__ import annotations
from libs.utils.time_window import TimeWindowSpec

# Solomon R101 원본 데이터 (앞 25개 고객)
# 형식: (customer_id, x, y, demand, ready_time, due_date, service_time)
_R101_RAW = [
    # depot: (0, 35, 35, 0, 0, 230, 0)
    (1,  45, 68,  10,  912, 967, 90),
    (2,  45, 70,  30,  825, 870, 90),
    (3,  42, 66,  10,   65, 146, 90),
    (4,  42, 68,  10,  727, 782, 90),
    (5,  42, 65,  10,   15,  67, 90),
    (6,  40, 69,  20,  621, 702, 90),
    (7,  40, 66,  20,  170, 225, 90),
    (8,  38, 68,  20,  255, 324, 90),
    (9,  38, 70,  10,  534, 605, 90),
    (10, 35, 66,  10,  357, 410, 90),
    (11, 35, 69,  10,  448, 505, 90),
    (12, 33, 67,  20,  652, 721, 90),
    (13, 33, 69,  10,   30,  92, 90),
    (14, 32, 66,  10,  567, 620, 90),
    (15, 32, 68,  20,  384, 429, 90),
    (16, 30, 67,  10,  475, 528, 90),
    (17, 30, 69,  20,   99, 148, 90),
    (18, 28, 67,  20,  179, 254, 90),
    (19, 28, 69,  10,  278, 345, 90),
    (20, 26, 67,  10,  710, 761, 90),
    (21, 26, 69,  10,  148, 191, 90),
    (22, 25, 66,  20,  893, 940, 90),
    (23, 25, 68,  20,  480, 503, 90),
    (24, 44, 67,  10,    6,  68, 90),
    (25, 44, 65,  10,  727, 782, 90),
]

DEPOT_X, DEPOT_Y = 35, 35
TUG_SPEED_KN = 12.0  # 예인선 속도
SCALE = 0.1          # 좌표 → 해리 스케일 (xy단위=km → 0.1 = 해리 근사)


def _xy_to_latlon(x: float, y: float) -> tuple[float, float]:
    """Solomon XY → 위도경도 근사 변환 (부산항 기준)."""
    base_lat, base_lon = 35.0, 129.0
    # 1도 ≈ 60해리, 0.1 = 6해리 → km 단위 좌표를 도 단위로
    lat = base_lat + (y - DEPOT_Y) * 0.01
    lon = base_lon + (x - DEPOT_X) * 0.01
    return lat, lon


def make_solomon_r101_25() -> tuple[list[TimeWindowSpec], dict]:
    """Solomon R101 25-node 인스턴스 생성.

    Returns:
        (windows, meta) — TimeWindowSpec 리스트, 메타정보
    """
    windows = []
    for row in _R101_RAW:
        cid, x, y, demand, ready, due, service = row
        lat, lon = _xy_to_latlon(x, y)
        windows.append(TimeWindowSpec(
            vessel_id=str(cid),
            berth_id=f"B{(cid - 1) % 5}",  # 5개 선석에 순환 배정
            earliest_start=float(ready),
            latest_start=float(due),
            service_duration=float(service),
            priority=max(1, demand // 10),
        ))

    depot_lat, depot_lon = _xy_to_latlon(DEPOT_X, DEPOT_Y)
    berth_locs = {
        f"B{i}": (_xy_to_latlon(DEPOT_X + i*2, DEPOT_Y + i)[0],
                  _xy_to_latlon(DEPOT_X + i*2, DEPOT_Y + i)[1])
        for i in range(5)
    }

    meta = {
        "n_customers": len(windows),
        "depot": (depot_lat, depot_lon),
        "berth_locations": berth_locs,
        "tug_fleet": ["T0", "T1", "T2", "T3"],  # 4 tugs
        "reference": "Solomon (1987) R101, 25-node subset",
    }
    return windows, meta


# 빠른 임포트용
SOLOMON_R101_25, SOLOMON_META = make_solomon_r101_25()
