from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class ObservationRecord(Base):
    __tablename__ = "observation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(128), index=True)
    source_id: Mapped[str] = mapped_column(String(256), index=True)
    canonical_key: Mapped[str] = mapped_column(String(512), index=True)
    entity_type: Mapped[str] = mapped_column(String(128), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON)
    change_kind: Mapped[str] = mapped_column(String(32), index=True)
    changed_fields: Mapped[list] = mapped_column(JSON)


class ReconciliationRecord(Base):
    __tablename__ = "reconciliation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_key: Mapped[str] = mapped_column(String(512), index=True)
    reconciled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    sources: Mapped[list] = mapped_column(JSON)
    conflicting_fields: Mapped[list] = mapped_column(JSON)
    selected_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
