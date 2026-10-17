"""An external source adapter survives retirement of old opportunity wrappers."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from work.job_adapter import evaluate_job, load_all_jobs


class JobAdapterTests(unittest.TestCase):
    def test_source_schema_admissible_without_retaining_any_old_job_listings(self):
        # The repository no longer retains 15 historical freelance wrappers.
        # Test schema and protocol semantics using bounded independently
        # declared fixtures. No retired listing needs to be resurrected.
        fixtures=(
            {
                "id":"OBS-001","title":"Observed bounded research",
                "preferred_referent":"reproduce the test",
                "boundary":"Run independently specified observations",
                "acceptance":"The native test passes",
                "status":"tested","result":"source-bound evidence available",
            },
            {
                "id":"OBS-002","title":"Unresolved original",
                "preferred_referent":"original missing source",
                "boundary":"Verify the supplied source",
                "acceptance":"The source is present and independently checked",
                "status":"blocked","blockers":["Original source unavailable"],
            },
        )
        with TemporaryDirectory() as d:
            root=Path(d)
            for i,fixture in enumerate(fixtures,1):
                folder=root/f"JOB-{i:03d}_fixture"
                folder.mkdir()
                (folder/"job.json").write_text(json.dumps(fixture),encoding="utf-8")
            jobs=load_all_jobs(root)
            self.assertEqual(len(jobs),2)
            states=[evaluate_job(job) for job in jobs]
            self.assertLessEqual({item.result.state for item in states},
                                 {"MOVE","WALL","UNKNOWN","PARTIAL"})
            self.assertTrue(any(item.result.state=="WALL" for item in states))
            self.assertTrue(any(item.result.state in ("MOVE","PARTIAL") for item in states))
            # Retiring job wrappers does not imply historical failure.
            self.assertEqual(load_all_jobs(root/"unpopulated"),())

    def test_blocked_job_does_not_emit_completion_relations(self):
        source={
            "id":"OBS-X","title":"Original research with unresolved input",
            "preferred_referent":"spec","boundary":"do thing",
            "acceptance":"thing passes","status":"blocked",
            "blockers":["source input missing"],"result":"prototype exists",
        }
        state=evaluate_job(source)
        self.assertEqual(state.result.state,"WALL")
        self.assertEqual(state.result.outputs,())


if __name__=="__main__":
    unittest.main()
