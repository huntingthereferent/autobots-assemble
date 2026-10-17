# WITNESS → COORDINATOR — W13 independent two-room verification

**Verdict:** **W13 PASS — bounded local playable-browser candidate** (independent implementation of the native session replay).  
**Not:** `GAME-W13-WORLDS` CP promotion, authenticated browser provenance, deployment, user-independent/origin-signed witness, or validation of arbitrary worlds.

## CURRENT REFERENT

Independently evaluate WORLD W13 Movement 01's one explicit `advance`
between the original 4×3 W12 world and the previously proposed 3×3
second world, using original W12 source semantics as the authority.
BUILD's W13 engine, browser receipt verifier, deterministic fixture
generator and browser test suite are **not imported or used as this
WITNESS oracle**.

## INPUTS AND EVIDENCE IDENTITIES

- WORLD contract: `systems/workspace/WORLD_W13_MOVEMENT_01.md`,
  merged PR #45, commit `7774e22ef64fd209f60a6642fe395db4f6c7a293`.
- Preserved original W12 game source:
  `systems/workspace/game_construction.py`, SHA-256
  `dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1`.
  That source fingerprint is checked **at independent witness replay**.
- Source under observation: `docs/game_w13_preview.html` and its
  new W13 BUILD receipt exporter; BUILD merge commit
  `49a82fc09428ef413561edf3b9c1f612bab0232c`.
- Prior actual Chromium BUILD output: GitHub Actions
  [original main BUILD run #38999614131](https://github.com/huntingthereferent/autobots-assemble/actions/runs/38999614131);
  immutable build artifact **12088487637** named
  `w13-build-chromium-evidence`. WITNESS's GitHub workflow fetched this
  **previous** run with an exact run ID, not a source fixture substituted
  for the browser export.
- Independent WITNESS verification implementation:
  `network/witness_w13_independent.py`, distinct
  `network/tests/test_game_w13_independent_witness.py` and
  `network/browser_w13_independent_witness.py`.
- [Independent GitHub WITNESS run #39000587000](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39000587000):
  **PASS**. Real fresh Chromium witness artifacts: **12088822903**,
  `w13-independent-witness-chromium-evidence`.

## INDEPENDENT EXECUTION — NOT BUILD SELF-CERTIFICATION

The independent WITNESS oracle separately walks the global action
sequence through the WORLD-declared two fixed specs, calling the
**preserved original W12 native `transition`** for each local action.
It constructs its own expected `before/action/after/verdict`, records
the first room's final state at the single `advance` boundary,
requires the second world's original `(0,0,false,0)` initial state,
and compares all local, cross-world and session fields using canonical
JSON (so `false` cannot masquerade as `0`).

It separately calls original W12 `run_actions` and `verify_trace` to
check each world's original hash-chained native trace and verifies
the initial original W12 source SHA-256. It **does not** trust BUILD's
receipt verifier, W13 candidate engine, new BUILD tests, or any browser
claim of passing its own verification.

### Check matrix, exact run #39000587000

| Condition | Result |
| --- | --- |
| Original W12 native and receipt regression | **32/32 PASS**, no skips |
| WITNESS-authored native and negative cases | **26/26 PASS**, no skips |
| Original BUILD Chromium positive downloaded artifact | **1/1 independently accepted** |
| Original BUILD altered browser receipt artifacts (boundary, final, first-room, second-room) | **4/4 independently rejected** |
| Fresh real Chromium WITNESS button, keyboard, reset, blocked-move, diagonal and completion scenarios | **8/8 PASS**, no skips |
| Fresh tampered actual browser downloads (global ordering, first/second observations, first final, advance boundary, session completion) | **6/6 rejected** within Chromium case 8 |
| WITNESS artifact capture | **PASS** — actual downloaded JSON, altered receipts, headless Chromium screenshot |

The two-room observed success sequence is
`first-room: right → interact → advance → second-room: right → interact`.
Room 1 remains `(1,1,collected=true,turns=2)`, room 2 finishes at
`(1,0,collected=true,turns=2)`, and the second room begins with zero turns.
Blocked moves still consume a turn without moving; diagonal
`interact` cannot collect. One first-room `collected=true` does not
close the session. In the second room there is no allowed second
`advance`.

Negative tests also reject rewritten or borrowed world observations,
conflicting W12 specs/versions, modified native source fingerprints,
changed session world count/final state, swapped global action order,
duplicate JSON keys, extras/missing keys, and alleged evidence crossing
the wrong world.

## PROVENANCE AND VERDICT LIMITS

**PASS is source- and local-browser-behavior bounded.** Chromium was
invoked headlessly with `page.set_content` from the repository HTML,
with real input clicks/keys and actual downloaded JSON; this is not a
deployed website origin check. An observation hash or original W12
native replay cannot authenticate which deployed browser generated it.
The WITNESS checks are a **separately authored/implemented technical
oracle in this repository**, not proof of an independent organization,
owner attestation, separate private workstation, or third-party audit.

The candidate W13 source once admitted to the earlier CP lane declared
`checkpoint_verdict=CANDIDATE`. **Do not change that to `PASS`
automatically**, infer that all 2–4-world configurations are covered,
or claim the entire handoff route is witnessed. An admitted, source-pinned
native WITNESS result and coordinator review of its exact evidence is
a **separate boundary** before any `GAME-W13-WORLDS` CP promotion.

W12 original and W1–W12/C1/BUILD histories are retained unchanged.
No W12 gameplay, strict verifier, saved browser receipt, or native
source edition was rewritten by this W13 WITNESS movement.

## NEXT SINGLE MOVEMENT — COORDINATOR

Return **W13 PASS — bounded local-browser candidate** with exact
independent replay and GitHub test/artifact evidence to COORDINATOR.
Decide whether and how to bind this evidence into the existing
`GAME-W13-WORLDS` source-pinned native checkpoint without inventing
an owner, treating GitHub CI as an external identity, or silently
granting automatic source execution. Do **not** redefine the original
language referent or advance WORLD rules as part of WITNESS.
