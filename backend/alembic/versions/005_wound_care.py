"""Wound documentation, assessments, and AI assessment jobs.

Revision ID: 005
Revises: 004
Create Date: 2026-09-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "wounds",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patients.id")),
        sa.Column("clinician_id", sa.String(36), sa.ForeignKey("clinicians.id")),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("wound_type", sa.String(100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("image_data", sa.Text()),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("version", sa.Integer(), server_default="1"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "wound_assessments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("wound_id", sa.String(36), sa.ForeignKey("wounds.id")),
        sa.Column("clinician_id", sa.String(36), sa.ForeignKey("clinicians.id")),
        sa.Column("length_cm", sa.Numeric(5, 2)),
        sa.Column("width_cm", sa.Numeric(5, 2)),
        sa.Column("depth_cm", sa.Numeric(5, 2)),
        sa.Column("tissue_type", sa.String(100)),
        sa.Column("exudate_amount", sa.String(50)),
        sa.Column("healing_stage", sa.String(50)),
        sa.Column("push_score", sa.Numeric(4, 1)),
        sa.Column("ai_generated", sa.Boolean(), server_default=sa.false()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "ai_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("wound_id", sa.String(36), sa.ForeignKey("wounds.id")),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("result", sa.JSON()),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table("wounds")
    op.drop_table("wound_assessments")
    op.drop_table("ai_jobs")
