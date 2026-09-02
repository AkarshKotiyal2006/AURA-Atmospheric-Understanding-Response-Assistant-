from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .database import Base, engine, SessionLocal
from .models_db import User, Zone, VulnerabilityAsset
from .services.demo_data import ZONES, VULNERABILITY_ASSETS
from .api.routes import router

app = FastAPI(title="AURA - Atmospheric Understanding & Response Assistant", version="1.1.0")

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_if_empty():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(User(name="AURA Demo User", role="citizen"))
            db.commit()
        if db.query(Zone).count() == 0:
            for z in ZONES:
                db.add(Zone(**z))
            db.commit()
        if db.query(VulnerabilityAsset).count() == 0:
            for a in VULNERABILITY_ASSETS:
                db.add(VulnerabilityAsset(**a))
            db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    seed_if_empty()


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AURA backend"}


app.include_router(router)
