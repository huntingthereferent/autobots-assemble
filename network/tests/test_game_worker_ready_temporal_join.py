"""Real ten-job GAME-WORKER-READY admission and independent native checks."""
import json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.game_worker_ready_temporal_join import join
from systems.workspace.game_worker_ready_bridge import WORKER_ID,JOB_ID
from systems.workspace.controls import reverify_job,run_job

class GameReadyTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.data=Path(t.name)/"native"
        self.out=Path(t.name)/"artifacts"

    def test_01_actual_game_source_adapter_is_witnessed_after_w13_and_witness(self):
        proof=join(data_dir=self.data,output_dir=self.out,with_browser=False)
        self.assertEqual(proof["native_jobs"],10)
        self.assertTrue(proof["game_worker_ready_witnessed"])
        self.assertTrue(proof["independent_game_verifier_witnessed"])
        self.assertEqual(proof["next_admissible_NIH_checkpoint"],"NIH-P2-TEST")
        self.assertEqual(proof["nih_p2_test_state"],"ADMISSIBLE")
        self.assertFalse(proof["nih_p2_test_witnessed"])
        rt=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        child=rt.get(JOB_ID)
        self.assertEqual(child.metadata["worker_id"],WORKER_ID)
        self.assertEqual(child.metadata["checkpoint_contract"],"GAME-WORKER-READY")
        self.assertEqual(child.dependencies,("game-w13-cp-joined-001",
                         "game-native-verifier-joined-001","live-game-temporal-001"))
        self.assertEqual(rt.state(JOB_ID).status,"COMPLETE")
        self.assertEqual(reverify_job(data_dir=self.data,job_id=JOB_ID)["status"],"COMPLETE")
        graph=json.loads((self.out/"game-temporal-cp-frontier.json").read_text())
        self.assertIn("GAME-WORKER-READY",graph["witnessed"])
        self.assertNotIn("NIH-P2-TEST",graph["witnessed"])
        before=(self.data/"runtime.jsonl").read_bytes()
        with self.assertRaises(PermissionError):
            run_job(data_dir=self.data,job_id=JOB_ID,confirm_execute="anything-else")
        self.assertEqual(before,(self.data/"runtime.jsonl").read_bytes())

    def test_02_restart_does_not_reexecute_or_rebind(self):
        first=join(data_dir=self.data,output_dir=self.out,with_browser=False)
        journal=(self.data/"runtime.jsonl").read_bytes()
        index=(self.data/"coordinator-windows.jsonl").read_bytes()
        again=join(data_dir=self.data,output_dir=self.out,with_browser=False)
        self.assertEqual(first,again)
        self.assertEqual(journal,(self.data/"runtime.jsonl").read_bytes())
        self.assertEqual(index,(self.data/"coordinator-windows.jsonl").read_bytes())

    def test_03_mutated_game_ready_source_refuses_stale_native_cp(self):
        join(data_dir=self.data,output_dir=self.out,with_browser=False)
        from systems.workspace.workstation import ProcessWorkstation
        desk=ProcessWorkstation(self.data/"workstation")
        source=desk._edition(WORKER_ID,"adapter-v1")/"ready_worker.py"
        source.write_text(source.read_text()+"\n# tamper\n")
        with self.assertRaises(ValueError):
            reverify_job(data_dir=self.data,job_id=JOB_ID)

if __name__=="__main__":
    unittest.main()
