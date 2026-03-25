"""
Climate Analysis Service
========================
Analyzes climate suitability based on:
- 気象庁メッシュデータ (JMA mesh climate normals)
- Growing Degree Days (GDD) calculation
- Frost risk / drought risk / typhoon risk assessment
"""

import math
from typing import Optional

import httpx

# Japan climate normals by region (30-year averages, simplified mesh)
# Key: (lat_band, lon_band) -> climate data
# In production, replace with actual JMA mesh data
CLIMATE_NORMALS = {
    # Hokkaido
    "hokkaido": {"temp": 8.5, "precip": 1100, "sunshine": 1700, "frost_free": 150, "zone": "Dfb"},
    # Tohoku
    "tohoku": {"temp": 11.5, "precip": 1300, "sunshine": 1650, "frost_free": 180, "zone": "Cfa/Dfb"},
    # Kanto
    "kanto": {"temp": 15.5, "precip": 1500, "sunshine": 1900, "frost_free": 220, "zone": "Cfa"},
    # Chubu (Pacific)
    "chubu_pacific": {"temp": 15.0, "precip": 1800, "sunshine": 1850, "frost_free": 210, "zone": "Cfa"},
    # Chubu (Japan Sea)
    "chubu_sea": {"temp": 13.0, "precip": 2200, "sunshine": 1500, "frost_free": 190, "zone": "Cfa"},
    # Kinki
    "kinki": {"temp": 16.0, "precip": 1400, "sunshine": 1900, "frost_free": 230, "zone": "Cfa"},
    # Chugoku
    "chugoku": {"temp": 15.5, "precip": 1600, "sunshine": 1800, "frost_free": 220, "zone": "Cfa"},
    # Shikoku
    "shikoku": {"temp": 16.5, "precip": 1800, "sunshine": 1950, "frost_free": 240, "zone": "Cfa"},
    # Kyushu
    "kyushu": {"temp": 17.0, "precip": 1900, "sunshine": 1850, "frost_free": 250, "zone": "Cfa"},
    # Okinawa
    "okinawa": {"temp": 23.0, "precip": 2100, "sunshine": 1700, "frost_free": 365, "zone": "Cfa"},
}

# Crop climate requirements
CROP_CLIMATE = {
    "rice": {"temp_min": 15, "temp_max": 30, "precip_min": 1000, "gdd_min": 2000, "frost_sens": "high"},
    "tomato": {"temp_min": 15, "temp_max": 30, "precip_min": 600, "gdd_min": 1500, "frost_sens": "high"},
    "strawberry": {"temp_min": 10, "temp_max": 25, "precip_min": 800, "gdd_min": 1200, "frost_sens": "medium"},
    "cabbage": {"temp_min": 5, "temp_max": 25, "precip_min": 600, "gdd_min": 1000, "frost_sens": "low"},
    "sweet_potato": {"temp_min": 18, "temp_max": 35, "precip_min": 800, "gdd_min": 2500, "frost_sens": "very_high"},
    "grape": {"temp_min": 12, "temp_max": 30, "precip_min": 500, "gdd_min": 1500, "frost_sens": "medium"},
    "tea": {"temp_min": 12, "temp_max": 28, "precip_min": 1300, "gdd_min": 1800, "frost_sens": "medium"},
    "soybean": {"temp_min": 15, "temp_max": 30, "precip_min": 500, "gdd_min": 1800, "frost_sens": "medium"},
    "wheat": {"temp_min": 3, "temp_max": 25, "precip_min": 400, "gdd_min": 1200, "frost_sens": "very_low"},
    "onion": {"temp_min": 5, "temp_max": 25, "precip_min": 600, "gdd_min": 1200, "frost_sens": "low"},
}


