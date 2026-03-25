"""
JMA AMeDAS Integration
======================
Fetches real-time weather data from Japan Meteorological Agency (気象庁).
Uses the unofficial but publicly accessible JSON endpoints.

Data sources:
- AMeDAS station table: https://www.jma.go.jp/bosai/amedas/const/amedastable.json
- AMeDAS observations: https://www.jma.go.jp/bosai/amedas/data/map/{timestamp}.json
- Latest time: https://www.jma.go.jp/bosai/amedas/data/latest_time.txt

All data is provided under 政府標準利用規約 (Government Standard Terms of Use).
"""

import math
import time
from typing import Optional

import httpx

# Cache for station table (loaded once, ~1286 stations)
_stations_cache: Optional[dict] = None
_stations_cache_time: float = 0
_CACHE_TTL = 86400  # 24 hours

# Cache for latest observations
_obs_cache: Optional[dict] = None
_obs_cache_time: float = 0
_OBS_CACHE_TTL = 600  # 10 minutes


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in km between two coordinates."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def _parse_lat_lon(coord: list) -> float:
    """Parse JMA coordinate format [degrees, minutes*10] -> decimal degrees."""
    return coord[0] + coord[1] / 60.0


async def get_stations() -> dict:
    """Load AMeDAS station table with caching."""
    global _stations_cache, _stations_cache_time
    if _stations_cache and (time.time() - _stations_cache_time) < _CACHE_TTL:
        return _stations_cache

    url = "https://www.jma.go.jp/bosai/amedas/const/amedastable.json"
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url)
        data = resp.json()

    # Convert to easier format
    stations = {}
    for sid, info in data.items():
        stations[sid] = {
            "name": info.get("kjName", ""),
            "lat": _parse_lat_lon(info["lat"]),
            "lon": _parse_lat_lon(info["lon"]),
            "alt": info.get("alt", 0),
        }

    _stations_cache = stations
    _stations_cache_time = time.time()
    return stations


async def get_latest_observations() -> dict:
    """Fetch latest AMeDAS observations for all stations."""
    global _obs_cache, _obs_cache_time
    if _obs_cache and (time.time() - _obs_cache_time) < _OBS_CACHE_TTL:
        return _obs_cache

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Get latest timestamp
        resp = await client.get("https://www.jma.go.jp/bosai/amedas/data/latest_time.txt")
        ts_str = resp.text.strip()
        # Convert: "2026-03-26T04:10:00+09:00" -> "20260326041000"
        ts = ts_str[:4] + ts_str[5:7] + ts_str[8:10] + ts_str[11:13] + ts_str[14:16] + "00"

        # Fetch observation data
        obs_url = f"https://www.jma.go.jp/bosai/amedas/data/map/{ts}.json"
        resp = await client.get(obs_url)
        data = resp.json()

    _obs_cache = data
    _obs_cache_time = time.time()
    return data


async def find_nearest_station(lat: float, lon: float) -> tuple[str, dict, float]:
    """Find nearest AMeDAS station. Returns (station_id, station_info, distance_km)."""
    stations = await get_stations()

    best_id, best_info, best_dist = None, None, float("inf")
    for sid, info in stations.items():
        d = _haversine(lat, lon, info["lat"], info["lon"])
        if d < best_dist:
            best_id, best_info, best_dist = sid, info, d

    return best_id, best_info, best_dist


async def get_realtime_weather(lat: float, lon: float) -> dict:
    """
    Get real-time weather data for a location from the nearest AMeDAS station.

    Returns:
        dict with temp, humidity, precipitation, sunshine, wind, station info
    """
    station_id, station_info, distance = await find_nearest_station(lat, lon)
    observations = await get_latest_observations()

    obs = observations.get(station_id, {})

    # Extract values (JMA format: [value, quality_flag])
    def val(key):
        v = obs.get(key)
        if v and isinstance(v, list) and len(v) >= 1 and v[0] is not None:
            return v[0]
        return None

    result = {
        "station_id": station_id,
        "station_name": station_info["name"] if station_info else "不明",
        "station_distance_km": round(distance, 1),
        "station_altitude": station_info.get("alt", 0) if station_info else 0,
        "temp_current": val("temp"),
        "humidity": val("humidity"),
        "precipitation_1h": val("precipitation1h"),
        "precipitation_24h": val("precipitation24h"),
        "sunshine_10min": val("sun10m"),
        "sunshine_1h": val("sun1h"),
        "wind_speed": val("wind"),
        "wind_direction": val("windDirection"),
        "data_quality": "realtime",
        "source": "気象庁 AMeDAS",
    }

    return result
