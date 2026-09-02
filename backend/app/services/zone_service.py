from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models_db import Zone, CommunityReport
from . import risk_engine
from .weather_service import get_current_weather
from .demo_data import ZONES


def get_zones_db(db: Session):
    zones = db.query(Zone).all()
    if not zones:
        return []
    return zones


def _report_count_for_zone(db: Session, zone_id: str) -> int:
    return db.query(func.count(CommunityReport.id)).filter(CommunityReport.zone_id == zone_id).scalar() or 0


def compute_zone_risk(db: Session, zone: Zone, weather: dict):
    zone_dict = dict(id=zone.id, name=zone.name, elevation_m=zone.elevation_m,
                      drainage_vulnerability=zone.drainage_vulnerability,
                      historical_waterlogging=zone.historical_waterlogging,
                      density=zone.density, rainfall_multiplier=zone.rainfall_multiplier)
    report_count = _report_count_for_zone(db, zone.id)

    flood = risk_engine.flood_risk(weather, zone_dict, report_count)
    heat = risk_engine.heat_risk(weather, zone_dict)
    aqi = risk_engine.aqi_risk(weather, zone_dict)

    hazards = [flood, heat, aqi]
    top = max(hazards, key=lambda h: h["score"])
    overall_score = round(0.6 * top["score"] + 0.4 * (sum(h["score"] for h in hazards) / 3), 1)
    confidence = risk_engine.forecast_confidence(weather["source"], hazards, report_count)

    return dict(
        zone_id=zone.id,
        zone_name=zone.name,
        lat=zone.lat, lon=zone.lon, radius_m=zone.radius_m,
        flood=flood, heat=heat, aqi=aqi,
        top_hazard=top["hazard"], overall_score=overall_score,
        overall_severity=risk_engine.severity_label(overall_score),
        confidence=confidence,
        community_report_count=report_count,
        potential_impact=build_impact_chain(top, zone.name),
    )


def build_impact_chain(top_hazard: dict, zone_name: str):
    if top_hazard["severity"] in ("LOW",):
        return []
    hazard = top_hazard["hazard"]
    if hazard == "flood":
        chain = ["Heavy/forecast rainfall", "Elevated flood risk", f"Low-lying stretches of {zone_name}",
                 "Potential road waterlogging", "Potential traffic disruption",
                 "Potential emergency-access risk"]
    elif hazard == "heat":
        chain = ["Elevated temperature and humidity", "Rising heat-stress risk", f"Outdoor and high-density areas of {zone_name}",
                 "Potential heat exhaustion risk for vulnerable groups", "Potential strain on local health facilities"]
    else:
        chain = ["Elevated particulate concentration", "Rising AQI risk", f"Exposed population in {zone_name}",
                 "Potential respiratory discomfort", "Potential advisory for outdoor activity"]
    if top_hazard["severity"] == "CRITICAL":
        chain.append("Critical severity - immediate attention recommended")
    return chain


def adaptive_alert_messages(zone_risk: dict):
    hazard = zone_risk["top_hazard"]
    severity = zone_risk["overall_severity"]
    name = zone_risk["zone_name"]
    hazard_label = {"flood": "flooding/waterlogging", "heat": "heat stress", "aqi": "poor air quality"}[hazard]

    return {
        "citizen": f"{severity.title()} risk of {hazard_label} expected near {name}. Stay informed and follow local advisories.",
        "resident": f"{severity.title()} {hazard_label} risk in your area ({name}). Prepare accordingly and avoid exposed low-lying spots." if hazard == "flood"
                    else f"{severity.title()} {hazard_label} risk in {name}. Limit outdoor exposure, especially for children and the elderly.",
        "commuter": f"Your route may pass through a {severity.lower()}-risk zone ({name}) for {hazard_label}. Plan an alternate route if possible.",
        "authority": f"{name} is showing {severity.lower()} {hazard_label} risk (score {zone_risk['overall_score']}/100, confidence {zone_risk['confidence']}%). Recommend monitoring and resource readiness.",
    }
