"""Executable cross-shape comparisons for the packaging contract.

These are controlled fixtures, not claims about external native packages.
"""
import unittest

from systems.workspace.packaging_harness import PackagingReferent, admit, verify


class PackagingComparisons(unittest.TestCase):
    def test_same_relations_across_shapes(self):
        cases = (
            ("source-tool", "importable artifact", "native import", b"import-ok"),
            ("document-set", "references retained", "reference reader", b"links-ok"),
            ("dataset", "schema retained", "schema reader", b"schema-ok"),
            ("physical-design", "assembly constraints retained", "assembly check", b"assembly-ok"),
        )
        for identity, relation, witness, observed in cases:
            with self.subTest(identity=identity):
                ref = PackagingReferent(identity, ("original",), (relation,))
                plan = admit(ref, inspect=lambda _, witness=witness: {
                    "representation": "finite relations",
                    "operations": ["transform", "compare"],
                    "outputs": ["package"],
                    "witnesses": [witness],
                })
                accepted = verify(
                    plan, evidence={witness: observed},
                    independent_witness=lambda key, blob, p, expected=observed: blob == expected,
                )
                self.assertEqual(accepted.status, "VERIFIED")
                rejected = verify(
                    plan, evidence={witness: b"claimed-pass"},
                    independent_witness=lambda key, blob, p, expected=observed: blob == expected,
                )
                self.assertEqual(rejected.status, "UNVERIFIED")

    def test_unknown_has_no_invented_format_or_pass(self):
        ref = PackagingReferent("unfamiliar", ("unclassified-object",),
                                ("survives intended transfer",))
        plan = admit(ref, inspect=lambda _: {
            "unresolved": ["native structure", "destination conditions", "verifier"],
        })
        self.assertEqual(plan.operations, ())
        self.assertEqual(plan.outputs, ())
        self.assertEqual(verify(plan, evidence={},
                                independent_witness=lambda *_: True).status,
                         "DISCOVERY_REQUIRED")

    def test_missing_evidence_is_not_success(self):
        ref = PackagingReferent("known", ("input",), ("relation",))
        plan = admit(ref, inspect=lambda _: {
            "representation": "relations", "operations": ["assemble"],
            "outputs": ["result"], "witnesses": ["native-reopen"]})
        self.assertEqual(verify(plan, evidence={},
                                independent_witness=lambda *_: True).status,
                         "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
