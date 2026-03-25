"""
FarmScore Integrated Scoring Engine
====================================
Combines all analyzers into a unified farmland suitability score.
"""

from typing import Optional

from app.services.soil_analyzer import analyze_soil
from app.services.climate_analyzer import analyze_climate, analyze_climate_async
from app.services.water_analyzer import analyze_water
from app.services.sunlight_analyzer import analyze_sunlight
from app.services.crop_recommender import recommend_crops
from app.services.fertilizer_advisor import get_fertilizer_recommendation
from app.services.jma_amedas import get_realtime_weather
from app.services.estat_client import get_crop_evidence
from app.services.global_data import (
    detect_country, get_global_elevation, estimate_global_soil,
    get_fao_context, GLOBAL_SOIL_TYPES, GLOBAL_CROPS_EXTRA,
)


def _grade(score: float) -> str:
    if score >= 85:
        return "S"
    if score >= 70:
        return "A"
    if score >= 55:
        return "B"
    if score >= 40:
        return "C"
    return "D"


async def calculate_farm_score(
    lat: float,
    lon: float,
    crop: Optional[str] = None,
) -> dict:
    """
    Calculate comprehensive farmland suitability score.
    Works globally — uses Japan-specific APIs for Japan, global APIs elsewhere.
    """
    # Detect country
    country = detect_country(lat, lon)
    is_japan = country["code"] == "JPN"

    # 1. Elevation (GSI for Japan, Open-Meteo for global)
    if is_japan:
        soil = await analyze_soil(lat, lon, crop)
        elevation = soil["elevation"]
    else:
        elevation = await get_global_elevation(lat, lon)
        soil = None  # Will be estimated from climate

    # 2. Climate analysis (Open-Meteo — works globally)
    try:
        climate = await analyze_climate_async(lat, lon, crop)
    except Exception:
        climate = analyze_climate(lat, lon, crop)

    # 3. Soil (Japan: eSoil system, Global: climate-based estimation)
    if not is_japan or soil is None:
        global_soil = estimate_global_soil(
            lat, lon, elevation,
            climate["annual_temp_avg"],
            climate["annual_precip_mm"],
        )
        if global_soil:
            soil = {
                "soil_type": global_soil["name"],
                "soil_group": global_soil["group"],
                "ph_range": global_soil["ph"],
                "drainage": global_soil["drainage"],
                "organic_matter": global_soil["organic"],
                "suitability_notes": f"気候・標高から推定（{country['name']}）",
                "score": float(global_soil["base_score"]),
                "elevation": elevation,
            }
        else:
            # Fallback: use Japanese analyzer
            soil = await analyze_soil(lat, lon, crop)
            elevation = soil["elevation"]

    # 4. Water analysis
    water = analyze_water(lat, lon, elevation, climate["annual_precip_mm"])

    # 5. Sunlight analysis
    sunlight = analyze_sunlight(lat, lon, elevation, climate["sunshine_hours"])

    # 6. Elevation score
    if elevation < 3:
        elev_score = 30
    elif elevation < 300:
        elev_score = 80 + min(20, (elevation - 3) * 0.1)
    elif elevation < 600:
        elev_score = 70
    elif elevation < 1000:
        elev_score = 50
    else:
        elev_score = 30

    elev_detail = {
        "elevation_m": elevation,
        "slope_deg": sunlight["slope_deg"],
        "aspect": sunlight["aspect"],
        "landform": _classify_landform(elevation),
    }

    # 7. Weighted overall score
    weights = {"soil": 0.25, "climate": 0.25, "water": 0.20, "sunlight": 0.15, "elevation": 0.15}
    overall = (
        soil["score"] * weights["soil"]
        + climate["score"] * weights["climate"]
        + water["score"] * weights["water"]
        + sunlight["score"] * weights["sunlight"]
        + elev_score * weights["elevation"]
    )
    overall = round(overall, 1)

    # 8. Real-time weather (JMA AMeDAS for Japan only)
    weather = None
    if is_japan:
        try:
            weather = await get_realtime_weather(lat, lon)
        except Exception:
            pass

    # 9. Production evidence
    evidence = None
    if is_japan:
        try:
            evidence = await get_crop_evidence(lat, lon, crop)
        except Exception:
            pass

    # 10. FAO global context
    fao_context = None
    if crop:
        fao_context = get_fao_context(crop, country["code"])

    # 11. Crop recommendations
    crops = recommend_crops(
        soil_group=soil["soil_group"],
        temp=climate["annual_temp_avg"],
        precip=climate["annual_precip_mm"],
        sunshine=climate["sunshine_hours"],
        target_crop=crop,
        top_n=5,
    )

    result = {
        "lat": lat,
        "lon": lon,
        "country": country,
        "overall_score": overall,
        "grade": _grade(overall),
        "soil": {
            "soil_type": soil["soil_type"],
            "soil_group": soil["soil_group"],
            "ph_range": soil["ph_range"],
            "drainage": soil["drainage"],
            "organic_matter": soil["organic_matter"],
            "suitability_notes": soil["suitability_notes"],
        },
        "soil_score": soil["score"],
        "climate": {
            "annual_temp_avg": climate["annual_temp_avg"],
            "annual_precip_mm": climate["annual_precip_mm"],
            "sunshine_hours": climate["sunshine_hours"],
            "frost_free_days": climate["frost_free_days"],
            "growing_degree_days": climate["growing_degree_days"],
            "climate_zone": climate["climate_zone"],
            "frost_risk": climate["frost_risk"],
            "drought_risk": climate["drought_risk"],
            "typhoon_risk": climate["typhoon_risk"],
        },
        "climate_score": climate["score"],
        "water": {
            "nearest_river_km": water["nearest_river_km"],
            "river_name": water["river_name"],
            "flood_risk_zone": water["flood_risk_zone"],
            "groundwater_depth_est": water["groundwater_depth_est"],
            "irrigation_accessibility": water["irrigation_accessibility"],
        },
        "water_score": water["score"],
        "sunlight": {
            "annual_sunshine_hours": sunlight["annual_sunshine_hours"],
            "avg_daily_radiation_mj": sunlight["avg_daily_radiation_mj"],
            "aspect": sunlight["aspect"],
            "slope_deg": sunlight["slope_deg"],
        },
        "sunlight_score": sunlight["score"],
        "elevation": elev_detail,
        "elevation_score": float(elev_score),
        "crop_recommendations": crops,
        "data_sources": {
            "soil": "農研機構 eSoil 土壌分類" if is_japan else f"気候・標高ベース推定（{country['name']}）",
            "elevation": "国土地理院 DEM" if is_japan else "Open-Meteo / Copernicus DEM",
            "climate": climate.get("climate_source", "Open-Meteo（5km解像度）"),
            "water": "国土数値情報 河川データ",
            "realtime_weather": "気象庁 AMeDAS" if weather else None,
            "crop_stats": "農水省 e-Stat" if evidence else ("FAO FAOSTAT 2022" if fao_context else None),
        },
        "disclaimer": "本スコアは公開データに基づく参考情報です。実際の農業判断には現地調査を推奨します。",
    }

    # 12. Fertilizer recommendation
    try:
        fertilizer = get_fertilizer_recommendation(
            soil_type=soil["soil_type"],
            soil_ph=soil["ph_range"],
            drainage=soil["drainage"],
            organic_matter=soil["organic_matter"],
            crop=crop,
        )
        result["fertilizer"] = fertilizer
    except Exception:
        pass

    if weather:
        result["realtime_weather"] = weather
    if evidence:
        result["production_evidence"] = evidence
    if fao_context:
        result["fao_global"] = fao_context

    return result


def _classify_landform(elevation: float) -> str:
    if elevation < 3:
        return "沿岸低地"
    if elevation < 15:
        return "氾濫原"
    if elevation < 30:
        return "低地"
    if elevation < 100:
        return "台地・段丘"
    if elevation < 300:
        return "丘陵地"
    if elevation < 600:
        return "山麓"
    if elevation < 1000:
        return "山地"
    return "高山"
