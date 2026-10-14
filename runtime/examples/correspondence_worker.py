"""Explicit, local finite-workstation job demonstration (not a background agent)."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.process_handoff import CorrespondenceWorkBridge, WORKER_ID

ROOT = Path(__file__).resolve().parents[2]
FINITE = ROOT / "work" / "arc_like_maze" / "chatbot"
INPUTS = {"old_phi": [0,0,1], "new_phi": [0,0,0],
          "candidate_words": [["ABAA","ABBABA"], ["ABAA","AAABB","BAAAB"]],
          "required_state": [0,0,0], "required_action": "B"}


def main():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        selected = root / "selected-source"
        selected.mkdir()
        for name in ("finite_goal_priority.py", "finite_required_edge_guard.py"):
            shutil.copyfile(FINITE / name, selected / name)
        workstation = ProcessWorkstation(root / "workstation")
        workstation.copy_source(selected, worker_id=WORKER_ID, version_id="local-demo")
        runtime = HandoffRuntime(event_store=RuntimeJournal(root / "runtime.jsonl"))
        bridge = CorrespondenceWorkBridge(runtime=runtime, workstation=workstation)
        handoff = bridge.admit(version_id="local-demo", inputs=INPUTS,
                               from_actor="local-demo", lane_id="finite-research")
        print("before:", bridge.inspect(handoff.handoff_id))
        result = bridge.execute(handoff.handoff_id, allow_local_execution=True)
        print("after:", bridge.inspect(handoff.handoff_id))
        print("native reverify:", bridge.reverify(handoff.handoff_id))
        print("child process:", result.output["child_pid"])
        resumed = CorrespondenceWorkBridge(
            runtime=HandoffRuntime(event_store=RuntimeJournal(root / "runtime.jsonl")),
            workstation=workstation)
        print("restarted native reverify:", resumed.reverify(handoff.handoff_id))


if __name__ == "__main__":
    main()
