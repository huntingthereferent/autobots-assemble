# ARC-like maze — inverted A/B, mathematics first

**Current referent:** construct a mathematical world by reversing the A/B direction, then find where *differing turns preserve the same underlying relations*. This is a new ARC-**like** research artifact, **not** an official ARC environment, native ARC observation, or a proven universal definition of A/B.

## Direction

Observation would start with two given states and extract preservation/change/relations. **This experiment starts from proposed relational constraints and constructs candidate states and transitions.** Do not design rooms, objectives, obstacles, user controls, or renderings first. Visual and interactive representations come after a mathematical construction witness.

~~~
proposed P / delta / R
  -> inverse construction: candidate (X, A, B)
  -> A/B relational alignment with another construction
  -> check whether distinct states/transitions have the same relation
  -> extend construction one layer and test whether alignment survives
  -> MOVE / OPEN / CANDIDATE / UNKNOWN, with witnesses
~~~

This is a search over candidates, not a mathematically unique inverse. Constraints may be underdetermined. The toy implementation enumerates nine different 3D variants of a stated finite-field construction; it must not be mistaken for inversion of all possible A/B relations.

## Aligned recurrence, not literal state repetition

For two reachable action systems with labeled transitions T and T', a proposed correspondence f is an *exact rooted relational alignment* if it is a bijection of reachable states, maps the selected origins, and for **both** actions and **every** reachable state satisfies:

~~~
f(T(x, a)) = T'(f(x), a)      for all x, a in {A, B}
~~~

This allows x != f(x) and different rendered worlds or different concrete turns while the action relations are preserved. It is stronger than matching screenshots, sharing a state count, returning to an exact origin, or merely having a projection from a deeper world to a shallower one. Other legitimate relation-preserving notions may later be required, but their contracts must be explicit instead of silently calling them identical.

**Construction closure is sought through this same alignment**: a repeated state graph isn't the stopping rule. Generate the next world, align its relations against an earlier world, and continue to the next construction to try to break the alignment. An aligned pair gives CANDIDATE; a further aligned layer gives CANDIDATE_NEXT_LAYER_VERIFIED. This is finite evidence, **not proof of indefinite or terminal closure**. A true stopping certificate would also need a justified invariant/closure rule over *all permitted subsequent constructions* (or a formally bounded generator exhausted under an explicit contract). Missing alignment is UNKNOWN; a counterexample is OPEN.

## Reproducible bounded witness

math.py constructs worlds over F_3^d with two actions:

~~~
A(x) = (x0 + 1, x1, x2, ...)
B(x) = (x0, x1 + x0 + 1, x2 + phi(x1), x3 + x2, ...)
~~~

All arithmetic is mod 3; the x2 term is omitted at depth two. Enumeration varies phi with phi(0)=0. The 3D worlds phi=(0,1,2) and phi=(0,2,1) do not share literal state values for every action sequence but align through f(x0,x1,x2)=(x0,x1,2*x2 mod 3). The nonlinearly changed phi=(0,1,1) supplies a counterexample to blindly aligning by identity. A fourth dimension preserves the three-dimensional *projection* while introducing new distinct states; it is **not** full aligned closure of the 3D world.

Run from repository root:

~~~bash
python -m unittest network.tests.test_arc_like_inverse_ab -v
~~~

## Boundary and next movement

- **Evidence depth:** mathematical model + executable finite checks, not empirical ARC performance.
- **Preserved:** candidate source rule, labeled transition graph, proposed alignment, full reachable-state witness, counterexample on break.
- **Unknown:** an A/B-general inverse-construction definition, a canonical alignment generator, a sound unbounded stopping theorem, an ARC-like gameplay realization.
- **Next:** generate and test alignments as outputs of the construction process, not manually supplied maps; then seek an invariant proving closure across *all* permitted future extensions. Keep the project math-first.

Related but separate: [runtime/ARC_NATIVE_OBSERVATIONS.md](../../runtime/ARC_NATIVE_OBSERVATIONS.md) captures observed native ARC moves; it does not generate these worlds. Repository-wide A/B evidence boundaries remain in [AB_CONTRACT.md](../../AB_CONTRACT.md).
