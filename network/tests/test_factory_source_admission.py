"""Factory source admission: one cannot promote simulation to physical evidence.

Exercise the existing Factory, native simulator and durable runtime directly.
These tests do not assert that any real-world machinery has been reached.
"""
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime import EvidenceRecord, ExecutionResult, HandoffRuntime
from runtime.journal import RuntimeJournal
from runtime.orchestrator import Orchestrator
from systems.bindings import factory_binding
from systems.factory import FactorySystem, default_simulated_actors
from systems.factory.simulated import (
    FactorySimulationAdmission, FACTORY_SIMULATION_VERIFIER,
)


class FactorySourceAdmissionTests(unittest.TestCase):
    def setUp(self):
        root = TemporaryDirectory()
        self.addCleanup(root.cleanup)
        self.root = Path(root.name)
        self.factory_path = self.root / "factory.jsonl"
        self.runtime_path = self.root / "runtime.jsonl"
        self.factory = FactorySystem(self.factory_path)
        self.factory.create_order(
            order_id="SOURCE-1",
            product="demo-part",
            quantity=3,
            material="demo-stock",
        )
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.runtime_path))
        self.actors = default_simulated_actors()

    def test_default_factory_refuses_fabricated_supplier_record(self):
        handoff = self.factory.next_handoff("SOURCE-1")
        self.assertEqual(handoff.admissible_evidence["material supplied"], ("simulation",))
        self.runtime.submit(handoff)
        before = len(self.runtime.event_store.all())
        with self.assertRaisesRegex(ValueError, "requires one of evidence kinds"):
            self.runtime.return_result(
                handoff.handoff_id, actor_id=handoff.to_actor,
                result=ExecutionResult(
                    status="COMPLETE",
                    output={"material_state": "received"},
                    evidence=(EvidenceRecord(
                        condition="material supplied",
                        kind="supplier_record",
                        source="unverified-supplier",
                        ref="supplier:unverified",
                        depth="physical",
                    ),),
                ),
            )
        self.assertEqual(len(self.runtime.event_store.all()), before)
        self.assertEqual(self.runtime.state(handoff.handoff_id).status, "READY")
        self.assertEqual(self.factory.order("SOURCE-1").stage_index, 0)

    def test_default_factory_refuses_fabricated_carrier_record(self):
        for _ in range(4):
            handoff = self.factory.next_handoff("SOURCE-1")
            self.runtime.submit(handoff)
            state = self.runtime.run(handoff.handoff_id, self.actors[handoff.to_actor])
            self.factory.reconcile("SOURCE-1", handoff=handoff, state=state)
        shipping = self.factory.next_handoff("SOURCE-1")
        self.runtime.submit(shipping)
        before = len(self.runtime.event_store.all())
        with self.assertRaisesRegex(ValueError, "requires one of evidence kinds"):
            self.runtime.return_result(
                shipping.handoff_id, actor_id=shipping.to_actor,
                result=ExecutionResult(
                    status="COMPLETE",
                    output={"shipment_state": "shipped"},
                    evidence=(EvidenceRecord(
                        condition="shipment recorded",
                        kind="carrier_record",
                        source="unverified-carrier",
                        ref="carrier:unverified",
                        depth="physical",
                    ),),
                ),
            )
        self.assertEqual(len(self.runtime.event_store.all()), before)
        self.assertEqual(self.factory.order("SOURCE-1").stage_index, 4)

    def test_native_replay_checks_actual_simulation_outputs(self):
        admission = FactorySimulationAdmission(self.runtime)
        original = self.factory.next_handoff("SOURCE-1")
        handoff = admission.admit(original)
        self.assertEqual(
            handoff.metadata["native_evidence_verifier"],
            FACTORY_SIMULATION_VERIFIER,
        )
        self.runtime.submit(handoff)
        expected = self.actors[handoff.to_actor].execute(handoff)
        forged = replace(
            expected, output={**expected.output, "quantity": 900}
        )
        before = len(self.runtime.event_store.all())
        with self.assertRaisesRegex(ValueError, "differs from native simulator"):
            self.runtime.return_result(
                handoff.handoff_id, actor_id=handoff.to_actor, result=forged
            )
        self.assertEqual(len(self.runtime.event_store.all()), before)
        self.assertEqual(self.runtime.state(handoff.handoff_id).status, "READY")
        accepted = self.runtime.return_result(
            handoff.handoff_id, actor_id=handoff.to_actor, result=expected
        )
        self.assertEqual(accepted.status, "COMPLETE")
        self.assertEqual(accepted.evidence[0].depth, "simulated")
        self.factory.reconcile("SOURCE-1", handoff=handoff, state=accepted)
        self.assertEqual(self.factory.order("SOURCE-1").stage_index, 1)

    def test_native_replay_rejects_correct_labels_with_fake_source(self):
        admission = FactorySimulationAdmission(self.runtime)
        handoff = admission.admit(self.factory.next_handoff("SOURCE-1"))
        self.runtime.submit(handoff)
        expected = self.actors[handoff.to_actor].execute(handoff)
        changed = replace(
            expected.evidence[0],
            source="supplier-device-that-did-not-run",
            ref="sim:fake",
        )
        with self.assertRaisesRegex(ValueError, "differs from native simulator"):
            self.runtime.return_result(
                handoff.handoff_id, actor_id=handoff.to_actor,
                result=replace(expected, evidence=(changed,)),
            )
        self.assertEqual(self.runtime.state(handoff.handoff_id).status, "READY")

    def test_marked_native_handoff_requires_registered_verifier(self):
        admission = FactorySimulationAdmission(self.runtime)
        handoff = admission.admit(self.factory.next_handoff("SOURCE-1"))
        fresh = HandoffRuntime(event_store=RuntimeJournal(self.root / "other.jsonl"))
        fresh.submit(handoff)
        result = self.actors[handoff.to_actor].execute(handoff)
        with self.assertRaisesRegex(ValueError, "not registered"):
            fresh.return_result(
                handoff.handoff_id, actor_id=handoff.to_actor, result=result
            )
        self.assertEqual(fresh.state(handoff.handoff_id).status, "READY")

    def test_verified_simulated_factory_runs_and_restarts_without_duplication(self):
        admission = FactorySimulationAdmission(self.runtime)
        orchestrator = Orchestrator(self.runtime)
        orchestrator.register_system(factory_binding(
            self.factory, order_ids=("SOURCE-1",),
            simulation_admission=admission,
        ))
        for actor in self.actors.values():
            orchestrator.register_actor(actor)
        steps = orchestrator.run_until_idle()
        self.assertEqual(self.factory.order("SOURCE-1").status, "complete")
        self.assertEqual(self.factory.order("SOURCE-1").stage_index, 5)
        self.assertEqual(
            sum(len(step.executed) for step in steps), 5
        )
        handoff_ids = [
            event["payload"]["handoff_id"] for event in self.factory.events()
            if event["event_type"] == "HANDOFF_EMITTED"
        ]
        self.assertEqual(len(handoff_ids), 5)
        previous_counts = {
            hid: len(self.runtime.event_store.for_handoff(hid))
            for hid in handoff_ids
        }
        self.factory = FactorySystem(self.factory_path)
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.runtime_path))
        admission = FactorySimulationAdmission(self.runtime)
        for hid in handoff_ids:
            state = admission.reverify(hid)
            self.assertEqual(state.status, "COMPLETE")
            self.assertEqual(state.evidence[0].kind, "simulation")
            self.assertEqual(state.evidence[0].depth, "simulated")
            self.assertEqual(
                len(self.runtime.event_store.for_handoff(hid)),
                previous_counts[hid],
            )
        self.assertEqual(self.factory.order("SOURCE-1").status, "complete")

    def test_persisted_output_mutation_is_not_reverified_as_native(self):
        admission = FactorySimulationAdmission(self.runtime)
        handoff = admission.admit(self.factory.next_handoff("SOURCE-1"))
        self.runtime.submit(handoff)
        expected = self.actors[handoff.to_actor].execute(handoff)
        self.runtime.return_result(
            handoff.handoff_id, actor_id=handoff.to_actor, result=expected
        )
        rows = [
            json.loads(line) for line in self.runtime_path.read_text().splitlines()
        ]
        for row in rows:
            if (row["record_type"] == "EVENT"
                    and row["event"]["event_type"] == "RESULT"):
                row["event"]["data"]["output"]["quantity"] = 999
        self.runtime_path.write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        restored = HandoffRuntime(event_store=RuntimeJournal(self.runtime_path))
        admission2 = FactorySimulationAdmission(restored)
        with self.assertRaisesRegex(ValueError, "differs from native simulator"):
            admission2.reverify(handoff.handoff_id)


if __name__ == "__main__":
    unittest.main()
