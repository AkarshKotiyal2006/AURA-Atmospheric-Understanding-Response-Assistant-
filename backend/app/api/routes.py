import re
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models_db import User, Zone, VulnerabilityAsset, CommunityReport, Prediction, ActualEvent
from ..schemas import ReportIn, SimulationIn, FeedbackIn, AssistantIn, DemoScenarioIn
from ..services import zone_service, clustering, assistant as assistant_service
from ..services.weather_service import get_current_weather, get_forecast
from ..services.demo_data import SCENARIOS
from ..services.clustering import haversine_m
from ..state import state

router = APIRouter(prefix="/api")


def _nearest_zone(db: Session, lat: float, lon: float) -> Zone:
    zones = db.query(Zone).all()
    return min(zones, key=lambda z: haversine_m(z.lat, z.lon, lat, lon))


def _all_zone_risks(db: Session):
    weather = get_current_weather()
    zones = db.query(Zone).all()
    return [zone_service.compute_zone_risk(db, z, weather) for z in zones], weather


def _log_predictions(db: Session, zone_risks: list, scenario: str):
    for zr in zone_risks:
        hazard = zr[zr["top_hazard"]]
        if hazard["severity"] in ("HIGH", "CRITICAL"):
            db.add(Prediction(zone_id=zr["zone_id"], hazard=hazard["hazard"],
                               severity=hazard["severity"], score=hazard["score"], scenario=scenario))
    db.commit()


# ---------- Weather ----------
@router.get("/weather")
def weather():
    return get_current_weather()


@router.get("/forecast")
def forecast():
    return get_forecast()


# ---------- Risks / Zones ----------
@router.get("/risks")
def risks(db: Session = Depends(get_db)):
    zone_risks, weather = _all_zone_risks(db)
    top = max(zone_risks, key=lambda z: z["overall_score"])
    return dict(
        data_source=weather["source"],
        top_risk=dict(hazard=top["top_hazard"], severity=top["overall_severity"],
                       score=top["overall_score"], zone=top["zone_name"], confidence=top["confidence"]),
        zones=zone_risks,
    )


@router.get("/zones")
def zones(db: Session = Depends(get_db)):
    zone_risks, weather = _all_zone_risks(db)
    return dict(data_source=weather["source"], zones=zone_risks)


@router.get("/map")
def map_data(db: Session = Depends(get_db)):
    zone_risks, weather = _all_zone_risks(db)
    assets = db.query(VulnerabilityAsset).all()
    reports = db.query(CommunityReport).all()
    incidents = clustering.cluster_reports([
        dict(id=r.id, incident_type=r.incident_type, lat=r.lat, lon=r.lon,
             created_at=r.created_at, zone_id=r.zone_id, zone_name=r.zone.name if r.zone else r.zone_id)
        for r in reports
    ])
    return dict(
        data_source=weather["source"],
        zones=[dict(zone_id=z["zone_id"], name=z["zone_name"], lat=z["lat"], lon=z["lon"],
                     radius_m=z["radius_m"], flood_score=z["flood"]["score"], heat_score=z["heat"]["score"],
                     aqi_score=z["aqi"]["score"], overall_score=z["overall_score"],
                     overall_severity=z["overall_severity"], top_hazard=z["top_hazard"],
                     confidence=z["confidence"]) for z in zone_risks],
        vulnerability_assets=[dict(id=a.id, zone_id=a.zone_id, name=a.name, type=a.type,
                                     lat=a.lat, lon=a.lon, exposure_note=a.exposure_note) for a in assets],
        community_incidents=incidents,
    )


@router.get("/vulnerability")
def vulnerability(db: Session = Depends(get_db)):
    assets = db.query(VulnerabilityAsset).all()
    zone_risks, _ = _all_zone_risks(db)
    risk_by_zone = {z["zone_id"]: z["overall_severity"] for z in zone_risks}
    return dict(assets=[
        dict(id=a.id, zone_id=a.zone_id, zone_risk=risk_by_zone.get(a.zone_id, "LOW"),
             name=a.name, type=a.type, lat=a.lat, lon=a.lon, exposure_note=a.exposure_note)
        for a in assets
    ])


