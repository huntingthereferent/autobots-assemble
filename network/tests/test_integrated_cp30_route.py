"""CP30 recovered owner/pin fixture route audit, source isolation and replay."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import ExecutionResult
from runtime.journal import RuntimeJournal
from systems.workspace.integrated_source import copy_integrated_source, WORKER_ID
from systems.workspace.integrated_route_bridge import (IntegratedRouteBridge,VERIFIER,
                                                       canonical_report)
from systems.workspace.integrated_route_verifier import validate_route_request
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.controls import run_job, reverify_job, admit_integrated_route

REPO=Path(__file__).resolve().parents[2]
PAYLOAD={"route":"left","scenario":"intact","tasks":[
    {"name":"a","state":[1,0,0],"action":"B"},
    {"name":"b","state":[1,1,2],"action":"A"},
    {"name":"unproved","state":[0,1,2],"action":"B"}]}

class CP30RouteTests(unittest.TestCase):
    def setUp(self):
        temp=TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.data=Path(temp.name)/"private"
        self.workstation=ProcessWorkstation(self.data/"workstation")
        copy_integrated_source(repo_root=REPO,data_dir=self.data,stage=30,
                               version_id="cp30-original",allow_copy=True)
        self.runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        self.bridge=IntegratedRouteBridge(runtime=self.runtime,workstation=self.workstation)

    def admit(self,inputs=None,job_id="cp30-route-test"):
        return self.bridge.admit(version_id="cp30-original",inputs=inputs or PAYLOAD,
                                 from_actor="test-source",job_id=job_id)

    def test_copy_alone_has_no_runtime_handoff(self):
        self.assertFalse((self.data/"runtime.jsonl").exists())
        self.assertEqual(self.runtime.snapshot(),{})

    def test_valid_left_route_does_not_transfer_unproved_edge(self):
        h=self.admit()
        self.assertEqual(self.runtime.state(h.handoff_id).status,"READY")
        self.bridge.execute(h.handoff_id,allow_local_execution=True)
        row=self.runtime.state(h.handoff_id).output["report"]
        self.assertEqual(row["receive_status"],"INDEPENDENT_PROCESS_FRESHLY_VERIFIED")
        self.assertEqual(row["replay_calls"],2)
        self.assertEqual(row["replay_trace"],{"left":2,"right":0})
        self.assertEqual(row["usable"],["a","b"])
        self.assertEqual(dict(row["task_statuses"])["unproved"],"ROUTE_TASK_REQUIREMENTS_UNPROVED")
        self.assertFalse(row["proof_for_all"])
        self.assertTrue(row["distinct_signer_verifier"])
        self.assertTrue(row["source_observations_unchanged"])
        self.assertEqual(h.metadata["native_evidence_verifier"],VERIFIER)
        self.assertEqual(self.runtime.state(h.handoff_id).evidence[0].depth,"synthetic-canonical-replay")
        self.assertTrue(self.bridge.reverify(h.handoff_id))

    def test_right_route_obligations_independent(self):
        data={**PAYLOAD,"route":"right"}
        self.admit(inputs=data)
        self.bridge.execute("cp30-route-test",allow_local_execution=True)
        row=self.runtime.state("cp30-route-test").output["report"]
        self.assertEqual(row["usable"],["b","unproved"])
        self.assertEqual(row["replay_trace"],{"left":0,"right":2})

    def test_selected_revocation_and_bad_trust_block_fresh_route_use(self):
        for n,scenario,expected in ((1,"revoke-selected","ATTESTATION_CLAIM_MISMATCH"),
                                    (2,"untrusted-key","ATTESTATION_SIGNATURE_UNPROVED")):
            job=f"negative-{n}"
            self.admit(inputs={**PAYLOAD,"scenario":scenario},job_id=job)
            self.bridge.execute(job,allow_local_execution=True)
            row=self.runtime.state(job).output["report"]
            self.assertEqual(row["receive_status"],expected)
            self.assertEqual(row["replay_calls"],0)
            self.assertFalse(row["proof_for_all"])
            self.assertFalse(row["usable"])

    def test_neighbor_revocation_does_not_poison_selected_route(self):
        self.admit(inputs={**PAYLOAD,"scenario":"revoke-neighbor"})
        self.bridge.execute("cp30-route-test",allow_local_execution=True)
        row=self.runtime.state("cp30-route-test").output["report"]
        self.assertEqual(row["receive_status"],"INDEPENDENT_PROCESS_FRESHLY_VERIFIED")
        self.assertEqual(row["replay_calls"],2)
        self.assertEqual(row["usable"],["a","b"])

    def test_fake_child_claim_cannot_pass_canonical_replay(self):
        h=self.admit()
        result=canonical_report(h.inputs)
        result["usable"]=["a","b","unproved"]
        fake=ExecutionResult(status="COMPLETE",output={
            "kind":"cp30-synthetic-route-audit-v1","report":result,
            "worker_version":"cp30-original","edition_fingerprint":h.metadata["edition_fingerprint"],
            "child_pid":1234},evidence=(self.bridge.runtime.state(h.handoff_id).evidence or ()))
        # Use a real expected evidence record; the host must then detect forged tasks.
        from runtime.handoff import EvidenceRecord
        from systems.workspace.integrated_route_bridge import WITNESS,SOURCE
        fake=ExecutionResult(status="COMPLETE",output=fake.output,evidence=(EvidenceRecord(
            condition=WITNESS,kind="computation",source=SOURCE,
            ref=h.metadata["edition_fingerprint"],depth="synthetic-canonical-replay"),))
        with self.assertRaisesRegex(ValueError,"canonical historical replay"):
            self.runtime.return_result(h.handoff_id,actor_id=h.to_actor,result=fake)
        self.assertEqual(self.runtime.state(h.handoff_id).status,"READY")

    def test_modified_edition_after_admission_refuses_execution(self):
        self.admit()
        f=self.data/"workstation"/WORKER_ID/"cp30-original"/"test_ab_chatbot_route_bound_task.py"
        f.write_text(f.read_text()+"\n# experiment\n")
        with self.assertRaisesRegex(ValueError,"source changed"):
            self.bridge.execute("cp30-route-test",allow_local_execution=True)
        self.assertEqual(self.runtime.state("cp30-route-test").status,"READY")

    def test_invalid_requests_not_admitted(self):
        for request in ({**PAYLOAD,"tasks":[]},
                        {**PAYLOAD,"tasks":[{**PAYLOAD['tasks'][0],"action":"X"}]},
                        {**PAYLOAD,"scenario":"physical"}):
            with self.assertRaises(ValueError):self.admit(inputs=request)
        self.assertEqual(self.runtime.snapshot(),{})

    def test_restart_no_duplicate_and_cli_dispatch(self):
        import json
        inp=self.data/"exact-tasks.json"
        inp.write_text(json.dumps(PAYLOAD))
        from systems.workspace.controls import prepare_integrated_route
        prep=prepare_integrated_route(data_dir=self.data,version_id="cp30-original",inputs_file=inp)
        self.assertFalse(prep["admitted"])
        admit_integrated_route(data_dir=self.data,version_id="cp30-original",inputs_file=inp,
                               job_id="cp30-new",confirm_admit="cp30-new",from_actor="test-source")
        self.assertEqual(HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl")).state("cp30-new").status,"READY")
        with self.assertRaises(PermissionError):
            run_job(data_dir=self.data,job_id="cp30-new",confirm_execute="other")
        done=run_job(data_dir=self.data,job_id="cp30-new",confirm_execute="cp30-new")
        self.assertEqual(done["status"],"COMPLETE")
        original=(self.data/"runtime.jsonl").read_bytes()
        self.assertTrue(reverify_job(data_dir=self.data,job_id="cp30-new")["reverified"])
        run_job(data_dir=self.data,job_id="cp30-new",confirm_execute="cp30-new")
        self.assertEqual((self.data/"runtime.jsonl").read_bytes(),original)

if __name__=="__main__":unittest.main()
