import httpx
import pytest

from app.acquisition import SourceFetchError, get_with_retry


def test_retry_recovers_after_transient_failures():
    calls = {"count": 0}
    sleeps = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] < 3:
            return httpx.Response(503, request=request)
        return httpx.Response(200, json={"ok": True}, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    response = get_with_retry(
        client,
        "https://example.test/data",
        source="fixture",
        attempts=3,
        backoff_seconds=0.1,
        sleep=sleeps.append,
    )

    assert response.json() == {"ok": True}
    assert calls["count"] == 3
    assert sleeps == [0.1, 0.2]


def test_retry_surfaces_typed_source_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    with pytest.raises(SourceFetchError) as exc_info:
        get_with_retry(
            client,
            "https://example.test/data",
            source="fixture",
            attempts=2,
            backoff_seconds=0,
            sleep=lambda _: None,
        )

    error = exc_info.value
    assert error.source == "fixture"
    assert error.attempts == 2
    assert "HTTPStatusError" in error.last_error
