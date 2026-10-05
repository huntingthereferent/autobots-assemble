from app.usgs import fetch_events


def test_live_usgs_feed_returns_valid_shape():
    events = fetch_events()
    assert isinstance(events, list)
    for event in events[:5]:
        assert event.source_id
        assert -180 <= event.longitude <= 180
        assert -90 <= event.latitude <= 90
        assert event.source_url.startswith("https://")
