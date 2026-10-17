"""Single-host multi-process A/B finite-world computation and replay boundaries."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.ab_math_cluster import (
    DEFAULT_PHIS, _classes, _reference_graph, _verify_graphs,
    read_receipts, run_cluster,
)


class ABMathClusterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_real_processes_verify_nine_worlds_and_five_classes(self):
        out = run_cluster(data_dir=self.root, execute=True, workers=3)
        self.assertFalse(out["reused"])
        self.assertEqual(out["workers_started"], 3)
        row = out["receipt"]
        self.assertEqual(len(row["graphs"]), 9)
        self.assertEqual(len(row["classes"]), 5)
        self.assertEqual(len(row["process_ids"]), 3)
        self.assertEqual(len(set(row["process_ids"])), 3)
        self.assertEqual(len(read_receipts(self.root / "ab_math_cluster.jsonl")), 1)
        self.assertIn([[0, 1, 2], [0, 2, 1]], row["classes"])

    def test_restart_does_not_spawn_or_duplicate(self):
        a = run_cluster(data_dir=self.root, execute=True, workers=2)
        before = (self.root / "ab_math_cluster.jsonl").read_bytes()
        b = run_cluster(data_dir=self.root, execute=True, workers=4)
        self.assertTrue(b["reused"])
        self.assertEqual(b["workers_started"], 0)
        self.assertEqual(a["receipt"], b["receipt"])
        self.assertEqual(before, (self.root / "ab_math_cluster.jsonl").read_bytes())

    def test_explicit_invocation_and_input_bounds(self):
        with self.assertRaises(PermissionError):
            run_cluster(data_dir=self.root)
        self.assertFalse(self.root.exists() and list(self.root.iterdir()))
        for invalid in ((0, 0, 0), ((0, 1, 0), (0, 1, 0)), ((0, 3, 0),), ((1, 0, 0),), ()):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                run_cluster(data_dir=self.root, execute=True, phis=invalid)
        with self.assertRaises(ValueError):
            run_cluster(data_dir=self.root, execute=True, workers=0)

    def test_fabricated_worker_edges_fail_independent_replay(self):
        row = _reference_graph((0, 1, 2))
        row["edges"][0][2] = [2, 2, 2]
        with self.assertRaisesRegex(ValueError, "independent"):
            _verify_graphs(((0, 1, 2),), [row])
        self.assertFalse((self.root / "ab_math_cluster.jsonl").exists())

    def test_replay_rejects_tampering_even_with_recomputed_hash(self):
        from systems.workspace.ab_math_cluster import _digest, _json
        run_cluster(data_dir=self.root, execute=True)
        path = self.root / "ab_math_cluster.jsonl"
        item = json.loads(path.read_text())
        item["classes"] = []
        item["receipt_hash"] = _digest({k: v for k, v in item.items() if k != "receipt_hash"})
        path.write_text(_json(item) + "\n")
        with self.assertRaisesRegex(ValueError, "class correspondence"):
            read_receipts(path)

    def test_duplicate_json_keys_fail(self):
        path = self.root / "ab_math_cluster.jsonl"
        path.write_text('{"a":1,"a":2}\n')
        with self.assertRaisesRegex(ValueError, "JSON"):
            read_receipts(path)

    def test_alignment_is_not_word_or_projection_similarity(self):
        self.assertEqual(_classes(DEFAULT_PHIS), [
            [[0, 0, 0]], [[0, 0, 1], [0, 0, 2]],
            [[0, 1, 0], [0, 2, 0]], [[0, 1, 1], [0, 2, 2]],
            [[0, 1, 2], [0, 2, 1]],
        ])

    def test_no_native_job_claim_and_second_set_of_worlds(self):
        a = run_cluster(data_dir=self.root, execute=True, phis=((0, 0, 0), (0, 1, 2)))
        b = run_cluster(data_dir=self.root, execute=True, phis=((0, 0, 0), (0, 1, 0)))
        self.assertEqual(b["receipt"]["previous_hash"], a["receipt"]["receipt_hash"])
        self.assertEqual(len(read_receipts(self.root / "ab_math_cluster.jsonl")), 2)
        self.assertFalse((self.root / "runtime.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
