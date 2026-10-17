# COORDINATOR W13 — source-bound browser evidence admission preflight

**Current referent:** carry the genuine WORLD W13 → BUILD W13 → independently implemented WITNESS W13 relation to the existing workstation checkpoint without treating that relation as native execution authority.

**Outcome:** `SOURCE_BOUND_BROWSER_EVIDENCE_ACCEPTED_FOR_OPERATOR_REVIEW`.  
**Checkpoint outcome:** `GAME-W13-WORLDS = ADMISSIBLE`; **not** `WITNESSED`.

## What moved

A read-only, executable handoff now gathers two **separate actual Chromium output sets** from the exact successful protected-main BUILD and WITNESS GitHub Actions runs:

| Origin | GitHub workflow run / code commit | Artifact ID | API-recorded archive digest |
| --- | --- | --- | --- |
| BUILD | [38999614131](https://github.com/huntingthereferent/autobots-assemble/actions/runs/38999614131) / `49a82fc09428ef413561edf3b9c1f612bab0232c` | `12088487637` | `sha256:bf94bd3420000fa1767f026ec03a8adf7a4e5c93647624d30032bd165a5242dc` |
| WITNESS | [39001126918](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39001126918) / `1b067e05e37f5629556defca5b406da6ecd3cbfb` | `12088694155` | `sha256:7b98c96ef0d8d9be5b63233bf65aec44d59278f4a667d5ad2818ba9e12a625b0` |

The CI workflow calls GitHub's authenticated **read-only** API to confirm exact run IDs, successful conclusions, main-commit heads, `push` event type, artifact IDs/names, expiration states, parent runs, and GitHub's recorded archive digests. It separately downloads both original artifact collections, rather than running BUILD again.

`systems/workspace/game_w13_cp_preflight.py` pins the Git **blob identity** of the unmodified W12 game source, original WORLD W13 contract, BUILD browser/engine/receipt, the separate WITNESS verifier/verdict and the existing two-world WORLD fixture. W12's original SHA-256 must also equal `dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1`.

The preflight independently checks **both** downloaded successful browser receipts using `network/witness_w13_independent.py` (original W12 native replay, not BUILD's W13 verifier). It requires the exact two-room global action history `right → interact → advance → right → interact`, matching local W12 trace head hashes, exactly one advance and a solved final session. It refuses changed source bytes, differing browser histories, missing receipts, duplicated JSON object keys, symlinks and altered state or world identity. It **must independently reject 4 BUILD-altered receipts and 6 WITNESS-altered receipts**.

The coordinator then consults the **unchanged** `cp_motion.checkpoint_frontier` with zero admitted native jobs. Its required result remains `ADMISSIBLE`, `witnessed=[]`, `started_workers=0`. Source evidence readiness is not a `cp-checker` result, workstation journal row, or an executed job.

## Actual evidence / tests

[First coordinator preflight PASS — GitHub Actions #39001725994](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39001725994).

- 11/11 original W12 and 21/21 original W12 receipt tests pass.
- 26/26 independent W13 WITNESS cases pass.
- 16/16 new coordinator, source pin, provenance and negative-boundary cases pass.
- Distinct archived BUILD and WITNESS browser completions replay against original W12; all **10/10 altered original browser receipts** are independently rejected.
- Two exact successful GitHub runs and the two corresponding artifact IDs/archive digests match GitHub API metadata.
- A read-only JSON review artifact is produced at `coordinator_w13_preflight/evidence-admission.json`. It contains local source identities, per-world original-native head hashes, browser artifact receipt hashes, negatives rejected, and exact required future native checkpoint boundary.

The unit tests use deterministic fixture copies **for adversarial isolated checks**. The separate integration test consumes the **real previously downloaded Chromium exports**; it does not relabel a Python fixture as a browser witness.

The GitHub artifact ZIPs are not archived forever. If the originals expire, the workflow must fail closed and a *separately admitted* archival/provenance decision is necessary; do not manufacture the same archived source.

## Local read-only usage after obtaining the two archived browser artifact folders

```sh
python -m unittest -v network.tests.test_game_w13_cp_preflight
python -m systems.workspace.game_w13_cp_preflight \
  --repo-root . \
  --build-evidence path/to/original_build_browser_artifact \
  --witness-evidence path/to/original_witness_browser_artifact \
  --output coordinator_w13_preflight/evidence-admission.json
```

The CLI writes **only** the requested review JSON file. It does not update `runtime.jsonl`, `coordinator-windows.jsonl`, `state/current.json`, `cp_motion.GRAPH` or a source-owner trust ledger. The report explicitly sets `execution_triggered=false`, `job_admitted=false`, `cp_witnessed=false`, `checkpoint_promoted=false`.

## The remaining native wall

The existing [CP automation contract](CP_AUTOMATION.md) requires all of the following before `GAME-W13-WORLDS` can become `WITNESSED`:

1. An explicitly admitted, source-pinned **native** Process Workstation job for `GAME-W13-WORLDS`, bound by exact job ID to the coordinator's game CP slot.
2. Its original immutable native handoff must declare `checkpoint_contract=GAME-W13-WORLDS`, `native_evidence_verifier=cp-checker:GAME-W13-WORLDS` and worker role `game-build`.
3. The **distinct native CP-specific verifier** must verify the exact source edition and return `checkpoint_verdict=PASS` for its bounded declared computation, with status `COMPLETE` and `source_state=MATCHES_ADMISSION`.
4. A **fresh read-only** native re-verification of that same job, matching the original coordinator binding, must succeed; every dependency must be witnessed.

The existing candidate worker from the October 15 game source library returned `checkpoint_verdict=CANDIDATE`, not `PASS`, and was not integrated as a CP-native adapter on `main` by this movement. A browser W13 PASS is **not** permission to change that result. It might justify a separately reviewed **narrower, source-bound CP-native job**, but that work still needs a defined source adapter and independent verifier.

**NEXT SINGLE MOVEMENT:** Define and implement a source-owned native GAME-W13-WORLDS adapter whose *finite, declared contract* can be independently freshly reverified, and require exact owner/operator-controlled admission and execution. Preserve original W12 source and separately evidenced browser W13 verification. Avoid modifying `cp_motion` to accept CI/browser reports as direct job witnesses.
