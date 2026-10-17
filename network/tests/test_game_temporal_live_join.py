"""New game-temporal worker must build live interaction and return it to SAME journal."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.game_temporal_bridge import JOB_ID,WORKER_ID
from systems.workspace.game_temporal_stack import continue_stack

class LiveTemporalGameTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.data=Path(t.name)/"same-native-workstation"
        self.output=Path(t.name)/"artifacts"

    def test_01_actual_game_calls_prototype_during_browser_moves(self):
        result=continue_stack(data_dir=self.data,output_dir=self.output,real_browser=True)
        self.assertEqual(result["source_owned_jobs"],7)
        self.assertEqual(result["game_temporal_browser"],"PASS")
        self.assertGreaterEqual(result["game_to_real_python_queries"],5)
        self.assertTrue(result["source_owned_witness"])
        self.assertEqual(result["new_native_build"],JOB_ID)
        self.assertFalse(result["formally_witnessed_nih_p2_test"])
        self.assertEqual(result["formal_cp_status"],"BLOCKED")
        self.assertIn("GAME-WORKER-READY",result["formal_cp_blocked_by"])
        rt=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        parent=rt.get(JOB_ID)
        self.assertEqual(parent.metadata["worker_id"],WORKER_ID)
        self.assertEqual(parent.dependencies,("build-game-room-v1","nih-prototype-001"))
        events=[e for e in rt.event_store.for_handoff(JOB_ID)
                if e.event_type=="GAME_TEMPORAL_LIVE_BROWSER_RETURNED"]
        self.assertEqual(len(events),1)
        self.assertEqual(events[0].data["original_prototype_job"],"nih-prototype-001")
        self.assertEqual(events[0].data["original_game_job"],"build-game-room-v1")
        observations=[json.loads(s) for s in
            (self.output/"game-temporal-query-events.jsonl").read_text().splitlines()]
        self.assertTrue(any(e["result"]["future_leakage_ids"]==["delayed-result"] for e in observations))
        self.assertTrue(any(e["result"]["temporal_ids"]==["delayed-result","prior-note"] for e in observations))
        self.assertTrue((self.output/"game-temporal-browser-witness.png").is_file())

    def test_02_source_editions_replay_without_duplicate_native_jobs(self):
        one=continue_stack(data_dir=self.data,output_dir=self.output,real_browser=False)
        journal=(self.data/"runtime.jsonl").read_bytes()
        links=(self.data/"coordinator-windows.jsonl").read_bytes()
        two=continue_stack(data_dir=self.data,output_dir=self.output,real_browser=False)
        self.assertEqual(one,two)
        self.assertEqual(journal,(self.data/"runtime.jsonl").read_bytes())
        self.assertEqual(links,(self.data/"coordinator-windows.jsonl").read_bytes())

    def test_03_tampered_generated_game_relation_refused(self):
        continue_stack(data_dir=self.data,output_dir=self.output,real_browser=False)
        from systems.workspace.workstation import ProcessWorkstation
        from systems.workspace.controls import reverify_job
        desk=ProcessWorkstation(self.data/"workstation")
        source=desk._edition(WORKER_ID,"live-v1")/"live_join_worker.py"
        source.write_text(source.read_text()+"\n# tampered\n")
        with self.assertRaises(ValueError):
            reverify_job(data_dir=self.data,job_id=JOB_ID)

if __name__=="__main__":
    unittest.main()
