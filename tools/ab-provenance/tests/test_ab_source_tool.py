"""A/B must operate existing source and never replace tests with fabricated proof."""
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from ab_prov.ab_tool import ABEvidenceError,PIN,STAGES,NATIVE_TESTS,CONTRACT_COPIES,main,_check_repo,_graph

class RealABSourceToolTests(unittest.TestCase):
    def test_pinned_original_source_stages(self):
        output=StringIO()
        with redirect_stdout(output):
            code=main(["source"])
        self.assertEqual(code,0)
        x=json.loads(output.getvalue())
        self.assertEqual(x["upstream"],"morluto/rea")
        self.assertEqual(x["pin"],PIN)
        self.assertEqual(x["actual_source_editions"],
                         ["observation","choice","construct","advance","checkpoint"])
        self.assertIn("MIT",x["original_LICENSE"])

    def test_explicit_source_edit_approval_required(self):
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as caught:
                main(["swallow","--out","runtime/data/bad"])
        self.assertEqual(caught.exception.code,2)

    def test_missing_source_fails_closed_without_creating_success(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            with redirect_stderr(StringIO()):
                result=main(["swallow","--repo-root",str(root),
                             "--out",str(root/"runtime/data/out"),
                             "--allow-source-edit"])
            self.assertEqual(result,2)
            self.assertFalse((root/"runtime/data/out").exists())

    def test_unrelated_source_cannot_be_substituted_for_rea(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaises(ABEvidenceError):
                _check_repo(root,root/"unrelated",root/"runtime/data/report")

    def test_existing_source_scripts_are_workstation_editions(self):
        src=Path(__file__).resolve().parents[3]/"experiments/rea-swallow"
        for name,script in STAGES:
            self.assertTrue((src/script).is_file(),name)
            text=(src/script).read_text()
            self.assertIn("ProcessWorkstation",text)
            self.assertIn("git",text)
        for src_file,_ in CONTRACT_COPIES:
            self.assertTrue((src/src_file).is_file())
        self.assertIn("javascriptCheckpoint.ab-swallow.test.ts",NATIVE_TESTS)

    def test_source_receipt_keeps_partial_stage_unproved(self):
        report={"stages":[{"name":"observation","timestamp":"2026-10-18T00:00:00Z",
                           "result":"PREPARED","prepare":{"log":"prepare.log"},
                           "apply":{"log":"apply.log"}}]}
        graph=_graph(report)
        edge=graph["provenance_links"][0]
        self.assertEqual(edge["from"]["ref"],"REA@"+PIN)
        self.assertIn("not individually native-tested"," ".join(edge["boundaries"]))
        self.assertEqual(edge["evidence_refs"],["local-log://prepare.log","local-log://apply.log"])
        self.assertEqual(edge["invalidated"],[])

    def test_inspection_is_part_of_one_ab_cli(self):
        sample=Path(__file__).resolve().parents[1]/"examples/illustrative-provenance.json"
        output=StringIO()
        with redirect_stdout(output):
            result=main(["inspect",str(sample)])
        self.assertEqual(result,0)
        self.assertFalse(json.loads(output.getvalue())["independently_verified_by_this_tool"])

    def test_arbitrary_commands_have_no_execution_route(self):
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                main(["execute-arbitrary-python"])

if __name__=="__main__":
    unittest.main()
