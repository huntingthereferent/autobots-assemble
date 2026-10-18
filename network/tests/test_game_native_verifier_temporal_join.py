"""Real GAME-NATIVE-VERIFIER source worker and CP boundary in original journal."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json,unittest
from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.game_native_verifier_temporal_join import join
from systems.workspace.game_native_verifier_bridge import JOB_ID,WORKER_ID
from systems.workspace.controls import reverify_job

class NativeGameVerifierCompleteStackTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data=Path(tmp.name)/"native"
        self.art=Path(tmp.name)/"artifacts"

    def test_01_new_independent_game_witness_is_a_real_ninth_job(self):
        result=join(data_dir=self.data,output_dir=self.art,with_browser=False)
        self.assertEqual(result["native_jobs"],9)
        self.assertTrue(result["game_native_verifier_witnessed"])
        self.assertEqual(result["source_owned_game_verifier"],JOB_ID)
        self.assertEqual(result["next_admissible_game_cp"],"GAME-WORKER-READY")
        self.assertEqual(result["phase_2_test"],"BLOCKED")
        self.assertEqual(result["phase_2_blocked_by"],["GAME-WORKER-READY"])
        rt=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        self.assertEqual(len(rt.snapshot()),9)
        self.assertEqual(rt.get(JOB_ID).metadata["worker_id"],WORKER_ID)
        self.assertEqual(rt.get(JOB_ID).metadata["checkpoint_contract"],"GAME-NATIVE-VERIFIER")
        self.assertEqual(rt.get(JOB_ID).dependencies,("game-w13-cp-joined-001",))
        self.assertEqual(rt.state(JOB_ID).status,"COMPLETE")
        self.assertEqual(reverify_job(data_dir=self.data,job_id=JOB_ID)["status"],"COMPLETE")
        graph=json.loads((self.art/"game-temporal-cp-frontier.json").read_text())
        self.assertIn("GAME-W13-WORLDS",graph["witnessed"])
        self.assertIn("GAME-NATIVE-VERIFIER",graph["witnessed"])
        self.assertNotIn("GAME-WORKER-READY",graph["witnessed"])
        self.assertNotIn("NIH-P2-TEST",graph["witnessed"])

    def test_02_restart_reuses_original_all_nine_jobs_without_reexecution(self):
        first=join(data_dir=self.data,output_dir=self.art,with_browser=False)
        j=(self.data/"runtime.jsonl").read_bytes()
        i=(self.data/"coordinator-windows.jsonl").read_bytes()
        second=join(data_dir=self.data,output_dir=self.art,with_browser=False)
        self.assertEqual(first,second)
        self.assertEqual(j,(self.data/"runtime.jsonl").read_bytes())
        self.assertEqual(i,(self.data/"coordinator-windows.jsonl").read_bytes())

    def test_03_tampered_independent_game_witness_revokes_CP(self):
        join(data_dir=self.data,output_dir=self.art,with_browser=False)
        from systems.workspace.workstation import ProcessWorkstation
        desk=ProcessWorkstation(self.data/"workstation")
        source=desk._edition(WORKER_ID,"witness-v1")/"native_verifier.py"
        source.write_text(source.read_text()+"\n# forged change\n")
        with self.assertRaises(ValueError):
            reverify_job(data_dir=self.data,job_id=JOB_ID)

if __name__=="__main__":
    unittest.main()
