"""Mutant tests for Phase-1 ontology-aligned WORLD RDF materialization."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from rdflib import Graph,Literal,RDF
from rdflib.namespace import XSD
from systems.workspace.world_temporal_blueprint import evaluate
from systems.workspace.world_blueprint_rdf import (
    TE,PROV,create_graph,independently_check_rdf)
FIXTURE=Path(__file__).resolve().parent/"fixtures/world_nih_phase1_phase2_blueprint_v1.json"
def fixture():
    return json.loads(FIXTURE.read_text())

class WorldPhase1RDFTests(unittest.TestCase):
    def test_01_source_qualified_synthetic_rdf_and_temporal_reasoning(self):
        bp=fixture()
        text=create_graph(bp,"synthetic").serialize(format="turtle")
        receipt=independently_check_rdf(bp,"synthetic",text)
        self.assertEqual(receipt["source_assertion_count"],2)
        self.assertEqual(receipt["source_derived_provenance_links"],2)
        self.assertEqual(receipt["eligible"],["prior-note"])
        self.assertEqual(receipt["withheld_future"],["delayed-result"])
        self.assertTrue(receipt["parsed_graph_query_oracle_agreed"])
        self.assertFalse(receipt["owl_reasoning_claimed"])
    def test_02_mutated_source_observation_moves_rdf_answer(self):
        bp=fixture()
        bp["sample_sets"]["synthetic"][1]["known_day"]="2026-01-03"
        bp["sample_sets"]["synthetic"][1]["object"]="real-edited-browser-value"
        bp["sample_sets"]["synthetic"].append({**bp["sample_sets"]["synthetic"][1],
          "id":"synthetic-added-1","source_ref":"synthetic-extra-source",
          "known_day":"2026-01-07"})
        rdf=create_graph(bp,"synthetic").serialize(format="turtle")
        result=independently_check_rdf(bp,"synthetic",rdf)
        self.assertEqual(result["source_assertion_count"],3)
        self.assertEqual(result["eligible"],["prior-note","delayed-result"])
        self.assertEqual(result["withheld_future"],["synthetic-added-1"])
    def test_03_original_registry_source_has_owner_day_but_no_known_instant(self):
        bp=fixture()
        rdf=create_graph(bp,"registry").serialize(format="turtle")
        result=independently_check_rdf(bp,"registry",rdf)
        self.assertEqual(result["source_assertion_count"],2)
        self.assertEqual(result["unresolved_validity"],["ctgov-v94","ctgov-v105"])
        self.assertEqual(result["eligible"],[])
        self.assertIs(result["original_real_publication_instant_authenticated"],False)
        self.assertIn("2019-11-25",rdf)
    def test_04_changed_synthetic_source_day_or_object_is_rejected(self):
        bp=fixture()
        rdf=create_graph(bp,"synthetic").serialize(format="turtle")
        for before,after in (("2026-01-05","2026-01-04"),
                              ("delayed-result-value","promoted-fake-observation")):
            changed=rdf.replace(before,after)
            self.assertNotEqual(changed,rdf)
            with self.subTest(before=before),self.assertRaises(ValueError):
                independently_check_rdf(bp,"synthetic",changed)
    def test_05_forged_real_posting_day_or_exact_time_refused(self):
        bp=fixture()
        rdf=create_graph(bp,"registry").serialize(format="turtle")
        changed=rdf.replace("2019-11-25","2019-11-22")
        self.assertNotEqual(rdf,changed)
        with self.assertRaises(ValueError):
            independently_check_rdf(bp,"registry",changed)
        forged=rdf+"""
te:world-assertion-ctgov-v105 te:knownFrom te:forged2019Instant .
"""
        with self.assertRaises(ValueError):
            independently_check_rdf(bp,"registry",forged)
    def test_06_removed_source_provenance_or_extra_assertion_refused(self):
        bp=fixture()
        base=create_graph(bp,"synthetic")
        pred=next(base.triples((None,PROV.wasDerivedFrom,None)))
        base.remove(pred)
        with self.assertRaises(ValueError):
            independently_check_rdf(bp,"synthetic",base.serialize(format="turtle"))
        extra=create_graph(bp,"synthetic")
        extra.add((TE["world-assertion-forged"],RDF.type,TE.TemporalAssertion))
        with self.assertRaises(ValueError):
            independently_check_rdf(bp,"synthetic",extra.serialize(format="turtle"))
if __name__=="__main__":unittest.main()
