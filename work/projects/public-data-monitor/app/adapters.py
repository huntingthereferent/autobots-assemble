from datetime import datetime, timezone

from .platform import SourceObservation
from .usgs import fetch_events


class LiveJsonAdapter:
    name = "live_json_api"

    def fetch(self) -> list[SourceObservation]:
        observed_at = datetime.now(timezone.utc)
        observations: list[SourceObservation] = []

        for event in fetch_events():
            observations.append(
                SourceObservation(
                    source=self.name,
                    source_id=event.source_id,
                    observed_at=observed_at,
                    source_updated_at=event.source_updated_at,
                    source_url=event.source_url,
                    entity_type="event",
                    canonical_key=f"event:{event.source_id}",
                    payload={
                        "magnitude": event.magnitude,
                        "place": event.place,
                        "longitude": event.longitude,
                        "latitude": event.latitude,
                        "depth_km": event.depth_km,
                        "occurred_at": event.occurred_at.isoformat(),
                    },
                )
            )

        return observations
