"""Movement 11: source-preserved integration of verified REA choice and construction.

This runner operates only inside CI's pinned REA copy and preexisting
ProcessWorkstation; it never modifies the original upstream checkout on GitHub.
"""
from pathlib import Path
from hashlib import sha256
import argparse, json, shutil, subprocess
from systems.workspace.workstation import ProcessWorkstation
PIN="f0b9ef34c404c1c65f8167502db972b0bd708403"
REL=Path("src/domain/javascript/javascriptApplicationVersionKeys.ts")
ADDITION="\n\n/**\n * REA experimental event-driven relationship advance. Merges the separately\n * verified observation choice and source-derived test construction operations.\n * Not wired into the shipped application pipeline: an independent runner must\n * capture both programs' results and return them as observations.\n */\nexport interface ApplicationVersionInvestigationAdvance {\n  readonly status:\n    | \"request-independent-capture\"\n    | \"awaiting-independent-capture\"\n    | \"blocked-evidence\"\n    | \"witnessed-difference\"\n    | \"undetermined\";\n  readonly request: ApplicationVersionConstructedObservation | null;\n  readonly acceptedContextIds: readonly string[];\n  readonly selectedContextId: string | null;\n  readonly reason: string;\n}\n\nexport const advanceJavaScriptApplicationInvestigation = (\n  pair: ApplicationVersionNodePair,\n  leftSource: string,\n  rightSource: string,\n  left: readonly ApplicationVersionInputObservation[],\n  right: readonly ApplicationVersionInputObservation[],\n  acceptedContextIds: readonly string[],\n  pending: ApplicationVersionConstructedObservation | null,\n): ApplicationVersionInvestigationAdvance => {\n  if (new Set(acceptedContextIds).size !== acceptedContextIds.length ||\n      acceptedContextIds.some((id) => id.length === 0))\n    throw new Error(\"Invalid or duplicated accepted context\");\n  // Reuse REA's existing observation verifier to enforce unique context IDs.\n  refineJavaScriptApplicationPairByObservations(pair, left, right);\n\n  const finish = (\n    status: ApplicationVersionInvestigationAdvance[\"status\"],\n    reason: string,\n    request: ApplicationVersionConstructedObservation | null = null,\n    selectedContextId: string | null = null,\n  ): ApplicationVersionInvestigationAdvance => ({\n    status, request,\n    acceptedContextIds: selectedContextId === null\n      ? [...acceptedContextIds]\n      : [...acceptedContextIds, selectedContextId],\n    selectedContextId, reason,\n  });\n\n  const acceptedLeft = left.filter((item) => acceptedContextIds.includes(item.contextId));\n  const acceptedRight = right.filter((item) => acceptedContextIds.includes(item.contextId));\n  const alreadyWitnessed = refineJavaScriptApplicationPairByObservations(\n    pair, acceptedLeft, acceptedRight,\n  );\n  if (alreadyWitnessed.result === \"witnessed-difference\")\n    return finish(\"witnessed-difference\", \"Previously accepted separating evidence is retained\");\n\n  const choose = (\n    candidates: readonly string[],\n  ): string | null => {\n    const available = new Set([...acceptedContextIds, ...candidates]);\n    const selection = selectNextJavaScriptApplicationObservation([{\n      ledgerId: \"current-matched-pair\",\n      pair,\n      left: left.filter((item) => available.has(item.contextId)),\n      right: right.filter((item) => available.has(item.contextId)),\n    }], acceptedContextIds);\n    return selection.status === \"selected\" ? selection.contextId : null;\n  };\n  const acceptWitness = (id: string): ApplicationVersionInvestigationAdvance => {\n    const chosen = [...acceptedContextIds, id];\n    const refined = refineJavaScriptApplicationPairByObservations(\n      pair,\n      left.filter((item) => chosen.includes(item.contextId)),\n      right.filter((item) => chosen.includes(item.contextId)),\n    );\n    if (refined.result !== \"witnessed-difference\")\n      return finish(\"blocked-evidence\", \"Selected evidence failed independent refinement\");\n    return finish(\"witnessed-difference\", \"Selected captured observation proves a difference on one shared input\", null, id);\n  };\n\n  if (pending !== null) {\n    // Validate the pending event against the source, not the caller's label.\n    const regenerated = constructNextJavaScriptApplicationObservation(\n      pair, leftSource, rightSource, [], [],\n    );\n    if (\n      pending.status !== \"proposed\" ||\n      regenerated.status !== \"proposed\" ||\n      pending.contextId !== regenerated.contextId ||\n      pending.inputDigest !== regenerated.inputDigest ||\n      JSON.stringify(pending.inputVectors) !== JSON.stringify(regenerated.inputVectors)\n    ) throw new Error(\"Pending observation is not source-derived\");\n    const a = left.find((item) => item.contextId === pending.contextId);\n    const b = right.find((item) => item.contextId === pending.contextId);\n    if ((a !== undefined && a.inputDigest !== pending.inputDigest) ||\n        (b !== undefined && b.inputDigest !== pending.inputDigest))\n      return finish(\"blocked-evidence\", \"Pending observation input digest disagrees with original proposal\", pending);\n    if (a === undefined || b === undefined ||\n        a.result.status === \"unknown\" || b.result.status === \"unknown\")\n      return finish(\"awaiting-independent-capture\", \"Both matching-context results are required\", pending);\n    const picked = choose([pending.contextId!]);\n    if (picked !== null && picked === pending.contextId) return acceptWitness(picked);\n    return finish(\"undetermined\", \"Completed observations did not witness a difference; no equivalence is inferred\");\n  }\n\n  // Prefer new *already captured* observations before requesting a new input.\n  const captured = [...new Set([...left.map((i) => i.contextId), ...right.map((i) => i.contextId)])]\n    .filter((id) => !acceptedContextIds.includes(id));\n  const selected = choose(captured);\n  if (selected !== null) return acceptWitness(selected);\n\n  const newInput = constructNextJavaScriptApplicationObservation(\n    pair, leftSource, rightSource, left, right,\n  );\n  if (newInput.status === \"proposed\")\n    return finish(\"request-independent-capture\", \"Constructed a previously unobserved input from source references\", newInput);\n  return finish(\"undetermined\", \"No justified new input; retain unresolved relationship\");\n};\n"
def digest(p):return sha256(p.read_bytes()).hexdigest()
def main(action,rea):
    head=subprocess.check_output(["git","-C",str(rea),"rev-parse","HEAD"],text=True).strip()
    if head!=PIN:raise ValueError("unpinned upstream REA")
    source=rea/REL
    current=source.read_text()
    for symbol in ("refineJavaScriptApplicationPairByObservations",
                   "selectNextJavaScriptApplicationObservation",
                   "constructNextJavaScriptApplicationObservation"):
        if symbol not in current:raise ValueError("missing verified source operation "+symbol)
    private=Path("runtime/data/rea-investigation-advance").resolve()
    desk=ProcessWorkstation(private/"editions")
    if action=="prepare":
        staged=private/"source"
        if staged.exists():raise FileExistsError("control edition already exists")
        (staged/REL).parent.mkdir(parents=True)
        shutil.copyfile(source,staged/REL)
        shutil.copyfile(rea/"LICENSE",staged/"LICENSE")
        control=desk.copy_source(staged,worker_id="rea-investigation-advance",
            version_id="control",source_locator="morluto/rea@"+PIN+"+movement8+9+10")
        candidate=desk.branch(worker_id="rea-investigation-advance",
            parent_version="control",version_id="experimental")
        target=Path(candidate["path"])/REL
        if "advanceJavaScriptApplicationInvestigation" in target.read_text():
            raise ValueError("advance operation already exists")
        target.write_text(target.read_text()+ADDITION)
        changes=desk.inspect(worker_id="rea-investigation-advance",version_id="experimental")
        if changes["modified"]!=[REL.as_posix()]:
            raise ValueError("experiment changed an unexpected source file")
        output=Path("experiments/rea-swallow/results")
        output.mkdir(parents=True,exist_ok=True)
        (output/"advance-edition.json").write_text(json.dumps({
            "upstream":PIN,"source":str(REL),"parent":"observed-movement-8+9+10",
            "control_sha256":digest(Path(control["path"])/REL),
            "experimental_sha256":digest(target),
            "source_fingerprint":control["source_fingerprint"],
            "state":"PENDING_NATIVE_TESTS"},indent=2)+chr(10))
        print("REAL_REA_ADVANCE_EDITION_CREATED",changes["modified"])
    elif action=="apply":
        control=private/"editions/rea-investigation-advance/control"/REL
        candidate=private/"editions/rea-investigation-advance/experimental"/REL
        if digest(source)!=digest(control) or digest(candidate)==digest(control):
            raise ValueError("control changed or no actual source modification")
        shutil.copyfile(candidate,source)
        subprocess.run(["git","-C",str(rea),"diff","--check"],check=True)
        print("REAL_REA_INVESTIGATION_SOURCE_APPLIED",REL)
    else:raise ValueError(action)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["prepare","apply"])
    parser.add_argument("--rea",required=True,type=Path)
    args=parser.parse_args()
    main(args.action,args.rea.resolve())
