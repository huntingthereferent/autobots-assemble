# A/B finite chatbot — two independently verified transport links

**Date:** October 13, 2026. **Boundary:** The finite A/B-labeled generators are scoped mathematical test operations, not the meaning of A/B as a relational language.

## Result

The unchanged CrossPinJoin and CrossScopeIntertwiningTransfer modules are composed with `ab_chatbot_two_hop_transport.py` across **three separately pinned owner pairs (six independent source snapshots)**. A donor-witnessed selected B edge is explicitly mapped to the middle scope and independently observed there; the newly certified middle edge is then explicitly mapped to the final scope and **independently observed again**.

| Scope | Old phi | New phi | Base joined words | Original admitted edges |
|---|---|---|---|---:|
| Donor | (0,0,1) | (1,0,1) | `AB`, `B` | 3 |
| Middle | (0,0,0) | (0,1,2) | `A`, `BAA` | 4 |
| Final | (2,0,0) | (2,2,1) | `A`, `BAA` | 4 |

The endpoint maps declare exactly the two old and new endpoints of the selected edge at each hop. First hop: donor NEW endpoint `(1,2,1)` maps to middle NEW `(1,2,0)`; second hop: middle old/new `(1,2,0)` map to final old/new `(1,2,2)`. These are **declared hypotheses**, checked at each scope's actual local owner transitions. All other states are deliberately unmapped.

With already-completed base joins, observations progress as follows (old/new transition counts **within each pair**):

| Stage | Donor | Middle | Final |
|---|---|---|---|
| Base evidence | 3/3 | 4/4 | 4/4 |
| Link 1 witnessed | 3/3 | 5/5 | 4/4 |
| Link 2 witnessed | 3/3 | 5/5 | 5/5 |
| New task consumes chain | 3/3 | 5/5 | 5/5 |

The final derived partial relation has **6 paired states, 5 admitted labeled edges**, all replayed under the *final* old and new laws. A task requiring `(1,1,2) A` (original final witness) **and** `(1,0,0) B` (newly certified final edge) completes **2/2** on that *new fingerprinted witness*, with zero additional task reads. Base joins are untouched.

Negative controls: incorrect second-side mapping or changed final law -> `CHAIN_INTERTWINING_CONFLICT` with independently observed endpoint mismatch; missing second map entries -> `CHAIN_MAPPING_INCOMPLETE`; exhausted final source budget -> `UNKNOWN_BUDGET`; revoked donor, middle or final pin, changed source revision, or tampered retained observations -> success withheld. A first-link success never counts as a successful entire chain.

## Files / commands

- `ab_chatbot_two_hop_transport.py`: in-process pinned-source chain adapter + typed final task.
- `test_ab_chatbot_two_hop_transport.py`: **14 focused integration tests** (run class `TwoHopTransportTests`; not the inherited imported fixtures).
- `finite_two_hop_transport.py`: independently checks two successive selected squares using fully declared 27-state finite laws, without HTTP or remote provenance.
- `test_finite_two_hop_transport.py`: **6 standalone mathematical tests**.
- `run_two_hop_transport_demo.py`: six-owner local demo, recording independently counted observations.
- `TWO_HOP_TRANSPORT_RESULTS.json`: recorded demo evidence.
- `TWO_HOP_TARGETED_REGRESSIONS.json`: completed adjacent module checks.

From an extracted archive directory:

```
python run_two_hop_transport_demo.py
python -m unittest -q test_ab_chatbot_two_hop_transport.TwoHopTransportTests
python -m unittest -q test_finite_two_hop_transport.TwoHopFiniteTests
python finite_two_hop_transport.py
```

Local completed verification: **14 integration + 6 finite + 12 prior cross-scope + 11 joint task + 13 same-pin transfer + 10 cross-pin join + 10 exact-owner tests = 76 passed**. Earlier three regression commands had *incorrect class selectors* and ran zero real tests; they were corrected and rerun, and are not included. Full historical suite and GitHub CI were **not** run. All prior base files are kept byte-for-byte unchanged.

This is **two selected commuting squares**, not a functor, a proof of general composition across any sources, full finite-system conjugacy, or a physical A/B transfer. The standalone finite checker knows its complete laws and cannot authenticate an external source; only the integrated owner's live local binding and replay support its limited provenance status.

**Next:** Explicitly detect conflicting composed endpoint maps across *two different chain routes* before selecting a route, and compare independently observed chain costs; keep each route's owner evidence disjoint.
