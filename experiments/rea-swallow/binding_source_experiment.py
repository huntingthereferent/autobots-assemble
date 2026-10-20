"""Bounded source-edition implementation of a new REA binding-aware fingerprint."""
from pathlib import Path
from hashlib import sha256
import argparse, json, shutil, subprocess
from systems.workspace.workstation import ProcessWorkstation

PIN = "f0b9ef34c404c1c65f8167502db972b0bd708403"
REL = Path("src/domain/javascript/javascriptAstFingerprint.ts")
ADDITION = "\n\n/**\n * Experimental lexical-reference fingerprint (babel-ast-parameter-relations-v1).\n * Preserves which formal parameter or simple local each reference selects,\n * independently of variable spelling. Returns null for unsupported binding\n * constructs instead of suggesting a stronger equivalence than was checked.\n * The shipped babel-ast-v3 fingerprint remains unchanged.\n */\nexport const fingerprintJavaScriptAstParameterRelations = (\n  node: t.Node,\n): string | null => {\n  const candidate = t.isFile(node)\n    ? node.program.body.length === 1 ? node.program.body[0] : null\n    : t.isProgram(node)\n      ? node.body.length === 1 ? node.body[0] : null\n      : node;\n  if (candidate === null || candidate === undefined || !t.isFunction(candidate))\n    return null;\n  if (!candidate.params.every(t.isIdentifier)) return null;\n  const parameterNames = candidate.params.map((value) => (value as t.Identifier).name);\n  if (new Set(parameterNames).size !== parameterNames.length) return null;\n  const locals: string[] = [];\n  let supported = true;\n  // First pass: collect all local declarations. Conservatively reject nested\n  // lexical scopes and binding forms this restricted probe cannot model.\n  traverseJavaScriptAst(candidate.body, {\n    enter: (current) => {\n      if (\n        t.isFunction(current) ||\n        t.isClass(current) ||\n        t.isCatchClause(current) ||\n        (t.isBlockStatement(current) && current !== candidate.body)\n      ) supported = false;\n      if (t.isVariableDeclarator(current)) {\n        if (!t.isIdentifier(current.id)) supported = false;\n        else locals.push(current.id.name);\n      }\n    },\n  });\n  if (\n    !supported ||\n    locals.some((name) => parameterNames.includes(name)) ||\n    new Set(locals).size !== locals.length\n  ) return null;\n\n  // Second pass: preserve exactly which declaration each referenced Identifier\n  // denotes. Unknown/free identifiers retain their names; only locally bound\n  // names are normalized. No runtime behavior is claimed.\n  const references: string[] = [];\n  traverseJavaScriptAst(candidate.body, {\n    enter: (current, parent) => {\n      if (!t.isIdentifier(current) || parent === null ||\n          !t.isReferenced(current, parent)) return;\n      const param = parameterNames.indexOf(current.name);\n      if (param !== -1) { references.push(\"parameter:\" + param); return; }\n      const local = locals.indexOf(current.name);\n      if (local !== -1) { references.push(\"local:\" + local); return; }\n      references.push(\"unresolved:\" + current.name);\n    },\n  });\n  return createHash(\"sha256\")\n    .update(JSON.stringify([\n      \"babel-ast-parameter-relations-v1\", fingerprintJavaScriptAst(node), references,\n    ]))\n    .digest(\"hex\");\n};\n"

def digest(path): return sha256(path.read_bytes()).hexdigest()

def run(action, rea):
    head = subprocess.check_output(["git", "-C", str(rea), "rev-parse", "HEAD"], text=True).strip()
    if head != PIN: raise ValueError("unverified upstream REA revision: "+head)
    private = Path("runtime/data/rea-binding-fingerprint").resolve()
    desk = ProcessWorkstation(private / "editions")
    if action == "prepare":
        selected = private / "selected-source"
        if selected.exists(): raise FileExistsError("do not replace previous editions")
        (selected/REL).parent.mkdir(parents=True)
        shutil.copyfile(rea/REL, selected/REL)
        shutil.copyfile(rea/"LICENSE", selected/"LICENSE")
        control = desk.copy_source(selected, worker_id="rea-binding-fingerprint", version_id="control", source_locator="morluto/rea@"+PIN)
        candidate = desk.branch(worker_id="rea-binding-fingerprint", parent_version="control", version_id="experimental")
        target = Path(candidate["path"])/REL
        source = target.read_text(encoding="utf-8")
        if "fingerprintJavaScriptAstParameterRelations" in source: raise ValueError("fingerprint already present")
        target.write_text(source + ADDITION, encoding="utf-8")
        inspection = desk.inspect(worker_id="rea-binding-fingerprint", version_id="experimental")
        if inspection["modified"] != [REL.as_posix()]: raise ValueError("unrecognized edit")
        results = Path("experiments/rea-swallow/results")
        results.mkdir(parents=True, exist_ok=True)
        (results/"binding-edition.json").write_text(json.dumps({"upstream":PIN,"source":str(REL),
            "control_sha256":digest(Path(control["path"])/REL),"candidate_sha256":digest(target),
            "parent":candidate["parent_version"],"fingerprint":control["source_fingerprint"],
            "status":"PENDING_REAL_NATIVE_TESTS"}, indent=2)+chr(10))
        print("SOURCE EDITION CREATED",inspection["modified"])
    else:
        control = private/"editions/rea-binding-fingerprint/control"/REL
        candidate = private/"editions/rea-binding-fingerprint/experimental"/REL
        if digest(rea/REL) != digest(control) or digest(candidate) == digest(control):
            raise ValueError("missing unaltered control or experimental transformation")
        shutil.copyfile(candidate,rea/REL)
        subprocess.run(["git","-C",str(rea),"diff","--check"],check=True)
        print("REAL_REA_FINGERPRINT_SOURCE_CHANGED",str(REL))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare","apply"])
    parser.add_argument("--rea", type=Path, required=True)
    args = parser.parse_args()
    run(args.action,args.rea.resolve())
