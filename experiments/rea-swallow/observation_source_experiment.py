"""Add an experimental evidence-refinement function to REAL REA matching source.

The unmodified original and the experimental edition are kept separately in
the existing ProcessWorkstation. Evidence comes from a trusted finite test
harness, never from arbitrary program execution inside the REA library.
"""
from pathlib import Path
from hashlib import sha256
import argparse, json, shutil, subprocess
from systems.workspace.workstation import ProcessWorkstation
PIN="f0b9ef34c404c1c65f8167502db972b0bd708403"
REL=Path("src/domain/javascript/javascriptApplicationVersionKeys.ts")
ADDITION="\n\n/**\n * A/B experimental observation refinement of an existing REA version pair.\n * A shared structural key proposes correspondence; identical, admitted\n * observations never establish general equivalence. A differing observation\n * on the same explicit input contract is a concrete separating witness.\n * Outcomes must come from an independent, trusted capture; this routine\n * NEVER executes untrusted program bytes.\n */\nexport interface ApplicationVersionInputObservation {\n  readonly contextId: string;\n  readonly inputDigest: string;\n  readonly result:\n    | {readonly status: \"returned\"; readonly canonicalValue: string}\n    | {readonly status: \"threw\"; readonly errorName: string; readonly message: string}\n    | {readonly status: \"unknown\"; readonly reason: string};\n}\n\nexport interface ApplicationVersionObservationRefinement {\n  readonly leftNodeId: string;\n  readonly rightNodeId: string;\n  readonly originalBasis: ApplicationVersionNodePair[\"basis\"];\n  readonly originalConfidence: ApplicationVersionNodePair[\"confidence\"];\n  readonly result: \"witnessed-difference\" | \"undetermined\";\n  readonly separatingContextIds: readonly string[];\n  readonly agreeingContextIds: readonly string[];\n  readonly unresolvedContextIds: readonly string[];\n  readonly incomparableContextIds: readonly string[];\n  readonly limitation: string;\n}\n\nexport const refineJavaScriptApplicationPairByObservations = (\n  pair: ApplicationVersionNodePair,\n  left: readonly ApplicationVersionInputObservation[],\n  right: readonly ApplicationVersionInputObservation[],\n): ApplicationVersionObservationRefinement => {\n  const index = (observations: readonly ApplicationVersionInputObservation[]) => {\n    const indexed = new Map<string, ApplicationVersionInputObservation>();\n    for (const item of observations) {\n      if (\n        item.contextId.length === 0 ||\n        item.inputDigest.length === 0 ||\n        indexed.has(item.contextId)\n      ) throw new Error(\"Invalid or duplicate observation context: \" + item.contextId);\n      indexed.set(item.contextId, item);\n    }\n    return indexed;\n  };\n  const l = index(left), r = index(right);\n  const contexts = [...new Set([...l.keys(), ...r.keys()])]\n    .sort(compareUnicodeCodePoints);\n  const separating: string[] = [];\n  const agreeing: string[] = [];\n  const unresolved: string[] = [];\n  const incomparable: string[] = [];\n  for (const id of contexts) {\n    const a = l.get(id), b = r.get(id);\n    if (a === undefined || b === undefined || a.inputDigest !== b.inputDigest) {\n      incomparable.push(id);\n      continue;\n    }\n    if (a.result.status === \"unknown\" || b.result.status === \"unknown\") {\n      unresolved.push(id);\n      continue;\n    }\n    if (canonicalJson(a.result) !== canonicalJson(b.result)) separating.push(id);\n    else agreeing.push(id);\n  }\n  return {\n    leftNodeId: pair.left.node_id,\n    rightNodeId: pair.right.node_id,\n    originalBasis: pair.basis,\n    originalConfidence: pair.confidence,\n    result: separating.length > 0 ? \"witnessed-difference\" : \"undetermined\",\n    separatingContextIds: separating,\n    agreeingContextIds: agreeing,\n    unresolvedContextIds: unresolved,\n    incomparableContextIds: incomparable,\n    limitation: \"A finite set of external observations can witness a difference but cannot establish semantic equivalence.\",\n  };\n};\n"
def digest(path): return sha256(path.read_bytes()).hexdigest()
def run(action,rea):
    head=subprocess.check_output(["git","-C",str(rea),"rev-parse","HEAD"],text=True).strip()
    if head!=PIN: raise ValueError("upstream source version unexpectedly changed")
    private=Path("runtime/data/rea-observation-refinement").resolve()
    desk=ProcessWorkstation(private/"editions")
    if action=="prepare":
        src=private/"selected-source"
        if src.exists():raise FileExistsError("control already exists; no overwrite")
        (src/REL).parent.mkdir(parents=True)
        shutil.copyfile(rea/REL,src/REL)
        shutil.copyfile(rea/"LICENSE",src/"LICENSE")
        control=desk.copy_source(src,worker_id="rea-observation-refinement",version_id="control",source_locator="morluto/rea@"+PIN)
        experimental=desk.branch(worker_id="rea-observation-refinement",parent_version="control",version_id="experimental")
        source=Path(experimental["path"])/REL
        old=source.read_text()
        if "refineJavaScriptApplicationPairByObservations" in old:raise ValueError("already modified")
        source.write_text(old+ADDITION)
        inspected=desk.inspect(worker_id="rea-observation-refinement",version_id="experimental")
        if inspected["modified"] != [REL.as_posix()]:raise ValueError("source boundary violated")
        output=Path("experiments/rea-swallow/results")
        output.mkdir(parents=True,exist_ok=True)
        (output/"observation-edition.json").write_text(json.dumps({
            "upstream_sha":PIN,"source":str(REL),"control_sha256":digest(Path(control["path"])/REL),
            "candidate_sha256":digest(source),"source_fingerprint":control["source_fingerprint"],
            "status":"PENDING_NATIVE_CHECKS"},indent=2)+chr(10))
        print("SOURCE_EDITION_OBSERVATION_CREATED",inspected["modified"])
    elif action=="apply":
        prior=private/"editions/rea-observation-refinement/control"/REL
        transformed=private/"editions/rea-observation-refinement/experimental"/REL
        if digest(rea/REL)!=digest(prior) or digest(prior)==digest(transformed):
            raise ValueError("missing stable control or source transformation")
        shutil.copyfile(transformed,rea/REL)
        subprocess.run(["git","-C",str(rea),"diff","--check"],check=True)
        print("REAL_REA_MATCH_SOURCE_REFINED",REL)
    else:raise ValueError(action)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["prepare","apply"])
    p.add_argument("--rea",type=Path,required=True)
    a=p.parse_args()
    run(a.action,a.rea.resolve())
