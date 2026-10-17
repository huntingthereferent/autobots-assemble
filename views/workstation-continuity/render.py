"""Read-only, source-derived workstation edition/edit/job visual data.

This is NOT a worker executor, scheduling system, source admission or proof.
It projects the existing native monitor. No private paths, source text or job
payloads are exported; publishing generated artifacts requires separate review.
"""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re

SCHEMA = "workstation-native-visual/v1"
_IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\\Z")
_ALLOWED_EDITION = {"AVAILABLE", "UNREADABLE"}
_ALLOWED_VERIFY = {"recorded-not-reverified", "not-complete"}


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _IDENT.fullmatch(value):
        raise ValueError("unsafe " + label)
    return value


def project_native(monitor: dict) -> dict:
    """Take ONLY source-owned edition ancestry, observed edit counts and jobs."""
    if (not isinstance(monitor, dict) or monitor.get("schema_version") != 1
            or monitor.get("read_only") is not True
            or monitor.get("worker_execution_triggered") is not False
            or monitor.get("runtime_execution_connected_by_view") is not False):
        raise ValueError("not an existing native read-only workstation monitor")
    if not isinstance(monitor.get("editions"), list) or not isinstance(monitor.get("jobs"), list):
        raise ValueError("missing native monitor collections")

    editions = []
    identities = set()
    for item in monitor["editions"]:
        worker = _identifier(item["worker_id"], "worker")
        version = _identifier(item["version_id"], "version")
        key = (worker, version)
        if key in identities:
            raise ValueError("duplicate native worker edition")
        identities.add(key)
        if item.get("state") not in _ALLOWED_EDITION:
            raise ValueError("unsupported edition state")
        parent = item.get("parent_version")
        if parent is not None:
            _identifier(parent, "parent version")
            if parent == version:
                raise ValueError("self-parented edition")
        status = item["state"]
        if status == "AVAILABLE":
            changes = {}
            for name in ("modified", "added", "deleted"):
                values = item.get(name)
                if not isinstance(values, list):
                    raise ValueError("missing native edited-file inventory")
                if any(not isinstance(s, str) for s in values):
                    raise ValueError("invalid edited-file names")
                changes[name] = len(values)  # Never export private filenames.
            if item.get("source_modified") is not any(changes.values()):
                raise ValueError("native source-change flag inconsistent")
            fingerprint = item.get("current_fingerprint")
            if not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
                raise ValueError("invalid native source fingerprint")
        else:
            changes = {"modified": 0, "added": 0, "deleted": 0}
        editions.append({
            "worker_id": worker,
            "version_id": version,
            "parent_version": parent,
            "state": status,
            "edits": changes,
            "edited": status == "AVAILABLE" and any(changes.values()),
        })

    connected = []
    for row in editions:
        parent = row["parent_version"]
        if parent is not None and (row["worker_id"], parent) in identities:
            connected.append({"kind": "edition-parent",
                              "from": row["worker_id"] + "/" + parent,
                              "to": row["worker_id"] + "/" + row["version_id"]})

    jobs = []
    seen_jobs = set()
    for item in monitor["jobs"]:
        job_id = _identifier(item["job_id"], "job ID")
        if job_id in seen_jobs:
            raise ValueError("duplicate admitted native job")
        seen_jobs.add(job_id)
        worker = item.get("worker_id")
        version = item.get("version_id")
        if worker:
            _identifier(worker, "job worker")
        if version:
            _identifier(version, "job edition")
        if not isinstance(item.get("status"), str) or len(item["status"]) > 32:
            raise ValueError("invalid native job status")
        if item.get("verification") not in _ALLOWED_VERIFY:
            raise ValueError("unsupported job verification scope")
        if not isinstance(item.get("source_state"), str) or len(item["source_state"]) > 48:
            raise ValueError("unsupported source-state label")
        association = (worker, version) in identities
        jobs.append({
            "job_id": job_id,
            "worker_edition": worker + "/" + version if association else None,
            "status": item["status"],
            "source_state": item["source_state"],
            "verification": item["verification"],
        })
    return {
        "schema": SCHEMA,
        "source": "systems.workspace.monitor.workstation_snapshot",
        "scope": "local native read-only evidence; not a live health check",
        "executed_by_this_view": False,
        "authorizes_edits": False,
        "editions": editions,
        "parent_edges": connected,
        "jobs": jobs,
        "counts": {
            "worker_families": len({e["worker_id"] for e in editions}),
            "editions": len(editions),
            "edited_editions": sum(e["edited"] for e in editions),
            "admitted_jobs": len(jobs),
            "recorded_complete": sum(j["status"] == "COMPLETE" for j in jobs),
        },
        "warnings": [
            "A source edition branch is not a new running process.",
            "A changed file is not a verified correct edit.",
            "COMPLETE is a recorded job status; this projection does not reverify it.",
            "Only registered edition ancestry yields a drawn parent edge.",
        ],
    }


