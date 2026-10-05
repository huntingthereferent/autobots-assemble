from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class IdentityDecisionRecord(Base):
    __tablename__ = "identity_decision_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    left_key: Mapped[str] = mapped_column(String(512), index=True)
    right_key: Mapped[str] = mapped_column(String(512), index=True)
    score: Mapped[int] = mapped_column(Integer)
    threshold: Mapped[int] = mapped_column(Integer)
    matched: Mapped[bool] = mapped_column(Boolean, index=True)
    evidence: Mapped[list] = mapped_column(JSON)
