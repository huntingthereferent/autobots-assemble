# Engine 2 — continuation witness re-entry at the repository research boundary

[Actual research entry/exit implementation](engine_two_continuation.py) · [16 focused regression tests](../../network/tests/test_arc_like_engine_two_continuation.py) · [preceding mathematical two-input grammar](window_two.py)

## Current referent

The [separate local Engine 2 continuation experiment](ENGINE_ONE.md) established that an inconclusive observation need not trigger an unrelated comparison. A bounded inquiry may instead continue the same admitted transformation, preserving its original domain and the observations already obtained.

The locally executed prototype carried the following controls on a declared 81-state, B-invariant fiber of a five-dimensional two-input system:

- At budget eight, fixed-point counts match and the correct outcome is **UNKNOWN**.
- At budget nine, the negative control has **81 versus zero** fixed states under B^9, proving the restricted B-actions are not conjugate.
- At budget 27, a separate positive control constructs and verifies a bijection intertwining the two restricted B-actions. At budget 26 its outcome remains **UNKNOWN**.
- At budget 27, the negative control has equal fixed counts again, but its earlier ninth-step distinction remains stored.

The new task is to verify these controls **through the repository's own research entry/re-entry/exit route**, using the actual generator implementation and existing Engine 2 handoff objects, not a second hand-written transformation.

## Entrances and boundaries

The committed [EngineTwoContinuationKernel](engine_two_continuation.py) exposes:

~~~python
witness = EngineTwoContinuationKernel.enter(left_engine, right_engine)
saved = witness.advance(8).snapshot()
reentered = EngineTwoContinuationKernel.reenter(
    saved, left_engine=left_engine, right_engine=right_engine
)
result = EngineTwoContinuationKernel.exit(reentered.advance(9))
~~~

Each input is an actual [ConstructedEngine](engine_one.py) object. Its law must be an actual [WindowProcess](window_two.py) carrying exactly three two-input coupling tables and the explicit zero higher tail. The research entry calls **WindowProcess.step** for every B transition; it does **not** copy the B arithmetic into another production module.

This is an explicitly supplied WindowProcess research law. The previous Engine 1 inverse-construction factory still selects only its previously declared families; the new research path does **not** claim Engine 1 can automatically generate this law, construct a new mathematical grammar, or invoke external persistent execution without a caller. Engine 1's existing construction algorithms were not modified.

The declared research domain is **all 81 states satisfying x0=2** inside F3^5. This domain is verified B-invariant and B-bijective for both supplied laws. The fiber is **not A-invariant**, so the observation cannot imply simultaneous A/B conjugacy.

The snapshot includes the exact two-process coupling tables, supplied ConstructedEngine version/history/phase provenance, generator B, relation scope, the literal 81-point domain, a source/action fingerprint, the sorted fixed-state index sets for every previously observed continuation, each actual observation budget, and any constructed B-intertwining bijection.

The snapshot fingerprint is a **local integrity check**, not an externally trusted signature. Re-entry also recomputes every old observation from the real WindowProcess action, and rejects a changed source, incorrect budget/depth, altered result label or unsupported domain.

## Mathematical stopping conditions

**UNKNOWN** means that no distinguishing periodic-count invariant and no verified bijection has been established through the available observation budget. This never implies equivalence.

**DISTINGUISHED** requires an actual mismatch of conjugacy-invariant fixed-point counts on the declared B-invariant fiber and retains its **earliest** witnessing depth. Ordinary continuation stops there. An explicitly labeled further **audit continuation** may preserve and append later observations without erasing the existing distinction.

**EQUIVALENT_FOR_B_ONLY** requires a complete constructed bijection H of all 81 states with the 81 intertwining equalities

~~~text
H(B_left(s))=B_right(H(s))
~~~

verified for every watched state. The positive control enables this construction when both actions have been observed to return on the entire declared fiber, rather than converting equal counts into equivalence by assumption. The construction uses full cycle decompositions and checks the entire mapping.

The two controls are question-guided and bounded. The ninth/27th observations are *first discriminating or positive under the declared fixed-point continuation policy*, not universal minimum proof complexities for these transformations.

## The two actual five-coordinate fixtures

All generators use old-state values and arithmetic in F3. The two-input process rules are:

~~~text
gain=1
q0 rows: (1,2,0), (0,0,0), (1,1,1)
q1(v,z)=z²
q2_A=all zero
q2_B=1 only at (z,y)=(1,0), otherwise 0
q2_C=1 only at (z,y)=(1,1), otherwise 0
higher tail=zero

negative pair: laws A and B
positive pair: laws B and C
watched space: x0=2 in F3^5
watched generator: B only
~~~

These are independently constructed test fixtures, not an assertion that the exact unpublished 13-test experiment's original laws were recovered.

The negative restricted B-actions consist of **nine cycles of length 9** versus **three cycles of length 27**. Their B^1 ... B^8 fixed-state counts all vanish, B^9 has 81 versus zero, and B^27 has 81 versus 81. The origin-shaped witness on the declared fiber is

~~~text
B_A^9(2,0,0,0,0)=(2,0,0,0,0)
B_B^9(2,0,0,0,0)=(2,0,0,0,1)
~~~

The positive pair consists of two different laws with matching restricted 27-cycle structure and a constructed 81-state B-intertwiner. Its B^26 WATCH remains UNKNOWN and B^27 admits the verified B-only correspondence.

## Evidence actually executed versus committed

**Executed locally:** the preceding self-contained prototype's 17 regression tests were rerun in the working environment and passed. That prototype reproduces the generator rule but does not import the repository's real WindowProcess.

**Committed to the repository:** the new actual-WindowProcess research entry and 16 focused regression tests. Those tests exercise exact kernel entry/exit, real generator calls, the two saved-and-reentered negative/positive controls, source-engine version checks, scope and observation mutation rejection, proof-only status promotion, inverse/periodic cycle outcomes, and the independent Engine 1 construction-grammar wall.

**Verification limit:** a successful GitHub CI run of the new 16-test suite has not yet been observed. The earlier local 17-test success is not presented as execution of the new repository suite.

Run from repository root:

~~~bash
python -m unittest network.tests.test_arc_like_engine_two_continuation -v
~~~

## Current result and next referent

**INTEGRATED AT A BOUNDED RESEARCH ENTRY:** a typed reproducible Engine 2 continuation path now accepts existing ConstructedEngine handoffs with explicitly declared WindowProcess laws, stores and replays native generator observations, and returns UNKNOWN, a distinguishing invariant, or a verified B-only equivalence without changing the watch.

**NOT INTEGRATED:** an autonomous global runtime routing mechanism, external event persistence, the original unpublished experiment's tests, unrestricted domain selection, a simultaneous A/B conjugacy engine, autonomous mathematical grammar invention, or native ARC execution.

**Next mathematical boundary:** align this typed continuation witness with the repository's persistent research/event handoff contract. Require explicit source/identity, observation ancestry, budget history and domain coverage; test recovery after an actual persisted handoff while preserving the stronger/smaller relation scope. Do not merge it with within-law selected-symmetry composition unless a proven conjugacy establishes the appropriate transport.
