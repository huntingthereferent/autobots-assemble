# CP30 — explicit live public-source preflight (staged)

**Status:** staged source and 163 local regression tests, **no real owner enrolled**. This is a *read-only preparatory check*, not native CP30 source registration, external owner identity proof, or completed route audit.

## What it checks

The command `readiness` reads the existing local hash-chained journals without making network requests or writing files. It reports whether the donor/middle/final source keys and their separate repository ID pins agree, and whether an authority anchor, independent witness pin, and signed receiver challenge exist. Missing or corrupt data **blocks** readiness. Even `PREREQUISITES_PRESENT_NOT_AUTHENTICATED` only describes configured local policy; it is not evidence of legitimate control.

The opt-in command `probe` requires the exact receiver challenge twice and `--network`. It first requires an *unconsumed*, accepted, still-unexpired signed challenge, all three enrolled source/repository pins, plus locally configured authority and witness policy. Before fetching file bytes, it checks GitHub's public numeric repository and account IDs against the operator-pinned IDs. Then it reads exactly the three enrolled public file paths at their current branch commit, verifies each returned Git blob hash and SHA-256 against the source's signed content digest, and verifies that branch heads, local trust journals, and original challenge remain unchanged after reading.

**No automatic upload, enrollment, signature, token use, evidence journal append, task admission, or runtime execution happens.** Even a successful probe can only return `LIVE_PUBLIC_BYTES_MATCH_PRIOR_SIGNED_CLAIMS`. It never returns a real-world identity/authority or native CP30 proof. This is a public-hosted-content check, not cryptographic Git ancestry proof.

## Run (after independently authorized enrollment)

```sh
python -m pip install 'cryptography>=45,<47'
python -m systems.workspace.live_source_preflight --data-dir runtime/data readiness

# Only after out-of-band verification of the actual source owners and keys,
# SourceEvidenceLedger enrollment, SourceOriginPolicy pinning,
# authority-anchor and witness enrollment, and three accepted fresh signatures:
python -m systems.workspace.live_source_preflight --data-dir runtime/data probe \
  --challenge REPLACE_WITH_ISSUED_48_HEX_CHALLENGE \
  --confirm-challenge REPLACE_WITH_THE_SAME_CHALLENGE --network
```

The challenge is short-lived (30–600 seconds); if it expires during the network call the probe fails. The probe does not consume or log an observation, so an operator must run the actual observed-evidence admission separately to record a canonical observation. A successful read-only probe does not transfer the authority grant or make a CP30 task eligible.

An empty private data directory produces a `BLOCKED` readiness report listing missing source keys, repository pins, witness, authority, and accepted signatures, and does not create the directory. This is the expected outcome before a genuine enrollment.

## Real-GitHub check performed during development

A read-only GitHub connection returned repository metadata for `huntingthereferent/autobots-assemble` (numeric repository ID `1403664339`, owner account ID `331854748`) and the integrated research README's Git blob ID. **This confirms a public provider read is available, not a signed source enrollment or actual CP30 authority.** No external signer was contacted or live CP30 source evaluated.

## Reproduce locally

```sh
CP30_NATIVE_SOURCE_DIR=/absolute/path/to/reconstructed/cp30 \
python -m unittest -v \
  network.tests.test_external_evidence \
  network.tests.test_github_observation \
  network.tests.test_external_route_mapping \
  network.tests.test_external_source_continuity \
  network.tests.test_native_owner_observation \
  network.tests.test_external_native_binding \
  network.tests.test_external_authority_binding \
  network.tests.test_independent_authority_source \
  network.tests.test_source_origin_authority \
  network.tests.test_live_source_preflight
```

Tests use synthetic signing keys, native synthetic owner objects, and mocked GitHub responses. They demonstrate fail-closed protocol behavior, **not** live third-party authorization.
