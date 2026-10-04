from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import json
import re

BANK_PATH = Path(__file__).with_name("shape_bank.json")


def _norm(value: str) -> str:
    value = value.casefold().strip()
    value = re.sub(r"[.!?]+$", "", value)
    value = re.sub(r"\s+", " ", value)
    return value


@lru_cache(maxsize=1)
def load_bank() -> dict:
    return json.loads(BANK_PATH.read_text(encoding="utf-8"))


def shape(shape_id: str) -> dict:
    for item in load_bank()["shapes"]:
        if item["id"] == shape_id:
            return item
    raise KeyError(shape_id)


@lru_cache(maxsize=1)
def reverse_index() -> dict[str, tuple[dict, ...]]:
    found: dict[str, list[dict]] = {}
    for item in load_bank()["shapes"]:
        for register, forms in item["surfaces"].items():
            for form in forms:
                found.setdefault(_norm(form), []).append(
                    {"shape": item["id"], "register": register, "surface": form}
                )
    return {key: tuple(value) for key, value in found.items()}


def candidates(surface: str, register: str | None = None) -> tuple[dict, ...]:
    matches = reverse_index().get(_norm(surface), ())
    if register is None:
        return matches
    return tuple(m for m in matches if m["register"] == register)


def render(shape_id: str, register: str = "standard", variant: int = 0) -> str:
    item = shape(shape_id)
    forms = item["surfaces"].get(register)
    if not forms:
        raise KeyError(f"{shape_id} has no register {register!r}")
    return forms[variant % len(forms)]
