"""add lifecycle records

Revision ID: 0003_lifecycle_records
Revises: 0002_identity_decisions
Create Date: 2026-10-05
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_lifecycle_records"
down_revision = "0002_identity_decisions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lifecycle_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("source_id", sa.String(length=256), nullable=False),
        sa.Column("canonical_key", sa.String(length=512), nullable=False),
        sa.Column("entity_type", sa.String(length=128), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("transition", sa.String(length=32), nullable=False),
        sa.Column("observation_id", sa.Integer(), nullable=True),
    )
    op.create_index("ix_lifecycle_records_source", "lifecycle_records", ["source"])
    op.create_index("ix_lifecycle_records_source_id", "lifecycle_records", ["source_id"])
    op.create_index("ix_lifecycle_records_canonical_key", "lifecycle_records", ["canonical_key"])
    op.create_index("ix_lifecycle_records_entity_type", "lifecycle_records", ["entity_type"])
    op.create_index("ix_lifecycle_records_recorded_at", "lifecycle_records", ["recorded_at"])
    op.create_index("ix_lifecycle_records_state", "lifecycle_records", ["state"])
    op.create_index("ix_lifecycle_records_transition", "lifecycle_records", ["transition"])


def downgrade() -> None:
    op.drop_table("lifecycle_records")
