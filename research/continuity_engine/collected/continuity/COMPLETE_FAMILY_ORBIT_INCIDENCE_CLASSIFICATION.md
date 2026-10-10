# Continuity Engine — exact classification of the 702-law finite family by orbit incidence

**Status:** Verified finite mathematical result and locally tested software integration. This report does not claim universal A/B equivalence, native ARC execution, unrestricted dimensions, or verified performance against remote mathematical engines. The repository was not modified.

## Current referent

The prior three-layer A→B→A generator-orbit-closure census distinguished **18** fingerprints among **39** full-action conjugacy classes. Extending the same alternating closure further saturated the state space and did not refine the classification. We continued the same finite actions but examined orbit closure under composed action words, and finally intersections of *linked* orbits at different base states.

State space is **exactly** \(X=\mathbb F_3^5\), 243 points. Let \(x=(u,v,z,y,t)\), all arithmetic mod 3:

\[
A(u,v,z,y,t)=(u+1,v,z,y,t),\qquad
B_q(u,v,z,y,t)=(u,\ v+u+1,\ z+[v=2],\ y+[v=2\land z=2],\ t+q(z,y)).
\]

We classify the declared linear-in-\(y\) coupling family

\[
q(z,y)=a_z+b_zy,\quad a,b\in\mathbb F_3^3,\quad b\ne(0,0,0),
\]

containing \(3^3(3^3-1)=702\) laws. All generator-word strings act **left to right**. Lowercase `a` and `b` denote inverse actions.

## Native invariants: generator-word orbit and linked intersection

For a word \(w\) in \(A,a,B,b\), define its full finite cyclic orbit from \(x\):

\[
O_w(x)=\{w^k(x):k\ge0\};\qquad C_w(E)=\bigcup_{x\in E}O_w(x).
\]

A complete simultaneous conjugacy \(H\), if it exists, satisfies for every \(w\):

\[
H(O_w(x))=O'_w(H(x)),\qquad H(C_w(E))=C'_w(H(E)).
\]

Consequently, the histogram over all 243 roots of \(|C_{w_r}\cdots C_{w_1}(\{x\})|\) is an unrooted-conjugacy invariant.

A second invariant arises *without discarding where each orbit is rooted*. For words \(p,q\) and a link word \(r\), define

\[
J_{p,q;r}(x)=|O_p(x)\cap O_q(r(x))|.
\]

