"""Read-only, native-scoped inspection adapters over existing handoff records.

Inspection NEVER runs a worker, replays an evidence verifier or changes the
handoff journal. A report is a view of recorded state, not fresh verification.
New process types supply a named projector without changing the common UI.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, TYPE_CHECKING
from runtime.handoff import Handoff

if TYPE_CHECKING:
    from runtime.handoff import HandoffState

Inspection = dict[str, Any]
Inspector = Callable[[Handoff, "HandoffState"], Inspection]


def _row(label: str, value: Any) -> dict[str, str]:
    """Keep UI values plain text; no URLs, HTML or private source paths."""
    return {"label": label, "value": str(value)}


def _finite(handoff: Handoff, state: HandoffState) -> Inspection:
    inputs = handoff.inputs
    candidates = inputs.get("candidate_words", [])
    outputs = state.output.get("verdicts")
    if not isinstance(outputs, list):
        outputs = []
    comparison = []
    for n, words in enumerate(candidates):
        # Persisted input may be inspected without re-running the validator.
        seeds = ", ".join(str(x) for x in words) if isinstance(words, (list, tuple)) else "not recorded"
        verdict = str(outputs[n]) if n < len(outputs) else "not recorded"
        comparison.append(_row(f"Candidate {n + 1}", f"{seeds} → {verdict}"))
    return {
        "kind": "finite-prefilter", "title": "Finite required-edge inspection",
        "scope": "Finite correspondence prefilter computation (recorded)",
        "inputs": [
            _row("Old law", inputs.get("old_phi")),
            _row("New law", inputs.get("new_phi")),
            _row("Required edge", f"{inputs.get('required_state')} / {inputs.get('required_action')}"),
            _row("Candidate count", len(candidates)),
        ],
        "outputs": comparison,
        "notes": [
            "NOT_CONTRADICTED does not prove a correspondence or an admitted edge.",
            "A recorded COMPLETE means only that this finite prefilter job completed.",
            "This viewer does not run the native verifier or authenticate external source ownership.",
        ],
    }


def _factory_machine(handoff: Handoff, state: HandoffState) -> Inspection:
    inputs, outputs = handoff.inputs, state.output
    return {
        "kind": "factory-machine-simulation",
        "title": "Factory machine simulation inspection",
        "scope": "Factory machine stage — simulated, not physical",
        "inputs": [
            _row("Factory order", inputs.get("order", "not recorded")),
            _row("Product", inputs.get("product", "not recorded")),
            _row("Material", inputs.get("material", "not recorded")),
            _row("Quantity", inputs.get("quantity", "not recorded")),
            _row("Material state", inputs.get("material_state", "not recorded")),
        ],
        "outputs": [
            _row("Simulated part", outputs.get("part", "not recorded")),
            _row("Simulated quantity", outputs.get("quantity", "not recorded")),
            _row("Simulated part state", outputs.get("part_state", "not recorded")),
        ],
        "notes": [
            "Factory evidence is simulation / simulated, not a physical measurement.",
            "This stage does not establish physical machining, inspection, or shipment.",
            "The viewer displays journal evidence without replaying the native simulator.",
        ],
    }


def _generic(handoff: Handoff, state: HandoffState) -> Inspection:
    return {
        "kind": "generic-handoff", "title": "Recorded job inspection",
        "scope": "Unrecognized process; no native inspection adapter registered",
        "inputs": [
            _row("Required relation", handoff.required_relation),
            _row("Receiving actor", handoff.to_actor),
        ],
        "outputs": [
            _row("Recorded status", state.status),
            _row("Output fields", len(state.output) if isinstance(state.output, dict) else 0),
        ],
        "notes": [
            "This generic view does not interpret or verify this process's result.",
            "Register a source-owned read-only inspector to show additional details.",
        ],
    }


# This maps existing native evidence verifier IDs to display-only projectors.
# No evidence verifier is installed, invoked or replaced by these entries.
DEFAULT_INSPECTORS: dict[str, Inspector] = {
    "finite-correspondence-prefilter-v1": _finite,
    "workstation.factory.machine.simulation.v1": _factory_machine,
}


def inspect_handoff(handoff: Handoff, state: HandoffState, *,
                    inspectors: Mapping[str, Inspector] | None = None) -> Inspection:
    """Project one handoff; native source retains all evidence authority."""
    registry = DEFAULT_INSPECTORS if inspectors is None else inspectors
    key = handoff.metadata.get("native_evidence_verifier")
    renderer = registry.get(key) if isinstance(key, str) else None
    report = renderer(handoff, state) if renderer is not None else _generic(handoff, state)
    expected = {"kind", "title", "scope", "inputs", "outputs", "notes"}
    if not isinstance(report, dict) or set(report) != expected:
        raise ValueError("inspection adapter returned invalid report shape")
    if not all(isinstance(report[k], str) and report[k] for k in ("kind", "title", "scope")):
        raise ValueError("inspection adapter returned invalid identifiers")
    if not isinstance(report["notes"], list) or not all(isinstance(x, str) for x in report["notes"]):
        raise ValueError("inspection notes must be text")
    for field in ("inputs", "outputs"):
        if not isinstance(report[field], list) or not all(
            isinstance(row, dict) and set(row) == {"label", "value"} and
            all(isinstance(row[k], str) for k in ("label", "value"))
            for row in report[field]
        ):
            raise ValueError("inspection rows must be label/value text")
    return report
