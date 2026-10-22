"""Author GenEx mapping provenance: negative controls and authentic original gate."""
from __future__ import annotations
import os
from pathlib import Path
import tempfile
import unittest

from rdflib import Graph,URIRef
from systems.workspace import nih_p2_author_genex_bgee_ro_mapping_gate as trial

RO=os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
CORE=os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")
AUTHOR=os.environ.get("NIH_ORIGINAL_BGEE_SOURCE_DIR")


class AuthoredBgeeBridgeTests(unittest.TestCase):
    def test_source_owner_git_blob_identity(self):
        raw=b"genex-bgee-sample"
        from hashlib import sha1
        expected=sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
        self.assertEqual(trial.git_blob(raw),expected)
        self.assertNotEqual(trial.git_blob(raw),trial.git_blob(raw+b"modified"))

    def test_only_three_exact_original_author_files_admitted(self):
        with self.assertRaises(ValueError):
            trial.validate_exact_owner({})
        with self.assertRaises(ValueError):
            trial.validate_exact_owner({"bgee_v14_genex.obda":Path("nothing")})

    def test_rejected_modified_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            parent=Path(folder)
            for name in trial.FILES:
                (parent/name).write_text("simulated altered original file")
            with self.assertRaisesRegex(ValueError,"blob changed"):
                trial.validate_exact_owner({name:parent/name for name in trial.FILES})

    def test_source_target_uri_classes_are_not_interchangeable(self):
        self.assertNotEqual(trial.RO_EXPRESSED,trial.RO_EXPRESSES)
        self.assertNotEqual(trial.GENEX.isExpressedIn,trial.RO_EXPRESSED)
        self.assertEqual(str(trial.RO_EXPRESSED),"http://purl.obolibrary.org/obo/RO_0002206")

    @unittest.skipUnless(AUTHOR and RO and CORE,
                          "requires pinned author three-file source and independent RO originals")
    def test_original_author_to_RO_bridge_conditional_and_no_db_rows(self):
        author_files={name:Path(AUTHOR)/name for name in trial.FILES}
        x=trial.examine(author_files,{"ro-base.owl":Path(RO),"core.owl":Path(CORE)})
        self.assertEqual(x["schema"],trial.SCHEMA)
        self.assertEqual(x["mapping_author_commit"],trial.COMMIT)
        self.assertEqual(len(x["author_R2RML_mappings"]),2)
        self.assertEqual(x["independent_original_RO_graph_triples"],8319)
        self.assertTrue(x["author_file_and_independent_RO_inverse_agree"])
        self.assertTrue(x["independent_original_graph_SPARQL_path_agrees"])
        self.assertTrue(all(m["original_sql_selects_expressed_call_type"] for m in x["author_R2RML_mappings"]))
        self.assertFalse(x["original_Bgee_SQL_rows_measured"])
        self.assertFalse(x["source_ground_biomedical_relationships_materialized_measured"])
        self.assertEqual(x["genuine_original_expression_direction_claim"],
                         "CONDITIONAL_ON_AUTHOR_SQL_DATA")
        self.assertFalse(x["official_NIH_phase2_benchmark"])
        self.assertFalse(x["original_W13_modified"])


if __name__=="__main__":
    unittest.main()
