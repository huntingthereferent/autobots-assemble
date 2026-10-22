"""E17 tests: synthetic counterexamples, not original biological evidence."""
import unittest
from rdflib import Graph,URIRef,RDFS,OWL
from systems.workspace import nih_p2_bgee_full_owlrl_source_axiom_ablations as e17
from systems.workspace import nih_p2_bgee_jena_four_rule_source_comparison as four

GENE=URIRef("urn:fixture:gene")
TARGET=URIRef("urn:fixture:target")
def fixture():
    graph=Graph()
    axioms=[
        (four.bridge.GENEX.isExpressedIn,RDFS.subPropertyOf,four.bridge.RO_EXPRESSED),
        (four.bridge.RO_EXPRESSED,RDFS.subPropertyOf,four.GENOMIC),
        (four.bridge.RO_EXPRESSED,OWL.inverseOf,four.bridge.RO_EXPRESSES),
        (four.bridge.RO_EXPRESSES,RDFS.subPropertyOf,four.GENOMIC)]
    for x in axioms: graph.add(x)
    graph.add((GENE,four.bridge.GENEX.isExpressedIn,TARGET))
    return graph,axioms

class FullProfileSourceAblationControls(unittest.TestCase):
    def test_exactly_one_source_axiom_per_fresh_copy(self):
        original,axioms=fixture()
        for name,index in four.PREMISE_MODES.items():
            derived=e17.independent_copy_without(original,axioms[index])
            self.assertEqual(len(derived),4)
            self.assertEqual(len(original),5)
            self.assertNotIn(axioms[index],derived)
            self.assertIn(axioms[index],original)

    def test_missing_premise_rejected(self):
        original,_=fixture()
        with self.assertRaises(ValueError):
            e17.independent_copy_without(original,(GENE,RDFS.subPropertyOf,TARGET))

    def test_set_identity_not_just_equal_counts(self):
        edges={(GENE,four.bridge.GENEX.isExpressedIn,TARGET)}
        expected={(GENE,four.bridge.RO_EXPRESSED,TARGET),
                  (GENE,four.GENOMIC,TARGET),
                  (TARGET,four.bridge.RO_EXPRESSES,GENE),
                  (TARGET,four.GENOMIC,GENE)}
        equal=e17.difference(expected,expected,edges)
        self.assertTrue(equal["equal_scoped_sets"])
        wrong=expected-{(TARGET,four.GENOMIC,GENE)} | {(TARGET,four.bridge.RO_EXPRESSED,GENE)}
        with self.assertRaises(ValueError):
            e17.difference(expected,wrong,edges)
        result=e17.difference(expected,expected-{(TARGET,four.GENOMIC,GENE)},edges)
        self.assertEqual(result["missing_selected_rule_consequences"],1)
        self.assertFalse(result["equal_scoped_sets"])

    def test_four_source_ablations_are_distinct(self):
        self.assertEqual(set(four.PREMISE_MODES),{
            "omit-genex","omit-genomic","omit-inverse","omit-inverse-genomic"})
        self.assertEqual(e17.SOURCE_GRAPH_SIZE,34181)
        self.assertEqual(e17.SOURCE_EDGES,25027)

if __name__=="__main__":
    unittest.main()
