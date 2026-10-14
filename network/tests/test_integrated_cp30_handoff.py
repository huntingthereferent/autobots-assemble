"""Live CP30 integrated-subprocess signature check, with independent native replay."""
from __future__ import annotations

import base64
import copy
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from runtime.engine import HandoffRuntime
from runtime.handoff import ExecutionResult
from runtime.journal import RuntimeJournal
from systems.workspace.integrated_source import copy_integrated_source, WORKER_ID
from systems.workspace.integrated_attestation_bridge import IntegratedCP30Bridge, VERIFIER
from systems.workspace.integrated_attestation_verifier import validate_request, native_verdict
from systems.workspace.monitor import workstation_snapshot
from systems.workspace.workstation import ProcessWorkstation

REPO = Path(__file__).resolve().parents[2]
JOB = "cp30-test-job"


def fixture():
    """Synthetic keys: only the public keys and signed claims enter the handoff."""
    nonce = "ab" * 24
    expect = {"challenge": nonce, "route": "left", "fingerprint": "12" * 32,
              "witness": "34" * 32,
              "source_digests": {"donor": "56" * 32, "middle": "78" * 32, "final": "9a" * 32}}
    public, signatures = {}, []
    for scope in ("donor", "middle", "final"):
        k = Ed25519PrivateKey.generate()
        public[scope] = base64.b64encode(k.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)).decode()
        claim = {"kind": "selected-route-source-attestation/v1", "scope": scope,
                 "challenge": nonce, "route": "left", "route_fingerprint": expect["fingerprint"],
                 "witness_sha256": expect["witness"],
                 "source_sha256": expect["source_digests"][scope]}
        raw = json.dumps(claim, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        signatures.append({"claim": claim, "signature": base64.b64encode(k.sign(raw)).decode()})
    return {"bundle": {"kind": "selected-route-source-bundle/v1", "attestations": signatures},
            "trust": public, "expect": expect}


class IntegratedCP30HandoffTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name) / "state"
        self.desk = ProcessWorkstation(self.data / "workstation")
        self.journal = self.data / "runtime.jsonl"
        self.inputs = fixture()

    def runtime(self):
        return HandoffRuntime(event_store=RuntimeJournal(self.journal))

    def edition(self, version="cp30-original"):
        return copy_integrated_source(repo_root=REPO, data_dir=self.data, stage=30,
                                      version_id=version, allow_copy=True)

    def bridge(self, runtime=None):
        return IntegratedCP30Bridge(runtime=runtime or self.runtime(), workstation=self.desk)

    def admit(self, version="cp30-original", inputs=None, job_id=JOB):
        b = self.bridge()
        h = b.admit(version_id=version, inputs=inputs or self.inputs,
                    from_actor="test-source", job_id=job_id)
        return b, h

    def test_copy_does_not_admit_any_job(self):
        copied = self.edition()
        self.assertEqual(copied["file_count"], 281)
        self.assertFalse(copied["capability_verified"])
        self.assertFalse(self.journal.exists())

    def test_requires_integrated_historical_source(self):
        self.edition()
        folder = self.desk._edition(WORKER_ID, "cp30-original")
        (folder / "finite_process_attestation.py").unlink()
        with self.assertRaisesRegex(ValueError, "source missing"):
            self.admit()
        self.assertFalse(self.journal.exists())

    def test_valid_signatures_with_native_replay_and_restart(self):
        self.edition()
        bridge, handoff = self.admit()
        self.assertEqual(bridge.runtime.state(JOB).status, "READY")
        with self.assertRaises(PermissionError):
            bridge.execute(JOB)
        self.assertEqual([e.event_type for e in bridge.runtime.event_store.for_handoff(JOB)], ["CREATED"])
        state = bridge.execute(JOB, allow_local_execution=True)
        self.assertEqual(state.status, "COMPLETE")
        self.assertEqual(state.output["signature_verdict"], "ATTESTATIONS_VERIFIED")
        self.assertEqual(state.output["verified_scopes"], ["donor", "middle", "final"])
        self.assertTrue(state.output["child_pid"] > 0)
        self.assertNotEqual(state.output["child_pid"], os.getpid())
        self.assertEqual(state.evidence[0].depth, "local-cryptographic-replay")
        self.assertEqual(bridge.runtime.get(JOB).metadata["native_evidence_verifier"], VERIFIER)
        before = self.journal.read_bytes()
        restarted = self.bridge()
        self.assertTrue(restarted.reverify(JOB))
        self.assertEqual(before, self.journal.read_bytes())
        self.assertEqual(workstation_snapshot(root=self.desk.root, runtime=restarted.runtime)["jobs"][0]["status"], "COMPLETE")

    def test_negative_signature_is_negative_verdict_not_owner_proof(self):
        self.edition()
        bad = copy.deepcopy(self.inputs)
        bad["bundle"]["attestations"][1]["signature"] = base64.b64encode(b"\x00" * 64).decode()
        bridge, _ = self.admit(inputs=bad)
        state = bridge.execute(JOB, allow_local_execution=True)
        self.assertEqual(state.status, "COMPLETE")  # verification computation completed
        self.assertEqual(state.output["signature_verdict"], "ATTESTATION_SIGNATURE_UNPROVED")
        self.assertEqual(state.output["verified_scopes"], [])
        self.assertTrue(self.bridge().reverify(JOB))

    def test_mismatched_claim_detected(self):
        self.edition()
        bad = copy.deepcopy(self.inputs)
        bad["bundle"]["attestations"][0]["claim"]["challenge"] = "cd" * 24
        bridge, _ = self.admit(inputs=bad)
        state = bridge.execute(JOB, allow_local_execution=True)
        self.assertEqual(state.output["signature_verdict"], "ATTESTATION_CLAIM_MISMATCH")

    def test_private_keys_and_oversized_requests_rejected(self):
        self.edition()
        bad = dict(self.inputs, private_keys={"donor": "secret"})
        with self.assertRaisesRegex(ValueError, "only bundle"):
            self.admit(inputs=bad)
        oversized = copy.deepcopy(self.inputs)
        oversized["bundle"]["attestations"][0]["claim"]["new"] = "z" * 20000
        with self.assertRaises(ValueError):
            self.admit(inputs=oversized)
        self.assertFalse(self.journal.exists())

    def test_source_edit_after_admission_refused_without_started_event(self):
        self.edition()
        bridge, _ = self.admit()
        f = self.desk._edition(WORKER_ID, "cp30-original") / "finite_process_attestation.py"
        f.write_text(f.read_text() + "\n# source edit\n")
        with self.assertRaisesRegex(ValueError, "source changed"):
            bridge.execute(JOB, allow_local_execution=True)
        self.assertEqual(bridge.runtime.state(JOB).status, "READY")
        self.assertEqual([e.event_type for e in bridge.runtime.event_store.for_handoff(JOB)], ["CREATED"])

    def test_changed_source_after_result_invalidates_reverify(self):
        self.edition()
        b,_=self.admit()
        b.execute(JOB, allow_local_execution=True)
        f=self.desk._edition(WORKER_ID,"cp30-original")/"finite_process_attestation.py"
        f.write_text(f.read_text()+"\n# edited later\n")
        with self.assertRaisesRegex(ValueError, "source changed"):
            self.bridge().reverify(JOB)

    def test_forged_child_verdict_rejected_before_result(self):
        self.edition()
        self.desk.branch(worker_id=WORKER_ID, parent_version="cp30-original", version_id="untrusted-copy")
        f=self.desk._edition(WORKER_ID,"untrusted-copy")/"finite_process_attestation.py"
        f.write_text("import json,os\nprint(json.dumps({'status':'ATTESTATIONS_VERIFIED','pid':os.getpid(),'verified_scopes':['donor','middle','final']}))\n")
        bad=copy.deepcopy(self.inputs)
        bad["bundle"]["attestations"][1]["signature"]=base64.b64encode(b"\x00"*64).decode()
        bridge,_=self.admit(version="untrusted-copy",inputs=bad)
        with self.assertRaisesRegex(ValueError,"host-owned CP30 signature replay"):
            bridge.execute(JOB, allow_local_execution=True)
        self.assertNotEqual(bridge.runtime.state(JOB).status, "COMPLETE")
        self.assertNotIn("RESULT", [e.event_type for e in bridge.runtime.event_store.for_handoff(JOB)])

    def test_mismatched_replayed_result_refused(self):
        self.edition()
        b,_=self.admit()
        state=b.execute(JOB,allow_local_execution=True)
        fabricated=ExecutionResult(status="COMPLETE",output={**state.output,"signature_verdict":"ATTESTATION_CLAIM_MISMATCH"},evidence=state.evidence)
        with self.assertRaisesRegex(ValueError,"host-owned CP30 signature replay"):
            self.bridge()._verify(self.runtime().get(JOB),fabricated)

if __name__ == "__main__":
    unittest.main()
