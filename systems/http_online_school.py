from __future__ import annotations

from urllib.parse import quote
from urllib.request import Request, urlopen
import json

from .bindings import online_school_binding
from .online_school import task_patch_from_handoff_state, task_to_handoff


class OnlineSchoolHttpClient:
    """Treat the existing Online School HTTP app as an independent system."""

    def __init__(self, base_url: str, *, timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _json(self, path: str, *, method: str = "GET", payload=None):
        body = None
        headers = {}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(
            self.base_url + path,
            data=body,
            headers=headers,
            method=method,
        )
        with urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def tasks(self) -> tuple[dict, ...]:
        payload = self._json("/api/tasks")
        return tuple(payload.get("tasks") or ())

    def patch_task(self, task_id: str, patch: dict) -> dict:
        return self._json(
            "/api/tasks/" + quote(task_id, safe=""),
            method="PATCH",
            payload=patch,
        )

    def binding(self):
        return online_school_binding(
            task_provider=self.tasks,
            task_to_handoff=task_to_handoff,
            apply_patch=lambda task_id, state: self.patch_task(
                task_id,
                task_patch_from_handoff_state(state),
            ),
        )
