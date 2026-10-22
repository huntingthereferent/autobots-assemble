"""E18 original source-referent all-RDF predicate coverage and fail-closed controls."""
from __future__ import annotations
from unittest.mock import patch
import unittest
from rdflib import Graph,URIRef,RDF,OWL,Literal
from systems.workspace import nih_p2_bgee_original_referent_all_predicate_inventory as e18
from systems.workspace import nih_p2_bgee_jena_four_rule_source_comparison as four

GENE=URIRef("urn:e18:gene")
ANATOMY=URIRef("urn:e18:anatomy")
OTHER=URIRef("urn:e18:other")
UNRELATED=URIRef("urn:e18:unrelated")
ORIGINAL={(GENE,four.bridge.GENEX.isExpressedIn,ANATOMY)}
RULE={
    (GENE,four.bridge.RO_EXPRESSED,ANATOMY),
    (GENE,four.GENOMIC,ANATOMY),
    (ANATOMY,four.bridge.RO_EXPRESSES,GENE),
    (ANATOMY,four.GENOMIC,GENE),
}


def fixture(add=True):
    g=Graph()
    for triple in ORIGINAL|RULE:
        g.add(triple)
    if add:
        g.add((GENE,RDF.type,URIRef("urn:e18:GeneClass")))
        g.add((ANATOMY,OWL.sameAs,OTHER))
        g.add((GENE,URIRef("urn:e18:experimentalPredicate"),Literal("not biomedical")))
        g.add((OTHER,URIRef("urn:e18:unrelatedPredicate"),UNRELATED))
    return g


class E18OriginalReferentAllPredicateTests(unittest.TestCase):
    def test_native_and_sparql_agree_across_all_original_node_predicates(self):
        g=fixture()
        first=e18.graph_scope_native(g,ORIGINAL)
        second=e18.graph_scope_sparql(g,ORIGINAL)
        self.assertEqual(first,second)
        self.assertEqual(len(first),len(ORIGINAL|RULE)+3)
        self.assertNotIn((OTHER,URIRef("urn:e18:unrelatedPredicate"),UNRELATED),first)

    def test_full_profile_extra_schema_metadata_not_mislabeled_biological(self):
        graph=fixture()
        base=ORIGINAL
        full=e18.graph_scope_native(graph,ORIGINAL)
        with patch.object(e18,"FOUR_RULE_TOTAL",4):
            result=e18.compare(base,full,e18.graph_scope_sparql(graph,ORIGINAL),ORIGINAL,RULE)
        self.assertEqual(result["remaining_entailments_beyond_source_plus_four_rules"],3)
        self.assertEqual(result["other_predicate_classifications"]["rdf_type"],1)
        self.assertEqual(result["other_predicate_classifications"]["owl_sameAs"],1)
        self.assertEqual(result["other_predicate_classifications"]["other_predicates"],1)
        self.assertEqual(result["remaining_entailments_under_same_three_RO_predicates"],0)
        self.assertTrue(result["additional_RDF_closure_statements_are_not_new_biomedical_observations"])
        self.assertFalse(result["independent_complete_OWL_RL_reasoner_confirmed"])

    def test_separate_scan_disagreement_fails(self):
        first=e18.graph_scope_native(fixture(),ORIGINAL)
        with patch.object(e18,"FOUR_RULE_TOTAL",4):
            with self.assertRaisesRegex(ValueError,"native and SPARQL disagree"):
                e18.compare(ORIGINAL,first,first-{(GENE,RDF.type,URIRef("urn:e18:GeneClass"))},ORIGINAL,RULE)

    def test_missing_original_source_statement_fails(self):
        with patch.object(e18,"FOUR_RULE_TOTAL",4):
            with self.assertRaisesRegex(ValueError,"lost authenticated original"):
                e18.compare(ORIGINAL,RULE,RULE,ORIGINAL,RULE)

    def test_missing_original_rule_conclusion_fails(self):
        measured=ORIGINAL|set(list(RULE)[:3])
        with patch.object(e18,"FOUR_RULE_TOTAL",4):
            with self.assertRaisesRegex(ValueError,"four original-owner rule"):
                e18.compare(ORIGINAL,measured,measured,ORIGINAL,RULE)

    def test_no_beyond_source_set_can_be_reported_without_fake_differences(self):
        observed=ORIGINAL|RULE
        with patch.object(e18,"FOUR_RULE_TOTAL",4):
            result=e18.compare(ORIGINAL,observed,observed,ORIGINAL,RULE)
        self.assertEqual(result["remaining_entailments_beyond_source_plus_four_rules"],0)
        self.assertEqual(result["four_rule_source_relationships_missing"],0)

    def test_native_node_partition_overlap_is_invalid(self):
        with self.assertRaisesRegex(ValueError,"overlap"):
            e18.native_nodes({(GENE,four.bridge.GENEX.isExpressedIn,GENE)})

    def test_added_all_predicate_ontology_fact_is_counted_without_original_subject(self):
        graph=fixture(False)
        graph.add((OTHER,RDF.type,ANATOMY))
        native=e18.graph_scope_native(graph,ORIGINAL)
        sparql=e18.graph_scope_sparql(graph,ORIGINAL)
        self.assertEqual(native,sparql)
        self.assertIn((OTHER,RDF.type,ANATOMY),native)


if __name__=="__main__":
    unittest.main()
