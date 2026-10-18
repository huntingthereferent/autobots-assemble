"""Exact original W13 CP becomes a real witnessed job in temporal game stack."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest,json

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.game_w13_temporal_join import join,JOB
from systems.workspace.controls import reverify_job

class GameW13TemporalJoinTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data=Path(tmp.name)/"native"
        self.out=Path(tmp.name)/"artifacts"

    def test_01_original_w13_native_game_witnessed_in_same_temporal_stack(self):
        result=join(data_dir=self.data,output_dir=self.out,with_browser=False)
        self.assertTrue(result["w13_worlds_witnessed"])
        self.assertEqual(result["w13_worlds_completed"],2)
        self.assertEqual(result["native_w12_independent_replay"],"PASS")
        self.assertEqual(result["real_original_native_jobs"],8)
        self.assertEqual(result["next_game_checkpoint"],"GAME-NATIVE-VERIFIER")
        self.assertEqual(result["formal_nih_p2_test"],"BLOCKED")
        self.assertIn("GAME-WORKER-READY",result["formal_blocked_by"])
        self.assertEqual(result["live_game_browser"],"NOT_RUN")
        rt=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        self.assertEqual(len(rt.snapshot()),8)
        self.assertEqual(rt.get(JOB).metadata["checkpoint_contract"],"GAME-W13-WORLDS")
        self.assertEqual(rt.state(JOB).status,"COMPLETE")
        self.assertEqual(reverify_job(data_dir=self.data,job_id=JOB)["status"],"COMPLETE")
        cp=json.loads((self.out/"game-temporal-cp-frontier.json").read_text())
        self.assertIn("GAME-W13-WORLDS",cp["witnessed"])
        self.assertNotIn("GAME-WORKER-READY",cp["witnessed"])
        self.assertNotIn("NIH-P2-TEST",cp["witnessed"])

    def test_02_restarts_do_not_duplicate_game_worker_admission_or_journals(self):
        initial=join(data_dir=self.data,output_dir=self.out,with_browser=False)
        journal=(self.data/"runtime.jsonl").read_bytes()
        index=(self.data/"coordinator-windows.jsonl").read_bytes()
        again=join(data_dir=self.data,output_dir=self.out,with_browser=False)
        self.assertEqual(initial,again)
        self.assertEqual(journal,(self.data/"runtime.jsonl").read_bytes())
        self.assertEqual(index,(self.data/"coordinator-windows.jsonl").read_bytes())

    def test_03_original_w13_source_mutation_refuses_reverification(self):
        join(data_dir=self.data,output_dir=self.out,with_browser=False)
        from systems.workspace.workstation import ProcessWorkstation
        desk=ProcessWorkstation(self.data/"workstation")
        source=desk._edition("game-worlds-w13","world-v1")/"game_worlds_worker.py"
        source.write_text(source.read_text()+"\n# mutation\n")
        with self.assertRaises(ValueError):
            reverify_job(data_dir=self.data,job_id=JOB)

if __name__=="__main__":
    unittest.main()
