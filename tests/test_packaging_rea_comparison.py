"""Source-backed REA comparison contract tests (not a native REA execution)."""
import tempfile
import unittest
from pathlib import Path

from systems.workspace.packaging_harness import verify
from systems.workspace.packaging_rea_comparison import (
    REA_NATIVE_WITNESSES, plan_rea_comparison,
)


class REAPackagingComparisonTests(unittest.TestCase):
    def test_actual_contract_requires_native_receipts(self):
        # A real source file is required. The fixture reproduces only inspected
        # contract markers; it cannot impersonate an executed release.
        source_contract = '''
        upstream_commit") != PIN
        NATIVE_LOGS
        _archive_license
        validate_reference_comparison
        "sha256": _hash(src)
        "release-manifest.json"
        '''
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "release.py"
            source.write_text(source_contract, encoding="utf-8")
            plan = plan_rea_comparison(source)
            self.assertEqual(plan.witnesses, REA_NATIVE_WITNESSES)
            self.assertIn("execute native REA source and record fresh receipts", plan.unresolved)
            self.assertEqual(
                verify(plan, evidence={key: b"PASS" for key in REA_NATIVE_WITNESSES},
                       independent_witness=lambda *_: True).status,
                "DISCOVERY_REQUIRED",
            )

    def test_missing_release_relation_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "release.py"
            source.write_text("NATIVE_LOGS", encoding="utf-8")
            plan = plan_rea_comparison(source)
            self.assertIn("source pin", plan.unresolved)
            self.assertIn("rights", plan.unresolved)
            self.assertIn("release manifest", plan.unresolved)


if __name__ == "__main__":
    unittest.main()
