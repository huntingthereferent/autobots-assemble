from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EarthquakeIn(BaseModel):
    source_id: str
    magnitude: float | None = None
    place: str = Field(min_length=1)
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)
    depth_km: float
    occurred_at: datetime
    source_updated_at: datetime
    source_url: str


class EarthquakeOut(EarthquakeIn):
    model_config = ConfigDict(from_attributes=True)

    ingested_at: datetime
