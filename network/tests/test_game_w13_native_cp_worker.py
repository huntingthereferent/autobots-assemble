"""W13 native CP: source-owned admission, actual subprocess and exact coordinator witness.

Fixture tests are local bounded self-test of explicit controls; do not admit an
actual user's private job or imply that GitHub CI ran on an authorized machine.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult
from runtime.journal import RuntimeJournal
from systems.workspace.game_w13_native import (
    CP_ID, VERIFIER, WORKER_ROLE, validate_game_request,
    verify_native_report,
)
from systems.workspace.game_w13_native_bridge import (
    GameW13NativeBridge, WORKER_ID, SOURCE_DIRECTORY,
    copy_game_source, run_source, WITNESS, EVIDENCE_SOURCE,
)
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.controls import prepare, run_job, reverify_job
from systems.workspace.coordinator_window import (
    CoordinatorIndex, from_existing_workstation, freshly_reverify_linked_jobs,
)
from systems.workspace.cp_motion import (
    admit_research, one_cp_handoff, attach_native_cp_contracts,
)
from systems.workspace.game_w13_native_cli import main as cli_main

ROOT = Path(__file__).resolve().parents[2]
REQUEST = json.loads(
    (ROOT / "network/tests/fixtures/game_w13_native_cp_example.json").read_text()
)


class W13NativeSourceTests(unittest.TestCase):
    def test_01_fixed_WORLD_request_matches_declared_version(self):
        checked = validate_game_request(REQUEST)
        self.assertEqual(checked["contract"], "game-w13-multiworld-v1")
        self.assertEqual(checked["actions"], ["right","interact","advance","right","interact"])
        self.assertEqual([w["id"] for w in checked["worlds"]], ["first-room", "second-room"])

    def test_02_native_copied_source_matches_independent_original_W12(self):
        output = run_source(SOURCE_DIRECTORY, REQUEST)
        proof = verify_native_report(REQUEST, output)
        self.assertTrue(proof["solved"])
        self.assertEqual(proof["worlds_completed"], 2)
        self.assertEqual(proof["boundaries_checked"], 1)
        self.assertFalse(proof["browser_origin_authenticated"])
        self.assertFalse(proof["w13_checkpoint_promoted"])

    def test_03_changed_version_or_source_hash_rejected(self):
        for key, value in (("contract","v2"), ("w12_sha256","x")):
            with self.subTest(key=key):
                data = deepcopy(REQUEST);data[key]=value
                with self.assertRaises(ValueError):
                    validate_game_request(data)

    def test_04_bad_world_source_coordinate_and_count_rejected(self):
        for key, value in (("width",4.0),("target",[2,2]),("height",2)):
            with self.subTest(key=key):
                data=deepcopy(REQUEST);data["worlds"][1]["spec"][key]=value
                with self.assertRaises(ValueError):
                    validate_game_request(data)
        data=deepcopy(REQUEST);data["worlds"].append(deepcopy(data["worlds"][0]))
        with self.assertRaises(ValueError):validate_game_request(data)

    def test_05_premature_advance_or_lost_final_collection_rejected(self):
        for actions in (["advance"]+REQUEST["actions"],
                        REQUEST["actions"][:-1],
                        REQUEST["actions"]+["advance"]):
            with self.subTest(actions=actions):
                data=deepcopy(REQUEST);data["actions"]=actions
                with self.assertRaises(ValueError):
                    validate_game_request(data)

    def test_06_native_child_forged_first_second_receipt_rejected(self):
        native=run_source(SOURCE_DIRECTORY,REQUEST)
        for place in ("first","second","boundary","global","solved"):
            with self.subTest(place=place):
                forged=deepcopy(native)
                receipt=forged["receipt"]
                if place=="first":
                    receipt["worlds"][0]["observations"][0]["after"]["x"]=44
                elif place=="second":
                    receipt["worlds"][1]["final"]["turns"]=99
                elif place=="boundary":
                    receipt["boundaries"][0]["before"]["state"]["x"]=55
                elif place=="global":
                    receipt["actions"][2]="right"
                else:
                    receipt["final"]["solved"]=False
                with self.assertRaises(ValueError):
                    verify_native_report(REQUEST,forged)

    def test_07_native_worker_subprocess_output_schema_required(self):
        value=run_source(SOURCE_DIRECTORY,REQUEST)
        for modified in (
            {**value, "pid":True}, {**value,"pid":-1},
            {**value, "checkpoint_verdict":"PASS"},
            {"pid":123},
        ):
            with self.subTest(modified=modified):
                with self.assertRaises(ValueError):
                    verify_native_report(REQUEST,modified)


class W13NativeWorkstationTests(unittest.TestCase):
    def setUp(self):
        temp=TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)/"data";self.root.mkdir()
        self.desk=ProcessWorkstation(self.root/"workstation")
        self.runtime=HandoffRuntime(event_store=RuntimeJournal(self.root/"runtime.jsonl"))
        self.bridge=GameW13NativeBridge(runtime=self.runtime,workstation=self.desk)
        self.index=CoordinatorIndex(self.root/"coordinator-windows.jsonl")
        admit_research(self.index)
        copy_game_source(self.root,version_id="world-w13-v1",allow_copy=True)
        self.inputs=validate_game_request(REQUEST)

    def admit(self,job="game-w13-01"):
        return self.bridge.admit(version_id="world-w13-v1",inputs=self.inputs,
                                 from_actor="authorized-local-review",job_id=job)

    def bind(self,job="game-w13-01"):
        self.index.bind_planned("complete-stack","game",slot="cp-game-w13-worlds",
                                job_id=job,worker_id=WORKER_ID,version_id="world-w13-v1")

    def cp(self, *, fresh=False):
        view=attach_native_cp_contracts(
            from_existing_workstation(self.root),self.runtime._handoffs.values()
        )
        if fresh:
            view=freshly_reverify_linked_jobs(
                self.index,"complete-stack",view,
                lambda job:reverify_job(data_dir=self.root,job_id=job)
            )
        return one_cp_handoff(self.index,"complete-stack",view)["cp_automation"]

    def test_08_copy_only_does_not_admit_or_execute(self):
        self.assertEqual(self.runtime.snapshot(),{})
        self.assertFalse((self.root/"runtime.jsonl").exists())
        self.assertIn(CP_ID,self.cp()["frontier"])

    def test_09_copy_requires_explicit_operator_consent(self):
        with self.assertRaises(PermissionError):
            copy_game_source(self.root,version_id="untrusted-v1")
        self.assertFalse((self.root/"workstation"/WORKER_ID/"untrusted-v1").exists())

    def test_10_ready_job_does_not_pass_or_unlock_next_CP(self):
        self.admit();self.bind()
        result=self.cp()
        self.assertEqual(result["witnessed"],[])
        self.assertIn(CP_ID,result["frontier"])
        self.assertNotIn("GAME-NATIVE-VERIFIER",result["frontier"])

    def test_11_exact_operator_execution_required(self):
        self.admit()
        with self.assertRaises(PermissionError):
            self.bridge.execute("game-w13-01")
        with self.assertRaises(PermissionError):
            run_job(data_dir=self.root,job_id="game-w13-01",confirm_execute="wrong")
        self.assertEqual(self.runtime.state("game-w13-01").status,"READY")

    def test_12_actual_native_job_pass_requires_fresh_verified_binding(self):
        self.admit();self.bind()
        native=run_job(data_dir=self.root,job_id="game-w13-01",
                       confirm_execute="game-w13-01")
        self.assertEqual(native["status"],"COMPLETE")
        # Admission runtime is a pre-execution snapshot; replay durable journal.
        resumed=HandoffRuntime(event_store=RuntimeJournal(self.root/"runtime.jsonl"))
        self.assertTrue(GameW13NativeBridge(runtime=resumed,workstation=self.desk).reverify("game-w13-01"))
        fresh=self.cp(fresh=True)
        self.assertEqual(fresh["witnessed"],[CP_ID])
        self.assertIn("GAME-NATIVE-VERIFIER",fresh["frontier"])
        self.assertNotIn("GAME-WORKER-READY",fresh["frontier"])
        self.assertNotIn("NIH-P2-TEST",fresh["frontier"])

    def test_13_complete_without_fresh_cp_reverify_is_not_pass(self):
        self.admit();self.bind()
        run_job(data_dir=self.root,job_id="game-w13-01",
                confirm_execute="game-w13-01")
        state=self.cp()
        self.assertEqual(state["witnessed"],[])
        self.assertIn(CP_ID,state["frontier"])

    def test_14_unlinked_native_result_cannot_promote_coordinator(self):
        self.admit()
        run_job(data_dir=self.root,job_id="game-w13-01",
                confirm_execute="game-w13-01")
        self.assertNotIn(CP_ID,self.cp(fresh=True)["witnessed"])

    def test_15_reexecution_of_COMPLETE_is_read_only(self):
        self.admit();self.bind()
        run_job(data_dir=self.root,job_id="game-w13-01",
                confirm_execute="game-w13-01")
        before=(self.root/"runtime.jsonl").read_bytes()
        again=run_job(data_dir=self.root,job_id="game-w13-01",
                      confirm_execute="game-w13-01")
        self.assertEqual(again["status"],"COMPLETE")
        self.assertEqual(before,(self.root/"runtime.jsonl").read_bytes())

    def test_16_edit_source_after_admission_blocks_execute(self):
        self.admit()
        path=self.root/"workstation"/WORKER_ID/"world-w13-v1"/"game_worlds_worker.py"
        path.write_text(path.read_text()+"\n# altered source edition\n")
        with self.assertRaisesRegex(ValueError,"changed"):
            self.bridge.execute("game-w13-01",allow_local_execution=True)
        self.assertEqual(self.runtime.state("game-w13-01").status,"READY")

    def test_17_changed_source_blocks_fresh_reverification(self):
        self.admit();self.bind()
        run_job(data_dir=self.root,job_id="game-w13-01",
                confirm_execute="game-w13-01")
        source=self.root/"workstation"/WORKER_ID/"world-w13-v1"/"game_worlds_worker.py"
        source.write_text(source.read_text()+"\n# changed after completion\n")
        with self.assertRaises(ValueError):
            reverify_job(data_dir=self.root,job_id="game-w13-01")
        self.assertNotIn(CP_ID,self.cp(fresh=True)["witnessed"])

    def test_18_forged_PASS_without_host_native_proof_rejected(self):
        handoff=self.admit()
        real=run_source(SOURCE_DIRECTORY,self.inputs)
        real["receipt"]["worlds"][1]["final"]["collected"]=False
        fingerprint=handoff.metadata["edition_fingerprint"]
        fake=ExecutionResult(status="COMPLETE",output={
            "kind":"game-w13-worlds-native/v1","checkpoint_contract":CP_ID,
            "checkpoint_verdict":"PASS","checkpoint_worker_role":WORKER_ROLE,
            "native_verifier":VERIFIER,"report":real,
            "worker_version":"world-w13-v1","edition_fingerprint":fingerprint,
        },evidence=(EvidenceRecord(
            condition=WITNESS,kind="computation",source=EVIDENCE_SOURCE,
            ref=fingerprint,depth="independent-original-W12-native-session-replay",
        ),))
        with self.assertRaises(ValueError):
            self.runtime.return_result(handoff.handoff_id,actor_id=handoff.to_actor,result=fake)
        self.assertEqual(self.runtime.state(handoff.handoff_id).status,"READY")

    def test_19_restart_fresh_replay_does_not_require_running_child_again(self):
        self.admit();self.bind()
        run_job(data_dir=self.root,job_id="game-w13-01",
                confirm_execute="game-w13-01")
        before=(self.root/"runtime.jsonl").read_bytes()
        resumed=HandoffRuntime(event_store=RuntimeJournal(self.root/"runtime.jsonl"))
        bridge=GameW13NativeBridge(runtime=resumed,workstation=self.desk)
        self.assertTrue(bridge.reverify("game-w13-01"))
        self.assertEqual(before,(self.root/"runtime.jsonl").read_bytes())

    def test_20_cli_copy_prepare_admit_and_no_execution(self):
        with TemporaryDirectory() as temp:
            another=Path(temp)/"runtime"
            inp=Path(temp)/"input.json"
            inp.write_text(json.dumps(REQUEST))
            self.assertEqual(cli_main(["--data-dir",str(another),"copy",
                                       "--version","world-v1","--confirm-copy"]),0)
            self.assertEqual(cli_main(["--data-dir",str(another),"prepare",
                                       "--version","world-v1","--inputs-file",str(inp)]),0)
            self.assertEqual(cli_main(["--data-dir",str(another),"admit",
                                       "--version","world-v1","--inputs-file",str(inp),
                                       "--job-id","game-local-1","--confirm-admit","game-local-1",
                                       "--from-actor","local-user"]),0)
            reopened=HandoffRuntime(event_store=RuntimeJournal(another/"runtime.jsonl"))
            self.assertEqual(reopened.state("game-local-1").status,"READY")
            with self.assertRaises(PermissionError):
                cli_main(["--data-dir",str(another),"admit","--version","world-v1",
                          "--inputs-file",str(inp),"--job-id","game-local-2",
                          "--confirm-admit","other","--from-actor","local-user"])

    def test_21_original_W12_world_native_source_remains_unchanged(self):
        from hashlib import sha256
        from systems.workspace import game_construction as w12
        self.assertEqual(
            sha256(Path(w12.__file__).read_bytes()).hexdigest(),
            "dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1")


if __name__ == "__main__":
    unittest.main()
