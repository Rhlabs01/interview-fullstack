import threading
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import ai
from app.config import get_settings
from app.database import get_db
from app.models import AIJob, Clinician, Patient, Wound, WoundAssessment
from app.schemas import (
    AIJobOut,
    WoundAssessmentOut,
    WoundDetail,
    WoundListItem,
    WoundOut,
)

router = APIRouter()


def _kick_assessment(wound_id: str, job_id: str) -> None:
    """Trigger the assessment for a freshly created wound.

    Runs on its own thread so wound creation returns immediately; the UI polls
    ``GET /api/jobs/{job_id}`` for the outcome.
    """
    base_url = get_settings().app_base_url
    try:
        httpx.post(
            f"{base_url}/api/wounds/{wound_id}/assess",
            json={"job_id": job_id},
            timeout=None,
        )
    except Exception:
        pass


@router.get("/patients/{patient_id}/wounds")
def list_wounds(patient_id: str, db: Session = Depends(get_db)):
    try:
        rows = (
            db.query(Wound, Clinician.name)
            .outerjoin(Clinician, Wound.clinician_id == Clinician.id)
            .filter(Wound.patient_id == patient_id)
            .order_by(Wound.created_at.desc())
            .all()
        )
        wounds = []
        for wound, clinician_name in rows:
            item = WoundListItem.model_validate(wound)
            item.clinician_name = clinician_name
            item.assessment_count = (
                db.query(WoundAssessment)
                .filter(WoundAssessment.wound_id == wound.id)
                .count()
            )
            wounds.append(item.model_dump(mode="json"))
        return {"wounds": wounds}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.post("/patients/{patient_id}/wounds")
async def create_wound(patient_id: str, request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        clinician_id = body.get("clinician_id")
        location = body.get("location")
        wound_type = body.get("wound_type")
        if not clinician_id or not location or not wound_type:
            return JSONResponse(
                {"error": "clinician_id, location, and wound_type are required"},
                status_code=400,
            )

        wound = Wound(
            id=str(uuid4()),
            patient_id=patient_id,
            clinician_id=clinician_id,
            location=location,
            wound_type=wound_type,
            description=body.get("description") or "",
            image_data=body.get("image_data"),
        )
        db.add(wound)
        db.commit()

        job = AIJob(
            id=str(uuid4()),
            wound_id=wound.id,
            job_type="wound_assessment",
            status="pending",
        )
        db.add(job)
        db.commit()
        db.refresh(wound)

        threading.Thread(
            target=_kick_assessment, args=(wound.id, job.id), daemon=True
        ).start()

        return JSONResponse(
            {
                "wound": WoundOut.model_validate(wound).model_dump(mode="json"),
                "job_id": job.id,
            },
            status_code=201,
        )
    except Exception as exc:
        db.rollback()
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.get("/wounds/{wound_id}")
def get_wound(wound_id: str, db: Session = Depends(get_db)):
    try:
        wound = db.get(Wound, wound_id)
        if wound is None:
            return JSONResponse({"error": "Wound not found"}, status_code=404)
        patient = db.get(Patient, wound.patient_id) if wound.patient_id else None
        clinician = db.get(Clinician, wound.clinician_id) if wound.clinician_id else None

        assessments = (
            db.query(WoundAssessment)
            .filter(WoundAssessment.wound_id == wound_id)
            .order_by(WoundAssessment.created_at.desc())
            .all()
        )
        jobs = (
            db.query(AIJob)
            .filter(AIJob.wound_id == wound_id)
            .order_by(AIJob.created_at.desc())
            .all()
        )

        payload = WoundDetail.model_validate(wound)
        payload.patient_name = patient.name if patient else None
        payload.patient_mrn = patient.mrn if patient else None
        payload.clinician_name = clinician.name if clinician else None
        return {
            "wound": payload.model_dump(mode="json"),
            "assessments": [
                WoundAssessmentOut.model_validate(row).model_dump(mode="json")
                for row in assessments
            ],
            "jobs": [AIJobOut.model_validate(row).model_dump(mode="json") for row in jobs],
        }
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.put("/wounds/{wound_id}")
async def update_wound(wound_id: str, request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        values: dict = {"version": Wound.version + 1, "updated_at": func.now()}
        if body.get("status") is not None:
            values["status"] = body["status"]
        if body.get("description") is not None:
            values["description"] = body["description"]

        # Optimistic locking: only apply the update if the client's version
        # matches what is in the database.
        db.query(Wound).filter(
            Wound.id == wound_id, Wound.version == body.get("version")
        ).update(values)
        db.commit()

        wound = db.get(Wound, wound_id)
        if wound is None:
            return JSONResponse({"error": "Wound not found"}, status_code=404)
        return {"wound": WoundOut.model_validate(wound).model_dump(mode="json")}
    except Exception as exc:
        db.rollback()
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.post("/wounds/{wound_id}/assess")
async def assess_wound(wound_id: str, request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        job = (
            db.query(AIJob)
            .filter(AIJob.id == body.get("job_id"), AIJob.status == "pending")
            .first()
        )
        if job is None:
            return JSONResponse(
                {"error": "Job not found or already processed"}, status_code=404
            )

        result = ai.analyze_wound(db, wound_id, job.id)
        return {"success": True, "result": result}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    try:
        job = db.get(AIJob, job_id)
        if job is None:
            return JSONResponse({"error": "Job not found"}, status_code=404)
        return {"job": AIJobOut.model_validate(job).model_dump(mode="json")}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
