"""REA real-source source-edition experiment; no reconstructed simulator."""
from pathlib import Path
from hashlib import sha256
import argparse, json, shutil, subprocess
from systems.workspace.workstation import ProcessWorkstation

PIN = "f0b9ef34c404c1c65f8167502db972b0bd708403"
REL = Path("src/domain/javascript/javascriptFeatureTraversal.ts")
OLD = "  for (let offset = 0; offset < queue.length; offset += 1) {\n    const current = queue[offset];\n    if (current === undefined) continue;\n"
NEW = "  for (const current of queue) {\n"
def sha(path): return sha256(path.read_bytes()).hexdigest()
def main(action, root, work):
    head = subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"], text=True).strip()
    if head != PIN: raise ValueError("source SHA mismatch: "+head)
    desk = ProcessWorkstation(work / "editions")
    if action == "prepare":
        staging = work / "selected-source"
        if staging.exists(): raise ValueError("no implicit repeat")
        (staging / REL).parent.mkdir(parents=True)
        shutil.copyfile(root / REL, staging / REL)
        shutil.copyfile(root / "LICENSE", staging / "LICENSE")
        control = desk.copy_source(staging, worker_id="rea-traversal",
            version_id="control", source_locator="morluto/rea@"+PIN)
        experimental = desk.branch(worker_id="rea-traversal",
            parent_version="control", version_id="experimental")
        target = Path(experimental["path"]) / REL
        before = target.read_text()
        if before.count(OLD) != 1: raise ValueError("unexpected original implementation")
        target.write_text(before.replace(OLD, NEW))
        inspection = desk.inspect(worker_id="rea-traversal", version_id="experimental")
        if inspection["modified"] != [REL.as_posix()]: raise ValueError("unexpected source changes")
        report = {"original":PIN,"source":REL.as_posix(),"control":sha(Path(control["path"])/REL),
           "candidate":sha(target),"parent":experimental["parent_version"],
           "fingerprint":control["source_fingerprint"],"status":"UNTESTED"}
        out = Path("experiments/rea-swallow/results")
        out.mkdir(parents=True,exist_ok=True)
        (out/"edition.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps(report))
    else:
        original = root / REL
        left = work / "editions/rea-traversal/control" / REL
        right = work / "editions/rea-traversal/experimental" / REL
        if sha(original) != sha(left) or sha(right) == sha(left):
            raise ValueError("original not preserved or no source transformation")
        shutil.copyfile(right, original)
        subprocess.run(["git","-C",str(root),"diff","--check"],check=True)
        print("MODIFIED_REAL_REA_SOURCE",REL)
if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["prepare","apply"])
    p.add_argument("--rea",type=Path,required=True)
    a=p.parse_args()
    main(a.action,a.rea.resolve(),Path("runtime/data/rea-swallow").resolve())
