from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

import httpx


@dataclass
class SourceFetchError(RuntimeError):
    source: str
    url: str
    attempts: int
    last_error: str

    def __str__(self) -> str:
        return (
            f"source={self.source} url={self.url} attempts={self.attempts} "
            f"last_error={self.last_error}"
        )


def get_with_retry(
    client: httpx.Client,
    url: str,
    *,
    source: str,
    attempts: int = 3,
    backoff_seconds: float = 0.25,
    sleep: Callable[[float], None] = time.sleep,
) -> httpx.Response:
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    last_error = "unknown"

    for attempt in range(1, attempts + 1):
        try:
            response = client.get(url)
            response.raise_for_status()
            return response
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < attempts:
                sleep(backoff_seconds * (2 ** (attempt - 1)))

    raise SourceFetchError(
        source=source,
        url=url,
        attempts=attempts,
        last_error=last_error,
    )
