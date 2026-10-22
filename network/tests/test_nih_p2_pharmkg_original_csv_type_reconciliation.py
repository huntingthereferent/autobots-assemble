"""Source-original CSV schema, TRAIN join, and nonpromotion controls."""
from __future__ import annotations
import csv,os,unittest
from io import StringIO
from pathlib import Path
from systems.workspace import nih_p2_pharmkg_original_csv_type_reconciliation as trial
RAW=os.getenv("PHARMKG_AUTHOR_RAW")
TRAIN=os.getenv("PHARMKG_ORIGINAL_TRAIN")
class OriginalRawRelationTests(unittest.TestCase):
    def test_type_reconciliation_and_genuine_train_scope(self):
        content=("Entity1_ID,relation,Entity2_ID,Entity1_type,Entity2_type\n"
                 "a,GG,b,Gene,Gene\n"
                 "b,T,c,Chemical,Disease\n"
                 "z,T,x,Unknown,Unknown\n")
        train=[("a","GG","b"),("b","T","c")]
        r=trial.reconcile(csv.DictReader(StringIO(content)),train)
        self.assertEqual(r["distinct_authored_raw_triples_matching_original_train"],2)
        self.assertEqual(r["original_train_entity_ids_with_conflicting_raw_types"],1)
        self.assertEqual(r["original_train_entity_ids_with_one_raw_type"],2)
        self.assertEqual(r["original_train_unmatched_triples"],0)
        self.assertFalse(r["typed_biomedical_path_rule_admitted"])
    def test_no_type_columns_never_becomes_semantic_confirmation(self):
        reader=csv.DictReader(StringIO("Entity1_ID,relation,Entity2_ID\na,I,b\n"))
        r=trial.reconcile(reader,[("a","I","b")])
        self.assertFalse(r["original_raw_entity_type_columns_present"])
        self.assertEqual(r["original_train_entity_ids_without_raw_type"],2)
    def test_missing_owner_original_columns_is_refused(self):
        with self.assertRaisesRegex(ValueError,"lacks"):
            trial.reconcile(csv.DictReader(StringIO("foo,bar\na,b\n")),[("a","I","b")])
    @unittest.skipUnless(RAW and TRAIN,"authentic author CSV and TRAIN required")
    def test_full_original_source_from_immutable_owner_release(self):
        r=trial.audit(Path(RAW),Path(TRAIN))
        self.assertTrue(r["source_input_authenticated"])
        self.assertGreater(r["source_original_csv_rows"],0)
        self.assertLessEqual(r["original_train_unmatched_triples"],r["original_train_triples"])
        self.assertFalse(r["test_or_valid_label_used_for_model"])
        self.assertFalse(r["typed_biomedical_path_rule_admitted"])
        self.assertFalse(r["official_NIH_benchmark"])
if __name__=="__main__":unittest.main()
