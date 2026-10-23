"""Contract tests for the general packaging admission gate."""
import unittest

from systems.workspace.packaging_harness import PackagingReferent, admit, verify


class PackagingHarnessTests(unittest.TestCase):
    def test_unknown_input_requests_discovery(self):
        item = PackagingReferent("unknown-object", ("object-1",), ("usable after transfer",))
        plan = admit(item, inspect=lambda _: {"unresolved": ["identify native structure"]})
        self.assertEqual(verify(plan, evidence={}, independent_witness=lambda *_: True).status,
                         "DISCOVERY_REQUIRED")

    def test_shape_independence(self):
        for name in ("source-tree", "printed-object", "audio-session"):
            item = PackagingReferent(name, ("source",), ("reopenable",))
            plan = admit(item, inspect=lambda _: {
                "representation": "observed-structure",
                "operations": ["assemble"], "outputs": ["deliverable"],
                "witnesses": ["native-reopen"],
            })
            result = verify(plan, evidence={"native-reopen": b"observed"},
                            independent_witness=lambda key, blob, plan: blob == b"observed")
            self.assertEqual(result.status, "VERIFIED")
            self.assertEqual(len(result.evidence), 1)

    def test_claim_without_native_verification_fails(self):
        item = PackagingReferent("a", ("b",), ("c",))
        plan = admit(item, inspect=lambda _: {
            "representation": "x", "operations": ["y"],
            "outputs": ["z"], "witnesses": ["replay"]})
        result = verify(plan, evidence={"replay": b"PASS"},
                        independent_witness=lambda *_: False)
        self.assertEqual(result.status, "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
