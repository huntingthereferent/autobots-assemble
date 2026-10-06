from pathlib import Path
import unittest

from runtime import (
    EvidenceRecord,
    ExecutionResult,
    Handoff,
    HandoffRuntime,
    SimulatedActor,
)
from runtime.examples.cross_layer import all_examples
from runtime.examples.tiny_factory import simulate_order
from runtime.projections import command_projection, job_projection, task_projection


class HandoffRuntimeTests(unittest.TestCase):
    def test_unlike_layers_share_exact_same_carrier(self):
        examples = all_examples()
        self.assertEqual(len(examples), 4)
        self.assertTrue(all(isinstance(item, Handoff) for item in examples))
        fields = set(Handoff.__dataclass_fields__)
        for item in examples:
            self.assertEqual(set(item.__dataclass_fields__), fields)
            self.assertTrue(item.referent)
            self.assertTrue(item.required_relation)
            self.assertTrue(item.required_witnesses)

    def test_one_carrier_can_render_as_task_job_or_command(self):
        handoff = all_examples()[-1]
        runtime = HandoffRuntime()
        state = runtime.submit(handoff)

        task = task_projection(handoff, state)
        job = job_projection(handoff, state)
        command = command_projection(handoff, state)

        self.assertEqual(task["id"], handoff.handoff_id)
        self.assertEqual(job["job_id"], handoff.handoff_id)
        self.assertEqual(command["command_id"], handoff.handoff_id)
        self.assertEqual(job["operation"], handoff.required_relation)
        self.assertEqual(command["operation"], handoff.required_relation)

    def test_complete_rejects_wrong_evidence_kind(self):
        handoff = Handoff(
            handoff_id="evidence-test",
            referent="test referent",
            from_actor="router",
            to_actor="worker",
            required_relation="do work",
            required_witnesses=("work completed",),
            admissible_evidence={"work completed": ("measurement",)},
        )
        runtime = HandoffRuntime()
        runtime.submit(handoff)

        with self.assertRaisesRegex(ValueError, "requires one of evidence kinds"):
            runtime.return_result(
                handoff.handoff_id,
                actor_id="worker",
                result=ExecutionResult(
                    status="COMPLETE",
                    evidence=(
                        EvidenceRecord(
                            condition="work completed",
                            kind="simulation",
                            source="sim",
                        ),
                    ),
                ),
            )

        self.assertEqual(runtime.state(handoff.handoff_id).status, "READY")

    def test_complete_requires_every_witness(self):
        handoff = Handoff(
            handoff_id="missing-witness-test",
            referent="test referent",
            from_actor="router",
            to_actor="worker",
            required_relation="do work",
            required_witnesses=("operation completed", "output checked"),
            admissible_evidence={
                "operation completed": ("human_report",),
                "output checked": ("measurement",),
            },
        )
        runtime = HandoffRuntime()
        runtime.submit(handoff)

        with self.assertRaisesRegex(ValueError, "output checked"):
            runtime.return_result(
                handoff.handoff_id,
                actor_id="worker",
                result=ExecutionResult(
                    status="COMPLETE",
                    evidence=(
                        EvidenceRecord(
                            condition="operation completed",
                            kind="human_report",
                            source="worker",
                        ),
                    ),
                ),
            )

    def test_dependency_waits_until_parent_complete(self):
        runtime = HandoffRuntime()
        parent = Handoff(
            handoff_id="parent",
            referent="order",
            from_actor="router",
            to_actor="sim-a",
            required_relation="step a",
            required_witnesses=("a complete",),
            admissible_evidence={"a complete": ("simulation",)},
        )
        child = Handoff(
            handoff_id="child",
            referent="order",
            from_actor="router",
            to_actor="sim-b",
            required_relation="step b",
            dependencies=("parent",),
            required_witnesses=("b complete",),
            admissible_evidence={"b complete": ("simulation",)},
        )
        runtime.submit(parent)
        runtime.submit(child)
        self.assertEqual(runtime.state("child").status, "WAITING")

        actor = SimulatedActor(
            actor_id="sim-a",
            capabilities=("step a",),
            handler=lambda h: ExecutionResult(
                status="COMPLETE",
                evidence=(
                    EvidenceRecord(
                        condition="a complete",
                        kind="simulation",
                        source="sim-a",
                        depth="simulated",
                    ),
                ),
            ),
        )
        runtime.run("parent", actor)
        self.assertEqual(runtime.state("child").status, "READY")

    def test_event_history_is_append_only(self):
        handoff = Handoff(
            handoff_id="event-test",
            referent="thing",
            from_actor="router",
            to_actor="sim",
            required_relation="move",
            required_witnesses=("moved",),
            admissible_evidence={"moved": ("simulation",)},
        )
        runtime = HandoffRuntime()
        runtime.submit(handoff)
        before = tuple(runtime.event_store.all())

        actor = SimulatedActor(
            actor_id="sim",
            capabilities=("move",),
            handler=lambda h: ExecutionResult(
                status="COMPLETE",
                evidence=(
                    EvidenceRecord(
                        condition="moved",
                        kind="simulation",
                        source="sim",
                        depth="simulated",
                    ),
                ),
            ),
        )
        runtime.run(handoff.handoff_id, actor)
        after = tuple(runtime.event_store.all())

        self.assertEqual(after[:len(before)], before)
        self.assertGreater(len(after), len(before))

    def test_tiny_factory_runs_end_to_end_without_upgrading_simulation(self):
        runtime, trace = simulate_order()
        self.assertEqual(
            trace,
            [
                "factory-001-supply:COMPLETE",
                "factory-002-machine:COMPLETE",
                "factory-003-inspect:COMPLETE",
                "factory-004-assemble:COMPLETE",
                "factory-005-ship:COMPLETE",
            ],
        )

        final = runtime.state("factory-005-ship")
        self.assertEqual(final.output["state"], "shipped")
        self.assertEqual(final.output["quantity"], 10)
        self.assertTrue(final.evidence)
        self.assertTrue(all(item.kind == "simulation" for item in final.evidence))
        self.assertTrue(all(item.depth == "simulated" for item in final.evidence))

    def test_factory_output_becomes_next_handoff_input(self):
        runtime, _ = simulate_order()
        machine = runtime.get("factory-002-machine")
        inspect = runtime.get("factory-003-inspect")
        assemble = runtime.get("factory-004-assemble")

        self.assertEqual(machine.inputs["material_state"], "received")
        self.assertEqual(inspect.inputs["part_state"], "machined")
        self.assertEqual(assemble.inputs["inspection_state"], "inspected")


if __name__ == "__main__":
    unittest.main()
