from datetime import datetime

from sqlalchemy import DateTime, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class EarthquakeEvent(Base):
    __tablename__ = "earthquake_events"

    source_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    magnitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    place: Mapped[str] = mapped_column(String(512))
    longitude: Mapped[float] = mapped_column(Float)
    latitude: Mapped[float] = mapped_column(Float)
    depth_km: Mapped[float] = mapped_column(Float)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source_url: Mapped[str] = mapped_column(String(1024))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_earthquake_occurred_at", "occurred_at"),
        Index("ix_earthquake_magnitude", "magnitude"),
    )
