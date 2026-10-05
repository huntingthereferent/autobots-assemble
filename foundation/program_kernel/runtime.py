from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import importlib
from typing import Any, Callable
from uuid import uuid4

from .contracts import assert_contract


@dataclass(frozen=True)
class StepRecord:
    operation: str
    consumed: list[str]
    produced: list[str]
    started_at: str
    finished_at: str
    status: str


@dataclass(frozen=True)
class ExecutionRecord:
    execution_id: str
    manifest_id: str
    referent: str
    parent_executions: list[str]
    steps: list[StepRecord]
    witnesses: list[dict[str, Any]]
    values: dict[str, Any]
    provenance: dict[str, dict[str, Any]]


def _load_callable(path: str) -> Callable[..., dict[str, Any]]:
    module_name, function_name = path.rsplit(":", 1)
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    if not callable(function):
        raise TypeError(f"{path} is not callable")
    return function


def _contracts(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for section in ("inputs", "state", "outputs"):
        merged.update(manifest.get(section, {}))
    return merged


def _check_witness(witness: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    target = witness["target"]
    kind = witness["kind"]
    exists = target in values

    if kind == "exists":
        passed = exists
    elif kind == "equals":
        passed = exists and values[target] == witness.get("expected")
    else:
        # Predicate witnesses are admitted by schema but require an explicit
        # future predicate implementation. Never silently treat them as pass.
        passed = False

    return {
        "id": witness["id"],
        "kind": kind,
        "target": target,
        "passed": passed,
    }


def execute(
    manifest: dict[str, Any],
    inputs: dict[str, Any],
    *,
    initial_state: dict[str, Any] | None = None,
    input_provenance: dict[str, dict[str, Any]] | None = None,
    parent_executions: list[str] | None = None,
) -> ExecutionRecord:
    execution_id = str(uuid4())
    values: dict[str, Any] = {}
    provenance: dict[str, dict[str, Any]] = {}

    for name, value in (initial_state or {}).items():
        values[name] = value
        provenance[name] = {"kind": "initial_state"}

    for name, value in inputs.items():
        values[name] = value
        provenance[name] = (input_provenance or {}).get(
            name,
            {"kind": "external_input"},
        )

    contracts = _contracts(manifest)

    for name, contract in manifest.get("inputs", {}).items():
        if contract.get("required", True) and name not in values:
            raise KeyError(f"missing required input: {name}")
        if name in values:
            assert_contract(name, contract, values[name])

    steps: list[StepRecord] = []

    for operation in manifest["operations"]:
        missing = [name for name in operation["consumes"] if name not in values]
        if missing:
            raise KeyError(
                f"{operation['id']} missing consumed values: {', '.join(missing)}"
            )

        kwargs = {name: values[name] for name in operation["consumes"]}
        started = datetime.now(timezone.utc).isoformat()
        result = _load_callable(operation["implementation"])(**kwargs)
        finished = datetime.now(timezone.utc).isoformat()

        if not isinstance(result, dict):
            raise TypeError(f"{operation['id']} must return a dict")

        expected_outputs = set(operation["produces"])
        actual_outputs = set(result)
        if expected_outputs != actual_outputs:
            raise ValueError(
                f"{operation['id']} produced {sorted(actual_outputs)}, "
                f"expected {sorted(expected_outputs)}"
            )

        for name, value in result.items():
            if name in contracts:
                assert_contract(name, contracts[name], value)
            values[name] = value
            provenance[name] = {
                "kind": "operation_output",
                "execution_id": execution_id,
                "operation": operation["id"],
                "consumed": list(operation["consumes"]),
            }

        steps.append(
            StepRecord(
                operation=operation["id"],
                consumed=list(operation["consumes"]),
                produced=list(operation["produces"]),
                started_at=started,
                finished_at=finished,
                status="success",
            )
        )

    witnesses = [_check_witness(item, values) for item in manifest["witnesses"]]

    return ExecutionRecord(
        execution_id=execution_id,
        manifest_id=manifest["id"],
        referent=manifest["referent"],
        parent_executions=list(parent_executions or []),
        steps=steps,
        witnesses=witnesses,
        values=values,
        provenance=provenance,
    )


def execution_dict(record: ExecutionRecord) -> dict[str, Any]:
    return {
        "execution_id": record.execution_id,
        "manifest_id": record.manifest_id,
        "referent": record.referent,
        "parent_executions": record.parent_executions,
        "steps": [asdict(step) for step in record.steps],
        "witnesses": record.witnesses,
        "values": record.values,
        "provenance": record.provenance,
    }
