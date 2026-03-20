"""지리 좌표 유틸리티 — Haversine 거리 계산."""
from __future__ import annotations
import math

def haversine_nm(pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
    """두 (lat, lon) 좌표 사이 거리 (해리, Haversine)."""
    R = 3440.065
    lat1, lon1 = math.radians(pos1[0]), math.radians(pos1[1])
    lat2, lon2 = math.radians(pos2[0]), math.radians(pos2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))
