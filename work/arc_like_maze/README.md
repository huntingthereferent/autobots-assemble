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

## Automatic alignment and finite closure — constructed witness

The original `math.py` accepted a hand-written alignment. The new
[`alignment.py`](alignment.py) discovers rooted A/B correspondence directly
from generated transition graphs. Starting with the paired origins, it follows
both action labels; deterministic reachability forces every next image.
If two action words refer to the same source state but distinct target
states (or vice versa), it returns `OPEN` with those two words as an
explicit counterexample. If bounded exploration runs out, it returns
`UNKNOWN`, not false non-equivalence.

All nine 3D candidate relations `phi=(0,a,b)` have been classified by
that discovery process into **five** equivalence classes:
`(0,0,0)` alone, and the four paired classes
`[(0,0,1),(0,0,2)]`, `[(0,1,0),(0,2,0)]`,
`[(0,1,1),(0,2,2)]`, `[(0,1,2),(0,2,1)]`.
Concrete states often differ, but the labeled A/B transitions correspond.

An explicit **inverse-construction operator** transforms
`phi -> 2 phi (mod 3)`. It acts on the generated structure, not on
an observed ARC frame. Since multiplication by 2 is invertible and
`2*2=1 (mod 3)`, this operator permutes all nine candidates in one
fixed point and four two-cycles. `certify_finite_family` checks **every**
allowed family member and its entire reachable transition graph, also
requiring the successor to stay within the family and the constructor
to permute all its members. For that precisely declared finite family,
the result `CLOSED_FOR_DECLARED_FAMILY` is a justified stopping
certificate under indefinitely repeated applications of **that**
construction rule.

The certificate is **not** evidence that every inverted A/B extension
is closed. Raising the dimension, selecting a different nonlinear
construction, or adding operators changes the admitted family and can
break this alignment. No ARC solve, native observation, live agent,
rendered maze, or universal stopping theorem is implied.

Run from the repository root:

~~~bash
python -m unittest network.tests.test_arc_like_inverse_ab network.tests.test_arc_like_alignment -v
~~~

## One layer up — construction operators and an exact scoped stopping point

This extends the same construction experiment without changing A/B or the
native ARC observer. Here a *construction turn* is an operation on the
relation parameter `phi=(0,a,b)`, not a player action. The A/B transition
graphs of those produced worlds are still compared with the existing
`discover_alignment` evidence contract.

For the nine constructed 3D worlds, the exact rooted A/B classes were
exhaustively classified as the zero vector and four nonzero pairs
`(a,b) ~ (2a,2b)` in F_3. Distinct concrete worlds may therefore preserve
the same A/B structure. To promote a construction operator C to the quotient,
the **next-layer compatibility** requirement is:

~~~text
W ~ W'   implies   C(W) ~ C(W')
~~~

It is different from requiring each individual edge `W -> C(W)` to stay
in its original class. A valid construction can move between classes while
maintaining a reproducible, mathematically well-defined *relation between
classes*. Do not conflate these levels.

### Nontrivial closed construction cycle

The shear rule `H(a,b)=(a,a+b)` (mod 3) produces:

~~~text
(0,1,0) -> (0,1,1) -> (0,1,2) -> (0,1,0)
~~~

The first three worlds occupy **three distinct A/B equivalence classes**;
they are not falsely declared equivalent. However, the *construction rule*
is unchanged throughout and `H^3(a,b)=(a,b+3a)=(a,b)` for every parameter.
Thus we have an exact, nontrivial loop at the construction layer, with
different intermediate turns. `SCALE`, `SHEAR`, and `SWAP` together
preserve the quotient (zero plus four nonzero classes), yielding two closed
strongly connected components of sizes one and four.

### Full affine boundary: exhaust, don't guess

[`affine_scan.py`](affine_scan.py) enumerates all F_3-affine maps
`v -> Mv+t` on the two relation coordinates:

| Witness | Count |
|---|---:|
| All affine maps (3^6) | 729 |
| Reversible affine maps (9 times 48) | 432 |
| Quotient-compatible maps, including singular maps | 89 |
| Reversible quotient-compatible maps | 48 |
| Distinct induced quotient permutations | 24 |

Exactly the 48 invertible **linear** maps (`t=0`) preserve the
original A/B classes among all reversible affine maps. They compose
within the admitted 48; the resulting maps on the four nonzero
equivalence classes yield all 24 permutations of those classes,
fixing the zero class. This is an **exhaustive, finite scoped closure**
for the declared reversible affine constructor family.

Mathematically: there are 8 choices for the first nonzero matrix
column and 6 choices for an independent second column, giving 48
invertible matrices; 9 translations give 432 reversible affine maps.
If `t=0`, scalar-equivalent points stay scalar-equivalent. If
`t!=0`, let `v=M^{-1}t`; then the equivalent inputs `v` and `-v`
map to `2t` and `0`, which are *not* equivalent. Therefore no
nonzero translation can be admitted as a reversible class-preserving
constructor. The 48 linear maps form a group under composition,
and their induced quotient actions are closed under composition.

