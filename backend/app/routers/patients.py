from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Clinician, Patient, Visit
from app.schemas import PatientDetail, PatientOut, VisitListItem, VisitOut

router = APIRouter()


@router.get("/patients")
def list_patients(clinicianId: str | None = None, db: Session = Depends(get_db)):
    try:
        query = db.query(Patient)
        if clinicianId:
            query = query.filter(Patient.assigned_clinician_id == clinicianId)
        rows = query.order_by(Patient.name).all()
        return {
            "patients": [PatientOut.model_validate(row).model_dump(mode="json") for row in rows]
        }
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.get("/patients/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    try:
        patient = db.get(Patient, patient_id)
        if patient is None:
            return JSONResponse({"error": "Patient not found"}, status_code=404)
        clinician = (
            db.get(Clinician, patient.assigned_clinician_id)
            if patient.assigned_clinician_id
            else None
        )
        payload = PatientDetail(
            id=patient.id,
            name=patient.name,
            dob=patient.dob,
            mrn=patient.mrn,
            assigned_clinician_id=patient.assigned_clinician_id,
            clinician_name=clinician.name if clinician else None,
            clinician_specialty=clinician.specialty if clinician else None,
        )
        return {"patient": payload.model_dump(mode="json")}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.get("/patients/{patient_id}/visits")
def list_visits(patient_id: str, db: Session = Depends(get_db)):
    try:
        rows = (
            db.query(Visit, Clinician.name)
            .outerjoin(Clinician, Visit.clinician_id == Clinician.id)
            .filter(Visit.patient_id == patient_id)
            .order_by(Visit.visit_date.desc())
            .all()
        )
        visits = []
        for visit, clinician_name in rows:
            item = VisitListItem.model_validate(visit)
            item.clinician_name = clinician_name
            visits.append(item.model_dump(mode="json"))
        return {"visits": visits}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.post("/patients/{patient_id}/visits")
async def create_visit(patient_id: str, request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        clinician_id = body.get("clinician_id")
        visit_date = body.get("visit_date")
        if not clinician_id or not visit_date:
            return JSONResponse(
                {"error": "clinician_id and visit_date are required"},
                status_code=400,
            )
        visit = Visit(
            id=str(uuid4()),
            patient_id=patient_id,
            clinician_id=clinician_id,
            visit_date=visit_date,
            chief_complaint=body.get("chief_complaint") or "",
            notes=body.get("notes") or "",
        )
        db.add(visit)
        db.commit()
        db.refresh(visit)
        return JSONResponse(
            {"visit": VisitOut.model_validate(visit).model_dump(mode="json")},
            status_code=201,
        )
    except Exception as exc:
        db.rollback()
        return JSONResponse({"error": str(exc)}, status_code=500)
