"""Fixture-only contract tests. These do not claim real agent improvement."""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.contrastive_harness import (
    Probe, Verdict, contrast_and_record, pin_supported_candidate,
)
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.workstation_harness import WorkstationContinuationHarness


class ContrastiveHarnessTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name)
        source = self.data / "source"
        source.mkdir()
        (source / "worker.py").write_text("MODE = 'baseline'\n")
        self.desk = ProcessWorkstation(self.data / "workstation")
        self.worker = "fixture-harness-worker"
        self.desk.copy_source(source, worker_id=self.worker, version_id="base",
                              source_locator="fixture:local-source")
        self.desk.branch(worker_id=self.worker, parent_version="base",
                         version_id="candidate")
        candidate_file = self.data / "workstation" / self.worker / "candidate" / "worker.py"
        candidate_file.write_text("MODE = 'candidate'\n")
        self.h = WorkstationContinuationHarness(
            self.data, verify_observation=lambda o: False,
            verify_connection=lambda a, b: False)
        self.h.seed_lane("trial-lane", "one bounded harness task")
        self.calls = []
        self.allowed = {"native-base", "native-candidate"}
        common = dict(worker_id=self.worker, task_id="task-one",
                      input_sha256=sha256(b"same native inputs").hexdigest(),
                      model_id="ab-ai-builder", execution_mode="continuous",
                      agent_profile_sha256=sha256(b"fixed AB runtime and profile").hexdigest())
        self.base = Probe(
            job_id="native-base", version_id="base",
            source_sha256=self.desk.inspect(worker_id=self.worker, version_id="base")[
                "current_fingerprint"],
            result_sha256=sha256(b"base-result").hexdigest(),
            witness_ref="native:base-witness", **common)
        self.candidate = Probe(
            job_id="native-candidate", version_id="candidate",
            source_sha256=self.desk.inspect(worker_id=self.worker, version_id="candidate")[
                "current_fingerprint"],
            result_sha256=sha256(b"candidate-result").hexdigest(),
            witness_ref="native:candidate-witness", **common)

    def verify(self, probe):
        self.calls.append(probe.job_id)
        return probe.job_id in self.allowed

    def compare(self, base, candidate):
        self.calls.append("comparison")
        return Verdict("IMPROVED", "native:separate-contrast-witness",
                       "fixture:one-task-only")

    def args(self):
        return dict(data_dir=self.data, lane_id="trial-lane",
                    worker_id=self.worker, base_version="base",
                    candidate_version="candidate", component="tool-guidance",
                    base=self.base, candidate=self.candidate,
                    verify_probe=self.verify, compare_native=self.compare)

    def journal(self):
        runtime = HandoffRuntime(event_store=RuntimeJournal(self.data / "runtime.jsonl"))
        lane = WorkstationContinuationHarness._resolve_lane(runtime, "trial-lane")
        return [e for e in runtime.event_store.for_handoff(lane.handoff_id)
                if e.event_type == "WORKSTATION_HARNESS_CONTRAST"]

    def test_fresh_pair_records_once_and_rechecks_on_retry(self):
        first = contrast_and_record(**self.args())
        self.assertEqual(first["status"], "SUPPORTED")
        self.assertEqual(first["scope"], "one-matched-task")
        self.assertFalse(first["selection_performed"])
        self.assertFalse(first["execution_started"])
        self.assertFalse(first["already_recorded"])
        self.assertEqual(len(self.journal()), 1)
        second = contrast_and_record(**self.args())
        self.assertEqual(first["contrast_id"], second["contrast_id"])
        self.assertTrue(second["already_recorded"])
        self.assertEqual(len(self.journal()), 1)
        self.assertEqual(self.calls.count("native-base"), 2)
        self.assertEqual(self.calls.count("native-candidate"), 2)

    def test_unverified_candidate_remains_unknown_and_cannot_pin(self):
        self.allowed.remove("native-candidate")
        result = contrast_and_record(**self.args())
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["outcome"], "UNVERIFIED")
        self.assertNotIn("comparison", self.calls)
        with self.assertRaises(ValueError):
            pin_supported_candidate(approved=True, actor_id="operator", **self.args())
        self.assertFalse((self.data / "preferred_editions.jsonl").exists())

    def test_different_input_or_task_not_compared(self):
        for candidate in (
            replace(self.candidate, task_id="task-two"),
            replace(self.candidate, input_sha256="f" * 64),
            replace(self.candidate, job_id=self.base.job_id),
        ):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    contrast_and_record(**{**self.args(), "candidate": candidate})
        self.assertEqual(self.calls, [])
        self.assertFalse(self.journal())

    def test_switching_agent_or_build_mode_invalidates_comparison(self):
        for candidate in (
            replace(self.candidate, execution_mode="codex-build"),
            replace(self.candidate, model_id="different-agent-model"),
            replace(self.candidate, agent_profile_sha256="f" * 64),
            replace(self.candidate, execution_surface="foreign-substrate"),
            replace(self.candidate, model_id="codex"),
        ):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    contrast_and_record(**{**self.args(), "candidate": candidate})
        self.assertEqual(self.calls, [])
        self.assertFalse(self.journal())

    def test_codex_cannot_become_the_common_executor_even_if_profiles_match(self):
        # Equally configured on paper is not a reason to switch the tested system
        # to a different agent's frozen instructions or build mode.
        bad_base = replace(self.base, execution_mode="codex-build")
        bad_candidate = replace(self.candidate, execution_mode="codex-build")
        with self.assertRaisesRegex(ValueError, "Codex"):
            contrast_and_record(**{**self.args(),
                                  "base": bad_base, "candidate": bad_candidate})
        self.assertEqual(self.calls, [])

    def test_source_mutation_invalidates_old_probe(self):
        p = self.data / "workstation" / self.worker / "candidate" / "worker.py"
        p.write_text(p.read_text() + "# altered after receipt\n")
        with self.assertRaisesRegex(ValueError, "stale"):
            contrast_and_record(**self.args())
        self.assertFalse(self.journal())

    def test_rejects_self_report_or_shared_comparator_witness(self):
        with self.assertRaises(ValueError):
            contrast_and_record(**{**self.args(), "compare_native":
                lambda a, b: Verdict("IMPROVED", a.witness_ref, "no independent witness")})
        with self.assertRaises(ValueError):
            contrast_and_record(**{**self.args(), "compare_native":
                lambda a, b: True})
        self.assertFalse(self.journal())

    def test_regression_is_not_supported(self):
        result = contrast_and_record(**{**self.args(), "compare_native":
            lambda a, b: Verdict("REGRESSED", "native:separate", "one task")})
        self.assertEqual(result["status"], "NO_PREFERENCE")
        with self.assertRaises(ValueError):
            pin_supported_candidate(approved=True, actor_id="operator",
                **{**self.args(), "compare_native":
                   lambda a, b: Verdict("REGRESSED", "native:separate", "one task")})

    def test_pin_requires_approval_and_existing_native_replay(self):
        with self.assertRaises(PermissionError):
            pin_supported_candidate(approved=False, actor_id="operator", **self.args())
        self.assertFalse(self.journal())
        # Even fixture-positive callbacks cannot make an unregistered worker
        # a native COMPLETE job. Only existing controls may promote.
        with self.assertRaises(ValueError):
            pin_supported_candidate(approved=True, actor_id="operator", **self.args())
        self.assertEqual(len(self.journal()), 1)
        self.assertFalse((self.data / "preferred_editions.jsonl").exists())

    def test_unknown_lane_fails_without_new_scheduling(self):
        with self.assertRaises(ValueError):
            contrast_and_record(**{**self.args(), "lane_id": "nonexistent"})
        self.assertFalse(self.journal())


if __name__ == "__main__":
    unittest.main()
