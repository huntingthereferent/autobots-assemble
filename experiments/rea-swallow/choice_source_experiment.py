"""Move 9: preserve the genuine REA matcher, branch from the passing observation edition, and add selection."""
from pathlib import Path
from hashlib import sha256
import argparse, json, shutil, subprocess
from systems.workspace.workstation import ProcessWorkstation
PIN="f0b9ef34c404c1c65f8167502db972b0bd708403"
REL=Path("src/domain/javascript/javascriptApplicationVersionKeys.ts")
ADDITION="\n\n/**\n * Evidence-based next-observation choice for the experimental version matcher.\n * Candidate observations are supplied by an independent trusted runner.\n * This function does not execute candidate source or predict unmeasured results.\n */\nexport interface ApplicationVersionObservationLedger {\n  readonly ledgerId: string;\n  readonly pair: ApplicationVersionNodePair;\n  readonly left: readonly ApplicationVersionInputObservation[];\n  readonly right: readonly ApplicationVersionInputObservation[];\n}\nexport interface ApplicationVersionObservationSelection {\n  readonly status: \"selected\" | \"no-new-witness\";\n  readonly contextId: string | null;\n  readonly newlySeparatingPairs: number;\n  readonly remainingUndeterminedPairs: number;\n  readonly candidateScores: readonly {\n    readonly contextId: string;\n    readonly newSeparations: number;\n    readonly comparableUnresolvedPairs: number;\n    readonly unavailablePairs: number;\n  }[];\n  readonly limitation: string;\n}\n\n/**\n * Choose from contexts for which external observations already exist.\n * Greedy set-cover step: maximize newly witnessed differences, breaking ties\n * by deterministic Unicode-codepoint context order. Rerun after adding the\n * selected context to alreadyObservedContextIds to follow the new frontier.\n */\nexport const selectNextJavaScriptApplicationObservation = (\n  ledgers: readonly ApplicationVersionObservationLedger[],\n  alreadyObservedContextIds: readonly string[],\n): ApplicationVersionObservationSelection => {\n  const ledgerKeys = new Set<string>();\n  for (const ledger of ledgers) {\n    if (ledger.ledgerId.length === 0 || ledgerKeys.has(ledger.ledgerId))\n      throw new Error(\"Empty or duplicate observation ledger: \" + ledger.ledgerId);\n    ledgerKeys.add(ledger.ledgerId);\n  }\n  const observed = new Set(alreadyObservedContextIds);\n  if (observed.size !== alreadyObservedContextIds.length ||\n      alreadyObservedContextIds.some((id) => id.length === 0))\n    throw new Error(\"Empty or duplicate observed context\");\n\n  const front = ledgers.filter((ledger) =>\n    refineJavaScriptApplicationPairByObservations(\n      ledger.pair,\n      ledger.left.filter((item) => observed.has(item.contextId)),\n      ledger.right.filter((item) => observed.has(item.contextId)),\n    ).result === \"undetermined\",\n  );\n\n  const candidates = [...new Set(ledgers.flatMap((ledger) => [\n    ...ledger.left.map((item) => item.contextId),\n    ...ledger.right.map((item) => item.contextId),\n  ]))]\n    .filter((id) => !observed.has(id))\n    .sort(compareUnicodeCodePoints);\n\n  const scores = candidates.map((contextId) => {\n    let newSeparations = 0;\n    let comparableUnresolvedPairs = 0;\n    let unavailablePairs = 0;\n    for (const ledger of front) {\n      const result = refineJavaScriptApplicationPairByObservations(\n        ledger.pair,\n        ledger.left.filter((item) => item.contextId === contextId),\n        ledger.right.filter((item) => item.contextId === contextId),\n      );\n      if (result.result === \"witnessed-difference\") newSeparations += 1;\n      if (result.agreeingContextIds.length + result.separatingContextIds.length > 0)\n        comparableUnresolvedPairs += 1;\n      else unavailablePairs += 1;\n    }\n    return {contextId, newSeparations, comparableUnresolvedPairs, unavailablePairs};\n  });\n  const best = scores.reduce<(typeof scores)[number] | null>(\n    (winner, row) => winner === null || row.newSeparations > winner.newSeparations\n      ? row : winner,\n    null,\n  );\n  return {\n    status: best !== null && best.newSeparations > 0 ? \"selected\" : \"no-new-witness\",\n    contextId: best !== null && best.newSeparations > 0 ? best.contextId : null,\n    newlySeparatingPairs: best !== null && best.newSeparations > 0\n      ? best.newSeparations : 0,\n    remainingUndeterminedPairs: front.length,\n    candidateScores: scores,\n    limitation: \"Only previously supplied, same-input external observations can be ranked. No untested context is predicted and agreement cannot prove equivalence.\",\n  };\n};\n"
def digest(p):return sha256(p.read_bytes()).hexdigest()
def main(action,rea):
    head=subprocess.check_output(["git","-C",str(rea),"rev-parse","HEAD"],text=True).strip()
    if head!=PIN:raise ValueError("unpinned REA")
    source=rea/REL
    if "refineJavaScriptApplicationPairByObservations" not in source.read_text():
        raise ValueError("Move 8 actual REA edition not applied as parent")
    private=Path("runtime/data/rea-observation-choice").resolve()
    desk=ProcessWorkstation(private/"editions")
    if action=="prepare":
        stage=private/"source"
        if stage.exists():raise FileExistsError("existing control edition")
        (stage/REL).parent.mkdir(parents=True)
        shutil.copyfile(source,stage/REL)
        shutil.copyfile(rea/"LICENSE",stage/"LICENSE")
        control=desk.copy_source(stage,worker_id="rea-observation-choice",
            version_id="control",source_locator="morluto/rea@"+PIN+"+movement8")
        candidate=desk.branch(worker_id="rea-observation-choice",
            parent_version="control",version_id="experimental")
        dest=Path(candidate["path"])/REL
        text=dest.read_text()
        if "selectNextJavaScriptApplicationObservation" in text:
            raise ValueError("candidate already applied")
        dest.write_text(text+ADDITION)
        diff=desk.inspect(worker_id="rea-observation-choice",version_id="experimental")
        if diff["modified"] != [REL.as_posix()]:
            raise ValueError("unexpected modification")
        out=Path("experiments/rea-swallow/results")
        out.mkdir(parents=True,exist_ok=True)
        (out/"choice-edition.json").write_text(json.dumps({
            "upstream":PIN,"source":str(REL),"parent":"movement8",
            "control_sha256":digest(Path(control["path"])/REL),
            "experimental_sha256":digest(dest),
            "source_fingerprint":control["source_fingerprint"],
            "state":"PENDING_NATIVE_VERIFICATION"},indent=2)+chr(10))
        print("VERSIONED_REAL_REA_OBSERVATION_SELECTION",diff["modified"])
    elif action=="apply":
        control=private/"editions/rea-observation-choice/control"/REL
        candidate=private/"editions/rea-observation-choice/experimental"/REL
        if digest(source)!=digest(control) or digest(candidate)==digest(control):
            raise ValueError("original lost or candidate missing")
        shutil.copyfile(candidate,source)
        subprocess.run(["git","-C",str(rea),"diff","--check"],check=True)
        print("APPLIED_REAL_REA_OBSERVATION_SELECTOR",REL)
    else:raise ValueError(action)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["prepare","apply"])
    p.add_argument("--rea",type=Path,required=True)
    a=p.parse_args()
    main(a.action,a.rea.resolve())
