"""AI-generated wound assessments.

``analyze_wound`` sends the wound, the patient, and the patient's visit history
to the configured LLM and stores the structured assessment it returns as a
``WoundAssessment`` row. Progress is tracked on the ``AIJob`` row so the UI can
poll it.
"""

import json
import logging
from datetime import datetime
from uuid import uuid4

from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AIJob, Patient, Visit, Wound, WoundAssessment

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a clinical wound care assessment assistant. Analyze wound "
    "information and provide a structured assessment. Return valid JSON only."
)


def _build_prompt(wound: Wound, patient: Patient, visits: list[Visit]) -> str:
    history = "\n".join(
        f"{visit.visit_date}: {visit.chief_complaint} - {visit.notes}"
        for visit in visits
    )
    return f"""Assess this wound for patient {patient.name} (DOB: {patient.dob}).

Wound location: {wound.location}
Wound type: {wound.wound_type}
Description: {wound.description}

Patient visit history:
{history}

Return a JSON object with these fields:
- length_cm (number)
- width_cm (number)
- depth_cm (number)
- tissue_type (one of: epithelial, granulation, slough, necrotic)
- exudate_amount (one of: none, light, moderate, heavy)
- healing_stage (one of: hemostasis, inflammatory, proliferative, maturation)
- push_score (number, 0-17 scale)
- notes (string with clinical observations)"""


def analyze_wound(db: Session, wound_id: str, job_id: str) -> dict:
    settings = get_settings()
    job = db.get(AIJob, job_id)
    try:
        job.status = "processing"
        db.commit()

        wound = db.get(Wound, wound_id)
        if wound is None:
            raise ValueError("Wound not found")
        patient = db.get(Patient, wound.patient_id)
        visits = (
            db.query(Visit)
            .filter(Visit.patient_id == wound.patient_id)
            .order_by(Visit.visit_date.desc())
            .all()
        )

        logger.info("Assessing wound %s for %s", wound_id, patient.name)

        content: list[dict] = [
            {"type": "text", "text": _build_prompt(wound, patient, visits)}
        ]
        if wound.image_data:
            content.insert(
                0,
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{wound.image_data}"},
                },
            )

        client = OpenAI(api_key=settings.llm_api_key)
        completion = client.chat.completions.create(
            model=settings.llm_model,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
        )
        assessment = json.loads(completion.choices[0].message.content)

        db.add(
            WoundAssessment(
                id=str(uuid4()),
                wound_id=wound_id,
                clinician_id=wound.clinician_id,
                length_cm=assessment["length_cm"],
                width_cm=assessment["width_cm"],
                depth_cm=assessment["depth_cm"],
                tissue_type=assessment["tissue_type"],
                exudate_amount=assessment["exudate_amount"],
                healing_stage=assessment["healing_stage"],
                push_score=assessment["push_score"],
                ai_generated=True,
                notes=assessment.get("notes"),
            )
        )
        job.status = "completed"
        job.result = assessment
        job.completed_at = datetime.now()
        db.commit()
        return assessment
    except Exception as exc:
        db.rollback()
        job.status = "failed"
        job.error_message = str(exc)
        db.commit()
        raise
