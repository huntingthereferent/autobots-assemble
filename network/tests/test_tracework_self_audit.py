"""Regression: audit referent is finite; children and evidence determine closure."""
import copy
import unittest
from systems.workspace.bounded_audit import assess, add_child, close, validate


def fixture():
    return {"schema": "tracework/bounded-audit/v1", "id": "audit-a",
            "referent": "initial observed mismatch", "state": "open",
            "nodes": [{"id": "run", "parent": "audit-a", "kind": "workflow",
                       "requirement": "source verified workflow",
                       "state": "open", "evidence": None},
                      {"id": "repair", "parent": "run", "kind": "repair",
                       "requirement": "correct mismatch",
                       "state": "open", "evidence": None}]}


class FiniteAuditTests(unittest.TestCase):
    def test_missing_evidence_never_closes(self):
        self.assertFalse(assess(fixture())["ready_to_close"])

    def test_descendant_must_close_first(self):
        a = fixture()
        a["nodes"][0].update(state="passed", evidence={"verified": True, "source": "github",
                                   "run_id": 42, "head_sha": "abc", "conclusion": "success"})
        self.assertFalse(assess(a)["ready_to_close"])
        a["nodes"][1].update(state="passed", evidence={"verified": True, "source": "source diff"})
        self.assertTrue(assess(a)["ready_to_close"])
        b = close(a)
        self.assertTrue(assess(b)["closed"])
        with self.assertRaises(ValueError):
            add_child(b, {"id": "later", "parent": "audit-a", "kind": "check",
                          "state": "open", "requirement": "new work"})

    def test_failed_workflow_cannot_pass_by_label(self):
        a = fixture()
        for n in a["nodes"]:
            n.update(state="passed", evidence={"verified": True, "source": "source"})
        a["nodes"][0]["evidence"].update(run_id=1, head_sha="abc", conclusion="failure")
        self.assertFalse(assess(a)["ready_to_close"])

    def test_child_must_be_bounded_by_existing_parent(self):
        with self.assertRaises(ValueError):
            add_child(fixture(), {"id": "orphan", "parent": "other", "kind": "check",
                                  "state": "open", "requirement": "no"})

    def test_cycles_rejected(self):
        a = fixture()
        a["nodes"][0]["parent"] = "repair"
        with self.assertRaises(ValueError):
            validate(a)

    def test_original_referent_preserved(self):
        a = fixture()
        b = add_child(a, {"id": "next", "parent": "audit-a", "kind": "check",
                          "state": "open", "requirement": "nested check"})
        self.assertEqual(b["referent"], a["referent"])
        self.assertEqual(len(a["nodes"]), 2)


if __name__ == "__main__":
    unittest.main()
