"""Finite independent sound-OWL-RL consequences vs whole OWLRL reasoner."""
from __future__ import annotations

import os
from pathlib import Path
import unittest

from rdflib import Graph, URIRef, RDF, RDFS, OWL
from owlrl import DeductiveClosure, OWLRL_Semantics

from systems.workspace import nih_p2_original_full_owlrl_rule_audit as trial

RO=os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
CORE=os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")
N="urn:nih-p2:owlrl-rule-fixture:"


def u(name):
    return URIRef(N+name)


class OriginalFullOWLRLRuleAuditTests(unittest.TestCase):
    def setUp(self):
        g=Graph()
        g.add((u("p"),OWL.inverseOf,u("inv")))
        g.add((u("q"),OWL.equivalentProperty,u("eq")))
        g.add((u("sym"),RDF.type,OWL.SymmetricProperty))
        g.add((u("trans"),RDF.type,OWL.TransitiveProperty))
        g.add((u("domain-prop"),RDFS.domain,u("A")))
        g.add((u("range-prop"),RDFS.range,u("B")))
        for t in (
            (u("a"),u("p"),u("b")),
            (u("a"),u("q"),u("b")),
            (u("a"),u("sym"),u("b")),
            (u("a"),u("trans"),u("b")),
            (u("b"),u("trans"),u("c")),
            (u("a"),u("domain-prop"),u("b")),
            (u("a"),u("range-prop"),u("b")),
        ):
            g.add(t)
        self.g=g

    def test_all_nonasserted_sound_property_rule_instances_materialize(self):
        expected,counts=trial.independently_expected(self.g)
        self.assertGreaterEqual(len(expected),7)
        for s,p,o in (
            (u("inv"),OWL.inverseOf,u("p")),
            (u("eq"),OWL.equivalentProperty,u("q")),
            (u("b"),u("inv"),u("a")),
            (u("a"),u("eq"),u("b")),
            (u("b"),u("sym"),u("a")),
            (u("a"),u("trans"),u("c")),
            (u("a"),RDF.type,u("A")),
            (u("b"),RDF.type,u("B")),
        ):
            self.assertIn((s,p,o),expected)
            self.assertNotIn((s,p,o),self.g)
        reasoned=Graph()
        reasoned += self.g
        DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(reasoned)
        missing=[t for t in expected if t not in reasoned]
        # A documented engine-specific *schema serialization* boundary,
        # distinct from executing the inverse property assertion rule.
        self.assertEqual(missing,[(u("inv"),OWL.inverseOf,u("p"))])
        self.assertTrue(all(t in reasoned for t in expected
                            if expected[t][0]!="inverse_axiom_reverse"))
        self.assertIn((u("b"),u("inv"),u("a")),reasoned)

    def test_no_inference_without_exact_original_premises(self):
        graph=Graph()
        graph.add((u("a"),u("p"),u("b")))
        expected,counts=trial.independently_expected(graph)
        self.assertFalse(expected)
        self.assertEqual(counts["original_explicit_inverseOf_named_pairs"],0)
        self.assertEqual(counts["original_explicit_equivalentProperty_named_pairs"],0)

    def test_rule_directions_and_independent_premise_triples(self):
        expected,_=trial.independently_expected(self.g)
        rule,premises=expected[(u("b"),u("inv"),u("a"))]
        self.assertEqual(rule,"inverse_assertion")
        self.assertTrue(all(t in self.g for t in premises))
        self.assertNotIn((u("a"),u("inv"),u("b")),expected)

    def test_bnode_property_assertion_is_not_promoted_to_uri_proof(self):
        from rdflib import BNode
        g=Graph()
        g.add((u("p"),OWL.inverseOf,u("inv")))
        g.add((BNode(),u("p"),u("a")))
        inferred,inventory=trial.independently_expected(g)
        self.assertNotIn("inverse_assertion",set(rule for rule,_ in inferred.values()))
        self.assertEqual(inventory["original_explicit_inverseOf_named_pairs"],1)

    def test_full_source_graph_input_is_bounded(self):
        with self.assertRaises(ValueError):
            trial.examine(None)

    @unittest.skipUnless(RO and CORE,"requires two whole-source authenticated OBO files")
    def test_full_original_source_owlrl_closure_matches_independent_sound_rules(self):
        r=trial.execute({"ro-base.owl":Path(RO),"core.owl":Path(CORE)})
        self.assertEqual(r["schema"],trial.SCHEMA)
        self.assertEqual(r["original_source_commit"],
                         "091f4761ec84657cc336d623e02006d6c351722c")
        self.assertEqual(r["original_rdf_triples"],8319)
        self.assertGreater(r["full_source_owlrl_materialized_rdf_triples"],
                           r["original_rdf_triples"])
        self.assertTrue(r["engine_supported_rule_consequences_all_materialized"])
        self.assertFalse(r["all_candidate_rule_triples_materialized"])
        self.assertGreater(r["inverse_axiom_mirror_candidates_not_explicitly_materialized"],0)
        self.assertTrue(r["entire_source_OWL_RL_agrees_on_subproperty_closure"])
        self.assertEqual(r["original_source_nonasserted_subproperty_transitivity"],1656)
        self.assertFalse(r["whole_original_consistency_established"])
        self.assertFalse(r["official_NIH_Phase2_benchmark"])
        self.assertFalse(r["original_W13_modified"])


if __name__=="__main__":
    unittest.main()