@router.get("/alerts")
def alerts(db: Session = Depends(get_db)):
    zone_risks, weather = _all_zone_risks(db)
    active = [z for z in zone_risks if z["overall_severity"] in ("HIGH", "CRITICAL")]
    result = []
    for z in active:
        top = z[z["top_hazard"]]
        result.append(dict(
            zone_id=z["zone_id"], zone_name=z["zone_name"], hazard=top["hazard"],
            severity=top["severity"], score=top["score"], confidence=z["confidence"],
            factors=top["factors"], potential_impact=z["potential_impact"],
            messages=zone_service.adaptive_alert_messages(z),
        ))
    return dict(data_source=weather["source"], count=len(result), alerts=result)


# ---------- Community reporting ----------
@router.post("/reports")
def create_report(payload: ReportIn, db: Session = Depends(get_db)):
    zone = _nearest_zone(db, payload.lat, payload.lon)
    report = CommunityReport(zone_id=zone.id, incident_type=payload.incident_type,
                              text=payload.text, photo_url=payload.photo_url,
                              lat=payload.lat, lon=payload.lon)
    db.add(report)
    db.commit()
    db.refresh(report)
    return dict(id=report.id, zone_id=zone.id, zone_name=zone.name, incident_type=report.incident_type,
                created_at=report.created_at.isoformat())


