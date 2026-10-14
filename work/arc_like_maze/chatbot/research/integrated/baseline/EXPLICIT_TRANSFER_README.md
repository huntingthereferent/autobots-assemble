# Explicit witnessed edge transfer between finite joint histories

**Date:** 2026-10-13  
**Referent:** The existing A/B mathematical chatbot. Language-level A/B remains relational language; formal A and B are only two declared finite operators.

## Why this layer exists

Prior stages could compare separately pinned joins and certify a task only from one join at a time. This layer allows an **explicitly selected, already-witnessed donor edge** to enter a **new derived partial correspondence** when the independently verified recipient and donor share the **exact same local pinned original/new snapshots**, the transferred edge has a currently admitted rooted source prefix, and its endpoint assignments preserve the combined injective pairing. There is **no implied transfer across different owners or revisions**.

Both original joins remain unchanged, and their cached transitions are independently audited on every transfer attempt. The transfer is all-or-nothing for the declared edge list. A task can then be declared against the transfer's derived digest without asking either source owner for another transition.

## Reproduced finite laws and witness

Old law phi=(0,0,0); new law phi=(0,1,2). Two independently witnessed joins under the same pinned owner snapshots:

- Recipient words `A`, `BAA`: **5 paired states, 4 admitted edges**; contains old `(1,1,0)` action `A`.
- Donor words `B`, `ABB`: **5 paired states, 4 admitted edges**; contains old `(1,0,0)` action `B`.
- **Transfer exactly** old `(1,0,0)` action `B`: verified new derived pairing **6 states, 5 admitted edges**. A two-edge task requiring recipient's `(1,1,0) A` and transferred `(1,0,0) B` is now `TASK_COMPLETED_ON_TRANSFER_WITNESS`; neither base join could complete it independently.
- Attempt to transfer both `(1,0,0) B` and `(1,2,0) B`: **TRANSFER_STATE_CONFLICT**, entire batch rejected. Witnessed original words `BA` and `ABB` reach the same old state `(1,1,0)` but distinct new states `(1,1,0)` and `(1,1,2)`.
- Attempt to transfer `(1,2,0) B` without its rooted predecessor `(1,0,0) B`: **TRANSFER_UNROOTED**, never silently importing an unobserved prefix.
- Requesting a donor edge not in its admitted histories: **TRANSFER_EDGE_UNPROVED**, even if a complete law can compute that transition.
- New transition reads **0**; old/new owner caches hold **6 observed edges each** before and after task and conflict evaluation.

## Strict interface

```python
transfer = ExplicitEvidenceTransfer(recipient, donor, {
  'recipient_fingerprint': current_digest(recipient),
  'donor_fingerprint': current_digest(donor),
  'transfer_edges': [{'state':[1,0,0],'action':'B'}]
})
report=transfer.advance()    # zero-read audits of recipient and donor
# report.derived_digest is available only for verified compatible transfer
result=TransferredEvidenceTask(transfer, {
  'transfer_fingerprint': report.derived_digest,
  'required_edges': [
       {'state':[1,1,0],'action':'A'},
       {'state':[1,0,0],'action':'B'}]
}).advance()
```

A derived digest hashes both base witness digests, the explicitly selected ordered donor edge list, every derived paired state and admitted edge, and provenance per edge. Hashing is **not** owner authentication: exact live owner/snapshot proof still depends on the existing local pin/bridge protocol. Changing the source identity, revoking a pin, changing a version, or corrupting retained edges withholds the new result. Unrelated source owners or registry objects cannot share this witness.

## Run and verification

```bash
python run_explicit_transfer_demo.py
python -m unittest -q test_ab_chatbot_explicit_evidence_transfer.py
python finite_explicit_join_transfer.py
python -m unittest -q test_finite_explicit_join_transfer.py
```

The focused integrated module ran **23 tests** (13 new tests plus 10 tests imported from its historical fixture). The standalone finite oracle passed **5 tests**. Completed, separately run adjacent modules were `test_ab_chatbot_joint_witness_binding` (22), `test_ab_chatbot_joint_evidence_task` (11), `test_ab_chatbot_cross_pin_join` (20), `test_ab_chatbot_cross_pin_comparison` (10), and `test_ab_chatbot_owner_pin_contract` (10). Counted module runs contain **101 test executions** with overlap caused by imported test fixtures. Attempts to run other older modules in bounded groups did not finish; no full-suite pass is claimed. GitHub CI has not been verified.

## Critical boundary

This is **an explicitly certified composition of two partial relations over the exact same pinned local sources**, not arbitrary transport between different source owners or revisions. The donor edges remain historically attributed to the donor and each base join remains independently auditable; the recipient has not magically observed an edge it lacked. The new derived transfer witness is a **distinct mathematical/evidential object**, and it can be consumed only when its exact fingerprint and both live base witnesses match.

**Next:** Investigate whether a declared transport between **different** pinned versions can be witnessed via its own explicit state-level intertwining law, rather than extending this same-source case to different owners by analogy. Keep `state/current.json` owned by the separate Continuity referent.
