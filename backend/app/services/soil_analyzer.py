"""
Soil Analysis Service
=====================
Analyzes soil suitability based on:
- 農研機構 eSoil (Japan soil inventory)
- National Land Numerical Information (国土数値情報)
- Elevation-derived soil proxies

Returns soil type, pH range, drainage, organic matter estimates.
"""

import math
from typing import Optional

import httpx

# Japan soil classification to agricultural suitability mapping
SOIL_GROUPS = {
    "褐色森林土": {"group": "forest_brown", "ph": "5.0-6.5", "drainage": "good", "organic": "medium", "base_score": 60},
    "黒ボク土": {"group": "andosol", "ph": "5.5-6.5", "drainage": "good", "organic": "high", "base_score": 75},
    "灰色低地土": {"group": "lowland_gray", "ph": "5.5-7.0", "drainage": "moderate", "organic": "medium", "base_score": 70},
    "グライ土": {"group": "gley", "ph": "5.0-6.5", "drainage": "poor", "organic": "high", "base_score": 55},
    "褐色低地土": {"group": "lowland_brown", "ph": "5.5-7.0", "drainage": "good", "organic": "medium", "base_score": 72},
    "赤色土": {"group": "red", "ph": "4.5-6.0", "drainage": "good", "organic": "low", "base_score": 50},
    "泥炭土": {"group": "peat", "ph": "4.0-5.5", "drainage": "poor", "organic": "very_high", "base_score": 45},
    "砂丘未熟土": {"group": "sand_dune", "ph": "6.0-8.0", "drainage": "excessive", "organic": "very_low", "base_score": 35},
    "沖積土": {"group": "alluvial", "ph": "5.5-7.0", "drainage": "moderate", "organic": "medium", "base_score": 68},
    "ポドゾル": {"group": "podzol", "ph": "4.0-5.5", "drainage": "moderate", "organic": "low", "base_score": 40},
}

# Crop-soil suitability matrix
CROP_SOIL_AFFINITY = {
    "rice": {"gley": 0.9, "lowland_gray": 0.95, "alluvial": 0.85, "andosol": 0.6, "peat": 0.7},
    "tomato": {"andosol": 0.9, "lowland_brown": 0.85, "forest_brown": 0.75, "alluvial": 0.7},
    "strawberry": {"andosol": 0.9, "lowland_brown": 0.85, "forest_brown": 0.8},
    "cabbage": {"andosol": 0.85, "lowland_gray": 0.8, "lowland_brown": 0.85, "alluvial": 0.75},
    "sweet_potato": {"sand_dune": 0.85, "lowland_brown": 0.8, "andosol": 0.7, "red": 0.75},
    "grape": {"forest_brown": 0.85, "lowland_brown": 0.8, "andosol": 0.7},
    "tea": {"andosol": 0.9, "red": 0.85, "forest_brown": 0.75, "podzol": 0.65},
    "soybean": {"andosol": 0.85, "lowland_gray": 0.8, "lowland_brown": 0.85, "alluvial": 0.75},
    "wheat": {"lowland_brown": 0.85, "lowland_gray": 0.8, "andosol": 0.75, "alluvial": 0.7},
    "onion": {"alluvial": 0.85, "lowland_brown": 0.85, "andosol": 0.8},
}

# Default soil type estimation from elevation and latitude
ELEVATION_SOIL_RULES = [
    (0, 5, "グライ土"),       # Coastal lowland
    (5, 30, "灰色低地土"),    # Low plain
    (30, 100, "褐色低地土"),  # River terrace
    (100, 300, "黒ボク土"),   # Volcanic ash upland
    (300, 600, "褐色森林土"), # Hill/mountain
    (600, 2000, "ポドゾル"),  # High mountain
]


async def get_elevation(lat: float, lon: float) -> float:
    """Get elevation from GSI DEM API."""
    url = f"https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php?lat={lat}&lon={lon}&outtype=JSON"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url)
            data = resp.json()
            elev = data.get("elevation")
            if elev and elev != "-----":
                return float(elev)
        except Exception:
            pass
    return 50.0  # default fallback


def estimate_soil_type(lat: float, lon: float, elevation: float) -> str:
    """Estimate soil type from elevation. In production, use eSoil API."""
    for low, high, soil in ELEVATION_SOIL_RULES:
        if low <= elevation < high:
            return soil
    return "褐色森林土"


def get_soil_properties(soil_type: str) -> dict:
    """Get properties for a soil type."""
    return SOIL_GROUPS.get(soil_type, SOIL_GROUPS["褐色森林土"])


def calculate_soil_score(soil_type: str, crop: Optional[str] = None) -> float:
    """Calculate soil suitability score (0-100)."""
    props = get_soil_properties(soil_type)
    base = props["base_score"]

    if crop:
        # Check explicit affinity table first
        if crop in CROP_SOIL_AFFINITY:
            affinity = CROP_SOIL_AFFINITY[crop].get(props["group"], 0.5)
            return min(100.0, base * affinity * 1.3)
        # Fall back to CROP_DATABASE soil_pref
        try:
            from app.services.crop_recommender import CROP_DATABASE
            if crop in CROP_DATABASE:
                prefs = CROP_DATABASE[crop].get("soil_pref", [])
                if props["group"] in prefs:
                    idx = prefs.index(props["group"])
                    affinity = 0.95 - idx * 0.05
                else:
                    affinity = 0.5
                return min(100.0, base * affinity * 1.3)
        except ImportError:
            pass

    return float(base)


async def analyze_soil(lat: float, lon: float, crop: Optional[str] = None) -> dict:
    """Full soil analysis for a location."""
    elevation = await get_elevation(lat, lon)
    soil_type = estimate_soil_type(lat, lon, elevation)
    props = get_soil_properties(soil_type)
    score = calculate_soil_score(soil_type, crop)

    suitability_notes = []
    if props["drainage"] == "poor":
        suitability_notes.append("排水性が低く、畑作には暗渠排水が推奨されます")
    if props["drainage"] == "excessive":
        suitability_notes.append("保水力が低く、頻繁な灌水が必要です")
    if props["organic"] in ("very_low", "low"):
        suitability_notes.append("有機物が少なく、堆肥投入で土壌改良が効果的です")
    if not suitability_notes:
        suitability_notes.append("標準的な農業利用に適した土壌です")

    return {
        "soil_type": soil_type,
        "soil_group": props["group"],
        "ph_range": props["ph"],
        "drainage": props["drainage"],
        "organic_matter": props["organic"],
        "suitability_notes": "。".join(suitability_notes),
        "score": score,
        "elevation": elevation,
    }
