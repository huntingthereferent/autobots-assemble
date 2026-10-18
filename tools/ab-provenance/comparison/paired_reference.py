"""Prospective before/after test of actual pinned REA source and A/B correction.

Original native REA tests run BEFORE source modification, then exactly those
original tests run AFTER ProcessWorkstation correction. Records original product
scope gaps rather than claiming source-subset parity means full REA equivalence.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tomllib

PIN="f0b9ef34c404c1c65f8167502db972b0bd708403"
TESTS=(
 "src/domain/javascript/javascriptApplicationVersionMatching.test.ts",
 "src/domain/javascript/javascriptApplicationVersionComparison.test.ts",
 "src/domain/javascript/javascriptApplicationVersionRelationshipUncertainty.test.ts",
)
SOURCE="src/domain/javascript/javascriptApplicationVersionKeys.ts"
DOCS=("docs/cli.md","docs/mcp-contracts.md","docs/javascript-application-workflows.md","docs/installation.md")

class ComparisonError(ValueError): pass
def digest(p): return sha256(Path(p).read_bytes()).hexdigest()

def identity(rea):
    if not (rea/"package.json").is_file() or not (rea/".git").exists():
        raise ComparisonError("actual pinned REA git checkout required")
    commit=subprocess.run(["git","-C",str(rea),"rev-parse","HEAD"],
          capture_output=True,text=True,check=True).stdout.strip()
    if commit!=PIN: raise ComparisonError("actual pinned REA source absent")
    pkg=json.loads((rea/"package.json").read_text())
    if pkg.get("name")!="rea-agents" or pkg.get("license")!="MIT":
        raise ComparisonError("actual upstream package or original license changed")
    return {"version":pkg.get("version"),"name":pkg["name"],"bins":pkg.get("bin"),
      "mcp_script":pkg.get("scripts",{}).get("start"),
      "docs":{p:digest(rea/p) for p in DOCS}}

def native(rea,out,tag):
    out.mkdir(parents=True,exist_ok=True)
    report=out/(tag+"-vitest.json")
    log=out/(tag+"-vitest.log")
    if report.exists() or log.exists(): raise ComparisonError("cannot rewrite native evidence")
    command=["npx","--no-install","vitest","run",*TESTS,
             "--reporter=json","--outputFile="+str(report)]
    try:
        proc=subprocess.run(command,cwd=rea,capture_output=True,text=True,timeout=300)
    except subprocess.TimeoutExpired as exc:
        raise ComparisonError("native comparison exceeded experiment bound") from exc
    log.write_text((proc.stdout or "")+"\n"+(proc.stderr or ""))
    if proc.returncode!=0 or not report.is_file():
        raise ComparisonError("native test failed: "+str(log))
    return {"json_sha256":digest(report),"log_sha256":digest(log),
            "exit_code":proc.returncode,"command":command}

def cases(report):
    obj=json.loads(report.read_text())
    if not isinstance(obj.get("testResults"),list): raise ComparisonError("missing Vitest testResults")
    found=[]
    for suite in obj["testResults"]:
        name=str(suite.get("name","")).replace("\\","/")
        matching=[p for p in TESTS if name.endswith(p)]
        if len(matching)!=1: raise ComparisonError("unknown original test path "+name)
        assertions=suite.get("assertionResults")
        if not isinstance(assertions,list) or not assertions: raise ComparisonError("missing test assertions")
        for a in assertions:
            if not isinstance(a.get("fullName"),str) or a.get("status")!="passed":
                raise ComparisonError("failed/skipped/unknown original assertion")
            found.append((matching[0],a["fullName"]))
    found.sort()
    if not found or set(x[0] for x in found)!=set(TESTS) or len(found)!=len(set(found)):
        raise ComparisonError("incomplete/duplicate original assertions")
    return found

def baseline(rea,out):
    pkg=identity(rea)
    if out.exists(): raise ComparisonError("original test record cannot be overwritten")
    out.mkdir(parents=True)
    source_hash=digest(rea/SOURCE)
    tests={p:digest(rea/p) for p in TESTS}
    execution=native(rea,out,"original")
    items=cases(out/"original-vitest.json")
    record={"kind":"ab/original-REA-before-correction-v1","pin":PIN,"package":pkg,
            "source_file":SOURCE,"source_before":source_hash,
            "test_file_hashes":tests,"original_test_cases":items,
            "native":execution,"test_count":len(items)}
    (out/"baseline.json").write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    return record

def compare(rea,tool,original_dir,out):
    pkg=identity(rea)
    frozen=json.loads((original_dir/"baseline.json").read_text())
    if (frozen.get("kind")!="ab/original-REA-before-correction-v1" or
        frozen.get("pin")!=PIN or pkg!=frozen["package"] or
        digest(original_dir/"original-vitest.json")!=frozen["native"]["json_sha256"] or
        digest(original_dir/"original-vitest.log")!=frozen["native"]["log_sha256"] or
        cases(original_dir/"original-vitest.json")!=[tuple(x) for x in frozen["original_test_cases"]]):
        raise ComparisonError("original frozen REA native witness changed")
    if any(digest(rea/p)!=h for p,h in frozen["test_file_hashes"].items()):
        raise ComparisonError("upstream original test definitions changed")
    changed=digest(rea/SOURCE)
    if changed==frozen["source_before"]:
        raise ComparisonError("A/B did not correct actual original source")
    if out.exists(): raise ComparisonError("original paired result cannot be overwritten")
    out.mkdir(parents=True)
    result=native(rea,out,"regrounded")
    after=cases(out/"regrounded-vitest.json")
    before=[tuple(x) for x in frozen["original_test_cases"]]
    same=before==after
    scripts=tomllib.loads((tool/"pyproject.toml").read_text())["project"]["scripts"]
    if not all(x in scripts for x in ("ab","ab-prov")):
        raise ComparisonError("A/B tool executable missing")
    ab_docs=("README.md","docs/quickstart.md","docs/swallow-repo-lane.md","docs/release.md","site/index.html","LICENSE")
    coverage={
      "native_original_matching_suite":{"status":"MATCH" if same else "DIVERGED",
        "case_count_original":len(before),"case_count_regrounded":len(after)},
      "source":{"status":"CORRECTED_SOURCE","source":SOURCE,
        "original_sha256":frozen["source_before"],"regrounded_sha256":changed},
      "original_cli_mcp_binary_android_and_other_providers":{
        "status":"NOT_RECONSTRUCTED","original_bin":pkg["bins"],
        "original_mcp_start":pkg["mcp_script"],"ab_bin":scripts,
        "claim":"A/B is not the same full program as REA"},
      "documentation":{"status":"ORIGINAL_AB_DOCS_NOT_COPIED",
        "upstream_source_hashes":pkg["docs"],
        "ab_source_hashes":{p:digest(tool/p) for p in ab_docs}},
      "license":{"status":"SEPARATE_RIGHTS","A/B":"All Rights Reserved",
                 "REA":"MIT on original REA source"}
    }
    verdict="PARTIAL_NATIVE_MATCH" if same else "NATIVE_DIVERGENCE"
    record={"kind":"ab/paired-reference-verdict-v1","verdict":verdict,
      "actual_original_pre_correction_run":True,
      "actual_regrounded_post_correction_run":True,
      "upstream_pin":PIN,
      "before_assertions":len(before),"after_assertions":len(after),
      "baseline_sha256":digest(original_dir/"baseline.json"),
      "original_native_json_sha256":frozen["native"]["json_sha256"],
      "regrounded_native_json_sha256":result["json_sha256"],
      "full_REA_reconstructed":False,"capability_coverage":coverage,
      "claim_limit":"Equal results on frozen upstream regression tests are not full program equivalence."}
    (out/"comparison.json").write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    lines=[
      "# A/B Swallow Repo — original versus corrected source",
      "",
      "Verdict: "+verdict,
      "",
      "Original pinned REA: "+PIN,
      "Native original test cases before changing source: "+str(len(before)),
      "Same native original test cases after workstation corrections: "+str(len(after)),
      "Exact original test identity and outcome parity: "+str(same),
      "Original source fingerprint differs after A/B change: "+str(frozen["source_before"]!=changed),
      "",
      "FULL REA CLI/MCP, native, Android, and other providers: NOT RECONSTRUCTED.",
      "The A/B Python product has its own CLI and original documentation.",
      "Original REA copyright/MIT stays with REA; A/B original code All Rights Reserved.",
      "The result supports only the compared original test cases, not a general theorem.",
      "Frozen baseline and original/regrounded native reports are retained separately."
    ]
    (out/"comparison.md").write_text("\n".join(lines)+"\n")
    return record

def main(argv=None):
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="phase",required=True)
    b=sub.add_parser("baseline")
    b.add_argument("--rea",type=Path,required=True)
    b.add_argument("--out",type=Path,required=True)
    e=sub.add_parser("compare")
    e.add_argument("--rea",type=Path,required=True)
    e.add_argument("--ab-tool",type=Path,required=True)
    e.add_argument("--baseline",type=Path,required=True)
    e.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    try:
        if a.phase=="baseline":
            r=baseline(a.rea.resolve(),a.out.resolve())
            print(json.dumps({"phase":"baseline","assertions":r["test_count"],"pin":PIN}))
        else:
            r=compare(a.rea.resolve(),a.ab_tool.resolve(),a.baseline.resolve(),a.out.resolve())
            print(json.dumps({"phase":"comparison","verdict":r["verdict"],
              "same_full_REA":False,"assertions":r["after_assertions"]}))
            if r["verdict"]!="PARTIAL_NATIVE_MATCH": return 3
        return 0
    except (ComparisonError,OSError,KeyError,subprocess.CalledProcessError) as err:
        print("ab comparison: "+str(err),file=sys.stderr)
        return 2
if __name__=="__main__": raise SystemExit(main())
