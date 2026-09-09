"""Index medication names for exact lookups.

The catalog can hold the full RxNorm ingredient set (~15k concepts), and
``rxnorm.local_lookup`` filters on ``lower(name)``. Without a matching
expression index every lookup is a sequential scan.

Revision ID: 003
Revises: 002
Create Date: 2026-09-04
"""

from typing import Sequence, Union

from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_medications_lower_name "
        "ON medications (lower(name))"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_medications_lower_name")
