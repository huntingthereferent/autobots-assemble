"""Original author Bgee SQL ZIP structure: independent finite intake controls."""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile,ZIP_DEFLATED
import unittest

from systems.workspace import nih_p2_original_bgee_archive_intake as lane

SOURCE_SQL=("COPY public.globalexpression (globalexpressionid, calltype, score) FROM stdin;\n"
            "1\tEXPRESSED\t100\n"
            "2\tNOT_EXPRESSED\t50\n"
            "\\.\n"
            "COPY public.gene (geneid) FROM stdin;\n"
            "ENSG0001\n"
            "\\.\n").encode()


class OriginalBgeeSQLIntakeTests(unittest.TestCase):
    def test_explicit_copy_rows_positive_calls_are_not_inferences(self):
        result=lane.sql_census(SOURCE_SQL)
        self.assertEqual(result["recognized_COPY_sections"],2)
        self.assertEqual(result["original_table_row_or_INSERT_statement_counts"]["globalexpression"],2)
        self.assertEqual(result["original_source_globalexpression_calltypes"]["EXPRESSED"],1)
        self.assertEqual(result["original_source_globalexpression_calltypes"]["NOT_EXPRESSED"],1)
        self.assertFalse(result["original_database_rows_executed_or_materialized"])
        self.assertFalse(result["frozen_author_mapping_join_executed"])

    def test_incomplete_source_copy_fails(self):
        with self.assertRaises(ValueError):
            lane.sql_census(SOURCE_SQL.split(b"\\.")[0])

    def test_counterexample_wrong_column_arity_fails(self):
        data=b"COPY public.globalexpression (globalexpressionid, calltype, score) FROM stdin;\n1\tEXPRESSED\n\\.\n"
        with self.assertRaises(ValueError):
            lane.sql_census(data)

    def test_exact_zip_original_id_and_digest_gate(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/"owner.zip"
            with ZipFile(path,"w",ZIP_DEFLATED) as z:
                z.writestr("original/postgresql.sql",SOURCE_SQL)
            blob=lane.bridge.git_blob(path.read_bytes())
            result=lane.examine_archive(path,expected_git_blob=blob)
            self.assertEqual(result["source_measured_expression_rows"],1)
            self.assertEqual(len(result["original_sql_censuses"]),1)
            self.assertTrue(result["git_blob_already_cross_checked_with_original_owner_api"])
            self.assertFalse(result["original_bgee_join_executed"])
            self.assertTrue(result["positives_are_not_materialized_gene_anatomy_edges"])
            with self.assertRaises(ValueError):
                lane.examine_archive(path,expected_git_blob="0"*40)

    def test_path_traversal_in_archive_refused(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/"owner.zip"
            with ZipFile(path,"w",ZIP_DEFLATED) as z:
                z.writestr("../fake.sql",SOURCE_SQL)
            with self.assertRaises(ValueError):
                lane.examine_archive(path)


if __name__=="__main__":
    unittest.main()
