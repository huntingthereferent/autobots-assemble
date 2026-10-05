from __future__ import annotations

from dataclasses import dataclass
from typing import Any


TYPE_CHECKS = {
    "string": lambda value: isinstance(value, str),
    "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
    "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
    "boolean": lambda value: isinstance(value, bool),
    "object": lambda value: isinstance(value, dict),
    "array": lambda value: isinstance(value, list),
    "bytes": lambda value: isinstance(value, (bytes, bytearray)),
    "any": lambda value: True,
}


@dataclass(frozen=True)
class ContractError(Exception):
    name: str
    expected_type: str
    actual_type: str

    def __str__(self) -> str:
        return (
            f"{self.name}: expected {self.expected_type}, "
            f"received {self.actual_type}"
        )


def assert_contract(name: str, contract: dict[str, Any], value: Any) -> None:
    expected = contract["type"]
    check = TYPE_CHECKS[expected]
    if not check(value):
        raise ContractError(name, expected, type(value).__name__)
