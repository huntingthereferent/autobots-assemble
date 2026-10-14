"""Read-only, native-scoped inspection adapters over existing handoff records.

Inspection NEVER runs a worker, replays an evidence verifier or changes the
handoff journal. A report is a view of recorded state, not fresh verification.
New process types supply a named projector without changing the common UI.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from runtime.handoff import Handoff
from typing import TYPE_CHECKING
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
        # The inputs were admitted by the finite input validator, but the
        # persisted record can be inspected without executing that validator.
        label = f"Candidate {n + 1}"
        seeds = ", ".join(str(x) for x in words) if isinstance(words, (list, tuple)) else "not recorded"
        verdict = str(outputs[n]) if n < len(outputs) else "not recorded"
        comparison.append(_row(label, f"{seeds} → {verdict}"))
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


def _integrated_cp30(handoff: Handoff, state: HandoffState) -> Inspection:
    """Display recorded signature check, not an independently enrolled owner."""
    e = handoff.inputs.get("expect", {})
    output = state.output if isinstance(state.output, dict) else {}
    return {
        "kind": "integrated-cp30-attestation",
        "title": "Integrated CP30 signed-scope verification",
        "scope": "Three cryptographic signatures checked against caller-supplied keys",
        "inputs": [
            _row("Route", e.get("route", "not recorded")),
            _row("Challenge", e.get("challenge", "not recorded")),
            _row("Route fingerprint", e.get("fingerprint", "not recorded")),
            _row("Expected scopes", "donor, middle, final"),
        ],
        "outputs": [
            _row("Signature verdict", output.get("signature_verdict", "not recorded")),
            _row("Verified key scopes", ", ".join(output.get("verified_scopes", [])) or "none"),
        ],
        "notes": [
            "The three public keys are caller-supplied, not independently enrolled identities.",
            "Valid signatures do not establish a fresh CP30 route audit or human owner identity.",
            "COMPLETE means this bounded computation finished, including negative verdicts.",
            "The dashboard displays persisted evidence and does not reverify it.",
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



def _cp30_route_fixture(handoff: Handoff, state: HandoffState) -> Inspection:
    """Inspect synthetic CP30 route/task report only; never replay from UI."""
    request=handoff.inputs
    output=state.output.get("report",{})
    if not isinstance(output,dict):output={}
    rows=[]
    statuses=dict(output.get("task_statuses") or [])
    for task in request.get("tasks",[]):
        rows.append(_row(task.get("name","?"),
              f"{task.get('state')} {task.get('action')} -> {statuses.get(task.get('name'),'not recorded')}"))
    return {
        "kind":"cp30-synthetic-route-audit",
        "title":"CP30 fresh route and exact task fixture",
        "scope":"Recovered CP30 owner/pin simulation; no external owner enrollment",
        "inputs":[_row("Selected route",request.get("route")),
                  _row("Scenario",request.get("scenario")),
                  _row("Declared task count",len(rows))],
        "outputs":[_row("Receiver verdict",output.get("receive_status","not recorded")),
                   _row("Fresh route audit calls",output.get("replay_calls","not recorded")),
                   _row("Usable fixture tasks",output.get("usable",[])),
                   *rows],
        "notes":[
          "These owners, keys and source pins are synthetic research fixtures.",
          "A completed computation can contain individual unproved task obligations.",
          "Two audit calls are source-owned fixture replay, not live external audits.",
          "Dashboard reports saved evidence; it does not re-execute source.",
        ],
    }

# Names come from the existing *native evidence verifier* contracts. Mapping
# to an inspector never registers, invokes or replaces those verifiers.
DEFAULT_INSPECTORS: dict[str, Inspector] = {
    "finite-correspondence-prefilter-v1": _finite,
    "workstation.factory.machine.simulation.v1": _factory_machine,
    "integrated-cp30-three-scope-attestation-v1": _integrated_cp30,
    "integrated-cp30-synthetic-route-audit-v1": _cp30_route_fixture,
}


def inspect_handoff(handoff: Handoff, state: HandoffState, *,
                    inspectors: Mapping[str, Inspector] | None = None) -> Inspection:
    """Project one handoff; native source retains all evidence authority."""
    registry = DEFAULT_INSPECTORS if inspectors is None else inspectors
    key = handoff.metadata.get("native_evidence_verifier")
    renderer = registry.get(key) if isinstance(key, str) else None
    report = renderer(handoff, state) if renderer is not None else _generic(handoff, state)
    # The shared viewer accepts only a display contract, never executable
    # instructions or an inferred verification result.
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
