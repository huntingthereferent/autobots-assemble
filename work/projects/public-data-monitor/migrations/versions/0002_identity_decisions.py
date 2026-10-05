from alembic import op
import sqlalchemy as sa

revision = "0002_identity_decisions"
down_revision = "0001_source_run_task_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "identity_decision_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("left_key", sa.String(length=512), nullable=False),
        sa.Column("right_key", sa.String(length=512), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("threshold", sa.Integer(), nullable=False),
        sa.Column("matched", sa.Boolean(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
    )
    op.create_index(
        "ix_identity_decision_records_decided_at",
        "identity_decision_records",
        ["decided_at"],
    )
    op.create_index(
        "ix_identity_decision_records_left_key",
        "identity_decision_records",
        ["left_key"],
    )
    op.create_index(
        "ix_identity_decision_records_right_key",
        "identity_decision_records",
        ["right_key"],
    )
    op.create_index(
        "ix_identity_decision_records_matched",
        "identity_decision_records",
        ["matched"],
    )


def downgrade() -> None:
    op.drop_table("identity_decision_records")
