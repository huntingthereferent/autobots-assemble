from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
import json
import re

from .handoff import Handoff, HandoffState
from .projections import task_projection


def normalize_surface(surface: str) -> str:
    """Normalize only enough to match an explicit activation surface."""
    return re.sub(r"\s+", " ", surface.strip().casefold())


@dataclass(frozen=True)
class ActivationRoute:
    activation_id: str
    surfaces: tuple[str, ...]
    actor_id: str
    referent: str
    projection: str
    selectors: dict[str, object] = field(default_factory=dict)
    sources: tuple[str, ...] = ()
    boundaries: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("activation_id", self.activation_id),
            ("actor_id", self.actor_id),
            ("referent", self.referent),
            ("projection", self.projection),
        ):
            if not str(value).strip():
                raise ValueError(f"{name} is required")
        if not self.surfaces:
            raise ValueError("activation requires at least one surface")


@dataclass(frozen=True)
class ActivationResult:
    route: ActivationRoute
    surface: str
    items: tuple[dict, ...]
    note: str = ""


class ActivationRegistry:
    """Explicit activation-word registry.

    This is intentionally narrower than general language understanding.
    A surface only activates a route when a registered actor+surface pair matches.
    """

    def __init__(self, routes: Iterable[ActivationRoute] = ()) -> None:
        self._routes = tuple(routes)

    @classmethod
    def from_json(cls, path: str | Path) -> "ActivationRegistry":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        routes = []
        for row in payload.get("activations", []):
            routes.append(
                ActivationRoute(
                    activation_id=row["activation_id"],
                    surfaces=tuple(row["surfaces"]),
                    actor_id=row["actor_id"],
                    referent=row["referent"],
                    projection=row["projection"],
                    selectors=dict(row.get("selectors") or {}),
                    sources=tuple(row.get("sources") or ()),
                    boundaries=tuple(row.get("boundaries") or ()),
                    provenance=tuple(row.get("provenance") or ()),
                )
            )
        return cls(routes)

    def resolve(self, surface: str, *, actor_id: str) -> ActivationRoute | None:
        normalized = normalize_surface(surface)
        actor = actor_id.strip().casefold()
        matches = [
            route for route in self._routes
            if route.actor_id.casefold() == actor
            and normalized in {normalize_surface(x) for x in route.surfaces}
        ]
        if not matches:
            return None
        if len(matches) > 1:
            raise ValueError(
                f"ambiguous activation {surface!r} for actor {actor_id!r}"
            )
        return matches[0]


def _matches(route: ActivationRoute, handoff: Handoff, state: HandoffState) -> bool:
    selectors = route.selectors

    if selectors.get("assignee") and handoff.to_actor != selectors["assignee"]:
        return False

    statuses = selectors.get("statuses")
    if statuses and state.status not in set(statuses):
        return False

    required_relation = selectors.get("required_relation")
    if required_relation and handoff.required_relation != required_relation:
        return False

    metadata = selectors.get("metadata")
    if isinstance(metadata, dict):
        for key, value in metadata.items():
            if handoff.metadata.get(key) != value:
                return False

    return True


def run_activation(
    route: ActivationRoute,
    *,
    surface: str,
    handoffs: Iterable[tuple[Handoff, HandoffState]],
) -> ActivationResult:
    """Project existing state through an activation route.

    Activations select and render existing handoffs. They do not manufacture
    unsupported work or mutate handoff state.
    """
    if route.projection not in {"task_queue", "day_attention"}:
        raise ValueError(f"unsupported projection: {route.projection}")

    items = []
    for handoff, state in handoffs:
        if _matches(route, handoff, state):
            items.append(task_projection(handoff, state))

    status_order = {
        "ACTIVE": 0,
        "READY": 1,
        "PARTIAL": 2,
        "BLOCKED": 3,
        "WAITING": 4,
        "UNKNOWN": 5,
        "FAILED": 6,
        "COMPLETE": 7,
    }
    items.sort(
        key=lambda item: (
            status_order.get(item["status"], 99),
            str(item["title"]).casefold(),
        )
    )

    note = (
        "Activation rendered existing attention; no new obligations were inferred."
        if route.projection == "day_attention"
        else "Activation rendered existing handoffs; no new work was inferred."
    )
    return ActivationResult(
        route=route,
        surface=surface,
        items=tuple(items),
        note=note,
    )
