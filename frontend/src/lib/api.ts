const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface ScoreResult {
  lat: number;
  lon: number;
  overall_score: number;
  grade: string;
  soil: {
    soil_type: string;
    soil_group: string;
    ph_range: string;
    drainage: string;
    organic_matter: string;
    suitability_notes: string;
  };
  soil_score: number;
  climate: {
    annual_temp_avg: number;
    annual_precip_mm: number;
    frost_free_days: number;
    growing_degree_days: number;
    climate_zone: string;
    frost_risk: string;
    drought_risk: string;
    typhoon_risk: string;
  };
  climate_score: number;
  water: {
    nearest_river_km: number;
    river_name: string;
    flood_risk_zone: string;
    groundwater_depth_est: string;
    irrigation_accessibility: string;
  };
  water_score: number;
  sunlight: {
    annual_sunshine_hours: number;
    avg_daily_radiation_mj: number;
    aspect: string;
    slope_deg: number;
  };
  sunlight_score: number;
  elevation: {
    elevation_m: number;
    slope_deg: number;
    aspect: string;
    landform: string;
  };
  elevation_score: number;
  crop_recommendations: CropRecommendation[];
  disclaimer: string;
}

export interface CropRecommendation {
  crop_name: string;
  suitability_score: number;
  reason: string;
  expected_yield_relative: string;
  growing_season: string;
}

export interface SampleRegion {
  name: string;
  lat: number;
  lon: number;
  description: string;
}

export async function fetchScore(
  lat: number,
  lon: number,
  crop?: string
): Promise<ScoreResult> {
  const params = new URLSearchParams({ lat: String(lat), lon: String(lon) });
  if (crop) params.set("crop", crop);
  const res = await fetch(`${API_BASE}/api/demo/score?${params}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchRegions(): Promise<SampleRegion[]> {
  const res = await fetch(`${API_BASE}/api/demo/regions`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchCrops(): Promise<
  Record<string, { name_ja: string; category: string; season: string }>
> {
  const res = await fetch(`${API_BASE}/api/demo/crops`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// Auth
export async function signup(email: string, password: string, name?: string) {
  const res = await fetch(`${API_BASE}/api/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API_BASE}/api/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
}