This certificate does **not** prove that arbitrary nonlinear
construction, additional dimensions, altered A/B transitions, or
unrestricted inverse A/B construction is closed. Those are new
mathematical referents requiring new witnesses.

### Boundary: when a constructor destroys the alignment

For example, translation `T(a,b)=(a+1,b)` maps the initially aligned
pair `(1,0) ~ (2,0)` to `(2,0)` and `(0,0)`, respectively.
The old A/B quotient no longer determines a unique successor class.
The algorithm reports `OPEN_AB_QUOTIENT` with two action-word
counterexamples for each broken pair; refining the quotient under
this extra operator produces **nine singleton classes**. A finite
parameter orbit still exists, but the earlier meaningful relational
compression has been lost. Do not promote this to the same closure.

[`operators.py`](operators.py) records constructed transitions,
exact A/B counterexamples, quotient congruence failures, partition
refinement and closed strongly connected quotient components. Empty
inputs or bounded search exhaustion remain `UNKNOWN` rather than
inventing a proof.

Reproduce all focused tests from the repository root:

~~~bash
python -m unittest network.tests.test_arc_like_inverse_ab network.tests.test_arc_like_alignment network.tests.test_arc_like_operators network.tests.test_arc_like_affine_scan -v
~~~

**Next required mathematical layer:** introduce explicitly admitted
non-affine/higher-depth construction rules and re-run the same
family-closure and quotient-compatibility contracts. Do not render a
maze or claim the universal stopping point until those rules have
their own witnesses.

## Nonlinear construction — maximal reversible closure at this layer

The previous affine certificate was not the maximum set of reversible
construction moves preserving the observed nine-world A/B quotient.
[nonlinear.py](nonlinear.py) generates **all bijections** of those nine
constructed worlds respecting the five witnessed A/B-equivalence classes.

Given the exact A/B classes `[1,2,2,2,2]`, one singleton must be fixed.
Four two-point classes may be permuted independently, and each paired
class may independently reverse its orientation. Consequently the maximal
reversible group *for this finite quotient* has size

```text
4! × (2!)^4 = 24 × 16 = 384
```

This is the finite wreath-product structure `C2 wr S4`.
Of its 384 maps, 48 are the affine maps already admitted; the other
336 are genuinely **nonaffine** permutations of constructed world
parameters. Each induced map of the five quotient classes fixes the
singleton and permutes the other four. Thus there are 24 different
quotient motions, with 16 underlying ways to realize any one quotient
motion. These new choices do **not** create new quotient classes.
They create different concrete construction turns that align to the
same relational structure.

Examples:

- **Nonaffine pair flip:** exchange just the two worlds in one aligned
  pair. It is not affine and its square is the identity, but its
  quotient action is the identity throughout.
- **Four-class cycle:** an admissible constructed-world permutation
  cycles the four nonzero quotient classes and returns on the fourth
  turn. Intermediate worlds occupy different classes, but the same
  construction law persists.
- **Many-to-one sink:** map every world to the zero-class world.
  This still respects equivalence but is *not* invertible, so it
  is not a reversible closed-loop certificate.
- **Translation:** maps formerly equivalent inputs to inequivalent
  outputs and remains **outside** the old quotient.

The verification independently enumerates all `9! = 362,880`
bijections, finding precisely the 384 constructed by the generator.
All `384 × 384 = 147,456` pairwise compositions are checked for
membership in the admitted group. Every generated world map preserves
the A/B alignment between the members of each equivalence pair.

**Higher-depth test:** at depths 3, 4, 5, and 6, the *within-depth*
nine-parameter families were classified into the same five relative
A/B classes. This is bounded evidence, **not** an unbounded depth
theorem. A three-dimensional world has 27 states and its
four-dimensional extension has 81; they are **not** related by the
bijective rooted state alignment required here. Do not mistake
stable quotient shape for equivalence across dimensions.

Run:

```bash
python -m unittest network.tests.test_arc_like_nonlinear -v
```

**Current stopping point:** maximal reversible nonlinear permutations
for the declared finite nine-world quotient. **Not** a universal
inverse A/B stopping point; the new required construction referent is
the extension of these relations to arbitrary depth or new state-space
constraints without presupposing the five-class quotient.

## Boundary and next movement

- **Evidence depth:** mathematical model + executable finite checks, not empirical ARC performance.
- **Preserved:** candidate source rule, labeled transition graph, proposed alignment, full reachable-state witness, counterexample on break.
- **Unknown:** an A/B-general inverse-construction definition, a canonical alignment generator, a sound unbounded stopping theorem, an ARC-like gameplay realization.
- **Next:** test higher-depth constructors and new relations that do not presuppose the finite five-class quotient. Preserve bounded witnessed equivalence separately from universal closure. Keep the project math-first.

Related but separate: [runtime/ARC_NATIVE_OBSERVATIONS.md](../../runtime/ARC_NATIVE_OBSERVATIONS.md) captures observed native ARC moves; it does not generate these worlds. Repository-wide A/B evidence boundaries remain in [AB_CONTRACT.md](../../AB_CONTRACT.md).
