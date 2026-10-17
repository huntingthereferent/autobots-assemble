"""Second source-level REA A/B experiment: invert candidate edges in one pass."""
from pathlib import Path
from hashlib import sha256
import argparse, json, shutil, subprocess
from systems.workspace.workstation import ProcessWorkstation

PIN = "f0b9ef34c404c1c65f8167502db972b0bd708403"
REL = Path("src/domain/javascript/javascriptApplicationVersionKeys.ts")
OLD = "  for (const leftNode of left) {\n    const candidates =\n      leftCandidates.get(leftNode.node_id) ?? new Set<string>();\n    for (const rightNode of right) candidates.add(rightNode.node_id);\n    leftCandidates.set(leftNode.node_id, candidates);\n  }\n  for (const rightNode of right) {\n    const candidates =\n      rightCandidates.get(rightNode.node_id) ?? new Set<string>();\n    for (const leftNode of left) candidates.add(leftNode.node_id);\n    rightCandidates.set(rightNode.node_id, candidates);\n  }"
NEW = "  // Materialize each ambiguity pair once and write the inverse relation with it.\n  const rightEntries = right.map((node) => {\n    const candidates = rightCandidates.get(node.node_id) ?? new Set<string>();\n    rightCandidates.set(node.node_id, candidates);\n    return { id: node.node_id, candidates };\n  });\n  for (const leftNode of left) {\n    const candidates = leftCandidates.get(leftNode.node_id) ?? new Set<string>();\n    for (const rightEntry of rightEntries) {\n      candidates.add(rightEntry.id);\n      rightEntry.candidates.add(leftNode.node_id);\n    }\n    leftCandidates.set(leftNode.node_id, candidates);\n  }"
def sha(path): return sha256(path.read_bytes()).hexdigest()
def main(action, rea):
    actual = subprocess.check_output(["git","-C",str(rea),"rev-parse","HEAD"], text=True).strip()
    if actual != PIN: raise ValueError("upstream changed: "+actual)
    private = Path("runtime/data/rea-swallow-match").resolve()
    desk = ProcessWorkstation(private / "editions")
    if action == "prepare":
        staging = private / "selected-source"
        if staging.exists(): raise FileExistsError("cannot silently overwrite control")
        (staging/REL).parent.mkdir(parents=True)
        shutil.copyfile(rea/REL,staging/REL)
        shutil.copyfile(rea/"LICENSE",staging/"LICENSE")
        control=desk.copy_source(staging,worker_id="rea-version-matching",
            version_id="control",source_locator="morluto/rea@"+PIN)
        experiment=desk.branch(worker_id="rea-version-matching",
            parent_version="control",version_id="experimental")
        target=Path(experiment["path"])/REL
        source=target.read_text(encoding="utf-8")
        if source.count(OLD)!=1: raise ValueError("upstream implementation mismatch")
        target.write_text(source.replace(OLD,NEW),encoding="utf-8")
        report=desk.inspect(worker_id="rea-version-matching",version_id="experimental")
        if report["modified"]!=[REL.as_posix()]: raise ValueError("unexpected source change")
        receipt={"upstream":PIN,"source":REL.as_posix(),
            "source_sha256_before":sha(Path(control["path"])/REL),
            "source_sha256_after":sha(target),
            "parent":experiment["parent_version"],
            "source_fingerprint":control["source_fingerprint"],
            "status":"PENDING_TEST_EXECUTION"}
        out=Path("experiments/rea-swallow/results")
        out.mkdir(parents=True,exist_ok=True)
        (out/"matching-edition.json").write_text(json.dumps(receipt,indent=2)+"
")
        print(json.dumps(receipt))
    elif action == "apply":
        source=rea/REL
        control=private/"editions/rea-version-matching/control"/REL
        experiment=private/"editions/rea-version-matching/experimental"/REL
        if sha(source)!=sha(control):raise ValueError("upstream control modified")
        if sha(control)==sha(experiment):raise ValueError("no actual rewrite")
        shutil.copyfile(experiment,source)
        subprocess.run(["git","-C",str(rea),"diff","--check"],check=True)
        print("MODIFIED_REAL_REA_MATCHER",REL)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["prepare","apply"])
    p.add_argument("--rea",type=Path,required=True)
    x=p.parse_args()
    main(x.action,x.rea.resolve())
