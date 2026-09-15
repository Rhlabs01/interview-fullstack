from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    false,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Clinician(Base):
    __tablename__ = "clinicians"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    specialty: Mapped[str] = mapped_column(String(255), nullable=False)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dob: Mapped[date] = mapped_column(Date, nullable=False)
    mrn: Mapped[str] = mapped_column(String(50), nullable=False)
    assigned_clinician_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("clinicians.id")
    )


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    patient_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("patients.id"))
    clinician_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("clinicians.id")
    )
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    chief_complaint: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class CatalogImportJob(Base):
    """Current / last RxNorm catalog import (singleton row, ``id=1``)."""

    __tablename__ = "catalog_import_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="idle")
    phase: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    concepts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[str | None] = mapped_column(String(40))
    finished_at: Mapped[str | None] = mapped_column(String(40))


class Medication(Base):
    """A normalized RxNorm ingredient concept used as a reference catalog.

    Seeded with real RxNorm attributes. Strength and dose form are not stored
    here — the catalog is ingredients (``tty=IN``) only.
    """

    __tablename__ = "medications"

    rxcui: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tty: Mapped[str] = mapped_column(String(20), nullable=False)
    synonym: Mapped[str | None] = mapped_column(String(255))
    # Comma-separated for portability; exposed as lists in the API.
    brand_names: Mapped[str | None] = mapped_column(Text)
    drug_class: Mapped[str | None] = mapped_column(String(255))


class Wound(Base):
    __tablename__ = "wounds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    patient_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("patients.id"))
    clinician_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("clinicians.id")
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    wound_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    # Base64-encoded photo of the wound, if one was attached.
    image_data: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), server_default="active")
    version: Mapped[int] = mapped_column(Integer, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class WoundAssessment(Base):
    __tablename__ = "wound_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    wound_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("wounds.id"))
    clinician_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("clinicians.id")
    )
    length_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    width_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    depth_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    tissue_type: Mapped[str | None] = mapped_column(String(100))
    exudate_amount: Mapped[str | None] = mapped_column(String(50))
    healing_stage: Mapped[str | None] = mapped_column(String(50))
    push_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    ai_generated: Mapped[bool] = mapped_column(Boolean, server_default=false())
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AIJob(Base):
    __tablename__ = "ai_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    wound_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("wounds.id"))
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), server_default="pending")
    result: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