This quantity is transported by any simultaneous conjugacy: \(J_{p,q;r}(x)=J'_{p,q;r}(H(x))\). Its **histogram over the 243 starting points** is therefore an unrooted invariant. Agreement of such fingerprints alone never implies equivalence in unrestricted actions.

## Four observations — complete classification for the declared family

The witness catalog consists of:

| Stage | Observation | Distinct signatures among the 39 verified positive transport orbits |
|---:|---|---:|
| 1 | Histogram of \(|C_A(C_B(C_A(\{x\})))|\) | **18** |
| 2 | Add histogram of \(|C_{ABBabbbb}(C_{BA}(\{x\}))|\) | **30** |
| 3 | Add histogram of \(|C_{BABa}(C_{ABab}(\{x\}))|\) | **33** |
| 4 | Add histogram of \(|O_{BAB}(x)\cap O_{Ab}(A(x))|\) | **39** |

The counts refer to the **combined** fingerprint through each stage, not the number of values for any one histogram alone. These are four *sufficient* features for this family, not a proof of minimum word length or globally minimal invariant count.

Six pairs of previously distinct classes still shared the first three observations. All six separate at stage four. For example:

\[
q_1: a=(0,0,0),\ b=(1,1,2),\qquad
q_2: a=(0,0,0),\ b=(1,2,2).
\]

Their first three fingerprints agree, but their stage-four histograms differ:

| \(J_{BAB,Ab;A}(x)\) | \(q_1\) root count | \(q_2\) root count |
|---:|---:|---:|
| 0 | 81 | 81 |
| 1 | 54 | 54 |
| 2 | **102** | **93** |
| 5 | **6** | **15** |
| Total | 243 | 243 |

This is a finite, explicit obstruction to full \(A/B\) conjugacy, with no origin-image trial needed for that pair.

## Why 39 is a complete answer here

The known state transports are:

\[
R(u,v,z,y,t)=(u,v,z+1,y+[z=2],t),\quad
S(u,v,z,y,t)=(u,v,z,y,2t).
\]

The corresponding **coupling-law** moves satisfy

\[
q_{R}(z+1,y+[z=2])=q(z,y),\qquad q_S(z,y)=2q(z,y).
\]

They commute, with orders 9 and 2 respectively. On the declared 702-law family, their group \(C_9\times C_2\) has **39 orbits containing 18 laws each**. A state-space \(R\) or \(S\) transports the full labeled A/B action, not merely the B-cycles.

The reproducible experiment checked **682,344 full generator-intertwining equations**, namely \(702\) laws × \(243\) states × \(2\) transported maps \(R,S\) × \(2\) generators \(A,B\), and established that the four-part signature is constant within every one of those positive orbits.

It also verified that the **39** orbit signatures are pairwise distinct. Therefore:

1. Two laws in the same \(R,S\) orbit are **positively** conjugate by an explicitly composed state transport.
2. Two laws in different orbits are **negatively** distinguished by at least one of the four conjugacy-invariant histograms.
3. No other full A/B conjugacy mergers are possible within these 702 laws.

Thus, independently of the previous exhaustive 243-candidate negative searches, the scoped census proves:

- **39** unrooted full A/B conjugacy classes, each containing **18** coupling laws;
- **12,636** positive **ordered law pairs** (including self-pairs);
- **480,168** negative ordered law pairs.

These counts refer to ordered *pairs of coupling laws*, **not the number of distinct intertwiners** for any pair. The four-part fingerprint is complete for this **declared finite family**, but not a general solution to graph isomorphism or all dynamical systems.

## Independently reconstructed evidence

An additional implementation computes A and B edges directly from the finite-field equations without importing `WindowProcess`, the orbit-incidence module, or the continuity engine. It separately generates composed permutations, generator-word cyclic orbits, complete closures, and linked intersections.

Across **702/702** laws, it verified:

- **341,172** independent labeled A/B state transitions (702×243×2);
- all **702 complete four-part fingerprints** against the separately implemented `WindowProcess` path;
- **zero** discrepancies and exactly **39** distinct fingerprints.

These are independent finite implementations, not formal mechanized proof certificates. The finite enumeration, explicit positive transports, and conjugacy invariance establish the claimed classification inside the declared space.

## Continuity Engine integration

- `research/action_orbit_incidence.py` preserves a separate, typed `finite_action/AB_orbit_incidence` question. It records the exact laws, full state-space dimension, entire feature catalog, source and target histograms, first negative witness, and SHA-256 question identity.
- `research/continuity_engine.py` adds `start_orbit_incidence(...)`, replaying every saved observation on re-entry, retaining earlier snapshots and forbidding question/scope/budget replacement.
- `research/continuity_board_bridge.py` stages the new results separately without overwriting the six frozen earlier questions. A negative result lacking a published witness remains REVIEW; matching histograms remain UNKNOWN.
- **The incidence adapter never claims positive A/B conjugacy from matching invariants.** Positive intertwiners are established separately by the existing full-action correspondence verifier and the explicit R/S transport experiment.

The new extension passed **98/98** local compatibility regressions (the earlier 84 plus 14 new tests), including tamper rejection, truncated UNKNOWN → verified negative, a positive control, transport preservation, and read-only board staging.

**Verification boundary:** the regression harness uses **test-only reproductions** of repository modules because remote computer capacity was unavailable. This is not a new run against GitHub's exact current source. No repository, published research checkpoint, or existing Cyclic Action mathematics was altered.

## Reproduction

From the package root:

```bash
python test_support/run_local_compatibility.py
PYTHONPATH="$PWD:$PWD/test_support/test_only_modules" python examples/reproduce_702_orbit_incidence.py
PYTHONPATH="$PWD:$PWD/test_support/test_only_modules" python examples/independent_orbit_incidence_crosscheck.py
PYTHONPATH="$PWD:$PWD/test_support/test_only_modules" python examples/build_incidence_witnesses.py
```

Machine-readable results are `examples/orbit_incidence_702_results.json`, `examples/independent_orbit_incidence_results.json` and the four replayable saved handoffs. Old results from the A/B intersection package remain included.

**Next referent:** generalize the construction of *linked orbit incidence witnesses* to other admitted finite action spaces, keeping positive equivalence evidence separate from negative invariants and retaining an explicit computational budget. Do not assume four features distinguish arbitrary generators or other coupling grammars.