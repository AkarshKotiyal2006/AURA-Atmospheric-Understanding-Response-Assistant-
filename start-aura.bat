@echo off
setlocal
cd /d "%~dp0"
if not exist .env copy .env.example .env >nul
where docker >nul 2>&1
if errorlevel 1 (
  echo Docker was not found. Install Docker Desktop, then run this file again.
  pause
  exit /b 1
)
echo Starting AURA...
docker compose up --build
