"""Real process observations control the next finite A/B cluster movement."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.ab_relational_cluster import (
    _canonical, _hash, _independent_step, advance, read_history,
)


class ABRelationalClusterTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.data = Path(temp.name)
        self.journal = self.data / "ab_relational_cluster.jsonl"

    def test_only_explicit_invocation_starts_any_worker(self):
        with self.assertRaises(PermissionError):
            advance(self.data)
        self.assertFalse(self.journal.exists())

    def test_first_wave_branches_and_next_is_caused_by_results(self):
        first = advance(self.data, execute=True, workers=3)
        self.assertEqual(first["workers_started"], 1)
        self.assertEqual(first["branches"], 2)
        self.assertEqual(first["connections"], 0)
        self.assertEqual(first["known_states"], 3)
        self.assertEqual(first["pending"], 2)
        second = advance(self.data, execute=True, workers=3)
        self.assertEqual(second["workers_started"], 2)
        self.assertEqual(second["paths"], ["A", "B"])
        self.assertEqual(len(set(second["process_ids"])), 2)
        self.assertEqual(second["known_states"], 7)
        self.assertEqual(second["branches"], 4)

    def test_actual_independent_paths_connect_on_witnessed_collision(self):
        advance(self.data, execute=True)
        advance(self.data, execute=True)
        third = advance(self.data, execute=True)
        self.assertGreater(third["connections"], 0)
        lines = [json.loads(s) for s in self.journal.read_text().splitlines()]
        witnessed = [m for m in lines[2]["movements"]
                     if m["kind"] == "CONNECTION"]
        self.assertTrue(any(x["word"] == "AAA" and x["existing_word"] == ""
                            and x["to"] == [0, 0, 0] for x in witnessed))
        self.assertTrue(all(x["word"] != x["existing_word"] for x in witnessed))
        replayed, _ = read_history(self.journal)
        self.assertEqual(replayed["connections"], third["connections"])

    def test_restart_moves_frontier_not_first_work_again(self):
        a = advance(self.data, execute=True)
        before = self.journal.read_bytes()
        state, head = read_history(self.journal)
        self.assertEqual(state["events"], 1)
        self.assertEqual(len(head), 64)
        self.assertEqual(self.journal.read_bytes(), before)
        b = advance(self.data, execute=True)
        self.assertEqual(b["paths"], ["A", "B"])
        self.assertNotEqual(b["entry_hash"], a["entry_hash"])
        self.assertEqual(read_history(self.journal)[0]["events"], 2)

    def test_changed_worker_result_cannot_manufacture_a_connection(self):
        advance(self.data, execute=True)
        lines = [json.loads(s) for s in self.journal.read_text().splitlines()]
        row = lines[0]
        row["movements"][0]["kind"] = "CONNECTION"
        row["movements"][0]["existing_word"] = ""
        row["entry_hash"] = _hash({k: v for k, v in row.items() if k != "entry_hash"})
        self.journal.write_text(_canonical(row) + "\n")
        with self.assertRaisesRegex(ValueError, "independent A/B replay"):
            read_history(self.journal)

    def test_deleting_parent_or_mutating_state_fails_replay(self):
        advance(self.data, execute=True)
        row = json.loads(self.journal.read_text())
        row["expanded_paths"] = ["nonexistent"]
        row["entry_hash"] = _hash({k: v for k, v in row.items() if k != "entry_hash"})
        self.journal.write_text(_canonical(row) + "\n")
        with self.assertRaisesRegex(ValueError, "frontier"):
            read_history(self.journal)

    def test_duplicate_json_property_rejected(self):
        self.journal.write_text('{"x":1,"x":2}\n')
        with self.assertRaisesRegex(ValueError, "JSON"):
            read_history(self.journal)

    def test_depth_wall_cannot_be_misreported_as_new_relation(self):
        advance(self.data, execute=True, depth=1)
        result = advance(self.data, execute=True, depth=1)
        self.assertEqual(result["status"], "QUIET")
        self.assertEqual(result["workers_started"], 0)
        self.assertEqual(result["known_states"], 3)
        self.assertEqual(result["pending"], 0)

    def test_invalid_process_and_depth_budgets(self):
        with self.assertRaises(ValueError):
            advance(self.data, execute=True, workers=0)
        with self.assertRaises(ValueError):
            advance(self.data, execute=True, depth=0)
        self.assertFalse(self.journal.exists())

    def test_math_uses_distinct_relations_not_always_commuting(self):
        origin = (0, 0, 0)
        ab = _independent_step(_independent_step(origin, "A"), "B")
        ba = _independent_step(_independent_step(origin, "B"), "A")
        self.assertNotEqual(ab, ba)
        self.assertEqual(_independent_step((2, 0, 0), "A"), origin)


if __name__ == "__main__":
    unittest.main()
