"""Evidence-constrained routing advice for ChatGPT/GitHub workstation windows.

This module does not dispatch work or read another ChatGPT window.
Route outputs only reflect recorded GitHub observations and admitted workflow lanes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


def stamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(dt.timezone.utc) if parsed.tzinfo else None
    except ValueError:
        return None


def paired_samples(history):
    observed = []
    for sample in history.get("samples", []):
        when = stamp(sample.get("ts")) if isinstance(sample, dict) else None
        nodes = sample.get("nodes", {}) if isinstance(sample, dict) else {}
        if not when or not isinstance(nodes, dict):
            continue
        values = {}
        for node in ("A", "B"):
            detail = nodes.get(node, {})
            required = ("in_progress", "queued", "pending", "waiting")
            if not isinstance(detail, dict) or detail.get("observed") is not True or any(
                not isinstance(detail.get(key), int) or isinstance(detail.get(key), bool)
                or detail[key] < 0 for key in required
            ):
                break
            values[node] = {
                "running": detail["in_progress"],
                "waiting": detail["queued"] + detail["pending"] + detail["waiting"],
            }
        if len(values) == 2:
            observed.append({"ts": when, "nodes": values})
    return sorted(observed, key=lambda s: s["ts"])


def spaced_recent(samples, minimum_minutes=10, count=3):
    selected = []
    for s in reversed(samples):
        if not selected or (selected[-1]["ts"] - s["ts"]).total_seconds() >= minimum_minutes * 60:
            selected.append(s)
        if len(selected) >= count:
            break
    return list(reversed(selected))


def rising_queue(points, node):
    if len(points) < 3:
        return False
    waits = [p["nodes"][node]["waiting"] for p in points[-3:]]
    return waits[0] <= waits[1] <= waits[2] and waits[-1] > waits[0] and waits[-1] >= 3


def decide(history, registry, now=None, max_age_minutes=90):
    now = now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    now = now.astimezone(dt.timezone.utc)
    if history.get("schema") != "ab-meta-observations/v1":
        raise ValueError("Unexpected observation history")
    if registry.get("schema") != "meta-workstation/registry-v1":
        raise ValueError("Unexpected routing registry")

    active = {n.get("id"):n.get("repo") for n in registry.get("nodes", [])
              if isinstance(n,dict)}
    if set(active)=={"A"}:
        # Archived node B must not be polled or used to route new work.
        raw=[]
        for sample in history.get("samples",[]):
            moment=stamp(sample.get("ts")) if isinstance(sample,dict) else None
            a=sample.get("nodes",{}).get("A",{}) if isinstance(sample,dict) else {}
            if not moment or moment>now or a.get("observed") is not True:
                continue
            keys=("queued","pending","waiting","in_progress")
            if any(type(a.get(k)) is not int or a[k]<0 for k in keys):
                continue
            raw.append({"ts":moment,"nodes":{"A":{
                "running":a["in_progress"],
                "waiting":sum(a[k] for k in keys[:3]),
            }}})
        raw.sort(key=lambda r:r["ts"])
        last=raw[-1] if raw else None
        recent=spaced_recent(raw)
        signal="SINGLE_NODE" if last and (now-last["ts"]).total_seconds()<=max_age_minutes*60 else "STALE"
        if not last:signal="UNKNOWN"
        return {
            "schema":"meta-workstation/routing-advice-v1",
            "generated_at":now.isoformat(timespec="seconds").replace("+00:00","Z"),
            "last_paired_observation":None,
            "signal":signal,
            "reason":"Only primary repository is active. Cross-account transfer is disabled.",
            "latest_nodes":last["nodes"] if last else None,
            "sample_count":len(recent),
            "lane_advice":[{
                "id":l["id"],"assigned":"A","admitted_nodes":["A"],
                "recommended":"A","action":"KEEP_ASSIGNED",
                "requires":"Verify primary GitHub workflow and source pin. No second-account fallback."
            } for l in registry.get("lane_rules",[]) if l.get("node")=="A"],
            "boundary":"Advisory only; historical second-account observations are not current routing evidence.",
        }
    samples = [s for s in paired_samples(history) if s["ts"] <= now]
    recent = spaced_recent(samples)
    last = samples[-1] if samples else None
    if not last:
        state, reason = "UNKNOWN", "No paired GitHub observation; cannot infer congestion."
    elif (now - last["ts"]).total_seconds() > max_age_minutes * 60:
        state, reason = "STALE", "Last paired GitHub observation exceeds the 90-minute freshness boundary."
    elif len(recent) < 3:
        state, reason = "OBSERVING", "Need three distinct paired observations spaced at least 10 minutes apart."
    else:
        a = recent[-1]["nodes"]["A"]["waiting"]
        b = recent[-1]["nodes"]["B"]["waiting"]
        ap = rising_queue(recent, "A")
        bp = rising_queue(recent, "B")
        if ap and a >= b + 2 and not bp:
            state, reason = "A_BACKLOG", "A's waiting-run backlog has grown over three checks; B's observed waiting count is lower."
        elif bp and b >= a + 2 and not ap:
            state, reason = "B_BACKLOG", "B's waiting-run backlog has grown over three checks; A's observed waiting count is lower."
        else:
            state, reason = "NO_CLEAR_PRESSURE", "No independently supported node-switch signal in the sampled waiting-run counts."

    lanes = []
    for lane in registry.get("lane_rules", []):
        node = lane.get("node")
        admitted = lane.get("admitted_nodes", [node])
        admitted = [x for x in admitted if x in ("A", "B")]
        if node not in ("A", "B"):
            continue
        preferred = node
        recommendation = "KEEP_ASSIGNED"
        if state == "A_BACKLOG" and node == "A" and "B" in admitted and lane.get("transferable") is True:
            preferred, recommendation = "B", "CANDIDATE_SWITCH"
        elif state == "B_BACKLOG" and node == "B" and "A" in admitted and lane.get("transferable") is True:
            preferred, recommendation = "A", "CANDIDATE_SWITCH"
        elif state in ("UNKNOWN", "STALE", "OBSERVING"):
            recommendation = "VERIFY_SOURCE"
        elif state in ("A_BACKLOG", "B_BACKLOG") and node == state[0] and (
            "B" not in admitted if node == "A" else "A" not in admitted
        ):
            recommendation = "NO_ADMITTED_ALTERNATE"

        lanes.append({
            "id": lane["id"],
            "assigned": node,
            "admitted_nodes": admitted,
            "recommended": preferred,
            "action": recommendation,
            "requires": "Re-read live workflow eligibility, preserve source SHA, and explicitly admit the next job. No automatic dispatch.",
        })

    return {
        "schema": "meta-workstation/routing-advice-v1",
        "generated_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "last_paired_observation": last["ts"].isoformat(timespec="seconds").replace("+00:00", "Z") if last else None,
        "signal": state,
        "reason": reason,
        "latest_nodes": last["nodes"] if last else None,
        "sample_count": len(recent),
        "lane_advice": lanes,
        "boundary": "Advisory only. GitHub's workflow-run backlog is not a proven slowdown or job-slot capacity. A ChatGPT window must read and revalidate the current source before moving work.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--history", required=True, type=Path)
    p.add_argument("--registry", required=True, type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--lane", type=str)
    args = p.parse_args()
    advice = decide(json.loads(args.history.read_text()), json.loads(args.registry.read_text()))
    if args.lane:
        advice["lane_advice"] = [a for a in advice["lane_advice"] if a["id"] == args.lane]
        if not advice["lane_advice"]:
            raise SystemExit("Unknown lane: " + args.lane)
    output = json.dumps(advice, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
