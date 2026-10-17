"""One Complete Stack actually executes the existing NIH temporal workers and game BUILDER."""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.nih_temporal_game_stack import join


class NIHTemporalGameStackTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name) / "shared-native"
        self.out = Path(tmp.name) / "created"

    def test_01_real_nih_workers_and_game_build_share_original_native_runtime(self):
        result = join(data_dir=self.data, output_dir=self.out)
        self.assertEqual(result["witnessed_nih_phase_1"], [
            "NIH-P1-ONTOLOGY", "NIH-P1-REASONING", "NIH-P1-SCOPE"])
        self.assertEqual(result["next_phase_1"], "NIH-P1-PACKET")
        self.assertEqual(result["phase_2_test"], "BLOCKED")
        self.assertIn("NIH-P1-PACKET", result["phase_2_test_blocked_by"])
        self.assertTrue(result["one_native_workstation"])
        self.assertTrue(result["synthetic_only"])
        self.assertEqual(result["game_native_build"], "COMPLETE")
        self.assertEqual(result["game_browser_witness"], "NOT_RUN")
        self.assertTrue((self.out / "built-world-room.html").is_file())
        journal = HandoffRuntime(event_store=RuntimeJournal(self.data / "runtime.jsonl"))
        self.assertEqual(len(journal.snapshot()), 4)
        for job in result["exact_nih_jobs"] + [result["native_game_build_job"]]:
            self.assertEqual(journal.state(job).status, "COMPLETE")

    def test_02_restart_does_not_reexecute_any_native_job(self):
        first = join(data_dir=self.data, output_dir=self.out)
        before = (self.data / "runtime.jsonl").read_bytes()
        indexes = (self.data / "coordinator-windows.jsonl").read_bytes()
        second = join(data_dir=self.data, output_dir=self.out)
        self.assertEqual(first, second)
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)
        self.assertEqual((self.data / "coordinator-windows.jsonl").read_bytes(), indexes)

    def test_03_damaged_temporal_source_refuses_inherited_success(self):
        join(data_dir=self.data, output_dir=self.out)
        from systems.workspace.workstation import ProcessWorkstation
        desk = ProcessWorkstation(self.data / "workstation")
        src = desk._edition("nih-temporal-reasoning", "reasoning-v1") / "reasoning_worker.py"
        src.write_text(src.read_text() + "\n# unauthorized mutation\n")
        with self.assertRaises(ValueError):
            join(data_dir=self.data, output_dir=self.out)

if __name__ == "__main__":
    unittest.main()
