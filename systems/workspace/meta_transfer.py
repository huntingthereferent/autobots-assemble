"""Observe explicit cross-repository departures and receiver acknowledgements.

This is a read-only receipt checker, NOT a transport, automatic scheduler or
scientific verifier. A DEPARTED event must be recorded on the sender before
publishing a receiving EXPECTED event. Only byte-matched destination payloads
with a separate RECEIVED acknowledgement become verified.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import quote

try:
    from .meta_collect import api, repositories
except ImportError:
    from meta_collect import api, repositories

SCHEMA = "meta-workstation/transfer-health-v1"
LEDGER_SCHEMA = "meta-workstation/handoffs-v1"
ID = re.compile(r"[A-Z0-9][A-Z0-9-]{2,79}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
SAFE_PATH = re.compile(r"[a-zA-Z0-9._/-]{1,240}\Z")
UTC = dt.timezone.utc
MAX_RECORDS = 200
MAX_CONTENT = 32_768


def when(value):
    if not isinstance(value, str):
        raise ValueError("missing UTC transfer timestamp")
    d = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None or d.utcoffset() != dt.timedelta():
        raise ValueError("handoff timestamps must contain UTC offset")
    return d.astimezone(UTC)


def validate_departure(row, nodes):
    if not isinstance(row, dict) or not ID.fullmatch(str(row.get("id", ""))):
        raise ValueError("missing or unsafe transfer identity")
    if row.get("status") not in ("BLOCKED_PRE_DEPARTURE", "DEPARTED"):
        raise ValueError("invalid departure transition")
    if row.get("from") not in nodes or row.get("to") not in nodes or row["from"] == row["to"]:
        raise ValueError("unregistered source/destination node")
    if row.get("lane") is None or not isinstance(row["lane"], str) or not row["lane"]:
        raise ValueError("missing source lane")
    if row["status"] == "DEPARTED":
        if row.get("source_repo") != nodes[row["from"]] or row.get("destination_repo") != nodes[row["to"]]:
            raise ValueError("departure repository identity mismatch")
        if not SHA.fullmatch(str(row.get("source_commit", ""))):
            raise ValueError("departure missing exact source commit")
        if not HASH.fullmatch(str(row.get("payload_sha256", ""))):
            raise ValueError("departure missing payload digest")
        for key in ("source_payload_path", "destination_payload_path"):
            p = row.get(key)
            if (not isinstance(p, str) or not SAFE_PATH.fullmatch(p)
                    or p.startswith("/") or ".." in p.split("/")):
                raise ValueError("unsafe transfer payload path")
        when(row.get("departed_at"))
    return row


def indexed(rows, label):
    if not isinstance(rows, list) or len(rows) > MAX_RECORDS:
        raise ValueError("missing or oversized " + label + " receipt list")
    out = {}
    for item in rows:
        if not isinstance(item, dict) or not ID.fullmatch(str(item.get("id", ""))):
            raise ValueError("invalid " + label + " receipt identity")
        if item["id"] in out:
            raise ValueError("duplicate " + label + " receipt")
        out[item["id"]] = item
    return out


def body(repo, path, getter, ref="main"):
    if not SAFE_PATH.fullmatch(path) or ".." in path.split("/"):
        raise ValueError("unsafe requested GitHub path")
    if ref != "main" and not SHA.fullmatch(ref):
        raise ValueError("source revision must be exact Git commit")
    url = "/repos/" + repo + "/contents/" + quote(path, safe="/") + "?ref=" + quote(ref, safe="")
    entry = getter(url)
    encoded = entry.get("content")
    if entry.get("encoding") != "base64" or not isinstance(encoded, str):
        raise ValueError("source file content not verified")
    raw = base64.b64decode(encoded, validate=False)
    if len(raw) > MAX_CONTENT:
        raise ValueError("transfer control payload exceeds safe limit")
    return raw


def observe(local_ledger, registry, getter=api, now=None):
    """Reconcile A/B source journals. Unavailable B is UNKNOWN, never zero."""
    now = now or dt.datetime.now(UTC)
    if now.tzinfo is None:
        raise ValueError("observation must be timezone-aware")
    nodes = repositories(registry)
    if local_ledger.get("schema") != LEDGER_SCHEMA:
        raise ValueError("unexpected canonical departure ledger schema")
    source_node = next(k for k,v in nodes.items() if v == local_ledger.get("source_of_truth"))
    departures = [validate_departure(r, nodes) for r in local_ledger.get("records", [])
                  if r.get("status") in ("DEPARTED", "BLOCKED_PRE_DEPARTURE")]
    source_index = indexed(departures, "departure")
    entries = {}
    errors = {}
    journals = {source_node: local_ledger}
    for node, repo in nodes.items():
        if node == source_node:
            continue
        try:
            doc = json.loads(body(repo, "docs/live/meta-handoffs.json", getter).decode("utf-8"))
            if doc.get("schema") != LEDGER_SCHEMA:
                raise ValueError("receiving repository handoff schema mismatch")
            journals[node] = doc
        except Exception as exc:
            errors[node] = type(exc).__name__ + ": " + str(exc)[:200]

    for rid, row in source_index.items():
        status = row["status"]
        target = row["to"]
        item = {"id": rid, "from": row["from"], "to": target,
                "lane": row["lane"], "status": status, "source_commit": row.get("source_commit")}
        if status == "BLOCKED_PRE_DEPARTURE":
            item.update({"delivery": "NOT_SENT", "attention": True,
                         "reason": row.get("description", "Destination not yet available")})
        elif target not in journals:
            item.update({"delivery": "UNKNOWN_DESTINATION", "attention": True})
        else:
            dest = journals[target]
            try:
                expected = indexed(dest.get("expectations", []), "expected")
                received = indexed(dest.get("received", []), "received")
                receipt = expected.get(rid)
                expected_fields = ("from", "to", "lane", "source_commit", "payload_sha256",
                                   "destination_payload_path")
                if not receipt:
                    item.update({"delivery": "DEPARTED_NO_EXPECTATION", "attention": True})
                elif any(receipt.get(k) != row.get(k) for k in expected_fields):
                    item.update({"delivery": "EXPECTATION_MISMATCH", "attention": True})
                else:
                    # Source is verified at the pinned commit; destination at
                    # main. The separate receiver acknowledgement is necessary.
                    src = body(row["source_repo"], row["source_payload_path"],
                               getter, ref=row["source_commit"])
                    if sha256(src).hexdigest() != row["payload_sha256"]:
                        item.update({"delivery": "SOURCE_DIGEST_MISMATCH", "attention": True})
                    else:
                        try:
                            dst = body(row["destination_repo"], row["destination_payload_path"], getter)
                        except Exception:
                            item.update({"delivery": "EXPECTED_NOT_ARRIVED", "attention": True})
                        else:
                            if sha256(dst).hexdigest() != row["payload_sha256"]:
                                item.update({"delivery": "DESTINATION_DIGEST_MISMATCH", "attention": True})
                            elif rid not in received:
                                item.update({"delivery": "ARRIVED_UNACKNOWLEDGED", "attention": True})
                            elif (received[rid].get("payload_sha256") != row["payload_sha256"]
                                  or received[rid].get("source_commit") != row["source_commit"]
                                  or received[rid].get("from") != row["from"]
                                  or received[rid].get("to") != target):
                                item.update({"delivery": "ACKNOWLEDGEMENT_MISMATCH", "attention": True})
                            else:
                                when(received[rid].get("received_at"))
                                item.update({"delivery": "RECEIVED_VERIFIED", "attention": False})
            except Exception as exc:
                item.update({"delivery": "UNKNOWN_SOURCE_ERROR", "attention": True,
                             "reason": type(exc).__name__ + ": " + str(exc)[:140]})
        if status == "DEPARTED":
            start = when(row["departed_at"])
            age = (now-start).total_seconds()/60
            item["age_minutes"] = max(0, round(age))
            item["overdue"] = age > 60 and item["delivery"] != "RECEIVED_VERIFIED"
        entries[rid] = item

    # Orphan receiver expectations matter: a destination anticipating a
    # transfer absent from source means the departure record may be lost.
    for node, doc in journals.items():
        try:
            expected = indexed(doc.get("expectations", []), "expected")
        except Exception as exc:
            errors[node] = type(exc).__name__ + ": " + str(exc)[:200]
            continue
        for rid, item in expected.items():
            if rid not in source_index:
                entries["orphan:"+node+":"+rid] = {
                    "id": rid, "to": node, "lane": item.get("lane"), "delivery": "ORPHAN_EXPECTATION",
                    "attention": True}
    complete = not errors and len(journals) == len(nodes)
    result = {
        "schema": SCHEMA, "observed_at": now.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "complete": complete, "source_nodes_observed": sorted(journals),
        "errors": errors,
        "transfers": sorted(entries.values(), key=lambda x: x["id"]),
        "summary": {
            "verified": sum(x["delivery"] == "RECEIVED_VERIFIED" for x in entries.values()),
            "blocked_or_attention": sum(bool(x["attention"]) for x in entries.values()),
            "unverified_destination": not complete,
            "no_traffic_asserted": False
        },
        "limits": "Read-only API observations; no background transport or execution. A successful source job is not a receipt. Missing destination data is UNKNOWN, never proof that no work exists."
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = observe(json.loads(args.source.read_text()), args.registry)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"complete": report["complete"], "summary": report["summary"]}))
    if not report["complete"]:
        print("WARNING: receiving workstation unavailable; no delivery is asserted")


if __name__ == "__main__":
    main()
