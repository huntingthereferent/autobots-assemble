# Trial 07: preserve the simultaneous arrival as an unresolved source event

Original WORLD Trial 07 locates a first-arrival tie between the two finite
source-derived segments within the declared `[1.35, 1.40]` entry-height
bracket. Its nominal virtual-mechanics model reports an arrival near
`1.3910443961`. The original two-face source solver stops at the tie with
`unresolved-multiple-contacts`, recording no outgoing impulse.

The new `world_trial07_handoff.py` is a domain-specific adapter, *not* a
revision to general A/B construction and *not* a new contact solver.

A dedicated CI job checks out exact original commit
`bda4bc271a985965558fc8f0d48e89fee07161d0`, executes Trial 07 and
its independent native verifier, then carries its original surfaces, arrival
candidate, explicit unresolved label, and nine nearby controls into A/B.
It independently reconstructs the resulting 32-operation neutral ledger,
preserving all ten observations and source identity. At the exact tie there
is **no comparison claiming an expected physical outcome**; an unresolved
source result stays unresolved. Nearby controls are retained, never
promoted into a made-up tie resolution.

The adapter verifies the record's declared shape, roster, source flags, and
preserved claims. It does **not** establish that arbitrary input bytes came
from the claimed commit, that the geometry or physics is correct, or that a
material physical object was measured. Original source-native execution and
its independent geometry/trajectory verifier are separately required before
a physical-model claim can be attributed to this trial.

Unchanged: original WORLD Trials 07–21 and their branch lineage, native
source code, general WORLD objects/operations, W13, ARC, NIH, renderer, and
the existing A/B All Rights Reserved notice.

Next boundary: investigate underdetermined multi-contact dynamics using
source-owned constraints and genuinely discriminating measurements. Do not
manufacture a single outgoing movement from a tied arrival.
