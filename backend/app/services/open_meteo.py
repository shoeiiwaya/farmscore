"""
Open-Meteo Climate Data Integration
=====================================
Fetches precise climate data from Open-Meteo Historical Forecast API.
Uses JMA (気象庁) model data at ~5km resolution.
No API key required for non-commercial use.

Source: https://open-meteo.com/
License: CC BY 4.0 (non-commercial free, commercial requires API key)
"""

import time
from typing import Optional

import httpx

# Cache for climate data (keyed by rounded lat/lon)
_climate_cache: dict = {}
_cache_time: dict = {}
_CACHE_TTL = 86400  # 24 hours (climate normals don't change often)


def _cache_key(lat: float, lon: float) -> str:
    """Round to 0.01 degree (~1km) for caching."""
    return f"{lat:.2f}_{lon:.2f}"


async def get_climate_normals(lat: float, lon: float) -> Optional[dict]:
    """
    Get annual climate normals from Open-Meteo using 2024 historical data.

    Returns:
        dict with annual_temp_avg, annual_precip_mm, sunshine_hours,
        monthly_temp, frost_days, etc.
    """
    key = _cache_key(lat, lon)
    if key in _climate_cache and (time.time() - _cache_time.get(key, 0)) < _CACHE_TTL:
        return _climate_cache[key]

    url = (
        "https://historical-forecast-api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&start_date=2024-01-01&end_date=2024-12-31"
        "&daily=temperature_2m_mean,temperature_2m_max,temperature_2m_min,"
        "precipitation_sum,sunshine_duration,wind_speed_10m_max"
        "&timezone=Asia%2FTokyo"
    )

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            resp = await client.get(url)
            data = resp.json()

            if "error" in data:
                return None

            daily = data.get("daily", {})
            temps = [t for t in daily.get("temperature_2m_mean", []) if t is not None]
            temps_min = [t for t in daily.get("temperature_2m_min", []) if t is not None]
            temps_max = [t for t in daily.get("temperature_2m_max", []) if t is not None]
            precip = [p for p in daily.get("precipitation_sum", []) if p is not None]
            sunshine = [s for s in daily.get("sunshine_duration", []) if s is not None]
            wind = [w for w in daily.get("wind_speed_10m_max", []) if w is not None]

            if not temps:
                return None

            # Calculate monthly averages
            monthly_temp = []
            days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # 2024 is leap year
            idx = 0
            for days in days_in_month:
                month_temps = temps[idx:idx + days]
                if month_temps:
                    monthly_temp.append(round(sum(month_temps) / len(month_temps), 1))
                idx += days

            # Frost days (min temp < 0)
            frost_days = sum(1 for t in temps_min if t < 0)

            # Growing degree days (base 10°C)
            gdd = sum(max(0, t - 10) for t in temps)

            # Frost-free period (approximate)
            frost_free = 365 - frost_days

            # Heavy rain days (>50mm)
            heavy_rain_days = sum(1 for p in precip if p > 50)

            result = {
                "annual_temp_avg": round(sum(temps) / len(temps), 1),
                "annual_temp_max": round(max(temps_max) if temps_max else 0, 1),
                "annual_temp_min": round(min(temps_min) if temps_min else 0, 1),
                "annual_precip_mm": round(sum(precip)),
                "sunshine_hours": round(sum(sunshine) / 3600),  # seconds → hours
                "monthly_temp": monthly_temp,
                "frost_days": frost_days,
                "frost_free_days": frost_free,
                "growing_degree_days": round(gdd),
                "heavy_rain_days": heavy_rain_days,
                "max_wind_speed": round(max(wind) if wind else 0, 1),
                "data_year": 2024,
                "source": "Open-Meteo Historical Forecast API (JMA model)",
                "resolution": "~5km mesh",
            }

            _climate_cache[key] = result
            _cache_time[key] = time.time()
            return result

        except Exception:
            return None
