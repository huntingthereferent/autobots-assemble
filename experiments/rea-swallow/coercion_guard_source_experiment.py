"""REA movement 7B: branch actual source from guarded version before changing it."""
from pathlib import Path
from hashlib import sha256
import argparse, json, shutil, subprocess
from systems.workspace.workstation import ProcessWorkstation
PIN="f0b9ef34c404c1c65f8167502db972b0bd708403"
REL=Path("src/domain/javascript/javascriptAstFingerprint.ts")
ADDITION="\n\n/**\n * Another bounded negative-evidence boundary. Source-to-primitive conversion\n * can observe function source spelling without .name or .toString tokens.\n * Return unknown for known coercion syntax. This is deliberately conservative\n * and is not a proof of equivalence for code not rejected by this function.\n */\nexport const fingerprintJavaScriptAstCoercionGuarded = (\n  node: t.Node,\n): string | null => {\n  let possibleFunctionStringification = false;\n  traverseJavaScriptAst(node, {\n    enter: (current) => {\n      if (\n        t.isBinaryExpression(current) && current.operator === \"+\" ||\n        t.isTemplateLiteral(current) && current.expressions.length > 0 ||\n        t.isCallExpression(current) &&\n          t.isIdentifier(current.callee) && current.callee.name === \"String\"\n      ) possibleFunctionStringification = true;\n      if (t.isMemberExpression(current) || t.isOptionalMemberExpression(current)) {\n        const property = semanticStaticPropertyKey(current.property, current.computed);\n        if (property === \"join\") possibleFunctionStringification = true;\n      }\n    },\n  });\n  return possibleFunctionStringification\n    ? null\n    : fingerprintJavaScriptAstScopedReferencesGuarded(node);\n};\n"
def digest(p):return sha256(p.read_bytes()).hexdigest()
def main(action,rea):
    head=subprocess.check_output(["git","-C",str(rea),"rev-parse","HEAD"],text=True).strip()
    if head!=PIN:raise ValueError("unverified original REA source")
    original=rea/REL
    if "fingerprintJavaScriptAstScopedReferencesGuarded" not in original.read_text():raise ValueError("prior verified guard is missing")
    private=Path("runtime/data/rea-coercion-guard").resolve()
    desk=ProcessWorkstation(private/"editions")
    if action=="prepare":
        selected=private/"source"
        if selected.exists():raise FileExistsError("source control already staged")
        (selected/REL).parent.mkdir(parents=True)
        shutil.copyfile(original,selected/REL)
        shutil.copyfile(rea/"LICENSE",selected/"LICENSE")
        control=desk.copy_source(selected,worker_id="rea-coercion-guard",version_id="control",source_locator="morluto/rea@"+PIN+"+movement6B")
        edition=desk.branch(worker_id="rea-coercion-guard",parent_version="control",version_id="experimental")
        dest=Path(edition["path"])/REL
        source=dest.read_text()
        if "fingerprintJavaScriptAstCoercionGuarded" in source: raise ValueError("existing candidate")
        dest.write_text(source+ADDITION)
        diff=desk.inspect(worker_id="rea-coercion-guard",version_id="experimental")
        if diff["modified"]!=[REL.as_posix()]:raise ValueError("unanticipated source edit")
        out=Path("experiments/rea-swallow/results")
        out.mkdir(parents=True,exist_ok=True)
        (out/"coercion-guard-edition.json").write_text(json.dumps({
          "upstream":PIN,"parent":"movement6B","source":str(REL),
          "control_sha256":digest(Path(control["path"])/REL),
          "experimental_sha256":digest(dest),"state":"PENDING_NATIVE_CHECKS"},indent=2)+chr(10))
        print("PRESERVED_GUARD_CONTROL",diff["modified"])
    elif action=="apply":
        control=private/"editions/rea-coercion-guard/control"/REL
        candidate=private/"editions/rea-coercion-guard/experimental"/REL
        if digest(original)!=digest(control) or digest(candidate)==digest(control):
            raise ValueError("control lost or no experimental source edit")
        shutil.copyfile(candidate,original)
        subprocess.run(["git","-C",str(rea),"diff","--check"],check=True)
        print("REAL_REA_COERCION_GUARD_APPLIED",REL)
    else:raise ValueError(action)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["prepare","apply"])
    parser.add_argument("--rea",type=Path,required=True)
    args=parser.parse_args()
    main(args.action,args.rea.resolve())