def get_region(lat: float, lon: float) -> str:
    """Determine climate region from coordinates."""
    if lat >= 41.5:
        return "hokkaido"
    if lat >= 38.0:
        return "tohoku"
    if lat >= 35.5 and lon >= 139.0:
        return "kanto"
    if lat >= 34.5 and lon < 137.0:
        return "chubu_sea" if lon < 137.0 else "chubu_pacific"
    if lat >= 34.5:
        return "chubu_pacific"
    if lat >= 33.5 and lon < 136.0:
        return "kinki"
    if lat >= 33.0 and lon < 134.0:
        return "chugoku"
    if lat >= 33.0:
        return "shikoku"
    if lat >= 26.0:
        return "kyushu"
    return "okinawa"


def calculate_gdd(avg_temp: float, frost_free_days: int, base_temp: float = 10.0) -> float:
    """Calculate Growing Degree Days."""
    if avg_temp <= base_temp:
        return 0.0
    daily_gdd = avg_temp - base_temp
    return daily_gdd * frost_free_days


def assess_frost_risk(frost_free_days: int) -> str:
    if frost_free_days >= 300:
        return "極低"
    if frost_free_days >= 240:
        return "低"
    if frost_free_days >= 180:
        return "中"
    if frost_free_days >= 150:
        return "高"
    return "極高"


def assess_drought_risk(precip: float, temp: float) -> str:
    aridity = precip / max(1, temp * 25)  # simplified aridity index
    if aridity >= 3.0:
        return "極低"
    if aridity >= 2.0:
        return "低"
    if aridity >= 1.2:
        return "中"
    if aridity >= 0.8:
        return "高"
    return "極高"


def assess_typhoon_risk(lat: float, lon: float) -> str:
    # Simplified: southern/eastern coasts have higher risk
    if lat < 30:
        return "極高"
    if lat < 33 and lon > 130:
        return "高"
    if lat < 36:
        return "中"
    if lat < 40:
        return "低"
    return "極低"


def calculate_climate_score(climate_data: dict, crop: Optional[str] = None) -> float:
    """Calculate climate suitability score (0-100)."""
    temp = climate_data["temp"]
    precip = climate_data["precip"]
    sunshine = climate_data["sunshine"]
    frost_free = climate_data["frost_free"]
    gdd = calculate_gdd(temp, frost_free)

    # Base score from general agricultural suitability
    temp_score = max(0, 100 - abs(temp - 16) * 5)  # optimal ~16°C
    precip_score = max(0, 100 - abs(precip - 1400) * 0.05)  # optimal ~1400mm
    sun_score = min(100, sunshine / 20)  # more is better
    frost_score = min(100, frost_free / 3)  # more is better

    base = temp_score * 0.3 + precip_score * 0.2 + sun_score * 0.25 + frost_score * 0.25

    if crop and crop in CROP_CLIMATE:
        req = CROP_CLIMATE[crop]
        penalties = 0

        if temp < req["temp_min"]:
            penalties += (req["temp_min"] - temp) * 5
        if temp > req["temp_max"]:
            penalties += (temp - req["temp_max"]) * 3

        if precip < req["precip_min"]:
            penalties += (req["precip_min"] - precip) * 0.02

        if gdd < req["gdd_min"]:
            penalties += (req["gdd_min"] - gdd) * 0.01

        base = max(0, base - penalties)

    return min(100.0, round(base, 1))


def analyze_climate(lat: float, lon: float, crop: Optional[str] = None) -> dict:
    """Full climate analysis for a location."""
    region = get_region(lat, lon)
    data = CLIMATE_NORMALS.get(region, CLIMATE_NORMALS["kanto"])

    gdd = calculate_gdd(data["temp"], data["frost_free"])
    score = calculate_climate_score(data, crop)

    return {
        "annual_temp_avg": data["temp"],
        "annual_precip_mm": data["precip"],
        "frost_free_days": data["frost_free"],
        "growing_degree_days": round(gdd, 0),
        "climate_zone": data["zone"],
        "sunshine_hours": data["sunshine"],
        "frost_risk": assess_frost_risk(data["frost_free"]),
        "drought_risk": assess_drought_risk(data["precip"], data["temp"]),
        "typhoon_risk": assess_typhoon_risk(lat, lon),
        "score": score,
    }