@router.post("/reports/upload")
async def create_report_with_photo(
    incident_type: str = Form(...),
    text: str = Form(""),
    lat: float = Form(...),
    lon: float = Form(...),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    """Create a community report and optionally persist a photo in backend/uploads."""
    zone = _nearest_zone(db, lat, lon)
    photo_url = None
    if photo and photo.filename:
        allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        if photo.content_type not in allowed:
            raise HTTPException(status_code=400, detail="Photo must be JPG, PNG, WEBP, or GIF")
        data = await photo.read()
        if len(data) > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Photo must be 5 MB or smaller")
        suffix = Path(photo.filename).suffix.lower() or ".jpg"
        filename = f"{uuid.uuid4().hex}{suffix}"
        upload_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        (upload_dir / filename).write_bytes(data)
        photo_url = f"/uploads/{filename}"

    demo_user = db.query(User).order_by(User.id.asc()).first()
    report = CommunityReport(
        user_id=demo_user.id if demo_user else None,
        zone_id=zone.id,
        incident_type=incident_type,
        text=text,
        photo_url=photo_url,
        lat=lat,
        lon=lon,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return dict(
        id=report.id, zone_id=zone.id, zone_name=zone.name,
        incident_type=report.incident_type, photo_url=photo_url,
        created_at=report.created_at.isoformat(),
    )


@router.get("/incidents")
def incidents(db: Session = Depends(get_db)):
    reports = db.query(CommunityReport).all()
    clustered = clustering.cluster_reports([
        dict(id=r.id, incident_type=r.incident_type, lat=r.lat, lon=r.lon,
             created_at=r.created_at, zone_id=r.zone_id, zone_name=r.zone.name if r.zone else r.zone_id)
        for r in reports
    ])
    return dict(count=len(clustered), incidents=clustered)


# ---------- What-if simulation ----------
@router.post("/simulation")
def run_simulation(payload: SimulationIn, db: Session = Depends(get_db)):
    state.set_rainfall_override(payload.rainfall_mm)
    zone_risks, weather = _all_zone_risks(db)
    _log_predictions(db, zone_risks, f"SIMULATION_{payload.rainfall_mm}mm")
    top = max(zone_risks, key=lambda z: z["overall_score"])
    return dict(
        rainfall_mm=payload.rainfall_mm,
        data_source=weather["source"],
        top_risk=dict(hazard=top["top_hazard"], severity=top["overall_severity"], score=top["overall_score"]),
        zones=zone_risks,
    )


# ---------- Prediction vs reality ----------
@router.get("/feedback")
def feedback_metrics(db: Session = Depends(get_db)):
    predictions = db.query(Prediction).all()
    events = db.query(ActualEvent).all()
    matched_ids = {e.prediction_id for e in events if e.prediction_id}
    false_alarm_ids = {e.prediction_id for e in events if e.prediction_id and not e.occurred}

    true_positive = sum(1 for e in events if e.occurred and e.prediction_id)
    false_positive = len(false_alarm_ids)
    false_negative = sum(1 for e in events if e.occurred and not e.prediction_id)
    unverified_predictions = len([p for p in predictions if p.id not in matched_ids])
    total_confirmed_positive = true_positive + false_negative

    precision = round(true_positive / (true_positive + false_positive), 2) if (true_positive + false_positive) else None
    recall = round(true_positive / total_confirmed_positive, 2) if total_confirmed_positive else None
    false_alarm_rate = round(false_positive / len(predictions), 2) if predictions else None

    return dict(
        note="Demo evaluation data - based on simulated/community-confirmed events, not verified ground-truth records.",
        total_predictions=len(predictions),
        total_actual_events=len(events),
        true_positive_detections=true_positive,
        false_alarms=false_positive,
        missed_events=false_negative,
        unverified_predictions=unverified_predictions,
        precision=precision, recall=recall, false_alarm_rate=false_alarm_rate,
        recent_predictions=[dict(zone_id=p.zone_id, hazard=p.hazard, severity=p.severity,
                                   score=p.score, scenario=p.scenario, created_at=p.created_at.isoformat())
                              for p in predictions[-10:]],
    )


@router.post("/feedback")
def submit_feedback(payload: FeedbackIn, db: Session = Depends(get_db)):
    latest_prediction = (db.query(Prediction)
                          .filter(Prediction.zone_id == payload.zone_id, Prediction.hazard == payload.hazard)
                          .order_by(Prediction.created_at.desc()).first())
    event = ActualEvent(prediction_id=latest_prediction.id if latest_prediction else None,
                         zone_id=payload.zone_id, hazard=payload.hazard,
                         occurred=payload.occurred, notes=payload.notes)
    db.add(event)
    db.commit()
    outcome = "no_prior_prediction"
    if latest_prediction:
        outcome = "successful_detection" if payload.occurred else "false_alarm"
    elif payload.occurred:
        outcome = "missed_event"
    return dict(recorded=True, matched_prediction_id=latest_prediction.id if latest_prediction else None, outcome=outcome)


@router.get("/predictions")
def predictions(db: Session = Depends(get_db)):
    preds = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(50).all()
    return dict(predictions=[dict(id=p.id, zone_id=p.zone_id, hazard=p.hazard, severity=p.severity,
                                    score=p.score, scenario=p.scenario, created_at=p.created_at.isoformat())
                               for p in preds])


# ---------- Assistant ----------
@router.post("/assistant")
def ask_assistant(payload: AssistantIn, db: Session = Depends(get_db)):
    zone_risks, weather = _all_zone_risks(db)
    active_alerts = alerts(db)["alerts"]

    # The assistant can answer what-if rainfall questions without mutating
    # global simulator state: calculate a temporary, evidence-backed view.
    simulation_zones = None
    match = re.search(r"(\d+(?:\.\d+)?)\s*mm", payload.question.lower())
    if match and any(term in payload.question.lower() for term in ("rain", "rainfall", "what if", "what happens")):
        rainfall_mm = float(match.group(1))
        simulated_weather = dict(weather)
        simulated_weather["rainfall_mm"] = rainfall_mm
        simulated_weather["rainfall_forecast_mm"] = max(weather["rainfall_forecast_mm"], rainfall_mm)
        simulation_zones = [
            zone_service.compute_zone_risk(db, z, simulated_weather)
            for z in db.query(Zone).all()
        ]

    reply = assistant_service.answer(
        payload.question, zone_risks, weather, active_alerts, simulation_zones=simulation_zones
    )
    return dict(question=payload.question, answer=reply)


# ---------- Demo mode ----------
@router.get("/demo")
def get_demo(db: Session = Depends(get_db)):
    return dict(current=state.scenario, available=list(SCENARIOS.keys()),
                descriptions={k: v["description"] for k, v in SCENARIOS.items()})


@router.post("/demo")
def set_demo(payload: DemoScenarioIn, db: Session = Depends(get_db)):
    if payload.scenario not in SCENARIOS:
        raise HTTPException(status_code=400, detail="Unknown scenario")
    state.set_scenario(payload.scenario)
    zone_risks, weather = _all_zone_risks(db)
    _log_predictions(db, zone_risks, payload.scenario)
    return dict(scenario=state.scenario, data_source=weather["source"], zones_updated=len(zone_risks))
