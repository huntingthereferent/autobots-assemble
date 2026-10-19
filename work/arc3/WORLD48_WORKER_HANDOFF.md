# WORLD48 finite-source worker handoff

Two **actual** GitHub Actions jobs now form a bounded WORLD48 mathematical evidence path:

1. `original-law-source-worker` replays all 48 source-owned challenge pairs and records every A/B step, before/after exact F3 state index and resulting paths in `world48-unverified-source-worker`.
2. `independent-source-replay-verifier` downloads **that actual first-job artifact**, recomputes the original source-file digests and every event/final/rooted-collision verdict using the authoritative Python implementation, rejects a missing or forged challenge, and uploads `world48-independent-replay-report`.

This is a **same-run actual artifact handoff**. The source SHA-256 strings are content identifiers, **not signatures** or authentication of a remote author. Passing means that particular bounded mathematical evidence packet is consistent with the repository's original finite laws; it does **not** mean W13 owner/child journal restoration, ARC original SDK action completion, physical simulation or proof of general equivalence.

Run directly:

```bash
python -m work.arc3.window48_worker_handoff produce --out runtime/world48/source-worker.json
python -m work.arc3.window48_worker_handoff verify --input runtime/world48/source-worker.json --report runtime/world48/verified-replay.json
python -m unittest -v network.tests.test_arc3_window48_worker_handoff
```

The GitHub workflow is `.github/workflows/world48-source-worker-handoff.yml` and may be started manually from Actions after merging or automatically for changes to the actual source or this workflow. The producer and verifier cannot promote a nonwinning observation to a winning certificate; alternative valid source paths are allowed. Previous W13 native evidence and the playable WORLD48 URL remain unchanged.
