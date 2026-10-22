"""Original inverse axioms: structural evidence stays separate from probe inputs."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import unittest

from rdflib import Graph, URIRef, OWL, RDF
from systems.workspace import nih_p2_ro_inverse_rule_original_source_probe as lane

HAS_OWL = importlib.util.find_spec("owlrl") is not None
RO=os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
CORE=os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")
BASE="urn:nih-p2:inverse-negative-control:"


class AuthenticatedInverseRuleProbeTests(unittest.TestCase):
    def base_source(self):
        g=Graph()
        g.add((URIRef(BASE+"p"),OWL.inverseOf,URIRef(BASE+"inv")))
        return g

    def test_spo_injection_is_explicitly_synthetic_and_independently_joined(self):
        g=self.base_source()
        pairs=lane.source_inverse_pairs(g)
        self.assertEqual(len(pairs),1)
        injected,expected,receipts=lane.fixture_assertions(pairs)
        self.assertEqual(len(injected),1)
        self.assertEqual(len(expected),1)
        self.assertEqual(expected,lane.oracle_sparql_source_join(g,injected))
        self.assertTrue(all(
            r["source_inverse_declaration"][1]==str(OWL.inverseOf)
            for r in receipts))
        self.assertEqual(len(g),1)
        self.assertTrue(all(
            str(h).startswith(lane.PROBE_BASE+"head/")
            for h,p,t in injected))

    def test_removing_only_source_axiom_prevents_static_oracle_inference(self):
        g=self.base_source()
        injected,expected,_=lane.fixture_assertions(lane.source_inverse_pairs(g))
        g.remove((URIRef(BASE+"p"),OWL.inverseOf,URIRef(BASE+"inv")))
        self.assertEqual(len(lane.oracle_sparql_source_join(g,injected)),0)
        self.assertEqual(len(expected),1)

    def test_altering_assertion_direction_does_not_fake_inverse_conclusion(self):
        g=self.base_source()
        injected,expected,_=lane.fixture_assertions(lane.source_inverse_pairs(g))
        changed=Graph()
        for h,p,t in injected:
            changed.add((t,p,h))
        self.assertFalse(expected & lane.oracle_sparql_source_join(g,changed))

    def test_unique_role_names_stay_bounded_and_immutable(self):
        with self.assertRaises(ValueError):
            lane.fixture_assertions([])
        p=(BASE+"p",BASE+"inv")
        with self.assertRaises(ValueError):
            lane.fixture_assertions([p]*(lane.MAX_PROBE_COUNT+1))
        before=self.base_source()
        lane.fixture_assertions(lane.source_inverse_pairs(before))
        self.assertEqual(len(before),1)

    @unittest.skipUnless(HAS_OWL,"optional OWL RL engine only installed by source-connected CI")
    def test_single_authentic_rule_shape_independent_vs_owlrl_engine(self):
        g=self.base_source()
        report=lane.examine(g)
        self.assertEqual(report["original_named_inverse_axioms"],1)
        self.assertEqual(report["independent_SPARQL_CONSTRUCT_source_join_predictions"],1)
        self.assertEqual(report["OWL_RL_correct_inverse_assertions"],1)
        self.assertEqual(report["OWL_RL_missing_inverse_assertions"],0)
        self.assertFalse(report["synthetic_probe_results_are_original_biomedical_data"])
        self.assertFalse(report["official_NIH_benchmark"])

    @unittest.skipUnless(HAS_OWL and RO and CORE,
                         "original SHA-pinned OBO files and installed OWL RL required")
    def test_all_123_original_inverse_axioms_with_independent_spaqrl(self):
        r=lane.execute({"ro-base.owl":Path(RO),"core.owl":Path(CORE)})
        self.assertEqual(r["schema"],lane.SCHEMA)
        self.assertEqual(r["original_source_rdf_triples"],8319)
        self.assertEqual(r["original_named_inverse_axioms"],123)
        self.assertEqual(r["unique_injected_synthetic_test_assertions"],123)
        self.assertEqual(r["independent_SPARQL_CONSTRUCT_source_join_predictions"],123)
        self.assertEqual(r["OWL_RL_correct_inverse_assertions"],123)
        self.assertEqual(r["OWL_RL_missing_inverse_assertions"],0)
        self.assertEqual(len(r["original_source_rule_receipts"]),123)
        self.assertTrue(r["OWL_RL_equal_to_independent_static_source_oracle"])
        self.assertFalse(r["synthetic_probe_results_are_original_biomedical_data"])
        self.assertFalse(r["original_W13_modified"])
        self.assertFalse(r["official_NIH_benchmark"])


if __name__=="__main__":
    unittest.main()
