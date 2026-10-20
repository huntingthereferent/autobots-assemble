# Continuity Engine — finite simultaneous A/B witnesses

Research continuation, 9 October 2026. **Local integration package; not a repository merge.**

## Current referent

The existing `cyclic_action/B` record watches a B-invariant fiber. Restricted-B
conjugacy cannot be interpreted as full A/B conjugacy because A moves between
fibers. The new `finite_action/AB` contract admits a **different explicitly
scoped mathematical claim**: simultaneous conjugacy of two finite **transitive**
A/B permutation actions on the full Cartesian `F3^d` state space.

## Mathematics

Starting at the canonical state `o=(0,...,0)`, construct shortest spanning-tree
paths `p_x` using A and B. For every generator edge `x -> gx`, the loop
`p_x g p_(gx)^(-1)` fixes the source origin. After removing the `N-1`
tree edges, exactly `2N-(N-1)=N+1` Schreier path-collision loops remain.
A target origin image `y` survives if every checked source-root loop fixes `y`
in the target system.

- **UNKNOWN_COLLISION_BUDGET**: some origin images remain but the full Schreier
  basis has not been checked. These are candidates, not proof of equivalence.
- **DISTINGUISHED_FULL_AB**: no target origin image survives the *checked*
  relations. This is a finite negative certificate, even if discovered before
  exhaustion of the full basis.
- **CONJUGATE_FULL_AB**: all loops have been checked, an origin image survives,
  and its 243-state or `3^d`-state transported map has been verified to be a
  bijection satisfying H(Ax)=A'H(x) and H(Bx)=B'H(x) on **every state**.

Rooted investigation restricts the target origin image to the target origin;
unrooted investigation checks all target origin images. Transitivity and
permutation invertibility are directly verified; unsupported nontransitive
systems are rejected without a false nonconjugacy claim.

## Exact finite controls

The declared five-coordinate laws have lower two couplings
`q0(u,v)=[v=2]`, `q1(v,z)=[v=2 and z=2]` and fifth coordinate
`q2(z,y)=a_z+b_z*y (mod 3)`. These are the same families in the archived
Cyclic Action stabilizer experiment.

**Negative:** source `(a,b)=((0,0,0),(1,0,1))`, target
`((0,0,1),(0,2,2))`. Of 243 possible origin images, all are excluded by
the first **17** inspected source-root collision words (the final included
word is `ABBBBBBabababa` in this implementation's breadth-first order).
The full basis has 244 words. It would be incorrect to infer that 17 is the
minimum number of equations required under all possible orders.

**Positive:** target law is obtained by the established nine-step lower
coordinate rotation of the source coupling. The exhaustive loop criterion
constructs a 243-state A/B bijection. Three unrooted origin-image candidates
survive; a rooted correspondence does not exist for this selected pair.

**Inconclusive:** with zero or too few collision observations and candidates
remaining, the record remains UNKNOWN, even for the positive pair.

## Verification scope

- **10/10** new focused unit tests passed locally against a test-only
  reproduction of the repository's `WindowProcess.step` and `.inverse` rules.
- **10/10** original independent stabilizer/correspondence research tests
  passed from the archived standalone mathematical experiment.
- **36** selected ordered law-pair comparisons, checked both rooted and
  unrooted (72 outcomes), matched the independently implemented exhaustive
  full A/B conjugacy search: 8 positive, 28 negative (unrooted); 6 positive,
  30 negative (rooted).
- **Prior integration baseline**: 74 repository tests passed in the previous
  turn against repository `main` at commit `47c2d8e`; those tests have not
  yet been rerun against the new extension's exact repository imports.

**Verification limitation:** the remote desktop connection exhausted its
usage allowance before the new extension could be run in the real repository.
The new implementation is therefore an independently cross-checked **local
integration candidate**, not a GitHub-verified merge or a running production
research agent.

## Continuity and publication

The earlier `continuity_engine.v1` envelope remains readable by the updated
adapter. The `area` and `scope` fields distinguish `cyclic_action/B` from
`finite_action/AB`. Every serialized mathematical snapshot must be reconstructed
from its original laws and exact budget. Every outer checkpoint must carry its
parent digest; modified observations are rejected even if outer hashes are
recomputed. A supplied expected question ID anchors the frozen mathematical
question. SHA-256 is not claimed to authenticate an external author.

The research-board bridge creates only a **separate candidate checkpoint**.
It never rewrites old freezes or silently marks prior questions answered.
Full A/B results are eligible for an ANSWERED candidate only when an external
HTTPS proof locator is supplied, and the bridge checks its syntax but not the
remote content. Inconclusive investigations remain UNKNOWN.

## Boundaries

This is not a general graph-isomorphism engine for nontransitive systems,
not arbitrary alphabets or infinite state spaces, not a proof about the
physical dimensionality of reality, and not a general autonomous research
engine. The outer engine has no fixed physical dimension. Individual exact
computations require explicit finite `dimension` and `max_states` budgets.

The next genuine research boundary is to transport both existing B-only and
full A/B records through a **witnessed mathematical relationship between
question scopes** without rewriting the underlying question identities.