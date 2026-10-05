from alembic import op
import sqlalchemy as sa

revision = "0001_source_run_task_id"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "source_runs",
        sa.Column("task_id", sa.String(length=128), nullable=True),
    )
    op.create_index(
        "ix_source_runs_task_id",
        "source_runs",
        ["task_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_source_runs_task_id", table_name="source_runs")
    op.drop_column("source_runs", "task_id")
