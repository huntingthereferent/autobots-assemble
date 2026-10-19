"""Actual Factory simulation worker -> native replay -> pinned Workstation evidence."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.factory import FactorySystem, default_simulated_actors
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.factory_machine_bridge import (
    FactoryMachineSimulationBridge, WORKER_ID as FACTORY_WORKER,
)
from systems.workspace.workflow_draft import SCHEMA
from systems.workspace.workflow_pins import WorkflowPins
from systems.workspace.workflow_native_results import WorkflowNativeResults, NativeResultBoundary

ROOT = Path(__file__).resolve().parents[2]
WORKER_SOURCE = ROOT / "systems/workspace/factory_machine_worker.py"


def draft():
    return {
        "schema": SCHEMA, "title": "Factory simulation observation",
        "provenance": "explicit source-owned test fixture", "auto_connect": False,
        "steps": [
            {"id": "machine", "label": "Simulated machine-stage work",
             "manifest": "foundation/program_examples/stateless.json",
             "inputs": {"text": "simulation-only"}},
        ], "links": [],
    }


class FactoryNativeWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data = Path(self.temp.name)
        original = self.data / "factory-source"
        original.mkdir()
        shutil.copyfile(WORKER_SOURCE, original / "factory_machine_worker.py")
        self.desk = ProcessWorkstation(self.data / "workstation")
        self.desk.copy_source(original, worker_id=FACTORY_WORKER, version_id="machine-original")
        copy = self.desk.branch(worker_id=FACTORY_WORKER, parent_version="machine-original",
                                version_id="machine-alternative")
        (Path(copy["path"]) / "research-note.txt").write_text("alternative source edition\n")
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.data / "runtime.jsonl"))
        self.factory = FactorySystem(self.data / "factory_orders.jsonl")
        self.bridge = FactoryMachineSimulationBridge(runtime=self.runtime, workstation=self.desk)
        self.results = WorkflowNativeResults(ROOT, self.data)
        self.pins = WorkflowPins(self.data)

    def run_native_factory(self, order_id, edition, product="test-widget", quantity=2):
        self.factory.create_order(order_id=order_id, product=product,
                                  material="test-material", quantity=quantity)
        supply = self.factory.next_handoff(order_id)
        self.runtime.submit(self.bridge.native.admit(supply))
        self.runtime.run(supply.handoff_id, default_simulated_actors()[supply.to_actor])
        self.factory.reconcile(order_id, handoff=supply,
                               state=self.runtime.state(supply.handoff_id))
        machine = self.factory.next_handoff(order_id)
        self.bridge.admit(machine, version_id=edition)
        state = self.bridge.execute(machine.handoff_id, allow_local_execution=True)
        self.assertEqual(state.status, "COMPLETE")
        return machine.handoff_id

    def pins_pair(self):
        parent = draft()
        first = self.pins.pin_candidate(parent, ROOT, reason="Original simulation")
        child = deepcopy(parent)
        child["parent_revision"] = first["revision"]
        child["steps"][0]["label"] = "Alternative simulation worker edition"
        second = self.pins.pin_candidate(child, ROOT, reason="Retain alternate source")
        return parent, child, first, second

    def test_native_factory_simulation_rechecked_no_physical_claim(self):
        job = self.run_native_factory("SIM-BASE", "machine-original")
        journal_before = (self.data / "runtime.jsonl").read_bytes()
        row = self.results.inspect(job)
        self.assertTrue(row["native_result_reverified"])
        self.assertTrue(row["simulation_only"])
        self.assertEqual(row["result_family"], "factory-machine-simulation-v1")
        self.assertEqual(row["simulated_part_state"], "machined")
        self.assertIsNone(row["verdict_counts"])
        self.assertFalse(row["branch_quality_verified"])
        self.assertFalse(row["native_job_reexecuted"])
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), journal_before)

    def test_replay_both_factory_editions_and_compare_bounded_equal_inputs(self):
        a = self.run_native_factory("SIM-A", "machine-original")
        b = self.run_native_factory("SIM-B", "machine-alternative")
        parent, child, first, second = self.pins_pair()
        self.results.attach(parent, step_id="machine", job_id=a)
        self.results.attach(child, step_id="machine", job_id=b)
        comparison = self.results.compare(
            parent_revision=first["revision"], branch_revision=second["revision"],
            parent_step_id="machine", branch_step_id="machine")
        self.assertTrue(comparison["source_owned_native_results_reverified_now"])
        self.assertEqual(comparison["result_family"], "factory-machine-simulation-v1")
        self.assertTrue(comparison["simulation_only"])
        self.assertTrue(comparison["identical_native_results"])
        self.assertIsNone(comparison["verdict_count_deltas"])
        self.assertFalse(comparison["physical_production_verified"])
        self.assertFalse(comparison["workflow_quality_ranked"])
        self.assertFalse(comparison["automatic_pin_promotion"])
        self.assertEqual(len(self.pins.list_pins()), 2)
        self.assertEqual(len(self.results.list_records()), 2)

    def test_changed_factory_inputs_are_incomparable(self):
        a = self.run_native_factory("SIM-X", "machine-original", quantity=2)
        b = self.run_native_factory("SIM-Y", "machine-alternative", quantity=3)
        parent, child, first, second = self.pins_pair()
        self.results.attach(parent, step_id="machine", job_id=a)
        self.results.attach(child, step_id="machine", job_id=b)
        with self.assertRaisesRegex(NativeResultBoundary, "inputs differ"):
            self.results.compare(
                parent_revision=first["revision"], branch_revision=second["revision"],
                parent_step_id="machine", branch_step_id="machine")

    def test_source_change_invalidates_native_simulation_verification(self):
        a = self.run_native_factory("SIM-C", "machine-original")
        parent, _, _, _ = self.pins_pair()
        self.results.attach(parent, step_id="machine", job_id=a)
        path = self.desk._edition(FACTORY_WORKER, "machine-original") / "factory_machine_worker.py"
        path.write_text(path.read_text() + "\n# changed source\n")
        with self.assertRaisesRegex(ValueError, "source changed"):
            self.results.inspect(a)
        self.assertEqual(len(self.results.list_records()), 1)

    def test_admitted_but_unexecuted_factory_is_not_recorded(self):
        self.factory.create_order(order_id="SIM-PENDING", product="test-widget",
                                  material="test-material", quantity=1)
        supply = self.factory.next_handoff("SIM-PENDING")
        self.runtime.submit(self.bridge.native.admit(supply))
        self.runtime.run(supply.handoff_id, default_simulated_actors()[supply.to_actor])
        self.factory.reconcile("SIM-PENDING", handoff=supply,
                               state=self.runtime.state(supply.handoff_id))
        machine = self.factory.next_handoff("SIM-PENDING")
        self.bridge.admit(machine, version_id="machine-original")
        parent, _, _, _ = self.pins_pair()
        with self.assertRaisesRegex(NativeResultBoundary, "completed"):
            self.results.attach(parent, step_id="machine", job_id=machine.handoff_id)
        self.assertFalse(self.results.path.exists())


if __name__ == "__main__":
    unittest.main()
