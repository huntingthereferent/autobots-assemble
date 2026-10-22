"""Synthetic-only tests for independent F distribution p-value reconstruction."""
import csv
import io
import unittest

from f_statistics import analyze, ALPHA, TOLERANCE


COLS = [
    "Local.ID",
    "T.Test.Statistic.O", "T.df1.O", "T.df2.O", "T.Test.value.O",
    "T.pval.recalc.O", "T.sign.O.131",
    "T.Test.Statistic.R", "T.df1.R", "T.df2.R", "T.Test.value.R",
    "T.pval.recalc.R", "T.sign.R.132",
]


def csv_rows(*records):
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=COLS)
    writer.writeheader()
    for row in records:
        writer.writerow(row)
    return buf.getvalue()


def a_record(**updates):
    record = {
        "Local.ID": "Row.A",
        "T.Test.Statistic.O": "F", "T.df1.O": "1", "T.df2.O": "13",
        "T.Test.value.O": "7.11", "T.pval.recalc.O": "0.019394664",
        "T.sign.O.131": "1",
        "T.Test.Statistic.R": "F", "T.df1.R": "1", "T.df2.R": "28",
        "T.Test.value.R": "0.63", "T.pval.recalc.R": "0.434030725",
        "T.sign.R.132": "0",
    }
    record.update(updates)
    return record


class FRecalculationTests(unittest.TestCase):
    def test_independent_p_values_match_known_f_distribution(self):
        result = analyze(csv_rows(a_record()))
        a = result["side_results"]["original"]
        b = result["side_results"]["replication"]
        for item in (a, b):
            self.assertEqual(item["eligible_f_tests"], 1)
            self.assertEqual(item["reported_p_agree"], 1)
            self.assertEqual(item["flags_agree"], 1)
            self.assertEqual(item["reported_p_disagree"], 0)
        self.assertEqual(ALPHA, 0.05)
        self.assertEqual(TOLERANCE, 1e-6)

    def test_disagreement_retained_not_silently_overridden(self):
        r = a_record()
        r["T.pval.recalc.O"] = "0.9"
        r["T.sign.R.132"] = "1"
        results = analyze(csv_rows(r))["side_results"]
        self.assertEqual(results["original"]["reported_p_disagree"], 1)
        self.assertGreater(results["original"]["largest_absolute_p_error"], 0.8)
        self.assertEqual(results["replication"]["flags_disagree"], 1)

    def test_missing_p_and_missing_flag_retained(self):
        r = a_record()
        r["T.pval.recalc.O"] = "NA"
        r["T.sign.R.132"] = "NA"
        results = analyze(csv_rows(r))["side_results"]
        self.assertEqual(results["original"]["reported_p_missing"], 1)
        self.assertEqual(results["replication"]["flags_missing"], 1)

    def test_non_f_family_not_wrongly_evaluated(self):
        r = a_record()
        r["T.Test.Statistic.O"] = "t"
        a = analyze(csv_rows(r))["side_results"]["original"]
        self.assertEqual(a["eligible_f_tests"], 0)

    def test_incomplete_f_statistic_is_explicit_unknown(self):
        r = a_record()
        r["T.df1.O"] = "NA"
        observed = analyze(csv_rows(r))["side_results"]["original"]
        self.assertEqual(observed["f_rows_seen"], 1)
        self.assertEqual(observed["missing_f_inputs"], 1)
        self.assertEqual(observed["eligible_f_tests"], 0)

    def test_threshold_disagreement_near_005_kept(self):
        r = a_record()
        r["T.Test.value.O"] = "4.1"
        r["T.df2.O"] = "31"
        r["T.pval.recalc.O"] = "0.051569634"
        r["T.sign.O.131"] = "1"
        observed = analyze(csv_rows(r))["side_results"]["original"]
        self.assertEqual(observed["reported_p_agree"], 1)
        self.assertEqual(observed["flags_disagree"], 1)

    def test_bad_df_rejected(self):
        r = a_record()
        r["T.df1.O"] = "0"
        with self.assertRaisesRegex(ValueError, "invalid F df1"):
            analyze(csv_rows(r))

    def test_bad_f_statistic_rejected(self):
        r = a_record()
        r["T.Test.value.R"] = "-2"
        with self.assertRaisesRegex(ValueError, "invalid F statistic"):
            analyze(csv_rows(r))

    def test_nonfinite_f_rejected(self):
        r = a_record()
        r["T.Test.value.O"] = "nan"
        with self.assertRaisesRegex(ValueError, "invalid F statistic"):
            analyze(csv_rows(r))

    def test_bad_reported_p_rejected(self):
        r = a_record()
        r["T.pval.recalc.R"] = "1.9"
        with self.assertRaisesRegex(ValueError, "supplied p above 1"):
            analyze(csv_rows(r))

    def test_duplicate_identifier_rejected(self):
        with self.assertRaisesRegex(ValueError, "repeated"):
            analyze(csv_rows(a_record(), a_record()))

    def test_source_columns_required(self):
        with self.assertRaisesRegex(ValueError, "missing statistical"):
            analyze("Local.ID,T.Test.Statistic.O\nRow.A,F\n")

    def test_source_flag_validation(self):
        r = a_record()
        r["T.sign.O.131"] = "yes"
        with self.assertRaisesRegex(ValueError, "unexpected source significance"):
            analyze(csv_rows(r))

    def test_empty_dataset_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty source"):
            analyze(csv_rows())


if __name__ == "__main__":
    unittest.main()
