"""Offline, synthetic-only controls for OpenML Iris v1 source and holdout rules."""
from __future__ import annotations

import hashlib
import json
import unittest

from experiment import (
    DATA_URL, META_URL, SPLIT_SEED, get_exact, measure, parse_iris_arff,
    split_indices, validate_metadata,
)


def toy_rows():
    rows = []
    for group, label in enumerate(["A", "B", "C"]):
        for k in range(50):
            feature = (float(group * 100 + k / 100), float(group * 10 + k / 200),
                       float(group * 20 + k / 300), float(group * 30 + k / 400))
            rows.append((feature, label))
    rows[149] = rows[148]  # The real Iris export may contain an exact duplicate.
    return rows


def toy_arff(rows=None):
    rows = rows or toy_rows()
    lines = [
        "@RELATION Iris",
        "@ATTRIBUTE f0 NUMERIC",
        "@ATTRIBUTE f1 NUMERIC",
        "@ATTRIBUTE f2 NUMERIC",
        "@ATTRIBUTE f3 NUMERIC",
        "@ATTRIBUTE class {A,B,C}",
        "@DATA",
    ]
    lines.extend(",".join(map(str, values)) + "," + label for values, label in rows)
    return ("\n".join(lines) + "\n").encode()


def metadata(**changes):
    d = {"id": "61", "version": "1", "name": "iris", "default_target_attribute": "class",
         "md5_checksum": "a" * 32, "NumberOfInstances": "150"}
    d.update(changes)
    return json.dumps({"data_set_description": d}).encode()


class DummyResponse:
    status = 200

    def __init__(self, source_url, data):
        self.url = source_url
        self.data = data

    def geturl(self):
        return self.url

    def read(self, n):
        return self.data[:n]

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None


class DummyOpener:
    def __init__(self, data, url=META_URL):
        self.data = data
        self.url = url

    def open(self, request, timeout=20):
        return DummyResponse(self.url, self.data)


class OpenMLExperimentTests(unittest.TestCase):
    def test_frozen_metadata_identity(self):
        x = validate_metadata(metadata())
        self.assertEqual(x["record_id"], "openml:61")
        self.assertEqual(x["version"], 1)
        self.assertEqual(x["target"], "class")
        self.assertEqual(x["source_md5"], "a" * 32)

    def test_wrong_version_or_target_rejected(self):
        for source in [metadata(version="2"), metadata(default_target_attribute="species"),
                       metadata(id="62"), metadata(name="not iris")]:
            with self.subTest(source=source[:80]):
                with self.assertRaises(ValueError):
                    validate_metadata(source)

    def test_bad_md5_rejected(self):
        with self.assertRaisesRegex(ValueError, "MD5"):
            validate_metadata(metadata(md5_checksum="not-a-hash"))

    def test_plain_source_metadata_and_exact_url(self):
        received, url = get_exact(META_URL, 400, opener=DummyOpener(metadata()))
        self.assertEqual(url, META_URL)
        self.assertEqual(hashlib.sha256(received).hexdigest(),
                         validate_metadata(received)["source_metadata_sha256"])
        with self.assertRaisesRegex(ValueError, "approved exact"):
            get_exact("https://evil.example/download", 400, opener=DummyOpener(b""))

    def test_cross_domain_redirect_rejected(self):
        with self.assertRaisesRegex(ValueError, "redirected"):
            get_exact(DATA_URL, 400, opener=DummyOpener(b"x", "https://example.com/exfil"))

    def test_source_byte_limit_rejected(self):
        with self.assertRaisesRegex(ValueError, "byte budget"):
            get_exact(DATA_URL, 2, opener=DummyOpener(b"12345", DATA_URL))

    def test_synthetic_arff_schema(self):
        rows = parse_iris_arff(toy_arff())
        self.assertEqual(len(rows), 150)
        self.assertEqual({cls for _, cls in rows}, {"A", "B", "C"})

    def test_leakage_free_grouped_holdout(self):
        rows = toy_rows()
        train, held = split_indices(rows)
        self.assertEqual((len(train), len(held)), (120, 30))
        self.assertFalse(set(train) & set(held))
        self.assertFalse({rows[i][0] for i in train} & {rows[i][0] for i in held})
        self.assertEqual([sum(rows[i][1] == cls for i in held) for cls in ["A", "B", "C"]],
                         [10, 10, 10])
        self.assertEqual((train, held), split_indices(rows))

    def test_real_algorithm_beats_majority_on_separated_fixture(self):
        out = measure(toy_rows())
        self.assertEqual(out["centroid_correct"], 30)
        self.assertEqual(out["majority_correct"], 10)
        self.assertAlmostEqual(out["delta_accuracy"], 2 / 3)
        self.assertTrue(out["train_only_scaler"])
        self.assertTrue(out["duplicate_feature_groups_kept_intact"])

    def test_bad_arff_row_and_na_rejected(self):
        with self.assertRaises(ValueError):
            parse_iris_arff(toy_arff().replace(b"0.0,0.0,0.0,0.0,A", b"?,?,0,0,A", 1))
        with self.assertRaises(ValueError):
            parse_iris_arff(toy_arff() + b"\n1,2,3,4,A\n")

    def test_wrong_class_balance_rejected(self):
        rows = toy_rows()
        rows[49] = (rows[49][0], "B")
        with self.assertRaisesRegex(ValueError, "class balance"):
            parse_iris_arff(toy_arff(rows))

    def test_identical_features_with_conflicting_labels_rejected(self):
        rows = toy_rows()
        rows[50] = (rows[0][0], rows[50][1])
        with self.assertRaisesRegex(ValueError, "contradictory"):
            split_indices(rows)

    def test_no_unearned_scientific_pass_with_zero_data(self):
        with self.assertRaisesRegex(ValueError, "incomplete dataset"):
            measure([])

    def test_saved_live_witness_is_one_bound_result(self):
        from pathlib import Path
        witness = json.loads((Path(__file__).parent / "observations" /
                              "2026-10-22-run-39784341501.json").read_text(encoding="utf-8"))
        r = witness["result"]
        self.assertEqual(witness["run_id"], 39784341501)
        self.assertEqual(r["status"], "MEASURED_ON_EXACT_SOURCE_BYTES")
        self.assertEqual(r["source_data_sha256"],
                         "38110f3fd3cef003ca4909038a4d6b235f36a85d036dc7eedeff67c5925e826c")
        self.assertTrue(r["md5_matched_declared_source"])
        self.assertEqual(r["comparison"]["n_held_out"], 30)
        self.assertEqual(r["comparison"]["centroid_correct"], 28)
        self.assertEqual(r["comparison"]["majority_correct"], 10)
        self.assertTrue(r["comparison"]["duplicate_feature_groups_kept_intact"])



if __name__ == "__main__":
    unittest.main()
