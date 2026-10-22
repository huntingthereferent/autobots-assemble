"""Lane C E15 synthetic set comparison controls, not evidence of biological facts."""
import unittest
from rdflib import Graph, URIRef
from systems.workspace import nih_p2_bgee_full_owlrl_source_comparison as e15
from systems.workspace import nih_p2_bgee_jena_four_rule_source_comparison as four

G = URIRef("urn:synthetic:gene")
T = URIRef("urn:synthetic:target")
X = URIRef("urn:synthetic:outsider")
RAW = {(G, four.bridge.GENEX.isExpressedIn, T)}
EXPECTED = {
    (G, four.bridge.RO_EXPRESSED, T),
    (G, four.GENOMIC, T),
    (T, four.bridge.RO_EXPRESSES, G),
    (T, four.GENOMIC, G),
}

class FullProfileComparisonControls(unittest.TestCase):
    def test_original_node_universe_does_not_hide_unknown_pairs(self):
        graph = Graph()
        for t in EXPECTED | {(G, four.GENOMIC, X), (X, four.GENOMIC, G)}:
            graph.add(t)
        self.assertEqual(e15.select_target(graph, RAW), EXPECTED)

    def test_missing_direction_is_a_failure(self):
        result = e15.compare(EXPECTED - {(T, four.GENOMIC, G)}, EXPECTED)
        self.assertEqual(result["missing_four_rule_triples"], 1)
        self.assertFalse(result["identical_target_sets"])

    def test_extra_direction_is_a_failure(self):
        result = e15.compare(EXPECTED | {(T, four.bridge.RO_EXPRESSED, G)}, EXPECTED)
        self.assertEqual(result["additional_full_profile_triples"], 1)
        self.assertFalse(result["identical_target_sets"])

    def test_wrong_set_with_same_count_is_not_agreement(self):
        wrong = EXPECTED - {(T, four.GENOMIC, G)} | {(T, four.bridge.RO_EXPRESSED, G)}
        out = e15.compare(wrong, EXPECTED)
        self.assertEqual(out["full_profile_scoped_triples"], len(EXPECTED))
        self.assertEqual(out["missing_four_rule_triples"], 1)
        self.assertEqual(out["additional_full_profile_triples"], 1)
        self.assertFalse(out["identical_target_sets"])

    def test_exact_set_digest(self):
        out = e15.compare(set(EXPECTED), EXPECTED)
        self.assertTrue(out["identical_target_sets"])
        self.assertEqual(out["full_profile_target_digest_sha256"],
                         out["source_rule_target_digest_sha256"])

    def test_fixed_source_boundary(self):
        self.assertEqual(e15.SOURCE_TRIPLES, 34181)
        self.assertEqual(e15.SOURCE_EDGES, 25027)
        self.assertEqual(e15.BASELINE, 100108)

if __name__ == "__main__":
    unittest.main()
