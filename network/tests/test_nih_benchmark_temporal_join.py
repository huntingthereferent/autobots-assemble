"""Independent source-bound Phase2 synthetic benchmark tests."""
import importlib.util
import json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.nih_benchmark_bridge import JOB_ID,WORKER_ID,validate_request,REQUEST
from systems.workspace.nih_benchmark_temporal_join import join
from systems.workspace.nih_benchmark_worker_source.benchmark_worker import compute
from systems.workspace.controls import run_job,reverify_job

class NIHBenchmarkTests(unittest.TestCase):
    def setUp(self):
        temp=TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.data=Path(temp.name)/"native"
        self.out=Path(temp.name)/"artifacts"

    def test_00_bounded_worker_compares_real_known_and_valid_time(self):
        rows=[
            {"id":"early","known_at":"2026-01-02","valid_from":"2026-01-04","valid_to":"2026-01-15"},
            {"id":"delayed-result","known_at":"2026-01-08","valid_from":"2026-01-04","valid_to":"2026-01-15"}
        ]
        queries=[{"known_at":f"2026-01-{d:02d}","target_at":f"2026-01-{t:02d}"}
                 for d in (1,3,7,9,16) for t in (3,4,10,14,15)]
        source={"kind":REQUEST["kind"],"synthetic":True,
                "queries":queries,"observations":rows,
                "query_history_sha256":"a"*64,"prototype_sha256":"b"*64}
        receipt=compute(source)
        self.assertEqual(receipt["query_count"],25)
        self.assertGreater(receipt["static_future_leakage_cases"],0)
        self.assertLess(receipt["static_future_leakage_cases"],25)
        self.assertEqual(receipt["temporal_leakage_ids_total"],0)
        self.assertFalse(receipt["official_nih_submission"])
        self.assertEqual(receipt["cases"][6]["future_leakage_ids"],["delayed-result"])
        with self.assertRaises(ValueError):
            compute({**source,"synthetic":False})
        with self.assertRaises(ValueError):
            compute({**source,"queries":queries+[queries[0]]})
        with self.assertRaises(ValueError):
            validate_request({**REQUEST,"official_nih_submission":True})

    @unittest.skipUnless(importlib.util.find_spec("playwright") is not None,
                         "actual native Chromium/temporal Python integration in dedicated workflow")
    def test_01_original_twelve_source_owned_jobs_and_no_duplicate_on_restart(self):
        result=join(data_dir=self.data,output_dir=self.out)
        self.assertEqual(result["native_jobs"],12)
        self.assertEqual(result["NIH_P2_BENCHMARK"],"WITNESSED")
        self.assertTrue(result["original_executable_and_source_oracle_checked"])
        self.assertGreaterEqual(result["new_boundary_queries_independently_executed"],20)
        self.assertGreater(result["static_future_leakage_cases"],0)
        self.assertEqual(result["temporal_leakage_ids_total"],0)
        self.assertFalse(result["official_NIH_submission"])
        runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        self.assertEqual(len(runtime.snapshot()),12)
        h=runtime.get(JOB_ID)
        self.assertEqual(h.metadata["worker_id"],WORKER_ID)
        self.assertEqual(h.metadata["checkpoint_contract"],"NIH-P2-BENCHMARK")
        self.assertEqual(h.dependencies,("nih-p2-game-test-001","nih-prototype-001"))
        self.assertEqual(reverify_job(data_dir=self.data,job_id=JOB_ID)["status"],"COMPLETE")
        graph=json.loads((self.out/"game-temporal-cp-frontier.json").read_text())
        self.assertIn("NIH-P2-BENCHMARK",graph["witnessed"])
        self.assertNotIn("NIH-P2-SUBMISSION",graph["witnessed"])
        before=(self.data/"runtime.jsonl").read_bytes()
        index=(self.data/"coordinator-windows.jsonl").read_bytes()
        self.assertEqual(result,join(data_dir=self.data,output_dir=self.out))
        self.assertEqual(before,(self.data/"runtime.jsonl").read_bytes())
        self.assertEqual(index,(self.data/"coordinator-windows.jsonl").read_bytes())
        with self.assertRaises(PermissionError):
            run_job(data_dir=self.data,job_id=JOB_ID,confirm_execute="wrong-job")
        src=self.data/"workstation"/WORKER_ID
        target=next(src.rglob("benchmark_worker.py"))
        target.write_text(target.read_text()+"\n# changed after native admission\n")
        with self.assertRaises(ValueError):
            reverify_job(data_dir=self.data,job_id=JOB_ID)

if __name__=="__main__":
    unittest.main()
