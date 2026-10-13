"""Service transport for externally supplied referent movement and lineage state.

This transports witnesses and closure claims; it is not a finite mathematical
implementation and does not certify arbitrary caller-supplied evidence.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .agent_lineage import AgentLineage, AgentMove
from .handoff import EvidenceRecord, ExecutionResult


class AgentBridge:
    def __init__(self, lineage: AgentLineage) -> None:
        self.lineage = lineage

    def activate(self, payload: dict[str, Any]) -> dict[str, Any]:
        surface = str(payload.get("surface") or "").strip()
        actor_id = str(payload.get("actor_id") or "").strip()
        instance_id = str(payload.get("instance_id") or "").strip()
        referent = payload.get("referent")
        if not all((surface, actor_id, instance_id)):
            raise ValueError("surface, actor_id, and instance_id are required")
        if referent is not None and not isinstance(referent, str):
            raise ValueError("referent must be a string")
        root = self.lineage.activate(surface, actor_id=actor_id,
                                     instance_id=instance_id, referent=referent)
        if root is None:
            raise KeyError("no agent lineage activation for actor and surface")
        return self.snapshot(root)

    @staticmethod
    def _evidence(rows: object) -> tuple[EvidenceRecord, ...]:
        if not isinstance(rows, list):
            raise ValueError("evidence must be a list")
        if not all(isinstance(row, dict) for row in rows):
            raise ValueError("evidence rows must be objects")
        return tuple(EvidenceRecord(
            condition=str(row.get("condition") or ""),
            kind=str(row.get("kind") or ""),
            source=str(row.get("source") or ""),
            ref=str(row.get("ref") or ""),
            note=str(row.get("note") or ""),
            depth=str(row.get("depth") or "reported"),
        ) for row in rows)

    def result(self, agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        actor_id = str(payload.get("actor_id") or "").strip()
        status = str(payload.get("status") or "").upper()
        if not actor_id:
            raise ValueError("actor_id is required")
        if status not in {"COMPLETE", "PARTIAL", "BLOCKED", "FAILED", "UNKNOWN"}:
            raise ValueError("invalid agent result status")
        output = payload.get("output") or {}
        if not isinstance(output, dict):
            raise ValueError("output must be an object")
        closes = payload.get("closes") or []
        if not isinstance(closes, list) or not all(isinstance(x, str) for x in closes):
            raise ValueError("closes must be a list of agent identifiers")
        move = AgentMove(
            result=ExecutionResult(
                status=status, output=output,
                evidence=self._evidence(payload.get("evidence") or []),
                note=str(payload.get("note") or ""),
            ),
            next_referent=str(payload.get("next_referent") or ""),
            closes=tuple(closes),
            closure_evidence=self._evidence(payload.get("closure_evidence") or []),
            closure_birth_referent=str(payload.get("closure_birth_referent") or ""),
        )
        step = self.lineage.submit_move(agent_id, move, actor_id=actor_id)
        agent = self.lineage.runtime.get(agent_id)
        return {
            "step": {key: list(value) for key, value in asdict(step).items()},
            "lineage": self.snapshot(agent.metadata["lineage_root"]),
        }

    def snapshot(self, root: str) -> dict[str, Any]:
        members = self.lineage._members(root)
        if not members:
            raise KeyError(f"unknown lineage: {root}")
        items = []
        for agent in members:
            state = self.lineage.runtime.state(agent.handoff_id)
            items.append({
                "agent_id": agent.handoff_id,
                "referent": agent.referent,
                "generation": agent.metadata["generation"],
                "birth_parent": agent.metadata["birth_parent"],
                "birth_reason": agent.metadata["birth_reason"],
                "status": state.status,
                "loop_status": self.lineage.loop_status(agent.handoff_id),
                "output": {k: v for k, v in state.output.items() if k != "_agent_lineage"},
                "evidence": [asdict(item) for item in state.evidence],
                "provenance": list(agent.provenance),
            })
        return {
            "root": root,
            "agents": items,
            "ready": [item["agent_id"] for item in items if item["status"] == "READY"],
            "closure_verifier_connected": self.lineage.admit_closure is not None,
            "automatic_evaluator_connected": self.lineage.evaluate is not None,
            "note": "Transport connected; reported source locators are not independently verified by this adapter.",
        }
