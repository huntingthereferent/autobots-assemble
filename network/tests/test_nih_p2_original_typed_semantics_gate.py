"""Test source-backed relation-role evidence versus invented clinical types."""
from __future__ import annotations

import os
from pathlib import Path
import unittest
from systems.workspace import nih_p2_original_typed_semantics_gate as audit

README=os.environ.get("PHARMKG_ORIGINAL_README")
TRAIN=os.environ.get("PHARMKG_ORIGINAL_TRAIN")


class OriginalTypedEvidenceBoundary(unittest.TestCase):
    def test_count_topology_not_chemical_disease_gene_entailment(self):
        rows=[
            ("gene-a","GG","gene-b"),("gene-b","GG","gene-c"),
            ("drug-a","T","disease-a"),("gene-a","P","disease-a"),
            ("drug-a","I","gene-a")
        ]
        c=audit.profile(rows)
        self.assertEqual(c["GG"]["training_source_edges"],2)
        self.assertEqual(c["GG"]["source_identifiers_seen_as_both_roles"],1)
        self.assertEqual(c["T"]["source_identifiers_seen_as_both_roles"],0)
        self.assertEqual(c["I"]["training_source_edges"],1)

    def test_source_owner_readme_must_be_exact_immutable_original(self):
        with self.assertRaises(ValueError):
            audit.original_overview(b"Gene Chemical Disease PharmKG-8k")
        with self.assertRaises(ValueError):
            audit.original_overview(b"completely unobserved metadata")

    def test_fabricated_edge_shape_refused(self):
        for wrong in ([("a","T")], [("a","T","")], ["a,T,b"]):
            with self.assertRaises(ValueError):
                audit.profile(wrong)

    @unittest.skipUnless(README and TRAIN,
                         "need original pinned source README and whole train.tsv")
    def test_exact_original_source_profiles_without_fabricating_type_map(self):
        d=audit.execute(readme_file=Path(README),train_file=Path(TRAIN))
        self.assertEqual(d["schema"],audit.SCHEMA)
        self.assertEqual(d["original_owner_metadata"]["README_git_blob_sha1"],
                         audit.OWNER_README_BLOB)
        self.assertEqual(d["independent_count_verification"],"PASS")
        self.assertEqual(d["type_grounded_metapath_rule_admission"],
                         "REFUSED_MISSING_SOURCE_OWNER_SEMANTICS")
        self.assertEqual(d["external_owner_semantic_entity_id_mapping"],
                         "UNAVAILABLE_FROM_PINNED_README_AND_TRAIN_TSV")
        self.assertFalse(d["clinical_biomedical_entailment_authenticated"])
        self.assertFalse(d["test_and_valid_used"])
        self.assertFalse(d["official_NIH_benchmark"])
        self.assertTrue(all(d["training_only_relation_code_profile"][c]
                            ["training_source_edges"]>0 for c in audit.CODES))

if __name__=="__main__":
    unittest.main()
