"""Separate RDFS inherited-type conflict test, including a controlled example."""
from __future__ import annotations

import os
from pathlib import Path
import unittest

from rdflib import Graph, URIRef, RDF, RDFS, OWL
from systems.workspace import nih_p2_obo_inherited_rdfs_audit as audit

BASE="urn:nih:p2:rdfs-test:"
RO=os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
CORE=os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")


def fixture(inherit=True,reverse=False):
    graph=Graph()
    a,b,c,individual=[URIRef(BASE+x) for x in ("A","B","C","i")]
    graph.add((a,OWL.disjointWith,b))
    graph.add((individual,RDF.type,c))
    graph.add((individual,RDF.type,b))
    if inherit:
        graph.add((a if reverse else c,RDFS.subClassOf,c if reverse else a))
    return graph


class InheritedSubclassTests(unittest.TestCase):
    def test_subclass_inference_exposes_separately_witnessed_conflict(self):
        result=audit.examine(fixture())
        self.assertEqual(result["direct_only_asserted_disjointness_conflicts"],0)
        self.assertEqual(result["source_inherited_rdfs_disjointness_conflicts"],1)
        self.assertTrue(result["independent_RDFLib_subclass_oracle_agreement"])
        self.assertEqual(result["additional_rdfs_superclass_type_bindings"],1)
        self.assertFalse(result["full_OWL_RL_materialization_claimed"])

    def test_without_subclass_original_type_is_not_a_disjoint_class(self):
        result=audit.examine(fixture(inherit=False))
        self.assertEqual(result["source_inherited_rdfs_disjointness_conflicts"],0)

    def test_subclass_direction_matters(self):
        result=audit.examine(fixture(reverse=True))
        self.assertEqual(result["source_inherited_rdfs_disjointness_conflicts"],0)

    def test_explicit_cycle_is_finite_without_faking_additional_conflicts(self):
        graph=fixture()
        graph.add((URIRef(BASE+"A"),RDFS.subClassOf,URIRef(BASE+"C")))
        result=audit.examine(graph)
        self.assertEqual(result["source_inherited_rdfs_disjointness_conflicts"],1)

    def test_non_graph_is_rejected(self):
        with self.assertRaises(ValueError):
            audit.examine(None)

    @unittest.skipUnless(RO and CORE,"original pinned two OBO RDF/XML source files required")
    def test_actual_original_ontology_inherited_conflicts_and_independent_oracle(self):
        result=audit.execute({"ro-base.owl":Path(RO),"core.owl":Path(CORE)})
        self.assertEqual(result["source_rdf_triples"],8319)
        self.assertEqual(result["original_external_ontology_source_commit"],
                         "091f4761ec84657cc336d623e02006d6c351722c")
        self.assertGreater(result["original_named_subclass_edges"],0)
        self.assertTrue(result["independent_RDFLib_subclass_oracle_agreement"])
        self.assertGreaterEqual(result["source_inherited_rdfs_disjointness_conflicts"],
                                result["direct_only_asserted_disjointness_conflicts"])
        self.assertFalse(result["full_OWL_DL_consistency_verified"])
        self.assertEqual(result["unsatisfiable_class_count"],"NOT_MEASURED")
        self.assertFalse(result["original_W13_modified"])
        self.assertFalse(result["official_NIH_benchmark"])


if __name__=="__main__":
    unittest.main()
