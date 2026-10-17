"""An evidence index cannot be promoted into fake runtime jobs."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.research_observatory import ROOT, SCHEMA, research_snapshot


class OriginalResearchTests(unittest.TestCase):
    def test_existing_one_month_records_are_preserved(self):
        source=research_snapshot()
        self.assertEqual(source["schema"],SCHEMA)
        self.assertTrue(source["read_only"])
        self.assertGreater(source["totals"]["source_files"],source["totals"]["structured_records"])
        self.assertEqual(source["totals"]["structured_records"],len(source["source_records"]))
        self.assertTrue(any(x["path"].endswith("ARC3-TRACE-001/dive.json")
                            and x["state"]=="MOVE_WITH_WALL" for x in source["source_records"]))
        self.assertTrue(any(x["kind"]=="CHECKPOINT" and "CP-0030" in x["path"]
                            for x in source["source_records"]))
        self.assertTrue(any(x["kind"]=="EXPERIMENT" and "FM-002" in x["path"]
                            for x in source["source_records"]))
        self.assertTrue(any("systems/workspace/WORLD_W13_MOVEMENT_01.md" in row["paths"]
                            for row in source["sections"]))
        self.assertTrue(any("language/SEPARATIONS.md" in row["paths"]
                            for row in source["sections"]))
        self.assertTrue(any("network/tests/test_arc_like_inverse_ab.py" in row["paths"]
                            for row in source["sections"]))
        self.assertGreater(source["totals"]["documented_wall_headings"],0)
        self.assertGreater(source["totals"]["documented_movement_headings"],0)
        self.assertTrue(any("systems/workspace/WORLD_W13_MOVEMENT_01.md"==x["path"]
                            for x in source["documented_marks"]))

    def test_explicit_status_not_filename_or_pretend_test_pass(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            dive=root/"research/dives/ARC3-TRACE-001/dive.json"
            dive.parent.mkdir(parents=True)
            dive.write_text(json.dumps({"schema_version":1,"title":"Observed A/B work",
              "result_state":"MOVE_WITH_WALL","walls":["One native missing relationship"],
              "next_movement":"Find the exact source"}))
            file=root/"systems/workspace/AN_UNVERIFIED_WALL.md"
            file.parent.mkdir(parents=True)
            file.write_text("## WALL\nThis is a prose document, not a recorded runtime WALL.\n")
            report=research_snapshot(root)
            self.assertEqual(report["totals"]["explicit_move_states"],1)
            self.assertEqual(report["totals"]["explicit_wall_entries"],1)
            self.assertEqual(report["totals"]["structured_records"],1)
            self.assertEqual(report["totals"]["source_files"],2)
            self.assertEqual(report["totals"]["documented_wall_headings"],1)
            self.assertEqual(report["totals"]["documented_movement_headings"],0)
            self.assertNotIn(file.as_posix(),[x["path"] for x in report["source_records"]])
            self.assertFalse((root/"runtime/data").exists())

    def test_original_source_tree_is_never_modified(self):
        original=[ROOT/"research/dives/ARC3-TRACE-001/dive.json",
                  ROOT/"state/pins/GEMS-001_2026-10-03.json"]
        before=[x.read_bytes() for x in original]
        research_snapshot()
        self.assertEqual(before,[x.read_bytes() for x in original])

    def test_stale_historical_pointer_is_not_active_directive(self):
        source=research_snapshot()
        old=next(x for x in source["source_records"] if x["path"]=="state/current.json")
        self.assertEqual(old["kind"],"HISTORICAL_POINTER")
        self.assertEqual(old["walls"],[])
        self.assertIn("Historical non-current",old["boundary"])
        self.assertNotEqual(old["scope"],"Active current focus")

    def test_missing_native_result_stays_failure_not_automatic_move(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            p=root/"research/dives/EX-01/dive.json"
            p.parent.mkdir(parents=True)
            p.write_text(json.dumps({"title":"Unknown", "walls":[]}))
            with self.assertRaises(ValueError):
                research_snapshot(root)


if __name__=="__main__":
    unittest.main()
