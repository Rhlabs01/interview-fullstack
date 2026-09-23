from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.config import get_settings
from app.routers import (
    analysis,
    clinicians,
    health,
    medications,
    patients,
    seed,
    visits,
)

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Visit Tracker")

settings = get_settings()
origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(seed.router, prefix="/api")
app.include_router(clinicians.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(visits.router, prefix="/api")
app.include_router(medications.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")


@app.get("/{full_path:path}")
def spa(full_path: str):
    if full_path == "api" or full_path.startswith("api/"):
        return JSONResponse({"error": "Not found"}, status_code=404)

    index = STATIC_DIR / "index.html"
    if not index.exists():
        return JSONResponse({"error": "Not found"}, status_code=404)

    candidate = STATIC_DIR / full_path
    if full_path and candidate.is_file():
        return FileResponse(candidate)
    return FileResponse(index)
