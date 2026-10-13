# Explicit finite edge transfer between independently witnessed joins — 2026-10-13

**Current referent:** Continue the existing A/B mathematical chatbot by allowing an *explicit, selected* donor edge, already witnessed on the **same pinned original/new owner snapshots**, to enter a NEW derived partial relation. A/B at the research level is language for tracing relational movement; the operators in this example are merely declared finite generators.

## Reproduced result

Original law phi=(0,0,0); changed law phi=(0,1,2). Recipient words `A` and `BAA` witness five paired states and four admitted transitions. Donor words `B` and `ABB` independently witness five paired states and four transitions.

The donor's original-state edge `(1,0,0) B` is both already witnessed and rooted from the recipient's existing `A` history. Adding **only this explicitly requested edge** and its endpoint produces a **new six-state, five-edge derived partial relation**. A task requiring both `(1,1,0) A` and `(1,0,0) B` now has an exact **2/2 witnessed completion**, whereas each original join alone satisfies only one of those required edges. The source owners observed **zero new transitions** for transfer or task evaluation; their old/new caches both held six transitions before and after. Neither original join is rewritten; each edge in the derivative records its provenance.

Attempting to include the donor's next `(1,2,0) B` edge also fails atomically. The original words `BA` and `ABB` reach the same old state `(1,1,0)`, but new endpoints `(1,1,0)` and `(1,1,2)`. The transfer returns `TRANSFER_STATE_CONFLICT` with this replayable counterexample, **not** a partially successful derivative. A requested edge absent from donor's witnessed history is `TRANSFER_EDGE_UNPROVED`; an edge with an unadmitted source prefix is `TRANSFER_UNROOTED`.

## Scoped integrated contract

The added `ab_chatbot_explicit_evidence_transfer.py` preserves the unchanged earlier `CrossPinJoin` and `JointEvidenceTask`. A strict transfer declaration specifies the recipient's exact fingerprint, donor's exact fingerprint and the **ordered explicit edge keys** to admit. Both joins must use the same in-process registry and exact original/new observer objects, have the same locally verified source pins and versions, and replay all cached edges on every read. Each selected edge must already be admitted by the donor and have a rooted prefix in the current derived relation. Any incompatibility fails the entire transfer. A subsequent task can bind to the new derivative's SHA-256 fingerprint, with zero additional source observations.

Source revisions, revoked pins, tampered cached edges, and mismatched fingerprints withhold completion. A digest or owner label does not authenticate a remote system.

**Critical limitation:** This establishes permitted composition of compatible observed partial relations over the **exact same pinned sources**, not arbitrary evidence transport between *different versions or different owners*. A separate transport proof would be needed for that. The full **185-file** snapshot-backed chatbot archive is in the conversation; GitHub contains this smaller independent finite oracle only. Archive SHA-256: `849a7b15969b31481e18fb882ab2c20815e0e85beacfa7847485eca86ffa2657`, preserving all 177 predecessor files byte-for-byte.

## Reproduction

From `work/arc_like_maze/chatbot`:

    python finite_explicit_join_transfer.py
    python -m unittest -q test_finite_explicit_join_transfer.py

The independent standalone finite reference passes **5 tests** and knows the whole declared finite law. The integrated layer has **13 new tests** and 10 imported fixture tests passed together; adjacent module runs completed for joint witness binding 22, joint evidence task 11, cross-pin join 20, cross-pin comparison 10, and owner pin 10. **101 completed test executions across separate module runs**, with overlaps from imported fixtures. Other older regression invocations were interrupted; no all-suite result or GitHub CI is claimed.

**Next:** Investigate a declared, separately evidenced state-level intertwining relation for transfer across distinct owner pins or historical revisions, instead of assuming that compatible same-source evidence authorizes it. The unrelated `state/current.json` and active Continuity frontpage referent are untouched.
