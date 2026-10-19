"""Two-job, source-owned WORLD48 finite-math evidence handoff.

Producer records actual finite F3 A/B steps. A separate job independently
replays every event and outcome against the original Python laws. This is
NOT native ARC/W13 evidence, a signature, or a claim of external causality.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from work.arc3.window48_challenges import (
    CHALLENGE_SCHEMA, SCOPE, rooted_roster, verify_certificate,
)
from work.arc_like_maze.window_combined import family

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATHS = (
    "work/arc_like_maze/window_combined.py",
    "work/arc_like_maze/window_two.py",
    "work/arc_like_maze/window_branch.py",
    "work/arc3/window48_challenges.py",
)
SCHEMA = "world48-source-worker-handoff/v1"


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def content_digest(value: object) -> str:
    """A content checksum; NOT an authentication signature."""
    return sha256(canonical(value)).hexdigest()


def source_digests() -> dict[str, str]:
    return {p: sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCE_PATHS}


def source_trial(laws, law_ids: list[int], word: str) -> dict:
    states = [(0, 0, 0), (0, 0, 0)]
    events = []

    def index(s):
        return s[0] * 9 + s[1] * 3 + s[2]

    for action in word:
        before = [index(s) for s in states]
        states = [laws[law_ids[k]].step(states[k], action) for k in range(2)]
        events.append({
            "action": action,
            "before": before,
            "after": [index(s) for s in states],
        })
    return {"actions": word, "events": events, "final": [index(s) for s in states]}


def produce_record() -> dict:
    roster = rooted_roster()
    laws = family()
    certificates = []
    for ch in roster:
        ids = ch["law_ids"]
        trials = [source_trial(laws, ids, word) for word in ch["example_words"]]
        certificates.append({
            "schema": CHALLENGE_SCHEMA,
            "scope": SCOPE,
            "challenge_id": ch["id"],
            "law_ids": ids,
            "trials": trials,
            "verdict": {"left_collides": True, "right_splits": True, "passed": True},
        })
    payload = {
        "schema": SCHEMA,
        "scope": SCOPE,
        "source_digests": source_digests(),
        "claims": {
            "challenges": len(certificates),
            "witnesses": len(certificates),
            "action_events": sum(
                len(t["events"]) for cert in certificates for t in cert["trials"]
            ),
        },
        "certificates": certificates,
    }
    return {**payload, "payload_sha256": content_digest(payload)}


def verify_record(record: dict) -> dict:
    if type(record) is not dict or set(record) != {
        "schema", "scope", "source_digests", "claims", "certificates", "payload_sha256"
    }:
        raise ValueError("WORLD48 handoff fields missing or altered")
    if record["schema"] != SCHEMA or record["scope"] != SCOPE:
        raise ValueError("wrong handoff referent or research scope")
    if record["source_digests"] != source_digests():
        raise ValueError("producer and verifier original source bytes differ")
    payload = {k: v for k, v in record.items() if k != "payload_sha256"}
    if record["payload_sha256"] != content_digest(payload):
        raise ValueError("handoff content checksum mismatch")

    certs = record["certificates"]
    roster = rooted_roster()
    if type(certs) is not list or len(certs) != len(roster):
        raise ValueError("handoff missing or extra original WORLD48 challenges")
    verified = []
    events = 0
    for i, cert in enumerate(certs):
        # Source verification accepts any genuine winning A/B paths, not only
        # the producer's suggested literal strings.
        result = verify_certificate(cert)
        if not result["verified"] or not result["passed"] or result["challenge_id"] != i:
            raise ValueError("missing or nonwinning original source witness")
        events += sum(len(trial["events"]) for trial in cert["trials"])
        verified.append(result["challenge_id"])

    expected = {"challenges": len(roster), "witnesses": len(verified), "action_events": events}
    if record["claims"] != expected:
        raise ValueError("producer progress or event-count claim unsupported")
    return {
        "verified": True,
        "scope": SCOPE,
        "source": "work/arc_like_maze/window_combined.py",
        "source_digests": source_digests(),
        "challenges": len(roster),
        "witnesses": len(verified),
        "action_events_replayed": events,
        "packet_sha256": record["payload_sha256"],
        "native_arc_evidence": False,
        "w13_evidence": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Original WORLD48 worker and independent source verifier")
    sub = parser.add_subparsers(dest="command", required=True)
    producer = sub.add_parser("produce")
    producer.add_argument("--out", type=Path, required=True)
    verifier = sub.add_parser("verify")
    verifier.add_argument("--input", type=Path, required=True)
    verifier.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "produce":
        args.out.parent.mkdir(parents=True, exist_ok=True)
        packet = produce_record()
        args.out.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"produced": packet["claims"], "packet_sha256": packet["payload_sha256"]}))
        return

    if args.input.stat().st_size > 1_000_000:
        raise ValueError("unbounded WORLD48 worker input refused")
    report = verify_record(json.loads(args.input.read_text(encoding="utf-8")))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
