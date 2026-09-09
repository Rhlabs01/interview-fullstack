from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Clinician
from app.schemas import ClinicianOut

router = APIRouter()


@router.get("/clinicians")
def list_clinicians(db: Session = Depends(get_db)):
    try:
        rows = db.query(Clinician).order_by(Clinician.name).all()
        return {
            "clinicians": [
                ClinicianOut.model_validate(row).model_dump(mode="json") for row in rows
            ]
        }
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
