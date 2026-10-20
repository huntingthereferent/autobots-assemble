"""A/B movement 6: source-preserved conservative observability guard for real REA."""
from pathlib import Path
from hashlib import sha256
import argparse, json, shutil, subprocess
from systems.workspace.workstation import ProcessWorkstation
PIN="f0b9ef34c404c1c65f8167502db972b0bd708403"
REL=Path("src/domain/javascript/javascriptAstFingerprint.ts")
ADDITION="\n\n/**\n * Safety boundary for the experimental scoped-reference fingerprint.\n * Name reflection and runtime string-to-code can make lexical alpha-renaming\n * observably change behavior. Do not emit a scoped digest in those cases.\n * This is not a proof that non-rejected JavaScript programs are equivalent.\n */\nexport const fingerprintJavaScriptAstScopedReferencesGuarded = (\n  node: t.Node,\n): string | null => {\n  let unsafeNameOrDynamicResolution = false;\n  traverseJavaScriptAst(node, {\n    enter: (current) => {\n      if (\n        (t.isIdentifier(current) && current.name === \"eval\") ||\n        (t.isStringLiteral(current) && current.value === \"name\")\n      ) unsafeNameOrDynamicResolution = true;\n      if (t.isMemberExpression(current) || t.isOptionalMemberExpression(current)) {\n        const key = semanticStaticPropertyKey(current.property, current.computed);\n        if (key === \"name\" || key === \"toString\" || key === \"caller\" ||\n            key === \"callee\" || key === \"arguments\") {\n          unsafeNameOrDynamicResolution = true;\n        }\n      }\n    },\n  });\n  return unsafeNameOrDynamicResolution ? null : fingerprintJavaScriptAstScopedReferences(node);\n};\n"
def digest(path): return sha256(path.read_bytes()).hexdigest()
def run(action,rea):
    head=subprocess.check_output(["git","-C",str(rea),"rev-parse","HEAD"],text=True).strip()
    if head != PIN: raise ValueError("pinned upstream differs")
    target=rea/REL
    prior=target.read_text()
    if "fingerprintJavaScriptAstScopedReferences" not in prior: raise ValueError("prior scoped source not applied")
    private=Path("runtime/data/rea-observability-guard").resolve()
    desk=ProcessWorkstation(private/"editions")
    if action=="prepare":
        stage=private/"source"
        if stage.exists(): raise FileExistsError("do not overwrite control")
        (stage/REL).parent.mkdir(parents=True)
        shutil.copyfile(target,stage/REL)
        shutil.copyfile(rea/"LICENSE",stage/"LICENSE")
        control=desk.copy_source(stage,worker_id="rea-observability-guard",version_id="control",source_locator="morluto/rea@"+PIN+"+v4+v5")
        exp=desk.branch(worker_id="rea-observability-guard",parent_version="control",version_id="experimental")
        dest=Path(exp["path"])/REL
        text=dest.read_text()
        if "fingerprintJavaScriptAstScopedReferencesGuarded" in text: raise ValueError("no repeated guard")
        dest.write_text(text+ADDITION)
        inspected=desk.inspect(worker_id="rea-observability-guard",version_id="experimental")
        if inspected["modified"]!=[REL.as_posix()]: raise ValueError("unexpected modifications")
        out=Path("experiments/rea-swallow/results")
        out.mkdir(parents=True,exist_ok=True)
        (out/"guard-edition.json").write_text(json.dumps({
            "control_sha256":digest(Path(control["path"])/REL),"experimental_sha256":digest(dest),
            "source":str(REL),"prior_edition":"movement5","upstream":PIN,
            "state":"PENDING_NATIVE_VERIFICATION"},indent=2)+chr(10))
        print("PRESERVED_CONTROL_AND_EXPERIMENTAL_SOURCE",str(REL))
    elif action=="apply":
        old=private/"editions/rea-observability-guard/control"/REL
        new=private/"editions/rea-observability-guard/experimental"/REL
        if digest(target)!=digest(old) or digest(old)==digest(new):
            raise ValueError("control changed or candidate missing")
        shutil.copyfile(new,target)
        subprocess.run(["git","-C",str(rea),"diff","--check"],check=True)
        print("GUARDED_SOURCE_REWRITE_APPLIED",str(REL))
    else: raise ValueError(action)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["prepare","apply"])
    p.add_argument("--rea",required=True,type=Path)
    a=p.parse_args()
    run(a.action,a.rea.resolve())
