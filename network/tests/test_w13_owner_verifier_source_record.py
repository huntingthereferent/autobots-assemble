"""Actual owner W13 child run record: source log and missing-journal negatives."""
from __future__ import annotations
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from systems.workspace.w13_owner_verifier_source_record import (
    RECORD,HEAD,RUN_ID,JOB_ID,AUTH_BLOB,READY_BLOB,
    extract_report,verify_source
)
ROOT=Path(__file__).resolve().parents[2]
REC=json.loads((ROOT/RECORD).read_text(encoding="utf8"))


def source_fixtures():
    run={"id":RUN_ID,"name":"owner-w13-native-verifier-one-shot",
         "head_sha":HEAD,"event":"push","head_branch":"main",
         "status":"completed","conclusion":"success","run_attempt":1,
         "actor":{"login":"huntingthereferent"}}
    job={"id":JOB_ID,"run_id":RUN_ID,"head_sha":HEAD,
         "name":"owner-exact-original-child","status":"completed",
         "conclusion":"success","steps":[{"name":name,"conclusion":"success"}
             for name in (
              "Authenticate NEW exact owner request before fetching original archive",
              "Authenticate original owner-run and immutable evidence artifact",
              "Download authenticated original W13 artifact with digest validation",
              "Execute exactly ONE separately authorized native verifier child")]}
    # Fake log used ONLY for structural unit tests; the real replay is in GitHub.
    lines=["2026-10-18T14:23:30.1Z "+json.dumps({key:value},sort_keys=True)[1:-1]
           for key,value in REC["reported_native_result"].items()]
    return run,{"jobs":[job]},{"artifacts":[]}, "\n".join(lines)


class OriginalOwnerNativeSourceTests(unittest.TestCase):
    def test_source_blobs_are_committed_pins(self):
        import subprocess
        def blob(path):
            return subprocess.check_output(["git","hash-object",str(ROOT/path)],text=True).strip()
        a=REC["source_run"];b=REC["original_readiness"]
        self.assertEqual(blob(a["owner_request_path"]),AUTH_BLOB)
        self.assertEqual(blob(b["bridge_path"]),READY_BLOB)
        self.assertEqual(b["separate_required_live_parent"],"live-game-temporal-001")
        self.assertFalse(b["native_child_replayable_in_later_runner"])

    def test_reported_log_and_authenticated_run_must_match_all_fields(self):
        run,jobs,arts,log=source_fixtures()
        with patch("systems.workspace.w13_owner_verifier_source_record._blob",
                   side_effect=[AUTH_BLOB,READY_BLOB]):
            out=verify_source(repo_root=ROOT,run=run,jobs=jobs,artifacts=arts,log_text=log)
        self.assertEqual(out["state"],"GITHUB_OWNER_RESULT_OBSERVED_NO_PORTABLE_CHILD_JOURNAL")
        self.assertFalse(out["ready_worker_executed"])
        self.assertFalse(out["native_child_replayed_from_retained_journal"])

    def test_fake_owner_or_commit_refused(self):
        run,jobs,arts,log=source_fixtures()
        run["actor"]["login"]="not-owner"
        with patch("systems.workspace.w13_owner_verifier_source_record._blob",
                   side_effect=[AUTH_BLOB,READY_BLOB]):
            with self.assertRaisesRegex(ValueError,"not the authorized original"):
                verify_source(repo_root=ROOT,run=run,jobs=jobs,artifacts=arts,log_text=log)

    def test_source_steps_and_child_report_cannot_be_substituted(self):
        run,jobs,arts,log=source_fixtures()
        jobs["jobs"][0]["steps"][-1]["conclusion"]="failure"
        with patch("systems.workspace.w13_owner_verifier_source_record._blob",
                   side_effect=[AUTH_BLOB,READY_BLOB]):
            with self.assertRaisesRegex(ValueError,"source gates"):
                verify_source(repo_root=ROOT,run=run,jobs=jobs,artifacts=arts,log_text=log)
        run,jobs,arts,log=source_fixtures()
        log=log.replace("evt_a58b931a7b9d4b43b7e9715d36bf6929","evt_00000000000000000000000000000000")
        with patch("systems.workspace.w13_owner_verifier_source_record._blob",
                   side_effect=[AUTH_BLOB,READY_BLOB]):
            with self.assertRaisesRegex(ValueError,"does not match"):
                verify_source(repo_root=ROOT,run=run,jobs=jobs,artifacts=arts,log_text=log)

    def test_lost_child_journal_cannot_be_claimed_replayable(self):
        run,jobs,arts,log=source_fixtures()
        arts["artifacts"]=[{"id":123,"name":"not-original"}]
        with patch("systems.workspace.w13_owner_verifier_source_record._blob",
                   side_effect=[AUTH_BLOB,READY_BLOB]):
            with self.assertRaisesRegex(ValueError,"unexpected child artifacts"):
                verify_source(repo_root=ROOT,run=run,jobs=jobs,artifacts=arts,log_text=log)

    def test_duplicate_log_event_is_not_authoritative(self):
        _,_,_,log=source_fixtures()
        with self.assertRaisesRegex(ValueError,"ambiguous duplicate"):
            extract_report(log+"\n"+'"child_result_event_id": "evt_00000000000000000000000000000000"')

    def test_cannot_execute_original_child_or_ready_worker(self):
        import inspect
        import systems.workspace.w13_owner_verifier_source_record as mod
        code=inspect.getsource(mod.verify_source)
        for forbidden in (".execute(",".admit(",".copy_source(","subprocess.run("):
            self.assertNotIn(forbidden,code)


if __name__=="__main__":
    unittest.main()
