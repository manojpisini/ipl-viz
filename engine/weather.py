"""
Open-Meteo historical weather client.

Fetches match-day conditions (temp, humidity, wind, rain) for a given
lat/lon + date, caching results locally so we only hit the API once per
venue-date combo.
"""

import json
import logging
from pathlib import Path

import requests

from engine.paths import get_resource_path

log = logging.getLogger(__name__)

CACHE_FILE = get_resource_path("data/weather_cache.json")
USER_AGENT = "IPLViz/1.0 (historical_weather_feature)"


# -- File-backed cache --------------------------------------------------------

def _load_cache():
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


# -- Public API ---------------------------------------------------------------

def get_match_weather(lat: float, lon: float, date_str: str):
    """
    Return a dict of weather conditions for the given coordinates + date,
    or None if anything goes sideways.  Results are cached to disk.
    """
    if lat == 0.0 or lon == 0.0 or not date_str:
        return None

    key = f"{lat:.4f}_{lon:.4f}_{date_str}"
    cache = _load_cache()
    if key in cache:
        return cache[key]

    try:
        resp = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": lat,
                "longitude": lon,
                "start_date": date_str,
                "end_date": date_str,
                "hourly": "temperature_2m,relative_humidity_2m,rain,wind_speed_10m,weather_code,apparent_temperature",
                "timezone": "auto",
            },
            headers={"User-Agent": USER_AGENT},
        )
        if resp.status_code != 200:
            log.error("Open-Meteo returned %d: %s", resp.status_code, resp.text[:200])
            return None

        hourly = resp.json().get("hourly", {})
        if not hourly or "time" not in hourly:
            return None

        # IPL starts around 7:30 PM local — hour index 19 is close enough
        idx = 19 if len(hourly["time"]) > 19 else len(hourly["time"]) - 1
        code = hourly["weather_code"][idx]

        result = {
            "air_temp":   f"{hourly['temperature_2m'][idx]}°C",
            "feels_like": f"{hourly['apparent_temperature'][idx]}°C",
            "humidity":   f"{hourly['relative_humidity_2m'][idx]}%",
            "wind":       f"{hourly['wind_speed_10m'][idx]} km/h",
            "rain":       f"{hourly['rain'][idx]} mm",
            "summary":    _wmo_summary(code),
            "icon":       _wmo_icon(code),
            "source":     "Open-Meteo",
        }

        cache[key] = result
        _save_cache(cache)
        return result

    except Exception as exc:
        log.error("Weather fetch failed: %s", exc)
        return None


# -- WMO weather code mapping -------------------------------------------------
# Full spec: https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM

def _wmo_summary(code):
    if code == 0:               return "Clear Sky"
    if code in (1, 2, 3):       return "Partly Cloudy"
    if code in (45, 48):        return "Foggy"
    if code in (51, 53, 55):    return "Drizzle"
    if code in (61, 63, 65):    return "Rain"
    if code in (80, 81, 82):    return "Showers"
    if code >= 95:              return "Thunderstorm"
    return "Unknown"


def _wmo_icon(code):
    if code == 0:               return "clear"
    if code in (1, 2):          return "cloudy_sun"
    if code == 3:               return "cloudy"
    if code in (45, 48):        return "cloudy_wind"
    if code in (51, 53, 55):    return "drizzle"
    if code in (61, 63, 65, 80, 81, 82): return "rain"
    if code >= 95:              return "thunder"
    return "cloudy"