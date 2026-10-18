"""Original browser game must produce actual source-owned temporal P2 test."""
import importlib.util
import json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.nih_game_test_bridge import JOB_ID,WORKER_ID,validate_request
from systems.workspace.nih_game_test_temporal_join import join
from systems.workspace.controls import reverify_job

class GameBackedTemporalP2Tests(unittest.TestCase):
    def setUp(self):
        temp=TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.data=Path(temp.name)/"native"
        self.out=Path(temp.name)/"artifacts"

    @unittest.skipUnless(importlib.util.find_spec("playwright") is not None,
                         "actual browser test runs in dedicated Chromium workflow")
    def test_01_actual_game_results_independently_replayed_into_nih_p2_test(self):
        proof=join(data_dir=self.data,output_dir=self.out)
        self.assertEqual(proof["native_jobs"],11)
        self.assertEqual(proof["NIH_P2_TEST"],"WITNESSED")
        self.assertTrue(proof["original_browser_queries_independently_replayed"])
        self.assertGreaterEqual(proof["actual_game_query_count"],4)
        self.assertEqual(proof["next_admissible_checkpoint"],"NIH-P2-BENCHMARK")
        self.assertFalse(proof["benchmark_witnessed"])
        self.assertFalse(proof["official_NIH_submission"])
        runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        self.assertEqual(len(runtime.snapshot()),11)
        h=runtime.get(JOB_ID)
        self.assertEqual(h.metadata["worker_id"],WORKER_ID)
        self.assertEqual(h.metadata["checkpoint_contract"],"NIH-P2-TEST")
        self.assertEqual(h.dependencies,("nih-packet-001","nih-prototype-001",
                                        "game-worker-ready-joined-001","live-game-temporal-001"))
        self.assertEqual(reverify_job(data_dir=self.data,job_id=JOB_ID)["status"],"COMPLETE")
        graph=json.loads((self.out/"game-temporal-cp-frontier.json").read_text())
        self.assertIn("NIH-P2-TEST",graph["witnessed"])
        self.assertNotIn("NIH-P2-BENCHMARK",graph["witnessed"])
        before=(self.data/"runtime.jsonl").read_bytes()
        links=(self.data/"coordinator-windows.jsonl").read_bytes()
        self.assertEqual(proof,join(data_dir=self.data,output_dir=self.out))
        self.assertEqual(before,(self.data/"runtime.jsonl").read_bytes())
        self.assertEqual(links,(self.data/"coordinator-windows.jsonl").read_bytes())
        log=self.out/"game-temporal-query-events.jsonl"
        rows=log.read_text().splitlines()
        row=json.loads(rows[0])
        row["result"]["future_leakage_ids"]=[]
        rows[0]=json.dumps(row)
        log.write_text("\n".join(rows)+"\n")
        with self.assertRaises(ValueError):
            join(data_dir=self.data,output_dir=self.out)

    def test_02_reject_undocumented_non_synthetic_requests(self):
        with self.assertRaises(ValueError):
            validate_request({"kind":"native-game-backed-temporal-test/v1","synthetic":False})
        with self.assertRaises(ValueError):
            validate_request({"kind":"native-game-backed-temporal-test/v1","synthetic":True,
                              "official_submission":True})

if __name__=="__main__":
    unittest.main()
