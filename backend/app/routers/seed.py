from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.seed import seed_database

router = APIRouter()


@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    try:
        counts = seed_database(db)
        return {
            "success": True,
            "message": "Database seeded successfully",
            "counts": counts,
        }
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
