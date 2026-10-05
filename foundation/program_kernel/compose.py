from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .runtime import ExecutionRecord, execute


class CompositionError(ValueError):
    pass


@dataclass(frozen=True)
class Link:
    source_output: str
    target_input: str


def _compatible(source: dict[str, Any], target: dict[str, Any]) -> bool:
    a = source["type"]
    b = target["type"]
    return a == b or a == "any" or b == "any"


def execute_linked(
    *,
    source_manifest: dict[str, Any],
    source_record: ExecutionRecord,
    target_manifest: dict[str, Any],
    link: Link,
    target_inputs: dict[str, Any] | None = None,
    initial_state: dict[str, Any] | None = None,
) -> ExecutionRecord:
    if link.source_output not in source_manifest.get("outputs", {}):
        raise CompositionError("source output is not declared")
    if link.target_input not in target_manifest.get("inputs", {}):
        raise CompositionError("target input is not declared")
    if link.source_output not in source_record.values:
        raise CompositionError("source output was not realized")

    source_contract = source_manifest["outputs"][link.source_output]
    target_contract = target_manifest["inputs"][link.target_input]
    if not _compatible(source_contract, target_contract):
        raise CompositionError(
            f"incompatible contracts: {source_contract['type']} -> {target_contract['type']}"
        )

    inputs = dict(target_inputs or {})
    if link.target_input in inputs:
        raise CompositionError("linked target input was already supplied")

    inputs[link.target_input] = source_record.values[link.source_output]
    provenance = {
        link.target_input: {
            "kind": "linked_execution_output",
            "source_execution_id": source_record.execution_id,
            "source_manifest_id": source_record.manifest_id,
            "source_output": link.source_output,
        }
    }

    return execute(
        target_manifest,
        inputs,
        initial_state=initial_state,
        input_provenance=provenance,
        parent_executions=[source_record.execution_id],
    )
