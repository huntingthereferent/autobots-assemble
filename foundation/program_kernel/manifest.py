from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ManifestError(ValueError):
    pass


_REQUIRED_TOP_LEVEL = {
    "id",
    "referent",
    "boundary",
    "inputs",
    "operations",
    "outputs",
    "witnesses",
}
_ALLOWED_TYPES = {
    "string",
    "integer",
    "number",
    "boolean",
    "object",
    "array",
    "bytes",
    "any",
}
_ALLOWED_WITNESS_KINDS = {"equals", "exists", "predicate"}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestError(message)


def _validate_contracts(section: str, contracts: Any) -> None:
    _require(isinstance(contracts, dict), f"{section} must be an object")
    for name, contract in contracts.items():
        _require(isinstance(name, str) and name, f"{section} key must be non-empty")
        _require(isinstance(contract, dict), f"{section}.{name} must be an object")
        _require("type" in contract, f"{section}.{name} missing type")
        _require(
            contract["type"] in _ALLOWED_TYPES,
            f"{section}.{name} has unsupported type",
        )


def validate_manifest(payload: Any) -> dict[str, Any]:
    _require(isinstance(payload, dict), "manifest must be an object")
    missing = _REQUIRED_TOP_LEVEL - set(payload)
    _require(not missing, f"missing required fields: {', '.join(sorted(missing))}")

    _require(isinstance(payload["id"], str) and payload["id"], "id must be non-empty")
    _require(
        isinstance(payload["referent"], str) and payload["referent"],
        "referent must be non-empty",
    )

    boundary = payload["boundary"]
    _require(isinstance(boundary, dict), "boundary must be an object")
    _require(
        isinstance(boundary.get("inside"), list) and boundary["inside"],
        "boundary.inside must be a non-empty array",
    )
    _require(
        isinstance(boundary.get("outside"), list),
        "boundary.outside must be an array",
    )

    _validate_contracts("inputs", payload["inputs"])
    _validate_contracts("state", payload.get("state", {}))
    _validate_contracts("outputs", payload["outputs"])

    operations = payload["operations"]
    _require(isinstance(operations, list) and operations, "operations must be non-empty")
    seen_operations: set[str] = set()
    for index, operation in enumerate(operations):
        _require(isinstance(operation, dict), f"operations[{index}] must be an object")
        for field in ("id", "implementation", "consumes", "produces"):
            _require(field in operation, f"operations[{index}] missing {field}")
        _require(
            isinstance(operation["id"], str) and operation["id"],
            f"operations[{index}].id must be non-empty",
        )
        _require(
            operation["id"] not in seen_operations,
            f"duplicate operation id: {operation['id']}",
        )
        seen_operations.add(operation["id"])
        _require(
            isinstance(operation["implementation"], str)
            and ":" in operation["implementation"],
            f"operations[{index}].implementation must be module:function",
        )
        _require(
            isinstance(operation["consumes"], list),
            f"operations[{index}].consumes must be an array",
        )
        _require(
            isinstance(operation["produces"], list) and operation["produces"],
            f"operations[{index}].produces must be a non-empty array",
        )

    witnesses = payload["witnesses"]
    _require(isinstance(witnesses, list) and witnesses, "witnesses must be non-empty")
    seen_witnesses: set[str] = set()
    for index, witness in enumerate(witnesses):
        _require(isinstance(witness, dict), f"witnesses[{index}] must be an object")
        for field in ("id", "kind", "target"):
            _require(field in witness, f"witnesses[{index}] missing {field}")
        _require(
            witness["kind"] in _ALLOWED_WITNESS_KINDS,
            f"witnesses[{index}] has unsupported kind",
        )
        _require(
            witness["id"] not in seen_witnesses,
            f"duplicate witness id: {witness['id']}",
        )
        seen_witnesses.add(witness["id"])

    return payload


def load_manifest(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_manifest(payload)
