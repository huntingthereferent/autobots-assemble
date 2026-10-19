"""Real native subprocess tests for the multi-task frontier adapter.

Unlike fixture-only frontier tests these admit and RUN four source-owned finite
worker jobs in isolated local test state, then reverify each independent
native result before computing decision coverage. They do not test scientific
predictive ability, physical world correctness, or a learned optimizer.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
import copy
import json
import shutil
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.controls import admit_finite, run_job, job_view
from systems.workspace.native_frontier import NativeCase, native_decision_frontier
from systems.workspace.process_handoff import WORKER_ID
from systems.workspace.workstation import ProcessWorkstation

ROOT = Path(__file__).resolve().parents[2]
INPUT = {
    "old_phi": [0, 0, 1], "new_phi": [0, 0, 0],
    "candidate_words": [["ABAA", "ABBABA"], ["ABAA", "AAABB", "BAAAB"]],
    "required_state": [0, 0, 0], "required_action": "B",
}


class NativeFrontierTests(unittest.TestCase):
    def setUp(self):
        t = TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.data = Path(t.name) / "private"
        source = Path(t.name) / "source"
        source.mkdir()
        for f in ("finite_goal_priority.py", "finite_required_edge_guard.py"):
            shutil.copyfile(ROOT / "work" / "arc_like_maze" / "chatbot" / f,
                            source / f)
        self.desk = ProcessWorkstation(self.data / "workstation")
        self.desk.copy_source(source, worker_id=WORKER_ID,
                              version_id="native-base")
        self.desk.branch(worker_id=WORKER_ID,
                         parent_version="native-base", version_id="native-alt")
        # Different real edition fingerprint, same mathematical algorithm.
        alt = (self.data / "workstation" / WORKER_ID / "native-alt"
               / "finite_goal_priority.py")
        alt.write_text(alt.read_text() + "\n# no-op source edition contrast\n")
        self.jobs = []

    def admitted(self, candidate, task, *, execute=True, changed=False):
        input_data = copy.deepcopy(INPUT)
        if task == "task-two":
            input_data["required_action"] = "A"
        if changed:
            input_data["required_action"] = "A" if task == "task-one" else "B"
        req = self.data.parent / f"{candidate}-{task}-{len(self.jobs)}.json"
        req.write_text(json.dumps(input_data))
        job = f"real-{candidate}-{task}-{len(self.jobs)}"
        edition = "native-base" if candidate == "baseline" else "native-alt"
        adm = admit_finite(
            data_dir=self.data, version_id=edition,
            inputs_file=req, job_id=job, confirm_admit=job,
            from_actor="isolated-native-frontier-test",
        )
        self.assertEqual(adm["status"], "READY")
        if execute:
            done = run_job(data_dir=self.data, job_id=job, confirm_execute=job)
            self.assertEqual(done["status"], "COMPLETE")
        case = NativeCase(candidate=candidate, task_id=task, job_id=job)
        self.jobs.append(case)
        return case

    def all_jobs(self):
        for c in ("baseline", "alternate"):
            for task in ("task-one", "task-two"):
                self.admitted(c, task)

    def report(self, cases=None):
        return native_decision_frontier(
            data_dir=self.data,
            cases=self.jobs if cases is None else cases,
            required_tasks=("task-one", "task-two"),
        )

    def test_reverify_four_real_native_jobs_and_preserve_shared_journal(self):
        self.all_jobs()
        before = (self.data / "runtime.jsonl").read_bytes()
        first = self.report()
        self.assertEqual(first["status"], "COMPLETE_FOR_DECLARED_TASKS")
        self.assertEqual(first["verified_frontier"], ["alternate", "baseline"])
        self.assertEqual(first["verified_count"], 2)
        self.assertEqual(len(first["observed_native_jobs"]), 4)
        self.assertTrue(first["only_native_reverification"])
        self.assertEqual(first["report_sha256"], self.report()["report_sha256"])
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())
        self.assertFalse((self.data / "preferred_editions.jsonl").exists())
        for c in self.jobs:
            self.assertEqual(job_view(data_dir=self.data, job_id=c.job_id)["status"],
                             "COMPLETE")

    def test_ready_job_cannot_be_scored_or_executed(self):
        pending = self.admitted("baseline", "task-one", execute=False)
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "COMPLETE"):
            self.report()
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())
        self.assertEqual(job_view(data_dir=self.data, job_id=pending.job_id)
                         ["status"], "READY")

    def test_same_task_with_changed_inputs_cannot_be_compared(self):
        self.admitted("baseline", "task-one")
        self.admitted("alternate", "task-one", changed=True)
        with self.assertRaisesRegex(ValueError, "test setup or scoring metric"):
            native_decision_frontier(
                data_dir=self.data, cases=self.jobs,
                required_tasks=("task-one",))

    def test_source_mutation_after_real_execution_refused(self):
        case = self.admitted("alternate", "task-one")
        target = (self.data / "workstation" / WORKER_ID / "native-alt"
                  / "finite_required_edge_guard.py")
        target.write_text(target.read_text() + "\n# stale source\n")
        with self.assertRaisesRegex(ValueError, "original source|source changed"):
            native_decision_frontier(
                data_dir=self.data, cases=[case],
                required_tasks=("task-one",))

    def test_one_job_cannot_be_counted_twice(self):
        case = self.admitted("baseline", "task-one")
        with self.assertRaisesRegex(ValueError, "more than once"):
            native_decision_frontier(
                data_dir=self.data, cases=[case, case],
                required_tasks=("task-one",))

    def test_unrecorded_job_not_invented(self):
        with self.assertRaises((ValueError, KeyError)):
            native_decision_frontier(
                data_dir=self.data,
                cases=[NativeCase("baseline", "task-one", "ghost-job")],
                required_tasks=("task-one",))


if __name__ == "__main__":
    unittest.main()
