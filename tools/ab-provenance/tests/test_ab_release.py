"""A/B release gate tests: fixture receipts are NOT independent native witnesses."""
from __future__ import annotations
from contextlib import redirect_stderr,redirect_stdout
from hashlib import sha256
from io import BytesIO,StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import tarfile
import unittest
from zipfile import ZipFile

from ab_prov.ab_tool import PIN, STAGES, ABEvidenceError, main
from ab_prov.release import BUNDLE, DIST_NAMES, DOC_FILES, GUIDES, validate_evidence, validate_reference_comparison, ship

LICENSE = "Copyright (c) 2026 James Muneoka. All rights reserved.\n\nTEST FIXTURE ONLY\n"

def h(path):
    return sha256(path.read_bytes()).hexdigest()

def dummy_workspace(root:Path):
    tool=root/"tools/ab-provenance"
    (tool/"docs").mkdir(parents=True)
    (tool/"site").mkdir(parents=True)
    (tool/"site"/"index.html").write_text("<html><title>A/B fixture docs</title></html>")
    (root/"runtime/data/evidence").mkdir(parents=True)
    dist=root/"runtime/data/evidence/dist"
    dist.mkdir(parents=True)
    (root/"LICENSE").write_text(LICENSE)
    for name in DOC_FILES:
        (tool/name).write_text(LICENSE if name=="LICENSE" else "fixture documentation\n")
    for name in GUIDES:
        (tool/"docs"/name).write_text("fixture A/B guide\n")
    for name in DIST_NAMES:
        path=dist/name
        if name.endswith(".whl"):
            with ZipFile(path,"w") as z:
                z.writestr("ab_tool-0.1.0.dist-info/licenses/LICENSE",LICENSE)
        else:
            with tarfile.open(path,"w:gz") as tar:
                data=LICENSE.encode()
                info=tarfile.TarInfo("ab_tool-0.1.0/LICENSE")
                info.size=len(data)
                tar.addfile(info,BytesIO(data))
    evidence=root/"runtime/data/evidence"
    stages=[]
    for n,(stage,_) in enumerate(STAGES):
        row={"name":stage,"result":"PREPARED"}
        for action in ("prepare","apply"):
            name=f"{stage}-{action}.log"
            p=evidence/name
            p.write_text("TEST FIXTURE — not a native command\n")
            row[action]={"log":name,"sha256":h(p),"returncode":0,"timed_out":False}
        if n==len(STAGES)-1:
            row["result"]="PASS"
            for field,name in (("native","native-rea-tests.log"),
                               ("typecheck","rea-typecheck.log"),
                               ("source_diff_check","source-diff-check.log")):
                p=evidence/name
                p.write_text("TEST FIXTURE — not a genuine upstream test\n")
                row[field]={"log":name,"sha256":h(p),
                            "returncode":0,"timed_out":False}
        stages.append(row)
    receipt={"kind":"ab-tool/real-rea-source-edition-v1",
             "upstream":"morluto/rea","upstream_commit":PIN,
             "result":"PASS","stages":stages}
    (evidence/"source-absorption-receipt.json").write_text(json.dumps(receipt))
    graph={"schema_version":1,"traces":[],
           "provenance_links":[
               {"provenance_id":f"ab-source-{i}-{row['name']}"}
               for i,row in enumerate(stages,1)]}
    (evidence/"source-provenance.json").write_text(json.dumps(graph))
    for name in ("source-provenance.html","graph.json","ancestry.json"):
        (evidence/name).write_text("TEST FIXTURE — illustrative only")
    comparison=evidence/"comparison"
    comparison.mkdir()
    # Synthetic fixtures verify structural gating only: these strings do not
    # masquerade as genuine native observations in a released experiment.
    original=comparison/"original-vitest.json"
    original.write_text('{"testResults":[],"fixture":true}')
    (comparison/"original-vitest.log").write_text("TEST FIXTURE: original\n")
    updated=comparison/"regrounded-vitest.json"
    updated.write_text('{"testResults":[],"fixture":true}')
    (comparison/"regrounded-vitest.log").write_text("TEST FIXTURE: regrounded\n")
    baseline={"kind":"ab/original-REA-before-correction-v1","pin":PIN,
      "original_test_cases":[["fixture-suite","fixture-assertion"]],
      "native":{"json_sha256":h(original),
                "log_sha256":h(comparison/"original-vitest.log")}}
    b=comparison/"baseline.json"
    b.write_text(json.dumps(baseline))
    result={"kind":"ab/paired-reference-verdict-v1","upstream_pin":PIN,
      "verdict":"PARTIAL_NATIVE_MATCH","full_REA_reconstructed":False,
      "baseline_sha256":h(b),
      "original_native_json_sha256":h(original),
      "regrounded_native_json_sha256":h(updated),
      "before_assertions":1,"after_assertions":1,
      "capability_coverage":{
        "original_cli_mcp_binary_android_and_other_providers":{"status":"NOT_RECONSTRUCTED"},
        "license":{"status":"SEPARATE_RIGHTS"}}}
    (comparison/"comparison.json").write_text(json.dumps(result))
    (comparison/"comparison.md").write_text("TEST FIXTURE: not real native witness\n")
    return evidence,dist,tool

