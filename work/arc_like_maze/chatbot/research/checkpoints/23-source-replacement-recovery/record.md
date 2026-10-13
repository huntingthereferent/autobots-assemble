# A/B chatbot — independently pinned source replacement recovery

**Date:** 2026-10-13. **Scope:** Bounded finite A/B-labeled mathematical chatbot. A/B as relational language is not equated with these specific finite transition generators.

## What was added

The opt-in `SourceReplacementRecovery` adapter composes the existing `SourceChangePropagation`, `TwoHopTransport`, and `TwoRouteComparison`. An external caller creates a **new**, separately observed and owner-pinned middle-scope route after the earlier middle source fails its evidence audit. The adapter does not modify either original route, infer mappings, initiate observations, or create its own task. It is invoked via `advance()` after the surrounding sources move.

The caller supplies three **exact** 64-character digests: `historical_left_fingerprint`, `historical_right_fingerprint`, and `replacement_right_fingerprint`. The previous conflict or agreement is retained as an **immutable historical report**, not an active certificate. The historical left route must still audit as `PRESERVED`, the old right route must audit as `WITHDRAWN`, and the replacement route must use a distinct in-process join, registry, owner observers, and independently established edge histories. Both audits repeat before a replacement comparison is published.

## Reproduced local witness

Historical pair: donor phi `(0,0,1)` / `(1,0,1)`; two intermediate pairs; final pair phi `(2,0,0)` / `(2,2,1)`. Both initial routes previously formed valid two-hop certificates and **conflicted** on composed endpoint images. Revoke the old right-middle source pin while leaving its 5+5 cached transitions in the historical record. Then create and locally verify a new owner pair with new registry, two new owner pins and rooted words `A`, `BAA`; observe 4 old and 4 new base transitions plus the selected `B` transition on each side (5+5 new-middle observations).

| New replacement middle laws, old/new phi | Result after explicit transport maps | Current output |
|---|---|---|
| `(0,0,0)` / `(0,1,2)` | Composed images agree with the unchanged left route | `RECOVERY_AGREEMENT_WITNESSED` |
| `(1,1,0)` / `(1,1,1)` | Both routes valid; their composed images still disagree | `RECOVERY_CONFLICT_WITNESSED` |

In **both** results the new derived route has six state pairs and five admitted labeled edges. The unchanged left route's old evidence remains 5+5 observations. Old withdrawn right source remains 5+5 **historical** observations. Donor remains 3+3 and final scope remains 6+6. The replacement independently acquired 5+5 observations before recovery comparison. Recovery/comparison then made **zero additional owner transition observations**. All five scopes are checked again on repeat invocation.

- A replacement pin revocation or owner-bound observation corruption removes recovered success on the next audit.
- Losing the previously unaffected left route returns `RECOVERY_LEFT_EVIDENCE_UNPROVED`.
- If the original right route is still valid, recovery returns `RECOVERY_NOT_NEEDED`; it cannot quietly replace a working result for convenience.
- Reusing the old right route or providing a wrong fingerprint is rejected before recovery.
- New owner-head revisions do not invalidate an earlier unmodified, owner-held pinned historical snapshot.
- Explicit route or scope substitution is rejected; no historical claim is rewritten to make a new result look like the old one.

## Testing and reproducibility

**92 tests passed across completed modules:**

- New integration `test_ab_chatbot_source_replacement_recovery.SourceReplacementRecoveryTests` — **13**.
- Independent complete-law `test_finite_source_replacement_recovery.FiniteReplacementTests` — **7**.
- Unchanged two-route and source-change suites — **25**.
- Unchanged two-hop and cross-scope suites — **26**.
- Unchanged exact-owner and joint-task suites — **21**.

An initial owner-pin test-class invocation used a nonexistent class and is **not counted**. Tests were rerun using the correct modules. Neither the full historical regression suite nor GitHub CI was verified.

Run from the extracted directory:

```bash
python -m unittest -q test_ab_chatbot_source_replacement_recovery.SourceReplacementRecoveryTests
python -m unittest -q test_finite_source_replacement_recovery.FiniteReplacementTests
python run_source_replacement_recovery_demo.py
```

The runnable demo writes `SOURCE_REPLACEMENT_RECOVERY_RESULTS.json` with a successful replacement and a conflicting replacement, including before/after owner-observation counts.

## Evidence boundary

The standalone finite reference **knows the full declared laws** and treats `old_right_valid` and `left_valid` as externally supplied flags. It does **not** prove that owner pins are genuine or that HTTP observations were made. The integrated tests use the existing in-process owner-backed loopback to obtain and recheck evidence. No remote identity authentication, automatic polling, indefinite autonomous behavior, global source equivalence, or transfer of unobserved edges follows from these finite results.

All 217 predecessor archive entries are preserved byte-for-byte. Eight additive files create this layer. GitHub remains unchanged; the work is packaged locally.

**Next boundary:** On an externally observed stream of multiple source revisions, test whether recovery identifies the *smallest* set of certificates needing recheck, and avoids reobserving completely independent source edges. Keep source identity/version evidence separate from mathematical relation claims.
