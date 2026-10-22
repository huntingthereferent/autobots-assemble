"""Independent Apache Jena comparison receipt checks; no false source promotion."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from rdflib import URIRef,Graph,RDFS,OWL

from systems.workspace import nih_p2_bgee_cross_engine_jena as lane
from systems.workspace import nih_p2_bgee_exhaustive_sharded_owlrl as previous
from systems.workspace import nih_p2_author_genex_bgee_ro_mapping_gate as bridge

S="http://omabrowser.org/ontology/oma#GENE_FIXTURE"
O="http://purl.obolibrary.org/obo/UBERON_0000955"


def mock_expectations():
    forward=(URIRef(S),bridge.RO_EXPRESSED,URIRef(O))
    inverse=(URIRef(O),bridge.RO_EXPRESSES,URIRef(S))
    return {forward,inverse}


class IndependentJenaComparisonControls(unittest.TestCase):
    def test_exact_equal_capability_consequences_have_stable_receipt(self):
        source=mock_expectations()
        self.assertEqual(lane.independent_rule_set_comparison(source,source),
                         previous.digest_set(source))

    def test_missing_source_consequence_is_not_silent_success(self):
        source=mock_expectations()
        with self.assertRaisesRegex(ValueError,"missing"):
            lane.independent_rule_set_comparison({next(iter(source))},source)

    def test_extra_jena_conclusion_retained_as_counterexample(self):
        source=mock_expectations()
        foreign=(URIRef("urn:independent-extra"),bridge.RO_EXPRESSED,URIRef(O))
        with self.assertRaisesRegex(ValueError,"unexpected"):
            lane.independent_rule_set_comparison(source | {foreign},source)

    def test_empty_jena_artifact_never_counted_as_verified(self):
        original={"independent":mock_expectations()}
        with tempfile.TemporaryDirectory() as folder:
            nt=Path(folder)/"empty.nt"
            nt.write_text("")
            with self.assertRaises(ValueError):
                lane.verify(original,nt)

    def test_jena_source_premise_ablations_disappear_as_expected(self):
        source=(URIRef(S),bridge.GENEX.isExpressedIn,URIRef(O))
        original={"source_edges":{source}}
        forward={(URIRef(S),bridge.RO_EXPRESSED,URIRef(O))}
        got=lane.verify_premise_ablations(original,set(),forward)
        self.assertTrue(got["control_removed_original_GenEx_subproperty_in_memory"])
        self.assertEqual(got["ablation_without_subproperty_inferred_triples"],0)
        self.assertEqual(got["ablation_without_inverse_expected_forward"],1)
        self.assertEqual(got["ablation_without_inverse_forward_triples"],1)
        self.assertTrue(got["ablation_is_alternative_rule_premise_test_not_biomedical_claim"])

    def test_mutation_without_subproperty_must_not_keep_inferences(self):
        source=(URIRef(S),bridge.GENEX.isExpressedIn,URIRef(O))
        original={"source_edges":{source}}
        forward={(URIRef(S),bridge.RO_EXPRESSED,URIRef(O))}
        with self.assertRaisesRegex(ValueError,"deletion"):
            lane.verify_premise_ablations(original,forward,forward)

    def test_mutation_without_inverse_must_not_keep_reverse_or_drop_forward(self):
        source=(URIRef(S),bridge.GENEX.isExpressedIn,URIRef(O))
        original={"source_edges":{source}}
        forward=(URIRef(S),bridge.RO_EXPRESSED,URIRef(O))
        reverse=(URIRef(O),bridge.RO_EXPRESSES,URIRef(S))
        with self.assertRaisesRegex(ValueError,"inverse-axiom ablation"):
            lane.verify_premise_ablations(original,set(),{forward,reverse})
        with self.assertRaisesRegex(ValueError,"inverse-axiom ablation"):
            lane.verify_premise_ablations(original,set(),set())

    def test_wrong_source_relation_fails_before_reasoner(self):
        raw={(URIRef(S),URIRef("http://purl.org/genex#notAuthentic"),URIRef(O))}
        with self.assertRaises(ValueError):
            previous.direct_entailed(raw)

    def test_owner_ontology_axioms_not_guessed_from_labels(self):
        genex=Graph()
        ro=Graph()
        genex.add((bridge.GENEX.isExpressedIn,RDFS.subPropertyOf,bridge.RO_EXPRESSED))
        with self.assertRaises(ValueError):
            previous.source_axioms(genex,ro)
        ro.add((bridge.RO_EXPRESSED,OWL.inverseOf,bridge.RO_EXPRESSES))
        self.assertEqual(len(previous.source_axioms(genex,ro)),2)


if __name__=="__main__":
    unittest.main()
