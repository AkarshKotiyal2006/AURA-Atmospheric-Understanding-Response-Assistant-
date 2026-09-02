# Realistic demo GIS + weather-scenario data for the Greater Noida pilot area.
# All values are synthetic but structured to behave like plausible real data.

ZONES = [
    dict(id="z1", name="Pari Chowk", lat=28.4712, lon=77.5040, radius_m=1100,
         elevation_m=200.5, drainage_vulnerability=0.72, historical_waterlogging=0.65,
         density="high", rainfall_multiplier=1.05),
    dict(id="z2", name="Knowledge Park III", lat=28.4595, lon=77.4930, radius_m=1000,
         elevation_m=203.8, drainage_vulnerability=0.35, historical_waterlogging=0.20,
         density="medium", rainfall_multiplier=0.95),
    dict(id="z3", name="Surajpur Industrial Area", lat=28.4880, lon=77.5240, radius_m=1300,
         elevation_m=198.2, drainage_vulnerability=0.81, historical_waterlogging=0.78,
         density="medium", rainfall_multiplier=1.15),
    dict(id="z4", name="Ecotech Zone I", lat=28.4460, lon=77.4700, radius_m=1000,
         elevation_m=205.1, drainage_vulnerability=0.28, historical_waterlogging=0.15,
         density="low", rainfall_multiplier=0.9),
    dict(id="z5", name="Chi-V Residential Sector", lat=28.4790, lon=77.4880, radius_m=950,
         elevation_m=201.9, drainage_vulnerability=0.55, historical_waterlogging=0.40,
         density="high", rainfall_multiplier=1.0),
    dict(id="z6", name="Alpha Commercial Belt", lat=28.4630, lon=77.5100, radius_m=900,
         elevation_m=199.4, drainage_vulnerability=0.6, historical_waterlogging=0.5,
         density="high", rainfall_multiplier=1.1),
]

VULNERABILITY_ASSETS = [
    dict(zone_id="z1", name="Pari Chowk District Hospital", type="hospital", lat=28.4720, lon=77.5052,
         exposure_note="Primary emergency facility; access road prone to waterlogging."),
    dict(zone_id="z1", name="Pari Chowk Metro Station", type="transit", lat=28.4708, lon=77.5031,
         exposure_note="Elevated station; approach roads low-lying."),
    dict(zone_id="z2", name="GL Bajaj Institute", type="school", lat=28.4603, lon=77.4918,
         exposure_note="Large student population, single main access road."),
    dict(zone_id="z3", name="Surajpur Community Health Centre", type="hospital", lat=28.4872, lon=77.5228,
         exposure_note="Adjacent to industrial drainage channel."),
    dict(zone_id="z3", name="Surajpur-Kasna Road", type="road", lat=28.4895, lon=77.5260,
         exposure_note="Arterial freight route; historically waterlogs above 60mm rainfall."),
    dict(zone_id="z4", name="Ecotech School of Business", type="school", lat=28.4468, lon=77.4712,
         exposure_note="Newer drainage infrastructure, lower exposure."),
    dict(zone_id="z5", name="Chi-V Government Sr. Secondary School", type="school", lat=28.4798, lon=77.4869,
         exposure_note="Dense residential catchment area."),
    dict(zone_id="z5", name="Chi Sector Residential Cluster", type="residential", lat=28.4785, lon=77.4895,
         exposure_note="High-density housing, ground-floor flooding risk."),
    dict(zone_id="z6", name="Alpha I Market Road", type="road", lat=28.4635, lon=77.5112,
         exposure_note="Commercial strip; storm drains frequently silted."),
    dict(zone_id="z6", name="Alpha Public Health Centre", type="hospital", lat=28.4622, lon=77.5088,
         exposure_note="Serves dense commercial + residential population."),
]

# Each scenario defines base atmospheric conditions before per-zone variation is applied.
SCENARIOS = {
    "NORMAL": dict(
        label="Normal",
        temperature_c=29.0, humidity_pct=55, wind_kmh=12,
        rainfall_mm=2, rainfall_forecast_mm=5,
        aqi=95, pm25=38, pm10=70,
        description="Typical fair-weather conditions.",
    ),
    "FLOOD": dict(
        label="Flood",
        temperature_c=26.0, humidity_pct=88, wind_kmh=18,
        rainfall_mm=52, rainfall_forecast_mm=78,
        aqi=60, pm25=22, pm10=45,
        description="Intense monsoon rainfall event over Greater Noida.",
    ),
    "HEAT": dict(
        label="Heat",
        temperature_c=44.5, humidity_pct=28, wind_kmh=8,
        rainfall_mm=0, rainfall_forecast_mm=0,
        aqi=110, pm25=55, pm10=95,
        description="Pre-monsoon heatwave with low humidity and weak winds.",
    ),
    "AQI": dict(
        label="AQI",
        temperature_c=22.0, humidity_pct=60, wind_kmh=4,
        rainfall_mm=0, rainfall_forecast_mm=0,
        aqi=310, pm25=210, pm10=340,
        description="Stagnant winter air trapping particulate pollution.",
    ),
    "STORM": dict(
        label="Storm",
        temperature_c=27.5, humidity_pct=82, wind_kmh=55,
        rainfall_mm=38, rainfall_forecast_mm=95,
        aqi=70, pm25=30, pm10=58,
        description="Severe thunderstorm with damaging wind gusts and heavy rain bands.",
    ),
}
