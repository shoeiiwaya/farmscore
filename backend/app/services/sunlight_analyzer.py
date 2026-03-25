"""
Sunlight / Solar Radiation Analysis Service
============================================
Analyzes sunlight conditions based on:
- 気象庁 日照時間データ
- GSI DEM for slope/aspect calculation
- Latitude-based solar radiation estimation
"""

import math
from typing import Optional


def estimate_solar_radiation(lat: float, sunshine_hours: float) -> float:
    """Estimate daily solar radiation (MJ/m²/day) from latitude and sunshine hours.
    Uses Angstrom-Prescott equation simplified.
    """
    # Extraterrestrial radiation approximation for Japan latitudes
    lat_rad = math.radians(lat)
    # Annual average day angle
    Ra = 30.0 - (lat - 35.0) * 0.5  # MJ/m²/day approximate for Japan
    # Angstrom coefficients for Japan
    a = 0.25
    b = 0.50
    n_over_N = sunshine_hours / (365 * 12)  # rough ratio
    Rs = Ra * (a + b * min(1.0, sunshine_hours / (365 * 10)))
    return round(Rs, 1)


def estimate_slope_aspect(lat: float, lon: float, elevation: float) -> tuple[float, str]:
    """Estimate slope and aspect. In production, use DEM raster analysis.
    Returns (slope_degrees, aspect_direction).
    """
    # Without actual DEM raster, estimate from elevation
    if elevation < 10:
        return 0.5, "平坦"
    if elevation < 50:
        return 2.0, "南向き"  # assume favorable
    if elevation < 200:
        return 5.0, "南〜南東"
    if elevation < 500:
        return 12.0, "混合"
    return 20.0, "急斜面"


def calculate_sunlight_score(
    sunshine_hours: float,
    radiation: float,
    slope: float,
    aspect: str,
) -> float:
    """Calculate sunlight suitability score (0-100)."""
    # Sunshine hours score (more = better, Japan avg ~1800h)
    sun_score = min(100, sunshine_hours / 22)

    # Radiation score
    rad_score = min(100, radiation * 7)

    # Aspect bonus/penalty
    aspect_mult = 1.0
    if "南" in aspect:
        aspect_mult = 1.1
    elif "北" in aspect:
        aspect_mult = 0.8
    elif aspect == "平坦":
        aspect_mult = 1.0

    # Steep slope penalty
    slope_penalty = max(0, (slope - 15) * 2)

    score = (sun_score * 0.5 + rad_score * 0.5) * aspect_mult - slope_penalty
    return max(0, min(100, round(score, 1)))


def analyze_sunlight(lat: float, lon: float, elevation: float, sunshine_hours: float) -> dict:
    """Full sunlight analysis for a location."""
    radiation = estimate_solar_radiation(lat, sunshine_hours)
    slope, aspect = estimate_slope_aspect(lat, lon, elevation)
    score = calculate_sunlight_score(sunshine_hours, radiation, slope, aspect)

    return {
        "annual_sunshine_hours": sunshine_hours,
        "avg_daily_radiation_mj": radiation,
        "aspect": aspect,
        "slope_deg": slope,
        "score": score,
    }
