"""Move 10: branch genuine REA source from verified Movement 8, no fake simulator."""
from pathlib import Path
from hashlib import sha256
import argparse, json, shutil, subprocess
from systems.workspace.workstation import ProcessWorkstation
PIN="f0b9ef34c404c1c65f8167502db972b0bd708403"
REL=Path("src/domain/javascript/javascriptApplicationVersionKeys.ts")
ADDITION="\n\n/**\n * Experimental next-input construction for a strictly delimited family of\n * JavaScript module sources. It analyzes source syntax but never runs code.\n * Only two-parameter functions returning four *direct*, computed vector\n * accesses at their matching positions are admitted. No generated input\n * represents a claim of observational or semantic equivalence.\n */\nexport interface ApplicationVersionConstructedObservation {\n  readonly status: \"proposed\" | \"unsupported-or-exhausted\";\n  readonly contextId: string | null;\n  readonly inputDigest: string | null;\n  readonly inputVectors: readonly [readonly number[], readonly number[]] | null;\n  readonly differentReferencePosition: number | null;\n  readonly method: \"source-reference-isolation-v1\";\n  readonly limitation: string;\n}\n\nconst extractFourVectorReferences = (source: string): readonly (0 | 1)[] | null => {\n  let program: ReturnType<typeof parseJavaScriptSource>;\n  try { program = parseJavaScriptSource(source, {sourceType: \"script\"}); }\n  catch { return null; }\n  if (program.program.body.length !== 1) return null;\n  const fn = program.program.body[0];\n  if (!t.isFunctionDeclaration(fn) || fn.id?.name !== \"pick\" ||\n      fn.params.length !== 2 || !fn.params.every(t.isIdentifier) ||\n      fn.body.body.length !== 1) return null;\n  const p0 = fn.params[0], p1 = fn.params[1];\n  if (!t.isIdentifier(p0) || !t.isIdentifier(p1) || p0.name === p1.name) return null;\n  const statement = fn.body.body[0];\n  if (!t.isReturnStatement(statement) || !t.isArrayExpression(statement.argument) ||\n      statement.argument.elements.length !== 4) return null;\n  const references: (0 | 1)[] = [];\n  for (let position = 0; position < 4; position += 1) {\n    const element = statement.argument.elements[position];\n    if (!t.isMemberExpression(element) || !element.computed ||\n        !t.isIdentifier(element.object) || !t.isNumericLiteral(element.property) ||\n        element.property.value !== position) return null;\n    if (element.object.name === p0.name) references.push(0);\n    else if (element.object.name === p1.name) references.push(1);\n    else return null;\n  }\n  return references;\n};\n\n/**\n * Construct an input from an *unresolved* REA source pair. Never executes it.\n * Attribution is checked against both REA source-digest observations.\n * The independent caller must execute the proposal and bring back separate\n * observations for BOTH sides before any difference can be reported.\n */\nexport const constructNextJavaScriptApplicationObservation = (\n  pair: ApplicationVersionNodePair,\n  leftSource: string,\n  rightSource: string,\n  alreadySeenLeft: readonly ApplicationVersionInputObservation[],\n  alreadySeenRight: readonly ApplicationVersionInputObservation[],\n): ApplicationVersionConstructedObservation => {\n  const limitation = \"Bounded four-access source family only; a constructed input is not a verified difference, and untested or agreeing inputs cannot prove equivalence.\";\n  const unsupported = (): ApplicationVersionConstructedObservation => ({\n    status: \"unsupported-or-exhausted\", contextId: null, inputDigest: null,\n    inputVectors: null, differentReferencePosition: null,\n    method: \"source-reference-isolation-v1\", limitation,\n  });\n  if (pair.left.kind !== \"javascript-module\" ||\n      pair.right.kind !== \"javascript-module\") return unsupported();\n  const sourceDigest = (s: string) =>\n    createHash(\"sha256\").update(s).digest(\"hex\");\n  if (uniqueStringProperty(pair.left, \"source_sha256\") !== sourceDigest(leftSource) ||\n      uniqueStringProperty(pair.right, \"source_sha256\") !== sourceDigest(rightSource))\n    return unsupported();\n  if (refineJavaScriptApplicationPairByObservations(\n    pair, alreadySeenLeft, alreadySeenRight,\n  ).result === \"witnessed-difference\") return unsupported();\n  const l = extractFourVectorReferences(leftSource);\n  const r = extractFourVectorReferences(rightSource);\n  if (l === null || r === null) return unsupported();\n  const position = l.findIndex((v, i) => v !== r[i]);\n  if (position < 0) return unsupported();\n  const left = [0, 0, 0, 0];\n  const right = [0, 0, 0, 0];\n  right[position] = 7;\n  const vectors = [left, right] as const;\n  const inputDigest = sourceDigest(JSON.stringify(vectors));\n  const contextId = \"constructed-reference-\" + position + \"-\" + inputDigest.slice(0, 16);\n  if ([...alreadySeenLeft, ...alreadySeenRight].some((item) =>\n      item.contextId === contextId)) return unsupported();\n  return {\n    status: \"proposed\", contextId, inputDigest, inputVectors: vectors,\n    differentReferencePosition: position,\n    method: \"source-reference-isolation-v1\", limitation,\n  };\n};\n"
def digest(p):return sha256(p.read_bytes()).hexdigest()
def run(action,rea):
    head=subprocess.check_output(["git","-C",str(rea),"rev-parse","HEAD"],text=True).strip()
    if head!=PIN:raise ValueError("pinned upstream mismatch")
    source=rea/REL
    if "refineJavaScriptApplicationPairByObservations" not in source.read_text():
        raise ValueError("Movement 8 must be preserved as parent")
    private=Path("runtime/data/rea-construct-observation").resolve()
    desk=ProcessWorkstation(private/"editions")
    if action=="prepare":
        stage=private/"selected-source"
        if stage.exists():raise FileExistsError("cannot overwrite control")
        (stage/REL).parent.mkdir(parents=True)
        shutil.copyfile(source,stage/REL)
        shutil.copyfile(rea/"LICENSE",stage/"LICENSE")
        control=desk.copy_source(stage,worker_id="rea-construct-observation",
          version_id="control",source_locator="morluto/rea@"+PIN+"+movement8")
        experiment=desk.branch(worker_id="rea-construct-observation",
          parent_version="control",version_id="experimental")
        candidate=Path(experiment["path"])/REL
        old=candidate.read_text()
        if "constructNextJavaScriptApplicationObservation" in old:raise ValueError("already applied")
        anchor='import { canonicalJson } from "../comparisonSemantics.js";'
        if old.count(anchor)!=1:raise ValueError("unexpected imports")
        imports='import {createHash} from "node:crypto";\nimport {parse as parseJavaScriptSource} from "@babel/parser";\nimport * as t from "@babel/types";\n'
        candidate.write_text(old.replace(anchor,imports+anchor)+ADDITION)
        check=desk.inspect(worker_id="rea-construct-observation",version_id="experimental")
        if check["modified"]!=[REL.as_posix()]:raise ValueError("unexpected source mutation")
        out=Path("experiments/rea-swallow/results")
        out.mkdir(parents=True,exist_ok=True)
        (out/"construct-edition.json").write_text(json.dumps({
            "upstream":PIN,"source":str(REL),"parent":"movement8",
            "control_sha256":digest(Path(control["path"])/REL),
            "experimental_sha256":digest(candidate),
            "source_fingerprint":control["source_fingerprint"],
            "status":"PENDING_NATIVE_RUN"},indent=2)+chr(10))
        print("REAL_REA_CONSTRUCTION_EDITION",check["modified"])
    elif action=="apply":
        old=private/"editions/rea-construct-observation/control"/REL
        new=private/"editions/rea-construct-observation/experimental"/REL
        if digest(old)!=digest(source) or digest(new)==digest(old):
            raise ValueError("source control changed or no transformation")
        shutil.copyfile(new,source)
        subprocess.run(["git","-C",str(rea),"diff","--check"],check=True)
        print("REAL_REA_NEW_INPUT_OPERATOR_APPLIED",REL)
    else:raise ValueError(action)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["prepare","apply"])
    p.add_argument("--rea",type=Path,required=True)
    a=p.parse_args()
    run(a.action,a.rea.resolve())
