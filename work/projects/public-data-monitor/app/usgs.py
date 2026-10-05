from datetime import datetime, timezone

import httpx

from .schemas import EarthquakeIn

USGS_ALL_HOUR = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"


def _millis_to_datetime(value: int) -> datetime:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc)


def parse_feature(feature: dict) -> EarthquakeIn:
    props = feature["properties"]
    coordinates = feature["geometry"]["coordinates"]

    return EarthquakeIn(
        source_id=feature["id"],
        magnitude=props.get("mag"),
        place=props.get("place") or "Unknown location",
        longitude=coordinates[0],
        latitude=coordinates[1],
        depth_km=coordinates[2],
        occurred_at=_millis_to_datetime(props["time"]),
        source_updated_at=_millis_to_datetime(props["updated"]),
        source_url=props["url"],
    )


def fetch_events(client: httpx.Client | None = None) -> list[EarthquakeIn]:
    owns_client = client is None
    client = client or httpx.Client(timeout=15)
    try:
        response = client.get(
            USGS_ALL_HOUR,
            headers={"User-Agent": "public-data-monitor/0.1"},
        )
        response.raise_for_status()
        payload = response.json()
        return [parse_feature(feature) for feature in payload["features"]]
    finally:
        if owns_client:
            client.close()
