"""
Water / Irrigation Analysis Service
====================================
Analyzes water accessibility based on:
- 国土数値情報 河川データ (river proximity)
- Flood risk zone overlay
- Groundwater depth estimation
"""

import math
from typing import Optional

import httpx

# Major rivers in Japan with approximate bounding boxes
# In production, use PostGIS with actual river geometries
MAJOR_RIVERS = [
    {"name": "利根川", "lat": 36.0, "lon": 139.8, "length_km": 322},
    {"name": "信濃川", "lat": 37.9, "lon": 139.0, "length_km": 367},
    {"name": "石狩川", "lat": 43.2, "lon": 141.3, "length_km": 268},
    {"name": "多摩川", "lat": 35.6, "lon": 139.4, "length_km": 138},
    {"name": "荒川", "lat": 35.8, "lon": 139.6, "length_km": 173},
    {"name": "相模川", "lat": 35.4, "lon": 139.3, "length_km": 113},
    {"name": "鶴見川", "lat": 35.5, "lon": 139.6, "length_km": 42},
    {"name": "淀川", "lat": 34.7, "lon": 135.5, "length_km": 75},
    {"name": "木曽川", "lat": 35.1, "lon": 136.7, "length_km": 229},
    {"name": "筑後川", "lat": 33.3, "lon": 130.5, "length_km": 143},
    {"name": "吉野川", "lat": 34.0, "lon": 134.5, "length_km": 194},
    {"name": "四万十川", "lat": 33.0, "lon": 132.9, "length_km": 196},
    {"name": "北上川", "lat": 39.1, "lon": 141.1, "length_km": 249},
    {"name": "最上川", "lat": 38.9, "lon": 139.9, "length_km": 229},
    {"name": "天竜川", "lat": 34.7, "lon": 137.7, "length_km": 213},
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearest_river(lat: float, lon: float) -> tuple[str, float]:
    """Find nearest major river and distance."""
    min_dist = float("inf")
    nearest = "不明"
    for river in MAJOR_RIVERS:
        d = haversine_km(lat, lon, river["lat"], river["lon"])
        if d < min_dist:
            min_dist = d
            nearest = river["name"]
    return nearest, round(min_dist, 1)


def estimate_flood_risk(distance_km: float, elevation: float) -> str:
    """Estimate flood risk from river distance and elevation."""
    if elevation < 5 and distance_km < 2:
        return "極高"
    if elevation < 10 and distance_km < 5:
        return "高"
    if elevation < 30 and distance_km < 10:
        return "中"
    if elevation < 50:
        return "低"
    return "極低"


def estimate_groundwater(elevation: float, precip: float) -> str:
    """Rough groundwater depth estimation."""
    if elevation < 10:
        return "浅い（1-3m）"
    if elevation < 30:
        return "やや浅い（3-5m）"
    if elevation < 100:
        return "中程度（5-10m）"
    if elevation < 300:
        return "やや深い（10-20m）"
    return "深い（20m以上）"


def assess_irrigation(distance_km: float, precip: float) -> str:
    """Assess irrigation accessibility."""
    if distance_km < 2 and precip > 1200:
        return "極めて良好（河川近接+十分な降水量）"
    if distance_km < 5 and precip > 1000:
        return "良好（水源アクセス容易）"
    if distance_km < 10:
        return "標準（灌漑設備推奨）"
    if distance_km < 20:
        return "やや不利（灌漑設備必須）"
    return "不利（水源確保が課題）"


def calculate_water_score(distance_km: float, elevation: float, precip: float) -> float:
    """Calculate water accessibility score (0-100)."""
    # Closer to river = better (diminishing returns)
    dist_score = max(0, 100 - distance_km * 3)

    # Precipitation bonus
    precip_score = min(100, precip / 20)

    # Flood risk penalty for very low elevation near river
    flood_penalty = 0
    if elevation < 5 and distance_km < 2:
        flood_penalty = 20
    elif elevation < 10 and distance_km < 5:
        flood_penalty = 10

    score = dist_score * 0.5 + precip_score * 0.5 - flood_penalty
    return max(0, min(100, round(score, 1)))


def analyze_water(lat: float, lon: float, elevation: float, precip: float) -> dict:
    """Full water analysis for a location."""
    river_name, distance = find_nearest_river(lat, lon)
    score = calculate_water_score(distance, elevation, precip)

    return {
        "nearest_river_km": distance,
        "river_name": river_name,
        "flood_risk_zone": estimate_flood_risk(distance, elevation),
        "groundwater_depth_est": estimate_groundwater(elevation, precip),
        "irrigation_accessibility": assess_irrigation(distance, precip),
        "score": score,
    }
