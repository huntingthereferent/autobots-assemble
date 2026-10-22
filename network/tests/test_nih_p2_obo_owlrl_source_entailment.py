"""Test true OWL RL schema entailment against independent RDF traversal."""
from __future__ import annotations

import os
import importlib.util
from pathlib import Path
import unittest

from rdflib import Graph, RDFS, URIRef
HAS_OWLRL=importlib.util.find_spec("owlrl") is not None

from systems.workspace import nih_p2_obo_owlrl_source_entailment as e

RO=os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
CORE=os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")
NS="urn:nih:original-owlrl-control:"


class OriginalSourceOwlRlTests(unittest.TestCase):
    def test_two_explicit_fixture_edges_require_inferred_nonasserted_third(self):
        a,b,c=[NS+x for x in "abc"]
        graph=Graph()
        graph.add((URIRef(a),RDFS.subPropertyOf,URIRef(b)))
        graph.add((URIRef(b),RDFS.subPropertyOf,URIRef(c)))
        edges=e.original_property_graph_control_for_unit_test(graph) if hasattr(
            e,"original_property_graph_control_for_unit_test") else {(a,b),(b,c)}
        paths=e.shortest_witnesses(edges)
        implied=e.original_nonasserted(paths,edges)
        self.assertEqual(implied[(a,c)],[a,b,c])
        self.assertTrue(e.oracle_all_reachable(graph,edges,paths))
        if HAS_OWLRL:
            self.assertTrue(e.materialized_by_owlrl(implied[(a,c)]))

    def test_source_witness_direct_and_reverse_absent(self):
        a,b,c=[NS+x for x in "abc"]
        edges={(a,b),(b,c)}
        paths=e.shortest_witnesses(edges)
        self.assertNotIn((c,a),e.original_nonasserted(paths,edges))
        self.assertNotIn((a,b),e.original_nonasserted(paths,edges))
        self.assertEqual(len(e.original_nonasserted(paths,edges)),1)

    def test_cycle_is_finite_no_self_entailment_reported(self):
        a,b,c=[NS+x for x in "abc"]
        edges={(a,b),(b,a),(b,c)}
        paths=e.shortest_witnesses(edges)
        implied=e.original_nonasserted(paths,edges)
        self.assertNotIn((a,a),implied)
        self.assertNotIn((b,b),implied)
        self.assertEqual(implied[(a,c)],[a,b,c])

    def test_missing_intermediate_source_edge_does_not_materialize(self):
        a,b,c=[URIRef(NS+x) for x in "abc"]
        g=Graph()
        g.add((a,RDFS.subPropertyOf,b))
        if not HAS_OWLRL:
            self.skipTest("optional OWL RL engine absent from general protocol runner")
        from owlrl import DeductiveClosure, OWLRL_Semantics
        DeductiveClosure(OWLRL_Semantics).expand(g)
        self.assertNotIn((a,RDFS.subPropertyOf,c),g)
        with self.assertRaises(ValueError):
            e.materialized_by_owlrl([str(a),str(a),str(c)])

    def test_forged_source_pairs_and_malformed_graph_refused(self):
        with self.assertRaises(ValueError):
            e.shortest_witnesses({("head","")})
        with self.assertRaises(ValueError):
            e.shortest_witnesses([("a","b")])

    @unittest.skipUnless(RO and CORE,"two exact original OBO source OWL files required")
    def test_original_release_nonasserted_entailed_schema_triples(self):
        result=e.execute({"ro-base.owl":Path(RO),"core.owl":Path(CORE)})
        self.assertEqual(result["schema"],e.SCHEMA)
        self.assertEqual(result["original_commit"],
                         "091f4761ec84657cc336d623e02006d6c351722c")
        self.assertEqual(result["original_source_rdf_triples"],8319)
        self.assertGreater(result["nonasserted_subproperty_triples_entailed_by_transitivity"],0)
        self.assertEqual(result["selected_source_owned_nonasserted_entailments"],24)
        self.assertTrue(result["independent_full_source_RDFLib_property_closure_agreement"])
        self.assertTrue(result["original_source_all_selected_OWL_RL_entailments_verified"])
        self.assertTrue(all(x["not_explicitly_asserted_in_source"]
                            and len(x["original_source_edge_sha256"])==x["source_edge_count"]
                            for x in result["selected_receipts"]))
        self.assertEqual(result["original_ontology_is_consistent"],"NOT_MEASURED")
        self.assertFalse(result["full_ontology_OWL_RL_closure_executed"])
        self.assertFalse(result["official_NIH_benchmark"])
        self.assertFalse(result["original_W13_modified"])


if __name__=="__main__":
    unittest.main()
