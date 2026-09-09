"""Medication reference catalog (RxNorm concepts).

Revision ID: 002
Revises: 001
Create Date: 2026-09-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "medications",
        sa.Column("rxcui", sa.String(20), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tty", sa.String(20), nullable=False),
        sa.Column("synonym", sa.String(255)),
        sa.Column("brand_names", sa.Text()),
        sa.Column("drug_class", sa.String(255)),
    )


def downgrade() -> None:
    op.drop_table("medications")
