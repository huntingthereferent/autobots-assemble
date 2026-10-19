"""Computational/consent tests; fixture inputs are not native source witnesses."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from systems.workspace.owner_game_ready_bridge import (
    expected_receipt, OwnerGameReadyBridge, SOURCE, FILE, TEMPORAL_EVENT, BROWSER_EVENT)
from systems.workspace.owner_game_ready_execution import REQUEST, expected_request, authenticate
from systems.workspace.owner_temporal_handoff import SOURCES, CHILD_EVENT


def computational_fixture():
    return {"kind":"owner-w13-adapter-readiness/v1","adapter":{
        "route":"controls.run_job","exact_confirmation":"game-w13-github-001",
        "wrong_confirmation_rejected":True},"source_pair":{
        "schema":"owner-temporal-source-pair/v1",
        "state":"BOTH_NATIVE_HISTORIES_FRESHLY_REVERIFIED_SEPARATELY",
        "owner_parent_event":"evt_208f2fbdb380437eb59790a9a704c0b9",
        "owner_child_event":CHILD_EVENT,"temporal_result_event":TEMPORAL_EVENT,
        "temporal_browser_event":BROWSER_EVENT,"source_artifacts":copy.deepcopy(SOURCES),
        "temporal_live_queries":5,"journal_hashes_unchanged":True,
        "owner_runtime_contains_temporal_source":False,"native_dependency_join_witnessed":False,
        "game_worker_ready_witnessed":False}}


class OwnerGameReadyTests(unittest.TestCase):
    def test_worker_subprocess_matches_independent_host_for_computational_fixture(self):
        data = computational_fixture()
        proc = subprocess.run([sys.executable,"-I",str(SOURCE/FILE)],input=json.dumps(data),
            capture_output=True,text=True,check=True,timeout=8)
        result = json.loads(proc.stdout)
        self.assertEqual(result["receipt"],expected_receipt(data))
        self.assertGreater(result["pid"],0)
        self.assertNotEqual(result["pid"],os.getpid())

    def test_host_refuses_source_event_or_scope_substitution(self):
        for key, value in (("owner_child_event","evt_"+"a"*32),
                ("temporal_result_event","evt_"+"b"*32),
                ("temporal_browser_event","evt_"+"c"*32),
                ("temporal_live_queries",0), ("journal_hashes_unchanged",False),
                ("owner_runtime_contains_temporal_source",True),
                ("native_dependency_join_witnessed",True),
                ("game_worker_ready_witnessed",True)):
            data = computational_fixture()
            data["source_pair"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                expected_receipt(data)
        data = computational_fixture()
        data["source_pair"]["source_artifacts"]["temporal"]["digest"] = "sha256:"+"0"*64
        with self.assertRaises(ValueError):
            expected_receipt(data)

    def test_wrong_route_is_refused_by_host_and_worker(self):
        data = computational_fixture()
        data["adapter"]["wrong_confirmation_rejected"] = False
        with self.assertRaises(ValueError):
            expected_receipt(data)
        proc = subprocess.run([sys.executable,"-I",str(SOURCE/FILE)],input=json.dumps(data),
            capture_output=True,text=True,timeout=8)
        self.assertEqual(proc.returncode,2)

    def test_delegated_bridge_does_not_register_a_second_native_verifier(self):
        class ExistingRuntime:
            def register_evidence_verifier(self,*args):
                raise AssertionError("duplicate native verifier")
        OwnerGameReadyBridge(runtime=ExistingRuntime(),workstation=object(),register=False)

    def test_owner_merge_consent_rejects_single_parent_replay_and_changed_scope(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                return subprocess.run(["git","-C",str(root),*args],check=True,
                    capture_output=True,text=True).stdout.strip()
            git("init","-q","-b","main")
            git("config","user.name","Consent Test")
            git("config","user.email","test@example.invalid")
            (root/"seed").write_text("source\n")
            git("add","."); git("commit","-qm","source")
            git("checkout","-qb","request")
            request = root/REQUEST
            request.parent.mkdir(parents=True)
            request.write_text(json.dumps(expected_request()))
            git("add","."); git("commit","-qm","request")
            single = git("rev-parse","HEAD")
            def environment(commit):
                return {"GITHUB_EVENT_NAME":"push","GITHUB_REF":"refs/heads/main",
                    "GITHUB_REPOSITORY":"huntingthereferent/autobots-assemble",
                    "GITHUB_ACTOR":"huntingthereferent","GITHUB_RUN_ATTEMPT":"1",
                    "GITHUB_SHA":commit}
            with patch.dict(os.environ,environment(single)), self.assertRaises(ValueError):
                authenticate(root,single)
            git("checkout","-q","main"); git("merge","--no-ff","-qm","owner merge","request")
            merge = git("rev-parse","HEAD")
            with patch.dict(os.environ,environment(merge)):
                authenticate(root,merge)
                with patch.dict(os.environ,{"GITHUB_RUN_ATTEMPT":"2"}), self.assertRaises(ValueError):
                    authenticate(root,merge)
                changed = expected_request(); changed["authorizes_NIH_P2_TEST"] = True
                request.write_text(json.dumps(changed))
                with self.assertRaises(ValueError):
                    authenticate(root,merge)


if __name__ == "__main__":
    unittest.main()
