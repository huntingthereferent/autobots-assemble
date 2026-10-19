"""Actual packaged A/B tool integration into the existing Continuity worker."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.ab_tool_worker import ABToolWorkerBridge, ABToolWorkerError
from runtime.continuity_pool import connect_pool
from runtime.pool_evaluator import ContinuityPoolEvaluator
from runtime.service import EcosystemService

ROOT = Path(__file__).resolve().parents[2]


class ABToolNativeWorkerTests(unittest.TestCase):
    @staticmethod
    def record(rel="runtime/pool_evaluator.py", task="task-one"):
        return [{"task_id": task, "native_sources": [{
            "source": rel, "sha256": sha256((ROOT / rel).read_bytes()).hexdigest(),
        }]}]

    def test_actual_ab_tool_graph_and_ancestry_are_used(self):
        result = ABToolWorkerBridge(ROOT).inspect_task_sources(self.record())
        self.assertEqual(result["capability"], "ab-tool/provenance-graph-v1")
        self.assertEqual(result["graph"]["kind"], "ab-provenance/graph-v1")
        self.assertEqual(result["graph_summary"]["relations"], 1)
        self.assertEqual(result["graph"]["edges"][0]["state"], "referenced")
        self.assertEqual(len(result["task_ancestry"]["task-one"]["recorded_ancestor_edges"]), 1)
        self.assertFalse(result["graph_summary"]["independently_verified_by_this_tool"])
        self.assertFalse(result["completion_verified"])
        self.assertFalse(result["source_edits_performed"])

    def test_source_drift_or_unsafe_source_is_not_absorbed(self):
        bridge = ABToolWorkerBridge(ROOT)
        record = self.record()
        record[0]["native_sources"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ABToolWorkerError, "fingerprint"):
            bridge.inspect_task_sources(record)
        record = self.record()
        record[0]["native_sources"][0]["source"] = "../private.py"
        with self.assertRaises(ABToolWorkerError):
            bridge.inspect_task_sources(record)

    def test_duplicate_tasks_and_unbounded_inputs_refused(self):
        bridge = ABToolWorkerBridge(ROOT)
        repeated = self.record() * 2
        with self.assertRaisesRegex(ABToolWorkerError, "duplicate"):
            bridge.inspect_task_sources(repeated)
        with self.assertRaises(ABToolWorkerError):
            bridge.inspect_task_sources([])

    def test_original_worker_uses_real_ab_tool_in_same_agent_lineage(self):
        with TemporaryDirectory() as tmp:
            evaluator = ContinuityPoolEvaluator(ROOT, ab_tool=ABToolWorkerBridge(ROOT))
            service = EcosystemService(
                data_dir=tmp,
                repository_work_file=ROOT / "TASKS.md",
                ab_evaluator=evaluator,
            )
            evaluator.bind(service)
            original = connect_pool(service, ROOT)
            root = original["root"]
            event = service.runtime.event_store.for_handoff(root)[-1]
            self.assertEqual(event.event_type, "AGENT_AB_OBSERVED")
            self.assertEqual(event.data["status"], "UNKNOWN")
            projection = event.data["output"]["ab_tool_worker"]
            self.assertEqual(projection["status"], "SOURCE_REFERENCES_RECHECKED")
            self.assertEqual(len(projection["task_ids"]), 3)
            self.assertEqual(projection["graph_summary"]["relations"], 6)
            self.assertTrue(all(len(r["recorded_ancestor_edges"]) == 2
                                for r in projection["task_ancestry"].values()))
            self.assertFalse(projection["completion_verified"])
            self.assertEqual(event.data["output"]["task_results"], "NOT_EXECUTED")
            self.assertEqual(service.runtime.state(root).status, "READY")
            self.assertEqual(service.runtime.state(root).missing_witnesses, ("movement witness",))
            count = len(service.runtime.event_store.all())
            self.assertEqual(connect_pool(service, ROOT)["evaluator_run"], "REUSED")
            self.assertEqual(len(service.runtime.event_store.all()), count)

    def test_tool_failure_rejects_source_evidence_without_promoting_agent(self):
        class RejectedSource:
            def inspect_task_sources(self, _matches):
                raise ABToolWorkerError("original source changed")
        with TemporaryDirectory() as tmp:
            evaluator = ContinuityPoolEvaluator(ROOT, ab_tool=RejectedSource())
            service = EcosystemService(data_dir=tmp, ab_evaluator=evaluator)
            evaluator.bind(service)
            root = connect_pool(service, ROOT)["root"]
            event = service.runtime.event_store.for_handoff(root)[-1]
            self.assertEqual(event.data["status"], "UNKNOWN")
            self.assertEqual(event.data["output"]["ab_tool_worker"]["status"], "UNKNOWN")
            self.assertEqual(event.evidence, ())
            self.assertEqual(service.runtime.state(root).status, "READY")


if __name__ == "__main__":
    unittest.main()
