import copy
import json
import unittest
from pathlib import Path
from reference import backward_paths, edge_verdict, toy_verifier, validate

EXAMPLE = json.loads((Path(__file__).parent / "example.json").read_text())


class ReferenceTests(unittest.TestCase):
    def test_two_routes_preserved(self):
        routes = backward_paths(EXAMPLE)
        self.assertEqual([[s["edge_id"] for s in x["steps"]] for x in routes], [["Q", "P"], ["S", "R"]])

    def test_claims_are_not_verified_by_default(self):
        first = backward_paths(EXAMPLE)[0]
        self.assertEqual([s["observation"] for s in first["steps"]], ["UNKNOWN", "UNKNOWN"])

    def test_toy_observations_do_not_replace_unobserved_branch(self):
        routes = backward_paths(EXAMPLE, toy_verifier)
        self.assertEqual([s["observation"] for s in routes[0]["steps"]], ["SUPPORTED", "SUPPORTED"])
        self.assertEqual([s["observation"] for s in routes[1]["steps"]], ["PROPOSED", "PROPOSED"])

    def test_one_missing_condition_not_supported(self):
        d = copy.deepcopy(EXAMPLE)
        d["observations"] = [o for o in d["observations"] if o["id"] != "demo-obs-P2"]
        self.assertEqual(backward_paths(d, toy_verifier)[0]["steps"][1]["observation"], "UNKNOWN")

    def test_contradiction_only_in_observational_gate(self):
        p = EXAMPLE["candidates"][0]
        obs = EXAMPLE["observations"]
        self.assertEqual(edge_verdict(p, obs, lambda edge, o: "CONTRADICTED" if o["condition"] == "schema_preserved" else "SUPPORTED"), "CONTRADICTED")

    def test_missing_middle_is_open_requirement(self):
        d = copy.deepcopy(EXAMPLE)
        d["candidates"] = [e for e in d["candidates"] if e["id"] == "Q"]
        d["observations"] = [o for o in d["observations"] if o["edge_id"] == "Q"]
        self.assertEqual(backward_paths(d)[0]["status"], "OPEN_REQUIREMENT")

    def test_cycle_is_bounded(self):
        d = copy.deepcopy(EXAMPLE)
        d["candidates"].append({"id": "LOOP", "from": "TARGET_B", "to": "NORMALIZED_P", "relation": "loop", "required_conditions": ["verified_loop"]})
        self.assertTrue(any(x["status"] == "CYCLE" for x in backward_paths(d)))

    def test_duplicate_node_refused(self):
        d = copy.deepcopy(EXAMPLE)
        d["nodes"].append(d["nodes"][0])
        with self.assertRaises(ValueError):
            validate(d)

    def test_unadmitted_observation_condition_refused(self):
        d = copy.deepcopy(EXAMPLE)
        d["observations"][0]["condition"] = "not_in_contract"
        with self.assertRaises(ValueError):
            validate(d)

    def test_unknown_verifier_result_refused(self):
        with self.assertRaises(ValueError):
            backward_paths(EXAMPLE, lambda edge, obs: "DONE")

    def test_unverified_scope_cannot_be_promoted(self):
        d = copy.deepcopy(EXAMPLE)
        d["observations"][0]["witness_ref"] = "fixture://wrong"
        self.assertEqual(backward_paths(d, toy_verifier)[0]["steps"][1]["observation"], "UNKNOWN")

    def test_proposed_route_does_not_automatically_finish_target(self):
        routes = backward_paths(EXAMPLE, toy_verifier)
        self.assertTrue(any(s["observation"] == "PROPOSED" for r in routes for s in r["steps"]))
        self.assertEqual([r["status"] for r in routes], ["REACHES_SOURCE", "REACHES_SOURCE"])
        # REACHES_SOURCE means a declared candidate path exists, not that a job ran.


if __name__ == "__main__":
    unittest.main()
