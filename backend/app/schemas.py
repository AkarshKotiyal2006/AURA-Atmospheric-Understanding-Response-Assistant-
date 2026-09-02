from pydantic import BaseModel
from typing import Optional, List


class ReportIn(BaseModel):
    incident_type: str
    text: str = ""
    lat: float
    lon: float
    photo_url: Optional[str] = None


class SimulationIn(BaseModel):
    rainfall_mm: float


class FeedbackIn(BaseModel):
    zone_id: str
    hazard: str
    occurred: bool
    notes: str = ""


class AssistantIn(BaseModel):
    question: str


class DemoScenarioIn(BaseModel):
    scenario: str
