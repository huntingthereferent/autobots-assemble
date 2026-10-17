"""Regression witnesses for convergence, dual reason and refusal boundaries."""
import unittest
from views.traces.convergence_focus import evaluate


def edge(a,b,ref="fixture:verified"):
    return {"from":a,"to":b,"kind":"continues_toward","witness":ref}


def verified(item):
    return item["witness"].startswith("fixture:verified")


class FocusTests(unittest.TestCase):
    def test_single_endpoint_must_have_every_observed_path(self):
        r=evaluate(["north","south","target"],
                   [edge("north","target"),edge("south","target")],
                   verify_relation=verified)
        self.assertEqual(r["status"],"ONE_OBSERVED")
        self.assertEqual(r["focus"],["target"])
        self.assertEqual(r["witnessed_relations"],2)

    def test_two_only_with_native_explanation(self):
        nodes=["alpha","beta","one","two"]
        arrows=[edge("alpha","one"),edge("beta","two")]
        result=evaluate(nodes,arrows,verify_relation=verified)
        self.assertEqual(result["status"],"OPEN")
        reason={"endpoints":["one","two"],"reason":"separately witnessed source boundaries",
                "witness":"fixture:verified-split"}
        result=evaluate(nodes,arrows,verify_relation=verified,
                        split=reason,verify_split=verified)
        self.assertEqual(result["status"],"TWO_WITNESSED")
        self.assertEqual(result["focus"],["one","two"])
        self.assertEqual(result["split_reason"],reason["reason"])
        with self.assertRaises(ValueError):
            evaluate(nodes,arrows,verify_relation=verified,
                     split={"endpoints":["one"]},verify_split=verified)

    def test_three_candidates_never_forced_to_one(self):
        r=evaluate(["a","b","c","d"],[edge("a","b")],
                   verify_relation=verified)
        self.assertEqual(r["status"],"OPEN")
        self.assertEqual(r["candidate_endpoints"],["b","c","d"])

    def test_cycles_without_endpoint_stay_open(self):
        r=evaluate(["a","b"],[edge("a","b"),edge("b","a")],
                   verify_relation=verified)
        self.assertEqual(r["status"],"OPEN")
        self.assertEqual(r["focus"],[])

    def test_original_witness_and_nonmatching_edges_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(["a","b"],[edge("a","b","unverified")],
                     verify_relation=verified)
        with self.assertRaises(ValueError):
            evaluate(["a","b"],[edge("a","b")],
                     verify_relation=None)
        with self.assertRaises(ValueError):
            evaluate(["a","b"],[edge("a","a")],
                     verify_relation=verified)

    def test_missing_relations_cannot_create_focus(self):
        r=evaluate(["a","b"],[],verify_relation=verified)
        self.assertEqual(r["status"],"OPEN")
        self.assertEqual(r["focus"],[])


if __name__=="__main__":
    unittest.main()
