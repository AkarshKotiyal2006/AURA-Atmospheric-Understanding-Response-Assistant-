"""
Risk Fusion Engine.

Every score is a transparent weighted combination of named factors so the
explainability layer can report exactly why a score is what it is. Nothing
here is a fixed constant score - every score is a function of current inputs.
"""


def _clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))


def _severity(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 40:
        return "MODERATE"
    return "LOW"


def severity_label(score: float) -> str:
    return _severity(score)


def flood_risk(weather: dict, zone: dict, community_report_count: int):
    rainfall_now = weather["rainfall_mm"] * zone["rainfall_multiplier"]
    rainfall_forecast = weather["rainfall_forecast_mm"] * zone["rainfall_multiplier"]
    rainfall_intensity = max(rainfall_now, rainfall_forecast * 0.7)

    rainfall_norm = _clamp(rainfall_intensity / 100 * 100, 0, 100) / 100          # 0-1, 100mm -> saturated
    elevation_norm = _clamp((zone["elevation_m"] - 195) / (210 - 195) * 100, 0, 100) / 100  # higher elevation -> safer
    drainage = zone["drainage_vulnerability"]                                      # 0-1
    historical = zone["historical_waterlogging"]                                   # 0-1
    community_norm = min(community_report_count / 5, 1.0)                          # 5+ reports saturates

    score = _clamp(
        40 * rainfall_norm +
        20 * (1 - elevation_norm) +
        20 * drainage +
        10 * historical +
        10 * community_norm
    )

    factors = []
    factors.append(f"{round(rainfall_now,1)} mm rainfall now / {round(rainfall_forecast,1)} mm forecast in {zone['name']}")
    factors.append(f"Elevation {zone['elevation_m']}m ({'low-lying' if elevation_norm < 0.4 else 'moderate elevation' if elevation_norm < 0.7 else 'higher ground'})")
    factors.append(f"Drainage vulnerability {round(drainage*100)}%")
    if historical > 0.3:
        factors.append(f"Historical waterlogging record {round(historical*100)}%")
    if community_report_count > 0:
        factors.append(f"{community_report_count} nearby community report(s)")

    return dict(hazard="flood", score=round(score, 1), severity=_severity(score), factors=factors,
                signals={"rainfall_norm": rainfall_norm, "elevation_norm": elevation_norm,
                         "drainage": drainage, "historical": historical, "community_norm": community_norm})


def heat_risk(weather: dict, zone: dict):
    t = weather["temperature_c"]
    rh = weather["humidity_pct"]
    wind = weather["wind_kmh"]

    # Simplified heat-index style combination (Celsius, bounded 20-50C practical demo range)
    heat_index = t + 0.05 * rh - 0.03 * wind
    temp_norm = _clamp((t - 25) / (46 - 25) * 100, 0, 100) / 100
    humidity_penalty = _clamp((rh - 30) / (95 - 30) * 100, 0, 100) / 100
    wind_relief = _clamp(wind / 40 * 100, 0, 100) / 100

    score = _clamp(65 * temp_norm + 30 * humidity_penalty - 15 * wind_relief)

    density_bonus = {"high": 8, "medium": 3, "low": 0}[zone["density"]]
    score = _clamp(score + density_bonus)

    factors = [
        f"Temperature {t}\u00b0C, humidity {rh}%",
        f"Approximate heat index {round(heat_index,1)}\u00b0C",
        f"Wind {wind} km/h ({'limited cooling effect' if wind_relief < 0.3 else 'some cooling relief'})",
    ]
    if density_bonus:
        factors.append(f"{zone['density'].title()}-density area increases heat exposure for residents")

    return dict(hazard="heat", score=round(score, 1), severity=_severity(score), factors=factors,
                signals={"temp_norm": temp_norm, "humidity_penalty": humidity_penalty, "wind_relief": wind_relief})


def aqi_risk(weather: dict, zone: dict):
    aqi = weather["aqi"]
    pm25 = weather["pm25"]
    pm10 = weather["pm10"]
    wind = weather["wind_kmh"]

    aqi_norm = _clamp(aqi / 400 * 100, 0, 100) / 100
    pm25_norm = _clamp(pm25 / 250 * 100, 0, 100) / 100
    pm10_norm = _clamp(pm10 / 430 * 100, 0, 100) / 100
    dispersal_bonus = _clamp(wind / 40 * 100, 0, 100) / 100  # higher wind disperses pollutants

    score = _clamp(55 * aqi_norm + 25 * pm25_norm + 20 * pm10_norm - 15 * dispersal_bonus)

    factors = [f"AQI {round(aqi)} (PM2.5 {round(pm25)} \u00b5g/m\u00b3, PM10 {round(pm10)} \u00b5g/m\u00b3)"]
    if dispersal_bonus > 0.3:
        factors.append(f"Wind {wind} km/h helping disperse pollutants")
    else:
        factors.append(f"Low wind ({wind} km/h) allowing pollutants to accumulate")

    return dict(hazard="aqi", score=round(score, 1), severity=_severity(score), factors=factors,
                signals={"aqi_norm": aqi_norm, "pm25_norm": pm25_norm, "pm10_norm": pm10_norm, "dispersal_bonus": dispersal_bonus})


def forecast_confidence(weather_source: str, hazard_results: list, community_report_count: int):
    """Honest, formula-based confidence estimate - not a black box."""
    base = 55
    completeness_bonus = 15 if weather_source == "LIVE" else 10  # demo data is internally consistent but not live-verified
    signal_bonus = sum(1 for h in hazard_results if len(h["factors"]) >= 3) * 5
    community_bonus = min(community_report_count * 3, 15)
    confidence = _clamp(base + completeness_bonus + signal_bonus + community_bonus, 30, 97)
    return round(confidence)
