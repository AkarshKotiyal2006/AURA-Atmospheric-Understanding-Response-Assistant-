import os
import requests
from .demo_data import SCENARIOS
from ..state import state

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
DEFAULT_LAT = float(os.getenv("AURA_DEFAULT_LAT", "28.4744"))
DEFAULT_LON = float(os.getenv("AURA_DEFAULT_LON", "77.5040"))


def _fetch_live_weather():
    """Attempt a real OpenWeatherMap call. Returns None on any failure so the
    caller can fall back to demo data transparently."""
    if not OPENWEATHER_API_KEY:
        return None
    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": DEFAULT_LAT, "lon": DEFAULT_LON, "appid": OPENWEATHER_API_KEY, "units": "metric"},
            timeout=4,
        )
        resp.raise_for_status()
        data = resp.json()
        rainfall = data.get("rain", {}).get("1h", 0.0)
        return dict(
            source="LIVE",
            temperature_c=data["main"]["temp"],
            humidity_pct=data["main"]["humidity"],
            wind_kmh=round(data["wind"]["speed"] * 3.6, 1),
            rainfall_mm=rainfall,
            rainfall_forecast_mm=rainfall * 1.4,
            aqi=None, pm25=None, pm10=None,  # AQI needs a second endpoint; demo-fills below if missing
            description=data.get("weather", [{}])[0].get("description", "live conditions"),
        )
    except Exception:
        return None


def get_current_weather():
    """Returns the current atmospheric snapshot plus whether it is LIVE or DEMO data."""
    # NORMAL may use live weather; explicit demo scenarios always use their
    # deterministic scenario data so the demo switcher remains reliable even
    # when a live API key is configured.
    live = None if state.scenario != "NORMAL" else _fetch_live_weather()
    if live is not None:
        # Fill any fields the free live endpoint doesn't provide with scenario-shaped demo values
        demo_fallback = SCENARIOS["NORMAL"]
        for k in ("aqi", "pm25", "pm10"):
            if live.get(k) is None:
                live[k] = demo_fallback[k]
        weather = live
    else:
        scenario = SCENARIOS[state.scenario]
        weather = dict(scenario)
        weather["source"] = "DEMO"

    # what-if rainfall override always wins, regardless of data source
    if state.rainfall_override_mm is not None:
        weather = dict(weather)
        weather["rainfall_mm"] = state.rainfall_override_mm
        weather["rainfall_forecast_mm"] = max(weather["rainfall_forecast_mm"], state.rainfall_override_mm)

    return weather


def get_forecast():
    """A simple short-range forecast derived from the current snapshot (demo-safe)."""
    current = get_current_weather()
    hours = []
    base_rain = current["rainfall_forecast_mm"]
    for h in (1, 3, 6, 12):
        decay = max(0.35, 1 - h * 0.05)
        hours.append(dict(
            hours_ahead=h,
            rainfall_mm=round(base_rain * decay, 1),
            temperature_c=round(current["temperature_c"] - h * 0.15, 1),
            aqi=max(10, round(current["aqi"] * (1 + (h * 0.01 if current["aqi"] > 150 else -h * 0.01)))),
        ))
    return dict(source=current["source"], generated_from="current_conditions", horizon=hours)
