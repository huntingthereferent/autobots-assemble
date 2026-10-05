from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .runtime import ExecutionRecord, execute


class RecurrenceError(ValueError):
    pass


@dataclass(frozen=True)
class Feedback:
    source_output: str
    target_input: str


@dataclass(frozen=True)
class RecurrenceExecution:
    records: list[ExecutionRecord]


def _compatible(source: dict[str, Any], target: dict[str, Any]) -> bool:
    a = source["type"]
    b = target["type"]
    return a == b or a == "any" or b == "any"


def execute_recurrence(
    manifest: dict[str, Any],
    *,
    seed_inputs: dict[str, Any],
    feedback: Feedback,
    steps: int,
    initial_state: dict[str, Any] | None = None,
) -> RecurrenceExecution:
    if steps < 1:
        raise RecurrenceError("steps must be at least 1")

    outputs = manifest.get("outputs", {})
    inputs = manifest.get("inputs", {})

    if feedback.source_output not in outputs:
        raise RecurrenceError("feedback source output is not declared")
    if feedback.target_input not in inputs:
        raise RecurrenceError("feedback target input is not declared")
    if not _compatible(
        outputs[feedback.source_output],
        inputs[feedback.target_input],
    ):
        raise RecurrenceError("feedback contracts are incompatible")

    if feedback.target_input not in seed_inputs:
        raise RecurrenceError(
            "seed inputs must provide the first feedback target value"
        )

    records: list[ExecutionRecord] = []
    current_inputs = dict(seed_inputs)
    parent: ExecutionRecord | None = None

    for iteration in range(steps):
        provenance = {}
        parents: list[str] = []

        if parent is not None:
            current_inputs[feedback.target_input] = parent.values[
                feedback.source_output
            ]
            provenance[feedback.target_input] = {
                "kind": "recurrence_feedback",
                "iteration": iteration,
                "source_execution_id": parent.execution_id,
                "source_manifest_id": parent.manifest_id,
                "source_output": feedback.source_output,
            }
            parents.append(parent.execution_id)

        record = execute(
            manifest,
            current_inputs,
            initial_state=initial_state,
            input_provenance=provenance,
            parent_executions=parents,
        )
        records.append(record)
        parent = record

    return RecurrenceExecution(records=records)