class ABShipTests(unittest.TestCase):
    def test_release_gate_assembles_owned_ab_package_and_separate_source_notice(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            evidence,dist,tool=dummy_workspace(root)
            out=root/"runtime/data/shipped"
            report=ship(repo=root,evidence=evidence,dist=dist,out=out)
            self.assertEqual(report["status"],"RELEASE_CANDIDATE_READY")
            self.assertEqual(report["source_referent_included"],False)
            manifest=json.loads((out/"release-manifest.json").read_text())
            self.assertEqual(manifest["product"],"A/B")
            self.assertEqual(manifest["source_referent"]["pin"],PIN)
            with ZipFile(out/BUNDLE) as archive:
                self.assertIn("LICENSE",archive.namelist())
                self.assertEqual(archive.read("LICENSE").decode(),LICENSE)
                self.assertIn("THIRD_PARTY_NOTICES.md",archive.namelist())
                self.assertIn("docs/quickstart.md",archive.namelist())
                self.assertIn("docs-site/index.html",archive.namelist())
                self.assertIn("comparison/comparison.json",archive.namelist())
                self.assertIn("comparison/baseline.json",archive.namelist())
                self.assertIn("evidence/source-absorption-receipt.json",archive.namelist())
                self.assertIn("dist/"+DIST_NAMES[0],archive.namelist())
                self.assertIn("release-manifest.json",archive.namelist())
                self.assertFalse(any("morluto/rea/" in n for n in archive.namelist()))
            with self.assertRaises(ABEvidenceError):
                ship(repo=root,evidence=evidence,dist=dist,out=out)

    def test_evidence_bytes_changed_after_receipt_never_ship(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            evidence,dist,_=dummy_workspace(root)
            (evidence/"native-rea-tests.log").write_text("tampered fixture")
            with self.assertRaisesRegex(ABEvidenceError,"hash mismatch"):
                validate_evidence(evidence)
            self.assertFalse((root/"runtime/data/shipped").exists())

    def test_failing_native_status_never_ships(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            evidence,dist,_=dummy_workspace(root)
            file=evidence/"source-absorption-receipt.json"
            receipt=json.loads(file.read_text())
            receipt["result"]="FAILED"
            file.write_text(json.dumps(receipt))
            with self.assertRaises(ABEvidenceError):
                ship(repo=root,evidence=evidence,dist=dist,
                     out=root/"runtime/data/shipped")

    def test_missing_upstream_paired_comparison_blocks_shipment(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            evidence,dist,_=dummy_workspace(root)
            (evidence/"comparison/comparison.json").unlink()
            with self.assertRaises(ABEvidenceError):
                ship(repo=root,evidence=evidence,dist=dist,
                     out=root/"runtime/data/shipped")

    def test_false_full_rea_identity_claim_blocks_shipment(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            evidence,dist,_=dummy_workspace(root)
            f=evidence/"comparison/comparison.json"
            wrong=json.loads(f.read_text())
            wrong["full_REA_reconstructed"]=True
            f.write_text(json.dumps(wrong))
            with self.assertRaises(ABEvidenceError):
                validate_reference_comparison(evidence)

    def test_modified_comparison_original_native_pixels_are_rejected(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            evidence,dist,_=dummy_workspace(root)
            (evidence/"comparison/original-vitest.json").write_text('{"changed":true}')
            with self.assertRaises(ABEvidenceError):
                validate_reference_comparison(evidence)

    def test_own_product_license_cannot_be_replaced_by_referent_license(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            evidence,dist,tool=dummy_workspace(root)
            (tool/"LICENSE").write_text("MIT License\nOriginal referent")
            with self.assertRaisesRegex(ABEvidenceError,"A/B product license diverged"):
                ship(repo=root,evidence=evidence,dist=dist,
                     out=root/"runtime/data/shipped")

    def test_wheel_license_required_as_well_as_top_level_notice(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            evidence,dist,_=dummy_workspace(root)
            with ZipFile(dist/DIST_NAMES[0],"w") as z:
                z.writestr("ab_tool-0.1.0.dist-info/licenses/LICENSE",
                           "MIT License — not A/B")
            with self.assertRaises(ABEvidenceError):
                ship(repo=root,evidence=evidence,dist=dist,
                     out=root/"runtime/data/shipped")

    def test_swallow_repo_is_same_real_source_adapter_not_arbitrary_clone(self):
        out=StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["source"]),0)
        self.assertEqual(json.loads(out.getvalue())["upstream"],"morluto/rea")
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as e:
                main(["swallow","repo","--out","runtime/data/illegal"])
        self.assertEqual(e.exception.code,2)

    def test_ship_command_rejects_missing_evidence_without_publishing(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            with redirect_stderr(StringIO()):
                result=main(["ship","--repo-root",str(root),
                             "--evidence",str(root/"empty"),
                             "--dist",str(root/"empty-dist"),
                             "--out",str(root/"runtime/data/release")])
            self.assertEqual(result,2)
            self.assertFalse((root/"runtime/data/release").exists())

if __name__=="__main__":
    unittest.main()
