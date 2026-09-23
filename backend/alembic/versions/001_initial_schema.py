"""Initial clinicians, patients, visits schema.

Revision ID: 001
Revises:
Create Date: 2026-09-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clinicians",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("specialty", sa.String(255), nullable=False),
    )
    op.create_table(
        "patients",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("dob", sa.Date(), nullable=False),
        sa.Column("mrn", sa.String(50), nullable=False),
        sa.Column("assigned_clinician_id", sa.String(36), sa.ForeignKey("clinicians.id")),
    )
    op.create_table(
        "visits",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patients.id")),
        sa.Column("clinician_id", sa.String(36), sa.ForeignKey("clinicians.id")),
        sa.Column("visit_date", sa.Date(), nullable=False),
        sa.Column("chief_complaint", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("visits")
    op.drop_table("patients")
    op.drop_table("clinicians")
