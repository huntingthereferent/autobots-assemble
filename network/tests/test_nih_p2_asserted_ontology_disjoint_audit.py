"""Source-and-fixture boundary for NIH OBO asserted disjointness."""
from __future__ import annotations

import os
from pathlib import Path
import unittest
from rdflib import Graph, RDF, OWL, URIRef
from systems.workspace import nih_p2_asserted_ontology_disjoint_audit as audit

RO = os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
CORE = os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")
BASE = "urn:nih-p2:independent-asserted:"


def fixture():
    g = Graph()
    A, B = URIRef(BASE+"A"), URIRef(BASE+"B")
    subject = URIRef(BASE+"subject")
    g.add((A, OWL.disjointWith, B))
    g.add((subject, RDF.type, A))
    g.add((subject, RDF.type, B))
    return g


class AssertedOntologyLimits(unittest.TestCase):
    def test_known_synthetic_asserted_conflict_with_independent_join(self):
        g=fixture()
        x=audit.examine(g)
        self.assertEqual(x["original_explicit_disjoint_pairs"],1)
        self.assertEqual(x["original_asserted_type_conflict_count"],1)
        self.assertTrue(x["independent_exact_triple_join_agreements"])
        self.assertEqual(x["separate_synthetic_control_conflicts"],1)
        self.assertEqual(x["unsatisfiable_class_count"],"NOT_MEASURED")
        self.assertFalse(x["complete_owl_dl_consistency_checked"])

    def test_removing_one_explicit_type_removes_source_conflict(self):
        g=fixture()
        g.remove((URIRef(BASE+"subject"),RDF.type,URIRef(BASE+"B")))
        result=audit.examine(g)
        self.assertEqual(result["original_asserted_type_conflict_count"],0)
        self.assertEqual(result["separate_synthetic_control_conflicts"],1)

    def test_reversed_disjoint_axioms_are_not_double_counted(self):
        g=fixture()
        g.add((URIRef(BASE+"B"),OWL.disjointWith,URIRef(BASE+"A")))
        self.assertEqual(len(audit.disjoint_pairs(g)),1)
        self.assertEqual(len(audit.asserted_conflicts(g,audit.disjoint_pairs(g))),1)
        self.assertEqual(len(audit.independently_scan(g)),1)

    def test_wrong_type_and_missing_disjoint_relation_cannot_create_conflict(self):
        g=fixture()
        g.remove((URIRef(BASE+"A"),OWL.disjointWith,URIRef(BASE+"B")))
        with self.assertRaises(ValueError):
            audit.examine(g)
        with self.assertRaises(ValueError):
            audit.examine(None)

    @unittest.skipUnless(RO and CORE,"needs exact pinned OBO sources")
    def test_original_ontology_source_is_actually_scanned(self):
        result=audit.execute({"ro-base.owl":Path(RO),"core.owl":Path(CORE)})
        self.assertEqual(result["source_commit"],
                         "091f4761ec84657cc336d623e02006d6c351722c")
        self.assertEqual(result["original_graph_triple_count"],8319)
        self.assertGreater(result["original_explicit_disjoint_pairs"],0)
        self.assertEqual(result["separate_synthetic_control_conflicts"],1)
        self.assertTrue(result["independent_exact_triple_join_agreements"])
        self.assertFalse(result["synthetic_control_in_original_graph"])
        self.assertFalse(result["inferred_owl_conflicts_checked"])
        self.assertEqual(result["unsatisfiable_class_count"],"NOT_MEASURED")
        self.assertFalse(result["official_NIH_benchmark"])

if __name__=="__main__":
    unittest.main()
