"""Native inspector regressions, including two unlike process types and UI safety."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff
from systems.workspace.inspections import inspect_handoff
from systems.workspace.monitor import workstation_snapshot
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.process_handoff import CorrespondenceWorkBridge, WORKER_ID as FINITE_WORKER
from runtime.examples.workstation_two_processes import populate

ROOT = Path(__file__).resolve().parents[2]
FINITE = ROOT / "work/arc_like_maze/chatbot"
INPUTS = {"old_phi": [0, 0, 1], "new_phi": [0, 0, 0],
          "candidate_words": [["ABAA", "ABBABA"], ["ABAA", "AAABB", "BAAAB"]],
          "required_state": [0, 0, 0], "required_action": "B"}


class InspectionTests(unittest.TestCase):
    def test_ready_job_does_not_invent_verdicts_or_execute(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            for f in ("finite_goal_priority.py", "finite_required_edge_guard.py"):
                shutil.copyfile(FINITE / f, source / f)
            desk = ProcessWorkstation(root / "station")
            desk.copy_source(source, worker_id=FINITE_WORKER, version_id="one")
            runtime = HandoffRuntime()
            bridge = CorrespondenceWorkBridge(runtime=runtime, workstation=desk)
            job = bridge.admit(version_id="one", inputs=INPUTS, from_actor="owner")
            before = tuple(runtime.event_store.for_handoff(job.handoff_id))
            view = workstation_snapshot(root=root / "station", runtime=runtime)
            record = view["jobs"][0]
            self.assertEqual(record["inspection"]["kind"], "finite-prefilter")
            self.assertEqual(len(record["inspection"]["outputs"]), 2)
            self.assertTrue(all("not recorded" in row["value"] for row in record["inspection"]["outputs"]))
            self.assertIn("NOT_CONTRADICTED", " ".join(record["inspection"]["notes"]))
            self.assertEqual(record["status"], "READY")
            self.assertEqual(tuple(runtime.event_store.for_handoff(job.handoff_id)), before)

    def test_two_unlike_processes_show_separate_native_scopes(self):
        with TemporaryDirectory() as tmp:
            view = populate(Path(tmp), execute=True)
            self.assertEqual({x["inspection"]["kind"] for x in view["jobs"]},
                             {"finite-prefilter", "factory-machine-simulation"})
            finite = next(x for x in view["jobs"] if x["inspection"]["kind"] == "finite-prefilter")
            self.assertEqual(finite["verification"], "recorded-not-reverified")
            self.assertTrue(all("not recorded" not in x["value"] for x in finite["inspection"]["outputs"]))
            machine = next(x for x in view["jobs"] if x["inspection"]["kind"] == "factory-machine-simulation")
            self.assertIn("simulated", machine["inspection"]["scope"].lower())
            self.assertIn("machined", {row["value"] for row in machine["inspection"]["outputs"]})
            self.assertTrue(all(e["kind"] == "simulation" and e["depth"] == "simulated" for e in machine["evidence"]))
            self.assertEqual(machine["verification"], "recorded-not-reverified")

    def test_unknown_process_gets_generic_view_and_custom_extension(self):
        handoff = Handoff(handoff_id="other", referent="new problem", from_actor="human",
                          to_actor="other-process", required_relation="new bounded computation",
                          metadata={"native_evidence_verifier": "other.namespace.v1"})
        runtime = HandoffRuntime()
        runtime.submit(handoff)
        state = runtime.state("other")
        self.assertEqual(inspect_handoff(handoff, state)["kind"], "generic-handoff")
        def extension(h, s):
            return {"kind": "other-process", "title": "Other inspection", "scope": "Local test",
                    "inputs": [{"label": "Question", "value": "one"}],
                    "outputs": [], "notes": ["Not independently verified"]}
        projected = inspect_handoff(handoff, state, inspectors={"other.namespace.v1": extension})
        self.assertEqual(projected["kind"], "other-process")
        self.assertEqual(runtime.state("other").status, "READY")

    def test_invalid_custom_adapter_fails_closed(self):
        handoff = Handoff(handoff_id="other", referent="new problem", from_actor="human",
                          to_actor="other-process", required_relation="test",
                          metadata={"native_evidence_verifier": "other.namespace.v1"})
        runtime = HandoffRuntime()
        runtime.submit(handoff)
        with self.assertRaises(ValueError):
            inspect_handoff(handoff, runtime.state("other"),
                            inspectors={"other.namespace.v1": lambda *args: {"html": "<script>"}})

    def test_changed_edition_stays_unverified(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            for f in ("finite_goal_priority.py", "finite_required_edge_guard.py"):
                shutil.copyfile(FINITE / f, source / f)
            desk = ProcessWorkstation(root / "station")
            desk.copy_source(source, worker_id=FINITE_WORKER, version_id="one")
            runtime = HandoffRuntime()
            bridge = CorrespondenceWorkBridge(runtime=runtime, workstation=desk)
            bridge.admit(version_id="one", inputs=INPUTS, from_actor="owner")
            edited = root / "station" / FINITE_WORKER / "one" / "finite_goal_priority.py"
            edited.write_text(edited.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8")
            row = workstation_snapshot(root=root / "station", runtime=runtime)["jobs"][0]
            self.assertEqual(row["source_state"], "SOURCE_CHANGED")
            self.assertEqual(row["verification"], "not-complete")
            self.assertEqual(row["inspection"]["kind"], "finite-prefilter")

    def test_browser_renders_data_as_text_never_html(self):
        js = (ROOT / "runtime/http/workstation.js").read_text(encoding="utf-8")
        css = (ROOT / "runtime/http/workstation.css").read_text(encoding="utf-8")
        self.assertIn("function inspectionPanel(report)", js)
        self.assertIn('el("dd", "", row.value)', js)
        self.assertIn('el("li", "", note)', js)
        self.assertNotIn("innerHTML", js)
        self.assertNotIn('method:"POST"', js)
        self.assertIn(".inspect-grid", css)


if __name__ == "__main__":
    unittest.main()
