"""E19 original-source type and OWL identity: independent scan controls."""
from __future__ import annotations
import unittest
from rdflib import Graph,URIRef,RDF,OWL
from systems.workspace import nih_p2_bgee_original_identity_type_audit as e19
from systems.workspace import nih_p2_bgee_jena_four_rule_source_comparison as owner

G=URIRef("urn:synthetic:e19:gene")
A=URIRef("urn:synthetic:e19:anatomy")
G2=URIRef("urn:synthetic:e19:external")
CLASS=URIRef("urn:synthetic:e19:class")
SOURCE={(G,owner.bridge.GENEX.isExpressedIn,A)}
SAME={(G,OWL.sameAs,G),(A,OWL.sameAs,A)}
TYPES={(G,RDF.type,CLASS),(A,RDF.type,CLASS)}


def graph(rows):
    g=Graph()
    for row in rows:g.add(row)
    return g


class E19SourceIdentityTypeTests(unittest.TestCase):
    def test_independent_type_identity_scans_agree(self):
        g=graph(SAME|TYPES|{(G2,URIRef("urn:foreign"),A)})
        native=e19.identity_type_scope_native(g,SOURCE)
        sparql=e19.identity_type_scope_sparql(g,SOURCE)
        self.assertEqual(native,sparql)
        self.assertEqual(native,SAME|TYPES)

    def test_self_only_identity_is_explicit_not_assumed(self):
        result=e19.compare_identity_type(set(),SAME|TYPES,SAME|TYPES,SOURCE)
        self.assertEqual(result["original_referent_nodes_total"],2)
        self.assertEqual(result["whole_closure_reflexive_sameAs"],2)
        self.assertEqual(result["whole_closure_nonreflexive_sameAs"],0)
        self.assertEqual(result["original_nodes_lacking_reflexive_self_identity"],0)
        self.assertEqual(result["full_profile_rdf_type_touching_original_nodes"],2)
        self.assertEqual(result["full_profile_inferred_rdf_type_touching_original_nodes"],2)
        self.assertFalse(result["independent_complete_general_OWL_RL_engine_run"])

    def test_source_authored_and_inferred_type_totals_reconcile(self):
        original={(G,RDF.type,CLASS),(A,RDF.type,CLASS)}
        new_class=URIRef("urn:synthetic:e19:inferred-only-class")
        inferred={(G,RDF.type,new_class),(A,RDF.type,new_class)}
        materialized=original|inferred|SAME
        result=e19.compare_identity_type(original,materialized,materialized,SOURCE)
        self.assertEqual(result["source_original_rdf_type"],2)
        self.assertEqual(result["full_profile_inferred_rdf_type_touching_original_nodes"],2)
        self.assertEqual(result["full_profile_rdf_type_touching_original_nodes"],4)
        self.assertEqual(result["full_profile_rdf_type_touching_original_nodes"],
                         result["source_original_rdf_type"]+
                         result["full_profile_inferred_rdf_type_touching_original_nodes"])
        self.assertEqual(sum(result["full_profile_added_type_endpoints"].values()),2)

    def test_nonreflexive_identity_alias_is_not_hidden(self):
        cross=(G,OWL.sameAs,A)
        results=SAME|TYPES|{cross}
        report=e19.compare_identity_type(set(),results,results,SOURCE)
        self.assertEqual(report["whole_closure_nonreflexive_sameAs"],1)
        self.assertEqual(report["nonreflexive_sameAs_orientation_counts"]["gene_to_target"],1)
        self.assertTrue(report["nonreflexive_identity_results_are_hypotheses_not_gene_alias_evidence"])

    def test_missing_original_gene_self_identity_is_counted(self):
        partial=(SAME-{(G,OWL.sameAs,G)})|TYPES
        report=e19.compare_identity_type(set(),partial,partial,SOURCE)
        self.assertEqual(report["original_nodes_lacking_reflexive_self_identity"],1)

    def test_source_authored_original_type_facts_separated_from_inferences(self):
        original={(G,RDF.type,CLASS)}
        observed=original|SAME|{(A,RDF.type,CLASS)}
        report=e19.compare_identity_type(original,observed,observed,SOURCE)
        self.assertEqual(report["source_original_rdf_type"],1)
        self.assertEqual(report["full_profile_inferred_rdf_type_touching_original_nodes"],1)
        self.assertEqual(report["full_profile_added_type_endpoints"]["target_subject_type"],1)

    def test_independent_sparql_identity_disagreement_fails(self):
        first=SAME|TYPES
        with self.assertRaisesRegex(ValueError,"scope mismatch"):
            e19.compare_identity_type(set(),first,first-{(G,OWL.sameAs,G)},SOURCE)

    def test_original_identity_statement_removed_by_closure_fails(self):
        with self.assertRaisesRegex(ValueError,"lost original source"):
            e19.compare_identity_type({(G,RDF.type,CLASS)},SAME,SAME,SOURCE)

    def test_original_gene_target_node_overlaps_are_rejected(self):
        with self.assertRaises(ValueError):
            e19.compare_identity_type(set(),set(),set(),{(G,owner.bridge.GENEX.isExpressedIn,G)})


if __name__=="__main__":
    unittest.main()
