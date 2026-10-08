"""Focused real service/HTTP integration; provider results are fixtures, not A/B proof."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import json
import threading
import unittest

from runtime.service import EcosystemService


def activation(instance="one", referent="Observed transition"):
    return {"surface": "begin comparison", "actor_id": "james",
            "instance_id": instance, "referent": referent}


def result(next_referent="", **more):
    return {
        "actor_id": "external-ab-provider",
        "status": "COMPLETE",
        "output": {"delta": {"before": 1, "after": 2}},
        "evidence": [{
            "condition": "movement witness", "kind": "source",
            "source": "example-native-repository-artifact", "ref": "sha256:1234",
            "depth": "reported"
        }],
        "next_referent": next_referent,
        **more
    }


class AgentServiceTests(unittest.TestCase):
    def test_activation_result_next_birth_and_restart_without_duplicates(self):
        with TemporaryDirectory() as tmp:
            first = EcosystemService(data_dir=tmp)
            root = first.activate_agent(activation())["root"]
            self.assertEqual(first.activate_agent(activation())["root"], root)
            with self.assertRaisesRegex(ValueError, "another referent"):
                first.activate_agent(activation(referent="unrelated"))
            self.assertEqual(first.agent_snapshot(root)["ready"], [root])
            event = first.agent_result(root, result(next_referent="Read result again"))
            child = event["step"]["born"][0]
            self.assertEqual(event["lineage"]["ready"], [child])
            self.assertEqual(event["lineage"]["agents"][0]["loop_status"], "OPEN")
            self.assertEqual(first.runtime.get(child).inputs["parent_output"]["delta"],
                             {"before": 1, "after": 2})
            second = EcosystemService(data_dir=tmp)
            self.assertEqual(len(second.agent_snapshot(root)["agents"]), 2)
            self.assertEqual(second.agent_snapshot(root)["ready"], [child])
            with self.assertRaisesRegex(ValueError, "already recorded"):
                second.agent_result(root, result(next_referent="Read result again"))

    def test_ohayo_remains_read_only_and_new_route_requires_post(self):
        with TemporaryDirectory() as tmp:
            service = EcosystemService(data_dir=tmp)
            before = len(service.runtime.snapshot())
            self.assertEqual(service.activate("ohayo", actor_id="james")["items"], [])
            with self.assertRaisesRegex(ValueError, "requires POST"):
                service.activate("begin comparison", actor_id="james")
            self.assertEqual(len(service.runtime.snapshot()), before)
            with self.assertRaises(KeyError):
                service.activate_agent({"surface": "ohayo", "actor_id": "james",
                                        "instance_id": "one"})

    def test_unwitnessed_and_simulated_results_never_move(self):
        with TemporaryDirectory() as tmp:
            service = EcosystemService(data_dir=tmp)
            root = service.activate_agent(activation("missing"))["root"]
            with self.assertRaisesRegex(ValueError, "movement witness"):
                service.agent_result(root, {"actor_id": "provider", "status": "COMPLETE",
                                            "output": {"claim": "done"}})
            bad = result("new")
            bad["evidence"][0]["kind"] = "simulation"
            with self.assertRaises(ValueError):
                service.agent_result(root, bad)
            missing_locator = result("new")
            missing_locator["evidence"][0]["ref"] = ""
            with self.assertRaisesRegex(ValueError, "native ref"):
                service.agent_result(root, missing_locator)
            self.assertEqual(service.agent_snapshot(root)["ready"], [root])

    def test_generic_result_endpoint_cannot_bypass_agent_gate(self):
        with TemporaryDirectory() as tmp:
            service = EcosystemService(data_dir=tmp)
            root = service.activate_agent(activation("spoof"))["root"]
            with self.assertRaisesRegex(ValueError, "agent lineage results require"):
                service.return_result(root, {"status": "COMPLETE", "output": {}},
                                      actor_id="anyone")
            self.assertEqual(service.runtime.state(root).status, "READY")

    def test_unverified_closure_is_not_accepted(self):
        with TemporaryDirectory() as tmp:
            service = EcosystemService(data_dir=tmp)
            root = service.activate_agent(activation("unverified"))["root"]
            child = service.agent_result(root, result("Next result"))["step"]["born"][0]
            claim = result("", closes=[root],
                           closure_evidence=[{"condition": "ancestor closure",
                                              "kind": "source", "source": "caller",
                                              "ref": "claim"}],
                           closure_birth_referent="Unverified new task")
            step = service.agent_result(child, claim)
            self.assertEqual(step["step"]["closed"], [])
            self.assertEqual(len(service.agent_snapshot(root)["agents"]), 2)

    def test_explicit_injected_closure_verifier_and_recovery(self):
        with TemporaryDirectory() as tmp:
            # This fixture's callback stands in for an external admission check;
            # it is not a claim to have proved semantic A/B correspondence.
            def verify(descendant, ancestor, evidence):
                return any(w.condition == "ancestor closure" and
                           w.ref == "test-only:checked" for w in evidence)
            service = EcosystemService(data_dir=tmp, closure_admitter=verify)
            root = service.activate_agent(activation("verified"))["root"]
            child = service.agent_result(root, result("Second comparison"))["step"]["born"][0]
            move = result("", closes=[root],
                          closure_evidence=[{"condition": "ancestor closure",
                                             "kind": "source", "source": "fixture",
                                             "ref": "test-only:checked"}],
                          closure_birth_referent="Closure exposed another comparison")
            out = service.agent_result(child, move)
            self.assertEqual(out["step"]["closed"], [root])
            self.assertEqual(len(out["lineage"]["agents"]), 3)
            restarted = EcosystemService(data_dir=tmp)
            self.assertEqual(len(restarted.agent_snapshot(root)["agents"]), 3)
            self.assertEqual(restarted.agent_snapshot(root)["agents"][0]["loop_status"], "CLOSED")

    def test_wall_is_preserved_without_birth(self):
        with TemporaryDirectory() as tmp:
            service = EcosystemService(data_dir=tmp)
            root = service.activate_agent(activation("wall"))["root"]
            out = service.agent_result(root, {"actor_id": "provider", "status": "UNKNOWN",
                                              "note": "missing source", "next_referent": "invented"})
            self.assertEqual(out["step"]["unresolved"], [root])
            self.assertEqual(len(out["lineage"]["agents"]), 1)
            self.assertEqual(out["lineage"]["agents"][0]["status"], "UNKNOWN")

    def test_registered_in_process_evaluator_advances_from_activation(self):
        from runtime.agent_lineage import AgentMove
        from runtime.handoff import EvidenceRecord, ExecutionResult

        calls = []
        def compare(handoff, _state):
            calls.append(handoff.handoff_id)
            generation = handoff.metadata["generation"]
            return AgentMove(
                result=ExecutionResult(
                    status="COMPLETE", output={"evaluated_generation": generation},
                    evidence=(EvidenceRecord(condition="movement witness", kind="source",
                                             source="test-provider", ref="native:fixture",
                                             depth="reported"),),
                ),
                next_referent="Admitted next comparison" if generation == 1 else "",
            )

        with TemporaryDirectory() as tmp:
            service = EcosystemService(data_dir=tmp, ab_evaluator=compare)
            result_view = service.activate_agent(activation("auto"))
            self.assertEqual(len(result_view["agents"]), 2)
            self.assertEqual([item["status"] for item in result_view["agents"]],
                             ["COMPLETE", "COMPLETE"])
            self.assertEqual(len(calls), 2)
            self.assertEqual(service.activate_agent(activation("auto"))["root"],
                             result_view["root"])
            self.assertEqual(len(calls), 2)
            # Recovered runtime state does not run a new comparator at startup.
            restarted = EcosystemService(data_dir=tmp, ab_evaluator=compare)
            self.assertEqual(len(calls), 2)
            self.assertEqual(len(restarted.agent_snapshot(result_view["root"])["agents"]), 2)

    def test_local_http_activation_and_handoff(self):
        import runtime.http_server as http
        from http.server import ThreadingHTTPServer
        with TemporaryDirectory() as tmp:
            service = EcosystemService(data_dir=Path(tmp) / "service")
            with patch.object(http, "SERVICE", service):
                server = ThreadingHTTPServer(("127.0.0.1", 0), http.Handler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                url = f"http://127.0.0.1:{server.server_port}"
                def request(path, data=None):
                    body = None if data is None else json.dumps(data).encode()
                    req = Request(url + path, data=body,
                                  headers={"Content-Type": "application/json"})
                    with urlopen(req, timeout=3) as response:
                        return json.load(response)
                try:
                    with self.assertRaises(HTTPError) as failure:
                        request("/api/activate?surface=begin%20comparison&actor=james")
                    self.assertEqual(failure.exception.code, 400)
                    root = request("/api/agents/activate", activation("http"))["root"]
                    self.assertEqual(request("/api/agents?root=" + root)["ready"], [root])
                    born = request("/api/agents/" + root + "/result",
                                   result("Another A/B"))["step"]["born"]
                    self.assertEqual(len(born), 1)
                    self.assertEqual(request("/api/agents?root=" + root)["ready"], born)
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
