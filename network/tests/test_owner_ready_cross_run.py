"""Source/event rejection tests. Fixtures are not native restoration evidence."""
import copy
import unittest
from scripts import w13_ready_cross_run as impl


class OwnerReadyCrossRunTests(unittest.TestCase):
    def origins(self):
        return ({"id":impl.RUN,"name":"owner W13 native adapter readiness","head_sha":impl.COMMIT,
            "run_attempt":1,"event":"push","head_branch":"main","status":"completed",
            "conclusion":"success","actor":{"id":impl.OWNER_ID,"login":"huntingthereferent"},
            "repository":{"id":impl.REPO_ID},
            "head_repository":{"id":impl.REPO_ID,"full_name":impl.REPO}},
            {"id":impl.ARTIFACT,"name":f"owner-ready-encrypted-{impl.RUN}","digest":impl.DIGEST,
             "expired":False,"workflow_run":{"id":impl.RUN,"head_sha":impl.COMMIT,
                                             "repository_id":impl.REPO_ID}})

    def test_owner_run_and_exact_artifact_bindings(self):
        run, artifact = self.origins()
        impl.validate_origin(run,artifact)
        for key,value in (("id",1),("head_sha","0"*40),("run_attempt",2),
                ("event","pull_request"),("conclusion","failure"),("actor",{"id":1}),
                ("head_repository",{"id":1})):
            changed = copy.deepcopy(run); changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                impl.validate_origin(changed,artifact)
        for key,value in (("id",1),("digest","sha256:"+"0"*64),("expired",True),
                ("workflow_run",{"id":1})):
            changed = copy.deepcopy(artifact); changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                impl.validate_origin(run,changed)

    def test_report_cannot_stand_in_for_fresh_native_readiness(self):
        receipt = {"job_id":impl.READY_JOB,"worker_id":"game-worker-ready",
            "worker_version":"owner-adapter-v1","source_fingerprint":impl.READY_FINGERPRINT,
            "recorded_status":"COMPLETE","verification":"FRESH_NATIVE_REVERIFICATION_LOCAL",
            "events":[{"type":"RESULT","event_id":impl.READY_EVENT,"result_status":"COMPLETE"}]}
        impl.validate_native(receipt)
        for key,value in (("verification","RECORDED_NOT_REVERIFIED"),
                ("source_fingerprint","0"*64),("events",[]),("recorded_status","READY")):
            changed = copy.deepcopy(receipt); changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                impl.validate_native(changed)
        changed = copy.deepcopy(receipt)
        changed["events"][0]["event_id"] = "evt_"+"0"*32
        with self.assertRaises(ValueError):
            impl.validate_native(changed)

    def test_incomplete_or_substituted_capsule_receipt_is_refused(self):
        with self.assertRaises(ValueError):
            impl.validate_receipt({},b"not the retained encrypted capsule")


if __name__ == "__main__":
    unittest.main()
