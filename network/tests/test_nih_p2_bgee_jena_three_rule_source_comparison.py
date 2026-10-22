"""Full-data three-source-rule Jena-vs-RDFLib oracle exact-set boundary."""
from __future__ import annotations

import unittest
from rdflib import Graph,URIRef,RDFS,OWL
from systems.workspace import nih_p2_bgee_jena_three_rule_source_comparison as trial
from systems.workspace import nih_p2_author_genex_bgee_ro_mapping_gate as owner

GENE=URIRef("http://omabrowser.org/ontology/oma#GENE_SYNTHETIC_ONLY")
TGT=URIRef("http://purl.obolibrary.org/obo/UBERON_0000955")


def fixture():
    combined=Graph()
    a=(owner.GENEX.isExpressedIn,RDFS.subPropertyOf,owner.RO_EXPRESSED)
    b=(owner.RO_EXPRESSED,RDFS.subPropertyOf,trial.GENOMIC)
    c=(owner.RO_EXPRESSED,OWL.inverseOf,owner.RO_EXPRESSES)
    for t in (a,b,c):
        combined.add(t)
    raw={(GENE,owner.GENEX.isExpressedIn,TGT)}
    for t in raw:
        combined.add(t)
    return {"full_combined":combined,"source_edges":raw,
            "independent":{(GENE,owner.RO_EXPRESSED,TGT),
                           (TGT,owner.RO_EXPRESSES,GENE)}},(a,b,c)


class JenaThreeRuleExactSourceTests(unittest.TestCase):
    def test_original_rule_premises_not_assumed_from_words(self):
        orig,premises=fixture()
        for index in range(3):
            bad,_=fixture()
            bad["full_combined"].remove(premises[index])
            with self.assertRaises(ValueError):
                trial.original_three_source_axioms(bad)

    def test_full_source_oracle_requires_actual_frozen_inventory(self):
        data,_=fixture()
        with self.assertRaises(ValueError):
            trial.original_three_source_axioms(data)

    def test_three_expected_predicate_directions_are_distinct(self):
        data,_=fixture()
        raw=next(iter(data["source_edges"]))
        expected={(raw[0],owner.RO_EXPRESSED,raw[2]),
                  (raw[0],trial.GENOMIC,raw[2]),
                  (raw[2],owner.RO_EXPRESSES,raw[0])}
        self.assertEqual(len(expected),3)
        self.assertEqual(set(data["full_combined"].query(trial.CONSTRUCT).graph),expected)

    def test_missing_original_genomic_axiom_abolishes_whole_three_rule_oracle(self):
        original,premises=fixture()
        original["full_combined"].remove(premises[1])
        self.assertEqual(set(original["full_combined"].query(trial.CONSTRUCT).graph),set())

    def test_real_input_not_a_clinical_outcome_claim(self):
        self.assertNotEqual(trial.GENOMIC,owner.RO_EXPRESSED)
        self.assertNotEqual(trial.GENOMIC,owner.RO_EXPRESSES)
        self.assertEqual(trial.N_TOTAL,3*trial.N_SOURCE)


if __name__=="__main__":
    unittest.main()
