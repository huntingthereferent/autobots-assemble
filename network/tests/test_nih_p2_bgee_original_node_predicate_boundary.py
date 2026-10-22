"""E16 neutral audit: keep all RO predicate facts touching original Bgee nodes."""
from __future__ import annotations
import unittest
from rdflib import Graph,URIRef
from systems.workspace import nih_p2_bgee_original_node_predicate_boundary as e16
from systems.workspace import nih_p2_bgee_jena_four_rule_source_comparison as four

G=URIRef("urn:e16:gene")
T=URIRef("urn:e16:anatomy")
OTHER=URIRef("urn:e16:unseen")
OTHER2=URIRef("urn:e16:unseen2")
SOURCE={(G,four.bridge.GENEX.isExpressedIn,T)}
EXPECTED={
    (G,four.bridge.RO_EXPRESSED,T),
    (G,four.GENOMIC,T),
    (T,four.bridge.RO_EXPRESSES,G),
    (T,four.GENOMIC,G),
}
EXTRA={
    (G,four.GENOMIC,OTHER),
    (OTHER,four.bridge.RO_EXPRESSES,G),
    (T,four.GENOMIC,OTHER),
}


def example(include_extra=True):
    g=Graph()
    for t in EXPECTED | (EXTRA if include_extra else set()):
        g.add(t)
    return g


class OriginalNodePredicateScopeAuditTests(unittest.TestCase):
    def test_unrestricted_scope_retains_new_pairings_not_in_prior_four_rule_set(self):
        graph=example()
        native=e16.unrestricted_direct_predicate_scan(graph,SOURCE)
        independent=e16.independent_sparql_predicate_scan(graph,SOURCE)
        self.assertEqual(native,EXPECTED|EXTRA)
        self.assertEqual(independent,native)
        got=e16.compare_all_source_nodes(native,independent,EXPECTED,SOURCE)
        self.assertEqual(got["additional_original_node_predicate_triples_not_in_four_rule_set"],3)
        self.assertEqual(got["additional_predicate_orientations"]["gene_to_other"],1)
        self.assertEqual(got["additional_predicate_orientations"]["other_to_gene"],1)
        self.assertEqual(got["additional_predicate_orientations"]["native_target_to_other"],1)
        self.assertFalse(got["official_NIH_score"])

    def test_non_original_node_pair_is_out_of_predeclared_scope(self):
        graph=example()
        graph.add((OTHER,four.GENOMIC,OTHER2))
        self.assertEqual(e16.unrestricted_direct_predicate_scan(graph,SOURCE),EXPECTED|EXTRA)

    def test_prior_source_owned_rule_missing_must_fail(self):
        graph=example(False)
        lost=EXPECTED-{(T,four.GENOMIC,G)}
        with self.assertRaisesRegex(ValueError,"absent"):
            e16.compare_all_source_nodes(lost,lost,EXPECTED,SOURCE)

    def test_native_vs_separate_sparql_disagreement_fails(self):
        got=EXPECTED|EXTRA
        with self.assertRaisesRegex(ValueError,"SPARQL disagreement"):
            e16.compare_all_source_nodes(got,EXPECTED,EXPECTED,SOURCE)

    def test_zero_extra_is_specific_verifiable_result_not_default(self):
        graph=example(False)
        a=e16.unrestricted_direct_predicate_scan(graph,SOURCE)
        b=e16.independent_sparql_predicate_scan(graph,SOURCE)
        result=e16.compare_all_source_nodes(a,b,EXPECTED,SOURCE)
        self.assertEqual(result["additional_original_node_predicate_triples_not_in_four_rule_set"],0)
        self.assertEqual(result["previously_verified_source_rule_triples_missing"],0)

    def test_foreign_predicate_and_wrong_node_uris_do_not_count(self):
        graph=example(False)
        graph.add((G,URIRef("urn:fake:unapproved"),OTHER))
        graph.add((OTHER,URIRef("urn:fake:unapproved"),G))
        self.assertEqual(e16.unrestricted_direct_predicate_scan(graph,SOURCE),EXPECTED)

    def test_original_referent_partition_is_not_synthetic_biology(self):
        genes,targets=e16.owner_node_universe(SOURCE)
        self.assertEqual(genes,{G})
        self.assertEqual(targets,{T})
        self.assertFalse(e16.compare_all_source_nodes(EXPECTED,EXPECTED,EXPECTED,SOURCE)
                         ["second_independent_complete_OWL_RL_engine_verified"])

    def test_overlapping_gene_target_node_roles_refused(self):
        with self.assertRaisesRegex(ValueError,"colliding"):
            e16.owner_node_universe({(G,four.bridge.GENEX.isExpressedIn,G)})


if __name__=="__main__":
    unittest.main()
