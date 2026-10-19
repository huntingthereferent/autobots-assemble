"""Bounded owner W13 adapter analysis. Native host supplies verified inputs."""
import hashlib
import json
import os
import sys


def compute(data):
    if type(data) is not dict or set(data) != {"kind", "source_pair", "adapter"}:
        raise ValueError("exact owner readiness envelope required")
    if data["kind"] != "owner-w13-adapter-readiness/v1":
        raise ValueError("owner adapter scope differs")
    pair = data["source_pair"]
    adapter = data["adapter"]
    if (pair["state"] != "BOTH_NATIVE_HISTORIES_FRESHLY_REVERIFIED_SEPARATELY"
            or pair["owner_runtime_contains_temporal_source"] is not False
            or pair["native_dependency_join_witnessed"] is not False
            or pair["game_worker_ready_witnessed"] is not False
            or pair["journal_hashes_unchanged"] is not True
            or pair["temporal_live_queries"] < 5
            or adapter != {"route":"controls.run_job",
                "exact_confirmation":"game-w13-github-001",
                "wrong_confirmation_rejected":True}):
        raise ValueError("native parents, external temporal source or route not verified")
    encoded = json.dumps(data, sort_keys=True, separators=(",",":"), allow_nan=False)
    return {"kind":"owner-w13-adapter-ready-receipt/v1",
        "input_sha256":hashlib.sha256(encoded.encode()).hexdigest(),
        "owner_parent_event":pair["owner_parent_event"],
        "owner_child_event":pair["owner_child_event"],
        "external_temporal_result_event":pair["temporal_result_event"],
        "external_temporal_browser_event":pair["temporal_browser_event"],
        "external_temporal_source_consumed":True,
        "histories_remain_separate":True,
        "adapter_route":"controls.run_job",
        "scope":"owner-W13-adapter-with-external-synthetic-temporal-source"}


if __name__ == "__main__":
    try:
        raw = sys.stdin.read(16001)
        if len(raw) > 16000:
            raise ValueError("owner readiness envelope exceeds bound")
        print(json.dumps({"receipt":compute(json.loads(raw)),"pid":os.getpid()},sort_keys=True))
    except (KeyError, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
