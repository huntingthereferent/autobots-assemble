"""ChatGPT-first audit gate into the existing Tracework HandoffRuntime.

Entry: audited current code + visual provenance -> external comparison ->
witnessed A/B decision -> an implementation handoff. No source-only admission.
This is a validation/transport gate, not the A/B mathematical definition.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from subprocess import run
import json
import re

from .engine import HandoffRuntime
from .handoff import Handoff
from .journal import RuntimeJournal, handoff_to_dict

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATHS = (
    "AB_CONTRACT.md",
    "TRACEWORK.md",
    "runtime/engine.py",
    "runtime/journal.py",
    "runtime/handoff.py",
    "runtime/agent_lineage.py",
    "runtime/agent_bridge.py",
    "runtime/observed_evaluator.py",
    "runtime/orchestrator.py",
    "runtime/service.py",
    "runtime/external_feed.py",
    "runtime/http_server.py",
    "runtime/http/index.html",
    "runtime/http/app.js",
    "runtime/http/styles.css",
    "runtime/http/monitor.html",
    "runtime/http/monitor.js",
    "design/visual-provenance/README.md",
    "design/visual-provenance/WEB_SURFACE_CONTRACT.md",
    "design/visual-provenance/registry.json",
    "runtime/http/visual-provenance.json",
    "design/visual-provenance/reports/2026-10-08-frontpage-neutral-audit.md",
    "network/tests/test_agent_lineage.py",
    "network/tests/test_external_live_feed.py",
    ".github/workflows/daily-source-handoff.yml",
)
VISUAL_PREFIXES = ("design/visual-provenance/", "runtime/http/visual-provenance")
SAFE = re.compile(r"^[A-Za-z0-9_.\-/]+$")


class GateWall(ValueError):
    pass


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def capture(root: Path) -> dict:
    """Read the real repository and supplied comparison criteria before ChatGPT."""
    root = root.resolve()
    config = json.loads((root / "runtime/audit_sources.json").read_text(encoding="utf-8"))
    refs = {}
    for relative in AUDIT_PATHS:
        path = root / relative
        if path.is_file():
            raw = path.read_bytes()
            refs[relative] = {
                "sha256": digest(raw),
                "size": len(raw),
                "content_excerpt": raw.decode("utf-8", errors="replace")[:12000],
            }
    if not any(k in refs for k in ("design/visual-provenance/registry.json",)):
        raise GateWall("visual provenance registry missing")
    result = run(["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
                 text=True, capture_output=True, check=False)
    revision = result.stdout.strip() if result.returncode == 0 else "UNKNOWN"
    status = run(["git", "-C", str(root), "status", "--porcelain"],
                 text=True, capture_output=True, check=False)
    return {
        "capture_kind": "tracework-current-source-and-visual-provenance",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "revision": revision,
        "working_tree_status": status.stdout.splitlines() if status.returncode == 0 else ["UNKNOWN"],
        "files": refs,
        "source_preferences": config,
        "visual_runtime": {
            "rendered_observation": "UNKNOWN",
            "reason": "Source scan alone cannot claim a currently rendered or interacted-with page.",
            "prior_report": "design/visual-provenance/reports/2026-10-08-frontpage-neutral-audit.md",
        },
    }


def nonempty(value, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GateWall(f"missing {name}")
    return value.strip()


def validate(root: Path, packet: dict, audit: dict) -> None:
    """Fail closed on invented source witnesses, visual claims and absent A/B."""
    if audit.get("entry_gate") != "chatgpt_tracework_audit":
        raise GateWall("ChatGPT-first entry gate missing")
    if audit.get("snapshot_revision") != packet["revision"]:
        raise GateWall("audit used another code revision")
    local = audit.get("local_witnesses")
    if not isinstance(local, list) or not local:
        raise GateWall("no local code witnesses")
    for item in local:
        path = nonempty(item.get("path"), "local witness path")
        sha = nonempty(item.get("sha256"), "local witness sha256")
        nonempty(item.get("observation"), "local observation")
        if not SAFE.fullmatch(path) or path not in packet["files"]:
            raise GateWall("unrecognized local witness path")
        if sha != packet["files"][path]["sha256"]:
            raise GateWall(f"stale or invented local witness {path}")
        if digest((root / path).read_bytes()) != sha:
            raise GateWall(f"source changed since snapshot: {path}")
    visual = audit.get("visual_provenance")
    if not isinstance(visual, dict):
        raise GateWall("visual provenance audit missing")
    vw = visual.get("witness_paths")
    if not isinstance(vw, list) or not vw or not any(
            str(x).startswith(VISUAL_PREFIXES) for x in vw):
        raise GateWall("visual binding/template witnesses required")
    for path in vw:
        if path not in packet["files"]:
            raise GateWall("visual provenance witness not in code snapshot")
        if not any(x["path"] == path for x in local):
            raise GateWall("visual provenance must be included in audited local witnesses")
    render_state = visual.get("rendered_state")
    if render_state not in {"OBSERVED", "UNKNOWN"}:
        raise GateWall("must distinguish rendered observation from UNKNOWN")
    if render_state == "OBSERVED":
        # A screenshot/trace cannot be verified from a text-only packet.
        raise GateWall("rendered OBSERVED requires independently captured visual artifact; not available in this gate")
    nonempty(visual.get("finding"), "visual provenance finding")
    comparisons = audit.get("comparisons")
    if not isinstance(comparisons, list) or not comparisons:
        raise GateWall("no external comparison")
    for c in comparisons:
        url = nonempty(c.get("url"), "comparison URL")
        if not url.startswith("https://") or any(x in url for x in (" ", "\n", "\r", "@")):
            raise GateWall("invalid external source URL")
        nonempty(c.get("observed"), "external observation")
        nonempty(c.get("selection_reason"), "why source is a strong comparison now")
        nonempty(c.get("relation"), "A/B relation")
    ab = audit.get("ab")
    if not isinstance(ab, dict):
        raise GateWall("A/B comparison missing")
    for field in ("current_referent", "preserved", "difference", "next_movement"):
        nonempty(ab.get(field), f"A/B {field}")
    if ab.get("status") not in ("MOVE", "WALL", "PARTIAL", "UNKNOWN"):
        raise GateWall("invalid A/B disposition")
    if ab.get("status") == "MOVE":
        nonempty(audit.get("worker_instruction"), "worker handoff implementation movement")
        tests = audit.get("required_tests")
        if not isinstance(tests, list) or not tests or not all(
                isinstance(x, str) and x.strip() for x in tests):
            raise GateWall("worker movement requires explicit tests")


def admit(root: Path, out: Path, packet: dict, audit: dict) -> dict:
    root = root.resolve()
    validate(root, packet, audit)
    out.mkdir(parents=True, exist_ok=True)
    # Audit is a model-supported comparison, not independent proof of its facts.
    (out / "chatgpt-audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = HandoffRuntime(event_store=RuntimeJournal(out / "runtime.jsonl"))
    move = audit["ab"]["status"]
    result = {
        "gate": "chatgpt_tracework_audit",
        "ab_status": move, "handed_off": False, "handoffs": [],
    }
    if move != "MOVE":
        result["reason"] = "A/B did not admit implementation; retain UNKNOWN/WALL/PARTIAL"
        (out / "handoffs.json").write_text("[]\n", encoding="utf-8")
        return result
    stable = json.dumps({
        "witnesses": [(x["path"], x["sha256"]) for x in audit["local_witnesses"]],
        "comparison": [(x["url"], x["relation"]) for x in audit["comparisons"]],
        "movement": audit["ab"]["next_movement"],
        "referent": audit["ab"]["current_referent"],
    }, sort_keys=True, separators=(",", ":"))
    hid = "chatgpt-audit-" + digest(stable.encode())[:24]
    handoff = Handoff(
        handoff_id=hid,
        referent=audit["ab"]["current_referent"],
        from_actor="chatgpt-audit-gate",
        to_actor="tracework-implementation-worker",
        required_relation="Implement witnessed A/B movement on current Tracework structure",
        inputs={
            "snapshot_revision": packet["revision"],
            "local_witnesses": audit["local_witnesses"],
            "visual_provenance": audit["visual_provenance"],
            "external_comparisons": audit["comparisons"],
            "ab_comparison": audit["ab"],
            "instruction": audit["worker_instruction"],
            "model_provenance": audit.get("model_provenance", {}),
        },
        expected_output={"implementation": "bounded source diff or explained wall",
                         "tests": audit["required_tests"],
                         "return": "observed before/after changes with provenance"},
        required_witnesses=("implemented difference", "test result", "visual provenance", "continuity audit"),
        admissible_evidence={
            "implemented difference": ("source", "measurement"),
            "test result": ("measurement",),
            "visual provenance": ("measurement", "source"),
            "continuity audit": ("measurement",),
        },
        boundaries=(
            "Do not change source solely because an external source claims superiority.",
            "Model assertions and evidence labels do not self-certify an implementation.",
            "Respect the current A/B contract, visual provenance and dirty working tree.",
            "Rendered visual work requires actual browser/interaction witness.",
        ),
        provenance=(
            f"git:{packet['revision']}",
            *(f"repository:{x['path']}@{x['sha256']}" for x in audit["local_witnesses"]),
            *(f"external:{x['url']}" for x in audit["comparisons"]),
        ),
        metadata={
            "source_system": "chatgpt-audit",
            "visual_provenance_checked": True,
            "rendered_visual_state": audit["visual_provenance"]["rendered_state"],
            "report": "chatgpt-audit.json",
            "implementation_verified": False,
        },
    )
    if hid not in ledger.snapshot():
        ledger.submit(handoff)
    result.update(handed_off=True, handoffs=[handoff_to_dict(ledger.get(hid))])
    (out / "handoffs.json").write_text(
        json.dumps(result["handoffs"], indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--audit", type=Path, help="ChatGPT audit JSON required for handoff")
    args = parser.parse_args()
    packet = capture(args.root)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "snapshot.json").write_text(
        json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    if args.audit is None:
        print(json.dumps({"gate": "AUDIT_REQUIRED",
                          "packet": str(args.out / "snapshot.json"),
                          "handoff": False}))
        return
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    print(json.dumps(admit(args.root, args.out, packet, audit), indent=2))


if __name__ == "__main__":
    main()
