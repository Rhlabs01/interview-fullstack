from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import rxnorm, rxnorm_bulk
from app.database import SessionLocal, get_db
from app.models import Medication
from app.schemas import (
    MedicationImportRequest,
    MedicationOut,
    MedicationScrapeRequest,
    MedicationScrapeResult,
    MedicationScrapeSummary,
)

router = APIRouter()

DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000


def _to_out(row: Medication) -> dict:
    return MedicationOut(**rxnorm.medication_to_info(row).to_dict()).model_dump()


@router.get("/medications")
def list_medications(
    db: Session = Depends(get_db),
    search: str | None = None,
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
):
    """Search and page through the RxNorm reference catalog.

    The catalog can hold the full RxNorm ingredient set (~15k concepts), so this
    is paginated. ``total`` is the number of rows matching ``search``, not the
    size of the page.
    """
    try:
        query = db.query(Medication)
        if search:
            term = f"%{search.strip().lower()}%"
            query = query.filter(
                func.lower(Medication.name).like(term)
                | func.lower(Medication.brand_names).like(term)
            )

        total = query.count()
        rows = (
            query.order_by(Medication.name).limit(limit).offset(offset).all()
        )
        return {
            "medications": [_to_out(row) for row in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.post("/medications/scrape")
def scrape_medications(
    payload: MedicationScrapeRequest | None = None,
    db: Session = Depends(get_db),
):
    """Resolve specific medication names against RxNav and upsert them.

    Use this to add a handful of concepts. Building the whole catalog goes
    through ``POST /api/medications/import`` instead — this path costs several
    requests per name and does not scale to thousands.

    With no ``names`` in the body, every concept already in the catalog is
    refreshed in place. Names RxNav cannot resolve are reported as ``not_found``
    rather than failing the request.
    """
    try:
        requested = [
            name.strip()
            for name in (payload.names if payload else None) or []
            if name.strip()
        ]
        if not requested:
            requested = [
                row.name
                for row in db.query(Medication).order_by(Medication.name).all()
            ]

        summary = MedicationScrapeSummary()
        for name, info in zip(requested, rxnorm.scrape_concepts(requested)):
            if info is None:
                summary.not_found += 1
                summary.results.append(
                    MedicationScrapeResult(name=name, status="not_found")
                )
                continue

            created = rxnorm.upsert_medication(db, info)
            if created:
                summary.created += 1
            else:
                summary.updated += 1
            summary.results.append(
                MedicationScrapeResult(
                    name=name,
                    status="created" if created else "updated",
                    rxcui=info.rxcui,
                )
            )

        db.commit()
        return {"scrape": summary.model_dump()}
    except Exception as exc:
        db.rollback()
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.post("/medications/import")
def start_medication_import(payload: MedicationImportRequest | None = None):
    """Start a full RxNorm catalog import in the background.

    Returns immediately; poll ``GET /api/medications/import`` for progress. A
    full import is ~15k concepts and takes a couple of minutes, so it cannot be
    served synchronously.
    """
    request = payload or MedicationImportRequest()
    if request.scope not in rxnorm_bulk.SCOPES:
        return JSONResponse(
            {"error": f"scope must be one of {sorted(rxnorm_bulk.SCOPES)}"},
            status_code=400,
        )

    started, job = rxnorm_bulk.start_import(
        SessionLocal,
        scope=request.scope,
        include_classes=request.include_classes,
        include_brands=request.include_brands,
        limit=request.limit,
    )
    if not started:
        return JSONResponse(
            {"error": "An import is already running", "job": job.to_dict()},
            status_code=409,
        )
    return {"job": job.to_dict()}


@router.get("/medications/import")
def medication_import_status():
    """Progress of the current or most recent catalog import."""
    return {"job": rxnorm_bulk.get_job().to_dict()}


@router.get("/medications/{rxcui}")
def get_medication(rxcui: str, db: Session = Depends(get_db)):
    try:
        row = db.get(Medication, rxcui)
        if row is None:
            return JSONResponse({"error": "Medication not found"}, status_code=404)
        return {"medication": _to_out(row)}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.get("/rxnorm/lookup")
def rxnorm_lookup(name: str, db: Session = Depends(get_db)):
    """Resolve a medication name to structured RxNorm data.

    Exact / case-insensitive match against the local catalog first, then the
    live RxNav API. This does NOT do fuzzy matching (see EXERCISE.md).
    """
    try:
        info = rxnorm.lookup(db, name)
        if info is None:
            return JSONResponse(
                {"error": f"No RxNorm concept found for '{name}'"},
                status_code=404,
            )
        return {"medication": MedicationOut(**info.to_dict()).model_dump()}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
