"""Source-preserving scoped REA experiment, branching directly from movement 4."""
from pathlib import Path
from hashlib import sha256
import argparse, json, shutil, subprocess
from systems.workspace.workstation import ProcessWorkstation
PIN = "f0b9ef34c404c1c65f8167502db972b0bd708403"
REL = Path("src/domain/javascript/javascriptAstFingerprint.ts")
ADDITION = "\n\n/** Experimental lexical scope reference fingerprint; does not replace babel-ast-v3. */\nexport const fingerprintJavaScriptAstScopedReferences = (node: t.Node): string | null => {\n  const root = t.isFile(node)\n    ? node.program.body.length === 1 ? node.program.body[0] : null\n    : t.isProgram(node)\n      ? node.body.length === 1 ? node.body[0] : null\n      : node;\n  if (!root || !(t.isFunctionDeclaration(root) ||\n        t.isFunctionExpression(root) || t.isArrowFunctionExpression(root))) return null;\n  interface Scope {\n    readonly id: number;\n    readonly parent: Scope | null;\n    readonly names: Map<string, string>;\n  }\n  let nextScope = 0;\n  let supported = true;\n  const links: string[] = [];\n  const newScope = (parent: Scope | null): Scope =>\n    ({id: nextScope++, parent, names: new Map<string, string>()});\n  const declare = (scope: Scope, name: string, role: string) => {\n    if (scope.names.has(name)) supported = false;\n    else scope.names.set(name, \"scope:\" + scope.id + \":\" + role);\n  };\n  const lookup = (scope: Scope, name: string): string => {\n    for (let current: Scope | null = scope; current !== null; current = current.parent) {\n      const bound = current.names.get(name);\n      if (bound !== undefined) return bound;\n    }\n    return \"free:\" + name;\n  };\n  const visit = (current: t.Node, parent: t.Node | null, scope: Scope | null): void => {\n    if (!supported) return;\n    // Every unsupported lexical-control construct is rejected, not guessed.\n    if (current.type.startsWith(\"TS\") || t.isClass(current) ||\n        t.isCatchClause(current) || t.isTryStatement(current) ||\n        t.isSwitchStatement(current) || t.isForStatement(current) ||\n        t.isForInStatement(current) || t.isForOfStatement(current) ||\n        t.isWhileStatement(current) || t.isDoWhileStatement(current) ||\n        t.isWithStatement(current) || t.isLabeledStatement(current) ||\n        t.isObjectMethod(current) || t.isClassMethod(current)) {\n      supported = false;\n      return;\n    }\n    if (t.isFunction(current)) {\n      if ((current !== root && t.isFunctionDeclaration(current)) ||\n          (current !== root && t.isFunctionExpression(current) && current.id !== null) ||\n          !current.params.every(t.isIdentifier)) { supported = false; return; }\n      const local = newScope(scope);\n      if (current === root && t.isFunctionDeclaration(current) && t.isIdentifier(current.id))\n        declare(local, current.id.name, \"self\");\n      current.params.forEach((param, index) => {\n        if (t.isIdentifier(param)) declare(local, param.name, \"param:\" + index);\n      });\n      visit(current.body, current, local);\n      return;\n    }\n    if (t.isBlockStatement(current)) {\n      if (scope === null) { supported = false; return; }\n      const block = newScope(scope);\n      for (const stmt of current.body) {\n        if (!t.isVariableDeclaration(stmt)) continue;\n        if (stmt.kind === \"var\") { supported = false; return; }\n        for (const decl of stmt.declarations) {\n          if (!t.isIdentifier(decl.id)) { supported = false; return; }\n          declare(block, decl.id.name, \"local:\" + block.names.size);\n        }\n      }\n      for (const child of childNodes(current)) visit(child, current, block);\n      return;\n    }\n    if (t.isVariableDeclaration(current) &&\n        (current.kind === \"var\" || !t.isBlockStatement(parent))) {\n      supported = false; return;\n    }\n    if (t.isVariableDeclarator(current) && !t.isIdentifier(current.id)) {\n      supported = false; return;\n    }\n    if (scope === null) { supported = false; return; }\n    if (t.isIdentifier(current) && parent !== null && t.isReferenced(current, parent))\n      links.push(lookup(scope, current.name));\n    for (const child of childNodes(current)) visit(child, current, scope);\n  };\n  visit(root, null, null);\n  if (!supported) return null;\n  return createHash(\"sha256\")\n    .update(JSON.stringify([\"babel-ast-scoped-references-v1\", fingerprintJavaScriptAst(node), links]))\n    .digest(\"hex\");\n};\n"
def digest(p): return sha256(p.read_bytes()).hexdigest()
def main(action, rea):
    head = subprocess.check_output(["git","-C",str(rea),"rev-parse","HEAD"],text=True).strip()
    if head != PIN: raise ValueError("upstream control changed")
    original = rea/REL
    if "fingerprintJavaScriptAstParameterRelations" not in original.read_text():
        raise ValueError("prior movement 4 edition was not applied")
    private=Path("runtime/data/rea-scoped-fingerprint").resolve()
    desk=ProcessWorkstation(private/"editions")
    if action == "prepare":
        stage=private/"source"
        if stage.exists(): raise FileExistsError("source edition already preserved")
        (stage/REL).parent.mkdir(parents=True)
        shutil.copyfile(original, stage/REL)
        shutil.copyfile(rea/"LICENSE",stage/"LICENSE")
        control=desk.copy_source(stage,worker_id="rea-scoped-references",version_id="control",source_locator="morluto/rea@"+PIN+"+movement4")
        experiment=desk.branch(worker_id="rea-scoped-references",parent_version="control",version_id="experimental")
        target=Path(experiment["path"])/REL
        before=target.read_text()
        old_import='import { traverseJavaScriptAst } from "./javascriptSemanticTraversal.js";'
        if before.count(old_import)!=1 or "fingerprintJavaScriptAstScopedReferences" in before:
            raise ValueError("source precondition not met")
        target.write_text(before.replace(old_import,
            'import { childNodes, traverseJavaScriptAst } from "./javascriptSemanticTraversal.js";')+ADDITION)
        check=desk.inspect(worker_id="rea-scoped-references",version_id="experimental")
        if check["modified"] != [REL.as_posix()]: raise ValueError("unexpected source edit")
        report=Path("experiments/rea-swallow/results")
        report.mkdir(parents=True,exist_ok=True)
        (report/"scoped-edition.json").write_text(json.dumps({"pinned_upstream":PIN,"parent":"movement4",
            "source":str(REL),"control_sha256":digest(Path(control["path"])/REL),
            "experiment_sha256":digest(target),"status":"PENDING_NATIVE_TESTS"},indent=2)+chr(10))
        print("CREATED_SCOPED_SOURCE_EDITION",check["modified"])
    elif action == "apply":
        control=private/"editions/rea-scoped-references/control"/REL
        candidate=private/"editions/rea-scoped-references/experimental"/REL
        if digest(original)!=digest(control) or digest(candidate)==digest(control):
            raise ValueError("missing control or no source change")
        shutil.copyfile(candidate,original)
        subprocess.run(["git","-C",str(rea),"diff","--check"],check=True)
        print("REAL_REA_SCOPED_SOURCE_APPLIED",REL)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["prepare","apply"])
    p.add_argument("--rea",type=Path,required=True)
    a=p.parse_args()
    main(a.action,a.rea.resolve())