def render_svg(data: dict) -> str:
    if data.get("schema") != SCHEMA:
        raise ValueError("unknown visual data source")
    n = data["counts"]
    editions = data["editions"][:8]
    jobs = data["jobs"][:7]
    text = lambda value: escape(str(value), quote=True)
    def block(x, y, w, h, tint, title, lines):
        labels = [f'<text x="{x+18}" y="{y+27}" fill="{tint}" font-size="14" font-weight="bold">{text(title)}</text>']
        for i, line in enumerate(lines):
            labels.append(f'<text x="{x+18}" y="{y+55+i*24}" fill="#D6E2F0" font-size="12">{text(line)}</text>')
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#101B2B" stroke="{tint}" stroke-opacity=".65"/>'
                + "".join(labels))
    pieces = []
    pieces.append(block(25,102,552,129,"#42D6F0","01 / WORKSTATION SOURCE",
        [f'{n["worker_families"]} worker families   /   {n["editions"]} source editions',
         f'{n["edited_editions"]} editions have local edits',
         "Copy / branch / inspect — no worker launched by view"]))
    pieces.append(block(594,102,581,129,"#8B95E6","02 / NATIVE JOB JOURNAL",
        [f'{n["admitted_jobs"]} admitted native jobs',
         f'{n["recorded_complete"]} recorded COMPLETE — not freshly reverified',
         "Source/native execution belongs to original controls"]))
    edition_lines = []
    for e in editions:
        c=e["edits"]
        history = (" < " + e["parent_version"]) if e["parent_version"] else ""
        change = f'  (+{c["added"]} ~{c["modified"]} -{c["deleted"]})' if e["state"]=="AVAILABLE" else " [UNREADABLE]"
        edition_lines.append(e["worker_id"]+"/"+e["version_id"]+history+change)
    edition_lines += (["No recorded editions in source"] if not edition_lines else [])
    pieces.append(block(25,250,552,285,"#42D6F0","EDITION TREE / ORIGINAL ANCESTRY",edition_lines))
    job_lines = [j["job_id"]+"  "+j["status"]+"  ["+j["verification"]+"]" for j in jobs]
    job_lines += (["No admitted native jobs in source"] if not job_lines else [])
    pieces.append(block(594,250,581,285,"#8B95E6","ADMITTED JOB RETURNS",job_lines))
    edge_count=len(data["parent_edges"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-labelledby="title desc">
<title id="title">Native process workstation — recorded editions, edits and jobs</title>
<desc id="desc">Read-only projection: {n['editions']} editions, {edge_count} directly recorded edition-parent edges, {n['edited_editions']} edited editions and {n['admitted_jobs']} jobs. Nothing is executed by this view.</desc>
<style>text{{font-family:ui-monospace,Consolas,monospace}}</style>
<rect width="1200" height="630" rx="14" fill="#080E19"/>
<rect x="9" y="9" width="1182" height="612" rx="11" fill="none" stroke="#33465E"/>
<text x="26" y="47" font-family="monospace" font-size="23" font-weight="bold" fill="#F1F7FF">WORKSTATION / SOURCE CONTINUITY</text>
<text x="27" y="72" font-family="monospace" font-size="13" fill="#AEC0D4">Evidence-derived editions · recorded changes · bounded native jobs</text>
{"".join(pieces)}
<text x="26" y="568" font-size="13" fill="#AFC1D7">Native parent edges: {edge_count} · source names and private output payloads withheld</text>
<text x="26" y="592" font-size="13" fill="#AFC1D7">Recorded status is not native re-verification. This view does not create workers or edits.</text>
</svg>"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    data_dir = args.data_dir.resolve()
    if not (data_dir / "workstation").is_dir() and not (data_dir / "runtime.jsonl").is_file():
        raise SystemExit("No native workstation source found; refusing to manufacture a view.")
    # Reuse the original native monitor and RuntimeJournal. Do not open or run a job.
    from runtime.engine import HandoffRuntime
    from runtime.journal import RuntimeJournal
    from systems.workspace.monitor import workstation_snapshot
    runtime = HandoffRuntime(event_store=RuntimeJournal(data_dir / "runtime.jsonl"))
    local = workstation_snapshot(root=data_dir / "workstation", runtime=runtime,
                                 workspace_journal=(data_dir / "workspace.jsonl")
                                 if (data_dir / "workspace.jsonl").is_file() else None)
    view = project_native(local)
    target = args.out_dir.resolve()
    target.mkdir(parents=True, exist_ok=True)
    (target / "snapshot.json").write_text(json.dumps(view, indent=2, sort_keys=True)+"\\n")
    (target / "visual.svg").write_text(render_svg(view))
    print(json.dumps({"editions":view["counts"]["editions"],
                      "admitted_jobs":view["counts"]["admitted_jobs"],
                      "source":"existing-native-monitor", "out_dir":str(target)}))


if __name__ == "__main__":
    main()
