# AURA — Atmospheric Understanding & Response Assistant

A hyperlocal weather-risk intelligence and decision-support prototype (SIH 2026 concept), covering flood/heat/AQI risk fusion, an interactive risk map, community reporting with incident clustering, adaptive alerts, forecast confidence, a what-if rainfall simulator, prediction-vs-reality evaluation, and a grounded (no-hallucination) AURA Assistant.

## Run it

### Windows
1. Install Docker Desktop and make sure it is running.
2. Extract this folder.
3. Double-click `start-aura.bat`, or run:

```powershell
copy .env.example .env
docker compose up --build
```

### macOS / Linux
```bash
cp .env.example .env
./start-aura.sh
```

Or directly:
```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000 (docs at /docs)
- Postgres: localhost:5432

The app works immediately with **no API key** — it automatically falls back to realistic demo data and labels itself `DEMO DATA` in the UI. In `NORMAL`, if `OPENWEATHER_API_KEY` is set, AURA attempts live weather and falls back to demo on failure. The explicit FLOOD / HEAT / AQI / STORM scenarios intentionally use deterministic demo conditions so the demo switcher always behaves predictably.

## What to try

1. Switch **scenarios** (NORMAL / FLOOD / HEAT / AQI / STORM) in the top bar — every risk score, the map, alerts, and the assistant update. NORMAL uses live weather when an API key is configured; the other scenarios intentionally use deterministic demo conditions.
2. Click zones on the **map** or in the zone grid to see the WHY explanation and contributing factors.
3. Drag the **What-If Rainfall Simulator** and run it — flood scores and affected zones recalculate live.
4. Switch **"View as"** (Citizen / Commuter / Resident / Authority) — alert wording changes per audience.
5. Submit a **community report** with text, photo, and coordinates (or use browser geolocation) — it's stored in Postgres, assigned to the nearest zone, and clustered with nearby reports into an incident.
6. Ask the **AURA Assistant** questions like "What is the biggest risk right now?" or "Why is Pari Chowk high risk?" — it only answers from live application data and says so when it can't.
7. Log an actual event in the **Prediction vs Reality** panel to see precision/recall/false-alarm metrics update.

## Architecture

```
frontend/   React + Tailwind + Leaflet (Vite dev server)
backend/    FastAPI + SQLAlchemy (Postgres in Docker, SQLite fallback for local dev without Docker)
docker-compose.yml   aura-frontend, aura-backend, aura-postgres
```

Backend service layout: `services/weather_service.py` (live/demo abstraction), `services/risk_engine.py` (flood/heat/AQI scoring + confidence), `services/zone_service.py` (zone aggregation, impact chains, adaptive messages), `services/clustering.py` (report clustering), `services/assistant.py` (grounded Q&A), `services/demo_data.py` (seed zones/assets/scenarios).

## Known limitations (prototype scope)

- Live weather integration covers current conditions only; AQI/PM figures fall back to demo-shaped values unless you wire in a second AQI provider.
- Forecast confidence is an explicit, documented formula (data completeness + signal count + community evidence), not a calibrated statistical model — labeled honestly in the UI/API rather than presented as a black box.
- Zone boundaries are circular approximations for the demo, not real administrative/GIS polygons.
- This was built and code-reviewed in an offline sandbox without network access, so `docker compose up --build` has not been executed end-to-end here — test it in your own environment and open an issue in the code if anything doesn't come up cleanly.
