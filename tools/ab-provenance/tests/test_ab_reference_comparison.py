"""The source-comparison verdict must distinguish native parity from full product identity."""
import importlib.util
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[1]/"comparison"/"paired_reference.py"
spec=importlib.util.spec_from_file_location("ab_paired_reference",HERE)
assert spec and spec.loader
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PairedReferenceTests(unittest.TestCase):
    def _vitest(self, statuses=("passed","passed","passed")):
        return {"testResults":[{"name":"/fixture/"+suite,"assertionResults":[{
           "fullName":"original test case "+str(i),"status":state}]
          } for i,(suite,state) in enumerate(zip(module.TESTS,statuses))]}

    def test_only_original_upstream_suite_assertions_are_accepted(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"original.json"
            p.write_text(json.dumps(self._vitest()))
            result=module.cases(p)
            self.assertEqual(len(result),3)
            self.assertEqual({x[0] for x in result},set(module.TESTS))

    def test_skipped_test_is_not_comparable_to_a_success(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"skipped.json"
            p.write_text(json.dumps(self._vitest(("passed","pending","passed"))))
            with self.assertRaises(module.ComparisonError):
                module.cases(p)

    def test_unknown_suite_cannot_stand_in_for_original_source(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"fake.json"
            data=self._vitest()
            data["testResults"][0]["name"]="/fixture/completely-different-suite.test.ts"
            p.write_text(json.dumps(data))
            with self.assertRaises(module.ComparisonError):
                module.cases(p)

    def test_identical_case_names_must_not_hide_duplicate_upstream_tests(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"bad.json"
            data=self._vitest()
            data["testResults"][0]["assertionResults"].append(
                data["testResults"][0]["assertionResults"][0])
            p.write_text(json.dumps(data))
            with self.assertRaises(module.ComparisonError):
                module.cases(p)

    def test_baseline_cannot_replace_original_result(self):
        with TemporaryDirectory() as d:
            with self.assertRaises(module.ComparisonError):
                module.baseline(Path(d),Path(d))

    def test_package_verdict_never_labels_shared_subset_as_complete_rea(self):
        text=HERE.read_text()
        self.assertIn('"full_REA_reconstructed":False',text)
        self.assertIn('"NOT_RECONSTRUCTED"',text)
        self.assertIn('"SEPARATE_RIGHTS"',text)
        self.assertIn('original_test_cases',text)
        self.assertNotIn("copytree(",text)

if __name__=="__main__":unittest.main()
