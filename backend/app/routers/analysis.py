"""Visit-note medication analysis.

``analyze_note`` is an empty stub — it finds nothing. The endpoint, the
response schema (``NoteAnalysis`` / ``MedicationMention``), and the RxNorm
catalog are wired up; detection and matching are not.

Implement ``analyze_note``, set ``implemented=True``, and build the UI that
surfaces the results.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Visit
from app.schemas import MedicationMention, NoteAnalysis

router = APIRouter()


def analyze_note(db: Session, note: str) -> list[MedicationMention]:
    """Find medication mentions in ``note`` and match them to RxNorm concepts.

    TODO(candidate): implement LLM detection + fuzzy RxNorm matching.

    The catalog of normalized concepts to match against is the ``medications``
    table — see ``app.rxnorm`` for helpers (``local_lookup``, ``live_lookup``)
    and ``GET /api/medications`` for the same data as JSON. Optional fields on
    ``MedicationMention`` (``strength``, ``dose_form``, ``product_rxcui``) are
    available when a mention includes strength or form.
    """
    return []


@router.post("/visits/{visit_id}/analyze")
def analyze_visit(visit_id: str, db: Session = Depends(get_db)):
    try:
        visit = db.get(Visit, visit_id)
        if visit is None:
            return JSONResponse({"error": "Visit not found"}, status_code=404)

        note = visit.notes or ""
        payload = NoteAnalysis(
            visit_id=visit_id,
            note=note,
            mentions=analyze_note(db, note),
            # TODO(candidate): set to True once detection + matching lands.
            implemented=False,
        )
        return {"analysis": payload.model_dump(mode="json")}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
