"""Inspector Gadget: native movement, pinning and negative-boundary regressions."""
import unittest
from systems.workspace.inspector_gadget_adapter import (
    activate, from_cancel_event, plan,
)


def entry(run_id=51, lane="ARC native", event="cancelled", workflow_id=20):
    return {
        "id": f"inspector-{workflow_id}-{event}-{run_id}",
        "kind": "candidate", "event": event, "lane": lane,
        "run_ids": [run_id],
        "sources": [f"https://github.com/o/r/actions/runs/{run_id}"],
        "head_shas": ["a" * 40],
    }


def scan(findings):
    return {"schema": "inspector-gadget/workflow-scan/v1", "findings": findings}


def source(selection):
    return {"id": selection["run_id"], "workflow_id": selection["workflow_id"],
            "name": selection["lane"], "conclusion": selection["event"],
            "html_url": selection["source"], "head_sha": selection["head_sha"]}


class InspectorGadgetAdapterTests(unittest.TestCase):
    def test_every_distinct_owner_lane_activates_native_handoff(self):
        findings = [entry(51, "ARC", "cancelled", 20),
                    entry(52, "NIH Phase 2", "failure", 21),
                    entry(53, "WORLD research", "timed_out", 22),
                    entry(54, "Meow Lab v2 browser", "action_required", 23)]
        prepared = plan(scan(findings))
        self.assertEqual(prepared["selected"], 4)
        self.assertEqual(prepared["overflow_count"], 0)
        for selection in prepared["matrix"]["include"]:
            checked = []
            def read(repo, run_id, token):
                checked.append((repo, run_id))
                return source(selection)
            result = activate(selection, repo="o/r", token="fake-test-token", fetcher=read)
            self.assertEqual(checked, [("o/r", selection["run_id"])])
            self.assertEqual(result["state"]["status"], "COMPLETE")
            self.assertEqual(result["audit"]["state"], "awaiting_verification")
            self.assertEqual(result["state"]["output"]["source_verified"], True)
            self.assertFalse(result["state"]["output"]["repair_dispatched"])
            self.assertEqual([e["event_type"] for e in result["events"]],
                             ["CREATED", "STARTED", "RESULT"])
            self.assertEqual(result["handoff"]["provenance"][1],
                             "workspace-lane:" + selection["lane"])
            self.assertEqual(result["handoff"]["metadata"]["native_evidence_verifier"],
                             "inspector-gadget-github-run-v1")

    def test_changed_source_is_partial_not_repaired(self):
        selection = plan(scan([entry()]))["matrix"]["include"][0]
        altered = source(selection)
        altered["conclusion"] = "success"
        r = activate(selection, repo="o/r", token="x",
                     fetcher=lambda *args: altered)
        self.assertEqual(r["state"]["status"], "PARTIAL")
        self.assertFalse(r["state"]["output"]["source_verified"])
        self.assertFalse(r["state"]["evidence"])

    def test_no_repair_from_expected_cancellation(self):
        selection = plan(scan([entry()]))["matrix"]["include"][0]
        r = activate(selection, repo="o/r", token="x",
                     fetcher=lambda *args: source(selection))
        self.assertEqual(r["state"]["output"]["diagnosis"], "not established")
        self.assertFalse(r["state"]["output"]["repair_dispatched"])

    def test_bad_source_and_cross_repo_cannot_activate(self):
        selection = plan(scan([entry()]))["matrix"]["include"][0]
        with self.assertRaises(ValueError):
            activate(selection, repo="wrong/repository", token="x",
                     fetcher=lambda *args: source(selection))
        selection["source"] = "https://example.invalid/actions/runs/51"
        with self.assertRaises(ValueError):
            activate(selection, repo="o/r", token="x",
                     fetcher=lambda *args: source(selection))

    def test_bounded_activation_reports_unprocessed_work(self):
        candidates = [entry(i, "NIH", "failure", i) for i in range(10, 15)]
        p = plan(scan(candidates), max_movements=2)
        self.assertEqual(p["selected"], 2)
        self.assertEqual(p["overflow_count"], 3)

    def test_self_incidents_do_not_recurse(self):
        p = plan(scan([entry(33, "Inspector Gadget - All Workflows")]))
        self.assertEqual(p["selected"], 0)
        self.assertEqual(len(p["self_observation_withheld"]), 1)

    def test_malformed_or_duplicate_finding_is_rejected(self):
        duplicate = entry()
        with self.assertRaises(ValueError):
            plan(scan([duplicate, duplicate]))
        wrong = entry()
        wrong["sources"] = []
        with self.assertRaises(ValueError):
            plan(scan([wrong]))

    def test_direct_cancel_event_is_also_real_movement(self):
        selection = from_cancel_event({"action": "completed", "workflow_run": {
            "id": 75, "workflow_id": 12, "name": "ARC",
            "conclusion": "cancelled",
            "html_url": "https://github.com/o/r/actions/runs/75",
            "head_sha": "c" * 40,
        }})
        self.assertEqual(selection["run_id"], 75)
        r = activate(selection, repo="o/r", token="x",
                     fetcher=lambda *args: source(selection))
        self.assertEqual(r["state"]["status"], "COMPLETE")
        with self.assertRaises(ValueError):
            from_cancel_event({"action": "completed",
                               "workflow_run": {"conclusion": "success"}})


if __name__ == "__main__":
    unittest.main()
