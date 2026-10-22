"""Offline controls for the source-pinned ML Iris benchmark."""
import unittest

from ml_iris_v1 import EXPECTED_LABELS, evaluate, parse_arff, stratified_split


def arff(rows):
    head = """@relation iris
@attribute sepallength numeric
@attribute sepalwidth numeric
@attribute petallength numeric
@attribute petalwidth numeric
@attribute class {Iris-setosa,Iris-versicolor,Iris-virginica}
@data
"""
    return (head + "\n".join(rows) + "\n").encode()


class MlIrisTests(unittest.TestCase):
    def setUp(self):
        rows = []
        for label, offset in [
            ("Iris-setosa", 0.0),
            ("Iris-versicolor", 3.0),
            ("Iris-virginica", 6.0),
        ]:
            for i in range(50):
                x = offset + i / 100
                rows.append(f"{x},1.0,{x + 0.1},0.2,{label}")
        self.raw = arff(rows)

    def test_pinned_shape_and_class_counts(self):
        rows = parse_arff(self.raw)
        self.assertEqual(len(rows), 150)
        self.assertEqual({label for _, label in rows}, EXPECTED_LABELS)

    def test_rejects_missing_or_wrong_shaped_rows(self):
        with self.assertRaises(ValueError):
            parse_arff(arff(["1,2,3,4,?"]))
        with self.assertRaises(ValueError):
            parse_arff(arff(["1,2,3,4,Iris-setosa"]))

    def test_split_is_seeded_stratified_and_disjoint(self):
        rows = parse_arff(self.raw)
        a = stratified_split(rows, 42)
        b = stratified_split(rows, 42)
        self.assertEqual(a, b)
        train, test = a
        self.assertEqual(len(train), 105)
        self.assertEqual(len(test), 45)
        self.assertFalse(set(train) & set(test))

    def test_benchmark_receipt_metrics_are_reproducible(self):
        rows = parse_arff(self.raw)
        first = evaluate(rows, 42)
        second = evaluate(rows, 42)
        self.assertEqual(first, second)
        self.assertEqual(first["train_rows"], 105)
        self.assertEqual(first["test_rows"], 45)
        self.assertEqual(first["train_test_overlap"], 0)
        self.assertEqual(sum(sum(v.values()) for v in first["confusion_matrix_rows_actual_columns_predicted"].values()), 45)

    def test_changes_to_split_seed_change_split(self):
        rows = parse_arff(self.raw)
        self.assertNotEqual(stratified_split(rows, 42), stratified_split(rows, 7))


if __name__ == "__main__":
    unittest.main()
