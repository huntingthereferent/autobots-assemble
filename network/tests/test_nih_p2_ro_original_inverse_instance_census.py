"""Inverse property rules on REAL original triples only, synthetic controls isolated."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import unittest

from rdflib import Graph, URIRef, OWL, BNode, Literal
from systems.workspace import nih_p2_ro_original_inverse_instance_census as trial

HAS_OWLRL=importlib.util.find_spec("owlrl") is not None
RO=os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
CORE=os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")
BASE="urn:nih-p2:original-fact-census-control:"


def iri(text):
    return URIRef(BASE+text)


def fixture(*, inverse=True, named_assertion=True):
    g=Graph()
    if inverse:
        g.add((iri("hasPart"),OWL.inverseOf,iri("partOf")))
    if named_assertion:
        g.add((iri("patient-not-real"),iri("hasPart"),iri("object-not-real")))
    return g


class OriginalInverseInstanceCensus(unittest.TestCase):
    def test_original_only_source_join_yields_one_inverse_witness(self):
        g=fixture()
        p=trial.previous.source_inverse_pairs(g)
        direct=trial.raw_source_matches(g,p)
        self.assertEqual(len(direct),1)
        inferred,proof=trial.independent_inverse_join(g,p)
        expected={(iri("object-not-real"),iri("partOf"),iri("patient-not-real"))}
        self.assertEqual(inferred,expected)
        self.assertEqual(set(g.query(trial.SOURCE_QUERY).graph),inferred)
        self.assertTrue(all(ax in g and assertion in g for ax,assertion in proof.values()))
        self.assertNotIn(next(iter(expected)),g)

    def test_missing_source_axiom_no_inverse_prediction(self):
        g=fixture(inverse=False)
        p=trial.previous.source_inverse_pairs(g)
        self.assertEqual(p,[])
        self.assertEqual(trial.raw_source_matches(g,p),set())
        self.assertEqual(trial.independent_inverse_join(g,p)[0],set())
        self.assertEqual(set(g.query(trial.SOURCE_QUERY).graph),set())

    def test_missing_source_relationship_no_fabricated_inverse(self):
        g=fixture(named_assertion=False)
        p=trial.previous.source_inverse_pairs(g)
        self.assertEqual(trial.raw_source_matches(g,p),set())
        self.assertEqual(trial.independent_inverse_join(g,p)[0],set())
        self.assertEqual(set(g.query(trial.SOURCE_QUERY).graph),set())

    def test_literal_and_blank_node_are_not_named_biomedical_facts(self):
        g=fixture(named_assertion=False)
        g.add((iri("one"),iri("hasPart"),Literal("not a named resource")))
        g.add((BNode(),iri("hasPart"),iri("two")))
        matches=trial.raw_source_matches(g,trial.previous.source_inverse_pairs(g))
        self.assertEqual(len(matches),2)
        inferred,_=trial.independent_inverse_join(g,trial.previous.source_inverse_pairs(g))
        self.assertEqual(inferred,set())
        self.assertEqual(set(g.query(trial.SOURCE_QUERY).graph),set())

    def test_source_inventory_mismatch_is_never_silently_promoted(self):
        with self.assertRaises(ValueError):
            trial.examine(fixture(),expected_original_count=123)
        with self.assertRaises(TypeError):
            trial.examine(None)

    @unittest.skipUnless(HAS_OWLRL,"optional OWL RL engine is installed in original-source CI")
    def test_positive_control_source_only_mechanism_entails_once(self):
        r=trial.examine(fixture(),expected_original_count=1)
        self.assertEqual(r["original_source_named_subject_object_assertions"],1)
        self.assertEqual(r["independent_original_source_inverse_predictions"],1)
        self.assertEqual(r["new_nonasserted_inverse_relationships_from_original_sources"],1)
        self.assertTrue(r["input_contains_no_injected_synthetic_assertions"])
        self.assertFalse(r["medical_treatment_efficacy_inferred"])

    @unittest.skipUnless(HAS_OWLRL and RO and CORE,
                         "original whole-source authenticated OBO OWL plus reasoner required")
    def test_real_original_ontology_source_assertion_inventory(self):
        r=trial.execute({"ro-base.owl":Path(RO),"core.owl":Path(CORE)})
        self.assertEqual(r["schema"],trial.SCHEMA)
        self.assertEqual(r["source_rdf_triples"],8319)
        self.assertEqual(r["source_named_inverse_axiom_declarations"],123)
        self.assertTrue(r["whole_original_OWL_RL_agrees_on_source_inverse_predictions"])
        self.assertEqual(r["independent_original_source_inverse_predictions"],
                         r["independent_original_only_SPARQL_CONSTRUCT_predictions"])
        self.assertLessEqual(r["new_nonasserted_inverse_relationships_from_original_sources"],
                             r["independent_original_source_inverse_predictions"])
        self.assertTrue(r["input_contains_no_injected_synthetic_assertions"])
        self.assertFalse(r["original_patient_level_records_used"])
        self.assertFalse(r["official_NIH_benchmark"])
        self.assertFalse(r["original_W13_modified"])


if __name__=="__main__":
    unittest.main()
