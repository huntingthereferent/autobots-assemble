"""Convert a cancelled GitHub workflow_run event into a source-bound audit receipt."""
import json
import pathlib
import sys

from audit_to_action import process


def cancellation_receipt(event):
    run = event.get("workflow_run") or {}
    if event.get("action") != "completed" or run.get("conclusion") != "cancelled":
        raise ValueError("not a completed cancelled workflow_run event")
    run_id = run.get("id")
    if not isinstance(run_id, int) or run_id <= 0:
        raise ValueError("missing run id")
    url = run.get("html_url", "")
    if not isinstance(url, str) or not url.startswith("https://github.com/"):
        raise ValueError("missing source URL")
    name = run.get("name") or "unnamed workflow"
    receipt = process({"findings": [{
        "id": f"workflow-cancel-{run_id}",
        "lane": "CI / " + name,
        "kind": "candidate",
        "observation": f"GitHub workflow run {run_id} completed with cancelled conclusion; reason not established",
        "source": url,
        "proposed_action": "Inspect cancellation cause, supersession, queue contention, and impact on source-owned evidence; retain if expected",
        "verification": "Compare event run, head SHA, run attempt, workflow concurrency and related newer runs",
        "workflow_run": {
            "id": run_id, "name": name, "head_sha": run.get("head_sha"),
            "run_attempt": run.get("run_attempt"), "event": run.get("event"),
            "created_at": run.get("created_at"), "updated_at": run.get("updated_at"),
        },
    }]})
    receipt["trigger"] = "workflow_run.completed.cancelled"
    return receipt


def main(argv):
    if len(argv) != 3:
        raise SystemExit("usage: audit_cancelled_run.py EVENT.json OUTPUT.json")
    event = json.loads(pathlib.Path(argv[1]).read_text(encoding="utf-8"))
    receipt = cancellation_receipt(event)
    pathlib.Path(argv[2]).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv)
