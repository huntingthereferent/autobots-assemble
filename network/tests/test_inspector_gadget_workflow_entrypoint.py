"""Run the same native Inspector module entrypoint scheduled by GitHub CI."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
WORKFLOW=ROOT/".github/workflows/inspector-gadget-all-workflows.yml"


class InspectorModuleEntrypointTests(unittest.TestCase):
    def test_calendar_was_retired_not_reintroduced_by_inspector_workflow(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("inspector_gadget_calendar.py", text)
        self.assertNotIn("meta-observations/health.json", text)
        self.assertIn("python -m systems.workspace.inspector_gadget_adapter matrix", text)
        self.assertIn("python -m systems.workspace.inspector_gadget_adapter inspect", text)
        self.assertNotIn("python systems/workspace/inspector_gadget_adapter.py", text)

    def test_real_module_matrix_cli_accepts_pinned_source_incident(self):
        report={
            "schema":"inspector-gadget/workflow-scan/v1",
            "since":"2026-10-22T00:00:00Z",
            "scanned":1,
            "findings":[{
                "id":"inspector-17-failure-121",
                "kind":"candidate","event":"failure",
                "lane":"protocol-tests",
                "run_ids":[121],
                "sources":["https://github.com/huntingthereferent/autobots-assemble/actions/runs/121"],
                "head_shas":["a"*40],
            }],
        }
        with TemporaryDirectory() as td:
            folder=Path(td)
            source=folder/"scan.json"
            target=folder/"plan.json"
            source.write_text(json.dumps(report),encoding="utf-8")
            result=subprocess.run(
                [sys.executable,"-m","systems.workspace.inspector_gadget_adapter",
                 "matrix",str(source),str(target)],
                cwd=ROOT,text=True,capture_output=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            plan=json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(plan["selected"],1)
            self.assertEqual(plan["matrix"]["include"][0]["run_id"],121)
            self.assertEqual(plan["matrix"]["include"][0]["head_sha"],"a"*40)

    def test_no_findings_is_zero_movement_without_fabrication(self):
        with TemporaryDirectory() as td:
            folder=Path(td)
            source=folder/"empty.json"
            target=folder/"plan.json"
            source.write_text(json.dumps({
                "schema":"inspector-gadget/workflow-scan/v1",
                "since":"2026-10-22T00:00:00Z","scanned":0,"findings":[]}),encoding="utf-8")
            result=subprocess.run(
                [sys.executable,"-m","systems.workspace.inspector_gadget_adapter",
                 "matrix",str(source),str(target)],
                cwd=ROOT,text=True,capture_output=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            plan=json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(plan["selected"],0)
            self.assertEqual(plan["matrix"],{"include":[]})


if __name__=="__main__":
    unittest.main()
