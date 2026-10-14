"""Explicit CLI controls; browser remains GET-only and no worker runs on selection."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.controls import (prepare, admit_finite, job_view, run_job,
                                        reverify_job, main)
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.process_handoff import WORKER_ID as FINITE
from systems.workspace.factory_machine_bridge import (WORKER_ID as FACTORY,
                                                       FactoryMachineSimulationBridge)
from systems.factory import FactorySystem, default_simulated_actors

REPO = Path(__file__).resolve().parents[2]
INPUTS = {"old_phi": [0,0,1], "new_phi": [0,0,0],
          "candidate_words": [["ABAA", "ABBABA"], ["ABAA", "AAABB", "BAAAB"]],
          "required_state": [0,0,0], "required_action": "B"}

class WorkstationControlsTests(unittest.TestCase):
    def setUp(self):
        td = TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)
        self.data = self.root / "private"
        self.source = self.root / "finite-src"
        self.source.mkdir()
        for filename in ("finite_goal_priority.py", "finite_required_edge_guard.py"):
            shutil.copyfile(REPO / "work/arc_like_maze/chatbot" / filename,
                            self.source / filename)
        self.desk = ProcessWorkstation(self.data / "workstation")
        self.desk.copy_source(self.source, worker_id=FINITE, version_id="base")
        self.inputs = self.root / "inputs.json"
        self.inputs.write_text(json.dumps(INPUTS), encoding="utf-8")

    def journal(self):
        return self.data / "runtime.jsonl"

    def count_events(self):
        return len(HandoffRuntime(event_store=RuntimeJournal(self.journal())).event_store.all())

    def admit(self, job_id="finite-test-job"):
        return admit_finite(data_dir=self.data, version_id="base",
                            inputs_file=self.inputs, job_id=job_id,
                            confirm_admit=job_id, from_actor="local-test")

    def test_prepare_is_read_only_and_does_not_execute(self):
        report = prepare(data_dir=self.data, worker_id=FINITE,
                         version_id="base", inputs_file=self.inputs)
        self.assertFalse(report["admitted"])
        self.assertFalse(report["executed"])
        self.assertEqual(report["inputs"]["required_action"], "B")
        self.assertFalse(self.journal().exists())
        self.assertFalse((self.data / "workspace.jsonl").exists())

    def test_cannot_admit_without_exact_confirmation(self):
        with self.assertRaises(PermissionError):
            admit_finite(data_dir=self.data, version_id="base", inputs_file=self.inputs,
                         job_id="finite-test-job", confirm_admit="different", from_actor="test")
        self.assertFalse(self.journal().exists())

    def test_admit_and_execute_are_distinct_explicit_operations(self):
        report = self.admit()
        self.assertEqual(report["status"], "READY")
        self.assertFalse(report["executed"])
        before = self.count_events()
        with self.assertRaises(PermissionError):
            run_job(data_dir=self.data, job_id="finite-test-job", confirm_execute="not-matching")
        self.assertEqual(self.count_events(), before)
        result = run_job(data_dir=self.data, job_id="finite-test-job",
                         confirm_execute="finite-test-job")
        self.assertEqual(result["status"], "COMPLETE")
        self.assertTrue(result["reverified"])
        self.assertEqual(job_view(data_dir=self.data, job_id="finite-test-job")["status"], "COMPLETE")
        self.assertTrue(reverify_job(data_dir=self.data, job_id="finite-test-job")["reverified"])
        after = self.journal().read_bytes()
        run_job(data_dir=self.data, job_id="finite-test-job", confirm_execute="finite-test-job")
        self.assertEqual(after, self.journal().read_bytes())

    def test_source_modified_after_admission_fails_closed(self):
        self.admit()
        target = self.data / "workstation" / FINITE / "base" / "finite_required_edge_guard.py"
        target.write_text(target.read_text() + "\n# test edit\n")
        with self.assertRaisesRegex(ValueError, "source changed"):
            run_job(data_dir=self.data, job_id="finite-test-job",
                    confirm_execute="finite-test-job")
        self.assertEqual(self.count_events(), 1)  # CREATED only

    def test_invalid_input_file_and_unknown_worker_rejected(self):
        with self.assertRaises(ValueError):
            prepare(data_dir=self.data, worker_id="generic-agent", version_id="base",
                    inputs_file=self.inputs)
        self.inputs.write_text(json.dumps({"output": "pretend proof"}))
        with self.assertRaises(ValueError):
            prepare(data_dir=self.data, worker_id=FINITE, version_id="base",
                    inputs_file=self.inputs)
        self.assertFalse(self.journal().exists())

    def test_factory_prepare_cannot_invent_an_order_from_json(self):
        src = self.root / "machine"
        src.mkdir()
        shutil.copyfile(REPO / "systems/workspace/factory_machine_worker.py",
                        src / "factory_machine_worker.py")
        self.desk.copy_source(src, worker_id=FACTORY, version_id="machine-1")
        a = prepare(data_dir=self.data, worker_id=FACTORY, version_id="machine-1")
        self.assertIsNone(a["inputs"])
        self.assertFalse(a["admitted"])
        with self.assertRaisesRegex(ValueError, "Factory admission"):
            prepare(data_dir=self.data, worker_id=FACTORY, version_id="machine-1",
                    inputs_file=self.inputs)

    def test_factory_explicit_execution_reconciles_once(self):
        src = self.root / "machine"
        src.mkdir()
        shutil.copyfile(REPO / "systems/workspace/factory_machine_worker.py",
                        src / "factory_machine_worker.py")
        self.desk.copy_source(src, worker_id=FACTORY, version_id="machine-1")
        factory = FactorySystem(self.data / "factory_orders.jsonl")
        factory.create_order(order_id="F-WORK", product="test-part", material="demo-stock", quantity=2)
        runtime = HandoffRuntime(event_store=RuntimeJournal(self.journal()))
        bridge = FactoryMachineSimulationBridge(runtime=runtime, workstation=self.desk)
        supply = factory.next_handoff("F-WORK")
        runtime.submit(bridge.native.admit(supply))
        runtime.run(supply.handoff_id, default_simulated_actors()[supply.to_actor])
        factory.reconcile("F-WORK", handoff=supply, state=runtime.state(supply.handoff_id))
        machine = factory.next_handoff("F-WORK")
        bridge.admit(machine, version_id="machine-1")
        self.assertEqual(runtime.state(machine.handoff_id).status, "READY")
        self.assertEqual(factory.order("F-WORK").stage_index, 1)
        result = run_job(data_dir=self.data, job_id=machine.handoff_id,
                         confirm_execute=machine.handoff_id)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(FactorySystem(self.data / "factory_orders.jsonl").order("F-WORK").stage_index, 2)
        original = (self.journal().read_bytes(),
                    (self.data / "factory_orders.jsonl").read_bytes())
        run_job(data_dir=self.data, job_id=machine.handoff_id,
                confirm_execute=machine.handoff_id)
        self.assertEqual(original, (self.journal().read_bytes(),
                                    (self.data / "factory_orders.jsonl").read_bytes()))

    def test_cli_prepare_does_not_start_runtime(self):
        output = StringIO()
        with redirect_stdout(output):
            main(["--data-dir", str(self.data), "prepare", "--worker", FINITE,
                  "--version", "base", "--inputs-file", str(self.inputs)])
        report = json.loads(output.getvalue())
        self.assertEqual(report["operation"], "finite-required-edge-prefilter")
        self.assertFalse(self.journal().exists())

    def test_read_only_viewer_has_no_control_routes(self):
        server = (REPO / "systems/workspace/view_server.py").read_text()
        self.assertIn("do_POST", server)
        self.assertIn("405", server)
        js = (REPO / "runtime/http/workstation.js").read_text()
        self.assertNotIn('fetch("/api/workstation", {method:', js)
        self.assertNotIn("innerHTML", js)
        self.assertIn('control-command', js)

if __name__ == "__main__":
    unittest.main()
