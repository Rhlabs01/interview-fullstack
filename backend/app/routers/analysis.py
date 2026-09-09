"""Visit-note medication analysis.

THIS IS THE TAKE-HOME EXERCISE. See EXERCISE.md.

``analyze_note`` below is an empty stub — it finds nothing. The endpoint, the
response schema (``NoteAnalysis`` / ``MedicationMention``), and the RxNorm
catalog it should resolve against are all wired up for you; the detection and
matching are not.

Your task is to implement ``analyze_note`` so that it:
  * uses an LLM to find medication mentions in free-text notes, and
  * fuzzy-matches each mention to a normalized RxNorm concept (misspellings,
    shorthand, brand names), and
  * reports the proper spelling for misspelled mentions.

Then set ``implemented=True`` and build the UI that surfaces the results.

Form/dosage matching and import-job hardening are optional stretches — only
if the core path works. See EXERCISE.md.
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
    there if you take the form/dosage stretch.
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
