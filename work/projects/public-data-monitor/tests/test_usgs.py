from app.usgs import parse_feature


def test_parse_feature_preserves_source_and_coordinates():
    feature = {
        "id": "example123",
        "properties": {
            "mag": 2.5,
            "place": "10 km N of Example",
            "time": 1_700_000_000_000,
            "updated": 1_700_000_001_000,
            "url": "https://example.test/event",
        },
        "geometry": {"type": "Point", "coordinates": [-94.5, 39.1, 8.2]},
    }

    event = parse_feature(feature)

    assert event.source_id == "example123"
    assert event.magnitude == 2.5
    assert event.longitude == -94.5
    assert event.latitude == 39.1
    assert event.depth_km == 8.2
    assert event.source_url == "https://example.test/event"
