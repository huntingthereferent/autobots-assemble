"""Small simulated proof: closure can produce a fourth agent."""
from pathlib import Path

from runtime.activation import ActivationRegistry
from runtime.agent_lineage import AgentLineage, AgentMove
from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult


def demo():
    registry = ActivationRegistry.from_json(
        Path(__file__).resolve().parents[2] / "activations" / "agent_lineage.example.json"
    )
    runtime = HandoffRuntime()
    root = ""

    def witness(condition="movement witness", ref="SIM-MOVE"):
        return EvidenceRecord(condition=condition, kind="simulation",
                              source="local synthetic example", ref=ref, depth="simulated")

    def evaluate(handoff, _state):
        generation = handoff.metadata["generation"]
        next_ref = {1: "first result", 2: "second result"}.get(generation, "")
        closes = (root,) if generation == 3 else ()
        return AgentMove(
            result=ExecutionResult(
                status="COMPLETE", output={"generation": generation},
                evidence=(witness(),),
            ),
            next_referent=next_ref,
            closes=closes,
            closure_evidence=(witness("ancestor closure", "SIM-CLOSURE"),) if closes else (),
            closure_birth_referent="closure opens next referent" if closes else "",
        )

    lineage = AgentLineage(
        runtime, registry, evaluate=evaluate,
        admit_closure=lambda descendant, ancestor, evidence: (
            descendant.metadata["generation"] == 3
            and ancestor.handoff_id == root
            and any(e.condition == "ancestor closure" and e.ref == "SIM-CLOSURE" for e in evidence)
        ),
    )
    root = lineage.activate("begin comparison", actor_id="test-operator", instance_id="demo-1")
    changes = lineage.run_until_idle(root)
    return lineage, root, changes


if __name__ == "__main__":
    lineage, root, changes = demo()
    for member in lineage._members(root):
        print(f"GEN {member.metadata['generation']}: {member.referent} -> "
              f"{lineage.runtime.state(member.handoff_id).status} / "
              f"{lineage.loop_status(member.handoff_id)} / "
              f"born-from={member.metadata['birth_reason']}")
    print("closure events:", sum(len(s.closed) for s in changes))
    print("evidence depth: simulated; no real A/B engine or autonomous actor invoked")
