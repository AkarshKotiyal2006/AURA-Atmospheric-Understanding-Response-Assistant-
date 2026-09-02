import datetime as dt
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="citizen")
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    reports = relationship("CommunityReport", back_populates="user")


class Zone(Base):
    __tablename__ = "zones"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    radius_m = Column(Integer, default=900)
    elevation_m = Column(Float, nullable=False)
    drainage_vulnerability = Column(Float, nullable=False)   # 0-1
    historical_waterlogging = Column(Float, nullable=False)  # 0-1
    density = Column(String, default="medium")               # low/medium/high
    rainfall_multiplier = Column(Float, default=1.0)

    reports = relationship("CommunityReport", back_populates="zone")


class VulnerabilityAsset(Base):
    __tablename__ = "vulnerability_assets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(String, ForeignKey("zones.id"))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # hospital, school, road, transit, residential
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    exposure_note = Column(String, default="")


class CommunityReport(Base):
    __tablename__ = "community_reports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    zone_id = Column(String, ForeignKey("zones.id"))
    incident_type = Column(String, nullable=False)
    text = Column(Text, default="")
    photo_url = Column(String, nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    zone = relationship("Zone", back_populates="reports")
    user = relationship("User", back_populates="reports")


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(String, ForeignKey("zones.id"))
    hazard = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    scenario = Column(String, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    events = relationship("ActualEvent", back_populates="prediction")


class ActualEvent(Base):
    __tablename__ = "actual_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    zone_id = Column(String, ForeignKey("zones.id"))
    hazard = Column(String, nullable=False)
    occurred = Column(Boolean, nullable=False)
    notes = Column(String, default="")
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    prediction = relationship("Prediction", back_populates="events")


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(String, ForeignKey("zones.id"))
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
