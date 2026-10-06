from __future__ import annotations

from .handoff import Handoff, HandoffState


def task_projection(handoff: Handoff, state: HandoffState) -> dict:
    """Human work-queue projection of a handoff."""
    return {
        "id": handoff.handoff_id,
        "title": handoff.metadata.get("title") or handoff.required_relation,
        "referent": handoff.referent,
        "assignee": handoff.to_actor,
        "status": state.status,
        "inputs": handoff.inputs,
        "blocked_by": list(state.blocked_by),
        "missing_witnesses": list(state.missing_witnesses),
    }


def job_projection(handoff: Handoff, state: HandoffState) -> dict:
    """Program/agent queue projection of the same carrier."""
    return {
        "job_id": handoff.handoff_id,
        "target": handoff.to_actor,
        "operation": handoff.required_relation,
        "payload": handoff.inputs,
        "expected_output": handoff.expected_output,
        "status": state.status,
    }


def command_projection(handoff: Handoff, state: HandoffState) -> dict:
    """Machine/simulator command projection of the same carrier."""
    return {
        "command_id": handoff.handoff_id,
        "device": handoff.to_actor,
        "operation": handoff.required_relation,
        "parameters": handoff.inputs,
        "ready": state.status == "READY",
        "boundaries": list(handoff.boundaries),
    }
