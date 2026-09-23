from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Clinician, Patient, Visit
from app.schemas import VisitDetail, VisitOut

router = APIRouter()


@router.get("/visits/{visit_id}")
def get_visit(visit_id: str, db: Session = Depends(get_db)):
    try:
        visit = db.get(Visit, visit_id)
        if visit is None:
            return JSONResponse({"error": "Visit not found"}, status_code=404)
        patient = db.get(Patient, visit.patient_id) if visit.patient_id else None
        clinician = db.get(Clinician, visit.clinician_id) if visit.clinician_id else None
        payload = VisitDetail(
            id=visit.id,
            patient_id=visit.patient_id,
            clinician_id=visit.clinician_id,
            visit_date=visit.visit_date,
            chief_complaint=visit.chief_complaint,
            notes=visit.notes,
            created_at=visit.created_at,
            updated_at=visit.updated_at,
            patient_name=patient.name if patient else None,
            patient_dob=patient.dob if patient else None,
            patient_mrn=patient.mrn if patient else None,
            clinician_name=clinician.name if clinician else None,
            clinician_specialty=clinician.specialty if clinician else None,
        )
        return {"visit": payload.model_dump(mode="json")}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.put("/visits/{visit_id}")
async def update_visit(visit_id: str, request: Request, db: Session = Depends(get_db)):
    try:
        visit = db.get(Visit, visit_id)
        if visit is None:
            return JSONResponse({"error": "Visit not found"}, status_code=404)
        body = await request.json()
        visit.chief_complaint = body.get("chief_complaint")
        visit.notes = body.get("notes")
        visit.updated_at = func.now()
        db.commit()
        db.refresh(visit)
        return {"visit": VisitOut.model_validate(visit).model_dump(mode="json")}
    except Exception as exc:
        db.rollback()
        return JSONResponse({"error": str(exc)}, status_code=500)
