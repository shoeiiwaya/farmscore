from pydantic import BaseModel, Field
from typing import Optional


class ScoreRequest(BaseModel):
    lat: float = Field(..., ge=20.0, le=46.0, description="Latitude (Japan: 20-46)")
    lon: float = Field(..., ge=122.0, le=154.0, description="Longitude (Japan: 122-154)")
    crop: Optional[str] = Field(None, description="Target crop (e.g. rice, tomato, strawberry)")


class SoilDetail(BaseModel):
    soil_type: str
    soil_group: str
    ph_range: str
    drainage: str
    organic_matter: str
    suitability_notes: str


class ClimateDetail(BaseModel):
    annual_temp_avg: float
    annual_precip_mm: float
    frost_free_days: int
    growing_degree_days: float
    climate_zone: str
    frost_risk: str
    drought_risk: str
    typhoon_risk: str


class WaterDetail(BaseModel):
    nearest_river_km: float
    river_name: str
    flood_risk_zone: str
    groundwater_depth_est: str
    irrigation_accessibility: str


class SunlightDetail(BaseModel):
    annual_sunshine_hours: float
    avg_daily_radiation_mj: float
    aspect: str
    slope_deg: float


class ElevationDetail(BaseModel):
    elevation_m: float
    slope_deg: float
    aspect: str
    landform: str


class CropRecommendation(BaseModel):
    crop_name: str
    suitability_score: float
    reason: str
    expected_yield_relative: str
    growing_season: str


class ScoreResponse(BaseModel):
    lat: float
    lon: float
    overall_score: float = Field(..., ge=0, le=100, description="Overall farmland suitability 0-100")
    grade: str  # S, A, B, C, D
    soil: SoilDetail
    soil_score: float
    climate: ClimateDetail
    climate_score: float
    water: WaterDetail
    water_score: float
    sunlight: SunlightDetail
    sunlight_score: float
    elevation: ElevationDetail
    elevation_score: float
    crop_recommendations: list[CropRecommendation]
    disclaimer: str = "本スコアは参考情報です。農業判断の結果について一切の責任を負いません。データソース: 農研機構eSoil, 気象庁, 国土数値情報, JAXA ALOS"


class BatchScoreRequest(BaseModel):
    locations: list[ScoreRequest] = Field(..., max_length=50)


class BatchScoreResponse(BaseModel):
    results: list[ScoreResponse]
    count: int
