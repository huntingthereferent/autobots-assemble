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

## Cross-depth construction — same relation, new concrete turns

[`vertical.py`](vertical.py) continues the mathematical construction
across depth rather than pretending the worlds are identical.

For a state x at depth d+1, let `pi_d(x)` discard the final coordinate.
The A/B actions are triangular: an existing coordinate never depends on
a later coordinate. Therefore (algebraically, for all admitted depths)

```text
pi_d(T_{d+1}(x,a)) = T_d(pi_d(x),a)  for a in {A,B}
```

This is a **transition-preserving projection**, generally *not* the
bijective whole-world alignment used to identify same-depth equivalents.
The actual reachable fibers are exhaustively checked for each of the nine
parameter constructions at depths 3->4, 4->5, 5->6, 6->7.

| Projection | Nonzero-phi reachable states | New-coordinate fiber | Shortest hidden return word |
|---|---:|---:|---|
| 3->4 | 27->81 | 3 | `BBB` |
| 4->5 | 81->243 | 3 | `ABABBAB` |
| 5->6 | 243->729 | 3 | `BABABAABAAB` |
| 6->7 | 729->2187 | 3 | `ABBBAABBB` |

Each reported word returns the **entire projected state** to its origin
while moving the new coordinate. Applying the *same word* three
consecutive times produces three different higher-dimensional states
and then returns to the exact full origin: a concrete **three-turn
hidden-fiber loop**. The words vary by depth, yet each witnesses the
same relation. This behavior was checked for all eight nonzero-phi
candidate worlds at each tested depth.

**Honest zero-relation exception:** `phi=(0,0,0)` has only nine reachable
states at every tested depth. Its new fiber has size **one**; no hidden
coordinate motion can be inferred simply from the existence of another
formal coordinate. Thus do not claim that every extension adds three
reachable alternatives.

Aligned same-depth world pairs also preserve the **vertical alignment
square**: independently discovered A/B alignments at depths d and d+1
commute with the forgetful projection. Pairs from different A/B classes
are rejected as alignment failures. Separately, all 384 admitted
nonlinear **parameter constructors** commute with adding the next
coordinate:

```text
extend(C(W_d)) = C(extend(W_d))
```

That last identity concerns parameter-world construction, **not** proof
that all such operators align states across inequivalent classes.

The tested stopping point here is the **three-turn loop within each
nontrivial fiber**. It is not a terminal stopping depth: a higher
dimension may add another fiber, so finite recurring alignment does
not by itself end unrestricted construction. Determining a terminal
relational fixed point needs an explicit admitted extension class and
proof that the next construction adds no distinct relation.

Tests, from the repository root:

```bash
python -m unittest network.tests.test_arc_like_vertical -v
```

## The inverse limit: exact coherence without a last dimension

[`inverse_limit.py`](inverse_limit.py) defines the next mathematical layer,
rather than drawing or manually programming an ARC-like maze.

### Which state spaces are in the limit?

Here `S_d = F_3^d` denotes the **full** d-coordinate state space for each
fixed `phi=(0,a,b)`, d >= 3, with the forgetful map `pi_d` dropping the
newest coordinate. The inverse limit is

```text
S_infinity(phi) = { (x_0,x_1,...) : each x_i in F_3 }
pi_d(x_0,...,x_d) = (x_0,...,x_{d-1})
```

This is the full product of countably many F_3 coordinates. Every finite
prefix has a compatible extension, and it is independent of a chosen
finite cut-off. **It is not identical to the set of states reachable by a
finite A/B word from the origin.** For example, `phi=(0,0,0)` has only
nine origin-reachable states at every checked depth, even though the full
spaces still have `3^d` states.

The operations are defined coordinatewise, modulo 3:

```text
A(x)_0 = x_0+1;           A(x)_i = x_i (i>=1)

B(x)_0 = x_0
B(x)_1 = x_1+x_0+1
B(x)_2 = x_2+phi[x_1]
B(x)_i = x_i+x_(i-1)     (i>=3)
```

Every output coordinate depends only on a finite input prefix; hence
the maps are defined at **every** finite depth and on the entire inverse
limit without guessing an infinite truncation. The same dependence
proves `pi_d T_(d+1) = T_d pi_d` for both actions, all depths.

Both operations are invertible. The inverse of A subtracts one from
coordinate zero. The inverse of B recovers, in order:

```text
x_0 = y_0
x_1 = y_1-x_0-1
x_2 = y_2-phi[x_1]
x_i = y_i-x_(i-1)       (i>=3)
```

Thus the inverse limit is **closed under A, B, and their inverses**,
and these maps are continuous homeomorphisms in the product topology.
This is an exact mathematical statement about these declared rules;
it is **not** a certificate of periodicity for every infinite state
or an end to the availability of more coordinates.

### The stronger stopping point is relational, not finite-state

The nine parameter-world towers have exactly **five projectively
compatible rooted A/B equivalence classes** under the admitted rules:
the zero vector and four nonzero `+/-` pairs. Necessity follows from
the already exhaustive rooted depth-3 classification: any family of
projectively compatible state alignments must restrict to a valid
depth-3 alignment. Sufficiency holds for every dimension by the
explicit scaling map below.

Given `s in {1,2}`, `phi' = s*phi (mod 3)`, set

```text
f_s(x_0,x_1,x_2,x_3,...)
  = (x_0,x_1,s*x_2,s*x_3,...)
```

For both actions and every finite coordinate, the equations directly
give

```text
f_s(T_phi(x,a)) = T_(s*phi)(f_s(x),a)
pi_d(f_s(x))    = f_s(pi_d(x))
```

The inverse is another scaling by `s^-1` in F_3. Thus the
**same higher-level A/B relation aligns every depth**, even as each
concrete world acquires new coordinates. The family of projectively
coherent *parameter equivalence classes* has stopped gaining classes
in this scope. The unbounded state-space construction itself has **not**
terminated.

This is compatible with the earlier 384 reversible nonlinear
**world-parameter** constructors. Those constructors permute the
well-defined five tower classes but may move between *different*
classes; they are not automatically state-level conjugacies.

### Explicit false stopping witness

Starting at the infinite zero point with `phi=(0,1,2)`, the word
`BBB` has a zero projection at depth three but nonzero fourth
coordinate:

```text
pi_3(BBB(0,0,...)) = (0,0,0)
pi_4(BBB(0,0,...)) = (0,0,0,1)
```

Therefore a closed *finite* path is not necessarily a loop in the
inverse-limit state. Agreement on N coordinates never certifies
infinite equality: a later coordinate can still differ.

`TowerPoint` represents a point lazily through a stable digit oracle
and finite action history. It supplies exact requested prefixes,
inverse action witnesses, and finite prefix comparisons; it refuses
to infer equality of arbitrary infinite oracles. The finite
`audit_prefixes` result is labeled `FINITE_PREFIX_VERIFIED`,
never an unlimited proof just because tests reached depth eight.

### Proof depth, tested depth, and remaining boundary

**Algebraic all-depth claims (conditional on the declared formula):**
triangular projection coherence, existence of inverse actions,
explicit scaling conjugacy, and five projectively compatible classes
(because all possible distinct classes already fail at depth three).

**Executable checks:** the new focused tests exercise several
finite depths, arbitrary finite-support initial coordinates, action
inverses, scaling compatibility, and the `BBB` false-closure
counterexample. These checks support the implementation but are not
the sole justification for the algebraic statements.

**Not yet established:** a universal inverse A/B stopping principle;
a canonical choice of admissible constructions beyond the nine
`phi` worlds; finite-action reachability of arbitrary infinite
points; true universal periodicity; an ARC solve or rendered maze.

Run:

```bash
python -m unittest network.tests.test_arc_like_inverse_limit -v
```

**Next:** decide, mathematically, which new construction rules are
admissible at the inverse-limit level, and test whether they preserve
the five-class relational quotient or require a new relation. A
closed inverse-limit action system and terminal closure of all
possible constructions are distinct statements.

## Constructed inverse-limit worlds: nonlinear gauge and a new relation

The next mathematical movement is **construction**, not observation
or a game mechanic. [Nonlinear gauge construction](gauge_construction.py)
produces distinct transition laws by a reversible coordinate change.

### Different turns, essentially the same A/B relations

Working over F_3, at every depth d>=3, define the compatible gauge:

~~~text
G_c(x)_3 = x_3 + c*x_2^2     (if depth >= 4)
G_c(x)_i = x_i              (otherwise)
c in {0,1,2}
~~~

This map is reversible: G_c^-1 = G_-c and G_c G_e = G_(c+e).
It commutes with every forgetful coordinate projection. Construct
new action systems, without observing an external world:

~~~text
A_c = G_c A G_-c
B_c = G_c B G_-c
f_(c->e) = G_e G_-c
~~~

Then for either action T and every depth:

~~~text
f_(c->e)(T_c(x)) = T_e(f_(c->e)(x))
pi_d f_(c->e) = f_(c->e) pi_d
~~~

This is an algebraic all-depth alignment. In the nonzero-phi
example (0,1,2), c=0,1,2 generate three different B transition
laws at depth four. The same construction c -> c+1 yields the
**genuine three-turn world-construction cycle**:

~~~text
World_0 -> World_1 -> World_2 -> World_0
~~~

The world laws change at each turn; their A/B relations are
exactly aligned. At phi=(0,0,0), the three gauge laws can coincide
at depth four, so changing a parameter alone is **not** proof of
new behavior. The implementation tests that distinction.

### New relation: a counterexample to universal closure

Construct a different B law at coordinate 3:

~~~text
Original: B(x)_3  = x_3 + x_2
Split:    B'(x)_3 = x_3 + x_2*(x_2-1)
~~~

All other A/B coordinates follow the previous triangular
construction. The split rule is still reversible, and its
transitions still commute with every dimensional projection.
But the two systems are **not** projectively conjugate.

The first counterexample appears at depth four. For phi=(0,1,2),
the original full four-dimensional state space has **three**
B-fixed states, versus **six** for the split rule. Every bijective
A/B conjugacy must preserve the number of B-fixed states.
At depth three the two worlds are identical, so depth four
is the first real boundary. No bijective alignment at depth
four means no projectively compatible all-depth alignment.

This distinguishes a *new relational class* from another
coordinate representation of an existing class. The zero-phi
case also retains a fixed-point obstruction despite having
no distinct depth-four gauge laws.

### Stopping criterion at this construction layer

- **CLOSED within the declared gauge operator:** the three
  different nonzero-phi world laws are exactly conjugate, and
  construction returns to the first law on the third turn.
- **OPEN under unrestricted new construction rules:** the
  split-coupling rule is a coherent, invertible construction
  not captured by this gauge equivalence.
- **UNKNOWN beyond admitted rules:** a universal stopping
  point would require proving that all allowed construction
  operations preserve the equivalence, or preserving each new
  class as it emerges. A closed subfamily is not the end of math.

Run focused regression tests:

~~~bash
python -m unittest network.tests.test_arc_like_gauge_construction -v
~~~

These test full-state gauge conjugacy and split reversibility at
finite depths, lazy inverse-limit prefix alignment, and both
degenerate/nondegenerate construction cases. The all-depth
claims above follow from the explicit coordinate equations,
not from the finite tests alone.

## Invert A/B again — a two-relation constructed world family

The gauge experiment distinguished an exactly aligned change of
coordinates from a new B coupling. Rather than manually selecting one
more puzzle, [`coupling_family.py`](coupling_family.py) constructs
**every allowed relation** in the next smallest finite family.

For each parameter pair `phi=(0,a,b)` and `h=(0,c,d)` in
`F_3^3`, define the *constructed* A/B actions:

~~~text
A(x)_0 = x_0 + 1                        (other coordinates preserved)
B(x)_0 = x_0
B(x)_1 = x_1 + x_0 + 1
B(x)_2 = x_2 + phi[x_1]
B(x)_3 = x_3 + h[x_2]
B(x)_i = x_i + x_(i-1)                  (i >= 4)
~~~

All arithmetic is modulo three. At depth three the new `h`
relation is invisible; at depth four it is measurable. The
triangular definitions guarantee invertibility and commuting
projection to every lower dimension, regardless of the chosen
`phi,h`. These are candidate **mathematical worlds**, not
an external ARC game, solved puzzle, or new claim about A/B's
universal definition.

### Rooted A/B classifications: 81 constructions, 21 classes

The nine choices of `phi` and nine choices of `h` generate
**81** parameter worlds. Exhaustive deterministic A/B alignment
from each world's zero origin partitions their reachable states
at depth four into exactly **21** equivalence classes:

| Class size (worlds) | Number of classes | Worlds covered |
|---|---:|---:|
| 9 | 1 | 9 |
| 4 | 16 | 64 |
| 2 | 4 | 8 |
| **Total** | **21** | **81** |

This is rooted **origin-reachable** equivalence, not a claim that
all pairs are conjugate on their complete `F_3^d` state spaces.
The 21 classes were independently checked against every other
class, not inferred from a B-fixed-point count alone. All 136
within-class pairs have directly witnessed rooted alignment.

For nonzero `phi`, the projectively coherent all-depth
conjugacy between aligned worlds `(phi,h)` and `(phi',h')`
is explicitly generated by scalars `s,t in {1,2}`:

~~~text
phi' = s phi
h'(s u) = t h(u)                      for u in F_3

f_(s,t)(x_0,x_1,x_2,x_3,x_4,...)
  = (x_0,x_1,s*x_2,t*x_3,t*x_4,...)
~~~

This equation preserves A, B, and all dimensional
projections for **any depth**. Failure between the remaining
classes is already witnessed at depth four.

There is an essential exception: if `phi=(0,0,0)`, the
origin-reachable orbit never reaches `x_2 != 0`.
All nine `h` values are therefore indistinguishable *on
that particular rooted orbit*, although some have different
B-fixed-state counts on the full coordinate space.
Their equivalence cannot be promoted silently to a full-space
or full inverse-limit conjugacy. This accounts for 36 of the
136 witnessed pairs, and is explicitly preserved as
`scoped_orbit_only_pairs`.

### A deliberately constructed closed relation loop

Using the *discovered* rooted partition as input,
`rotate_within_class` constructs a permutation sending
each parameter world to the next member of its own
equivalence class. This is a **chosen construction rule**,
not a naturally unique successor forced by A/B.

Every one of the 81 concrete world descriptions changes in
one construction turn, but its rooted A/B equivalence class
is preserved. Individual cycles have lengths **2, 4, or 9**.
Consequently the whole construction permutation returns
to itself after

~~~text
lcm(2, 4, 9) = 36 turns
~~~

while every step remains within its witnessed rooted class.
This is an exact finite **relational closure under the
declared class-rotation constructor**, not an assertion
that every world individually has 36 distinct forms.

### Why this is not universal closure

An admissible change of `h` can also move to a new class,
as seen previously with `h(u)=u` versus
`h(u)=u(u-1)`. For the fixed nonzero-phi example,
the depth-four B-fixed-state counts are **3** versus
**6**. The `h=0` example has **9**. Those counts
demonstrate some non-equivalences, but do not alone classify
all 21 classes; the full A/B transition comparisons do.

If we permit new independent coupling functions at further
coordinates, there is no proof that the number of
relational classes remains at 21. The current **36-turn
construction loop is genuine but scoped**: it closes only
the chosen finite family under an operator constrained to
preserve its rooted relations. The next layer must make a
rule for admitting or rejecting additional couplings and
test the resulting quotient again. Do not infer a
universal terminal depth or invisible global closure.

Reproduce the focused tests:

~~~bash
python -m unittest network.tests.test_arc_like_coupling_family -v
~~~

## Third independent coupling — tested recurrence and finite-depth obstruction

[third_coupling.py](third_coupling.py) generalizes the preceding two-coupling
construction to independent B rules \`r_i:F_3 -> F_3\` with \`r_i(0)=0\`.
Each rule has nine possible tables (values at inputs 1 and 2). The
constructed triangular action is

~~~text
A(x) = (x_0+1,x_1,x_2,...)
B(x)_0 = x_0
B(x)_1 = x_1+x_0+1
B(x)_i = x_i + r_(i-2)(x_(i-1))          2 <= i < n+2
B(x)_i = x_i + x_(i-1)                  i >= n+2
~~~

All calculations use F_3. The first n coupling tables appear at depth n+2.
Every action is reversible by recovering the prior coordinates from low
to high. Every projection to a shallower depth commutes with A and B.

### Exhaustive, exact rooted transition-graph comparisons

Instead of pairwise guesses or fixed-point histograms,
\`rooted_graph\` traverses the entire origin-reachable deterministic
A/B action graph in canonical breadth-first order. New states get their
index at first encounter while expanding A before B. Two worlds have
identical canonical transition-index sequences **iff** there is an exact
origin-preserving, action-label-preserving bijection of their reachable
graphs. Different concrete state coordinates are explicitly allowed.

| Independent couplings | Constructed worlds | Rooted A/B classes |
|---|---:|---:|
| 1 | 9 | 5 |
| 2 | 81 | 21 |
| 3 | 729 | 85 |
| 4 (stress test) | 6,561 | 341 |

These figures are **exhaustively computed for the declared finite
families**, not a proof that the apparent recurrence
\`C(n+1)=4*C(n)+1\` holds for all n.

For three couplings, the complete 729-world partition is:

| Distinct descriptions in each class | Number of classes |
|---|---:|
| 81 | 1 |
| 18 | 4 |
| 4 | 16 |
| 8 | 64 |
| **Total classes** | **85** |

The fifth-coordinate model has reachable-state sizes
9 (81 constructions), 27 (72), 81 (64), or 243 (512).
Extending each of those 729 worlds to six coordinates yields
**the same partition**: no rooted class splits at the next layer.
The four-coupling stress test gives the class-size distribution
\`[(729,1),(162,4),(36,16),(8,64),(16,256)]\`.

### Explicit all-depth alignments vs dormant-orbit coincidences

Let \`s_2,s_3,...,s_(n+1)\` each be 1 or 2 in F_3.
The map that scales coordinate \`x_i\` by \`s_i\`
(for i>=2, extending the final scale into subsequent coordinates)
is an exact full-state, projection-compatible A/B conjugacy when

~~~text
r'_i(s_(i+1)*u) = s_(i+2)*r_i(u)
~~~

where \`s_1=1\` handles the first unscaled input coordinate.
This is checked for every related pair in **80 of the 85**
rooted classes; the coordinate formula proves those maps across
all subsequent depths. For the remaining five classes, the current
certificate supports only origin-reachable equivalence across all
members, **not full-state conjugacy**.

Why? The first zero-valued coupling forces its output coordinate
to stay zero starting at the origin; every later rule also receives
zero and becomes unobservable on that orbit. Two worlds can then have
the same complete origin-reachable A/B graph but different full-space
B-fixed-state counts: one concrete five-dimensional pair has **81**
versus **54** fixed states. Do not promote those to the same full
inverse-limit dynamical system.

### Explicit class rotation and why it isn't a universal stop

Once the exact rooted classes are computed, a chosen constructor
rotates each class's concrete descriptions. For three couplings,
the cycles have lengths 81, 18, 4, and 8; every one of the 729
descriptions moves and returns after

~~~text
lcm(81,18,4,8) = 648 construction turns
~~~

This is a valid **closed permutation of the declared rooted
equivalence classes**. It is a deliberately selected construction
rule, not a naturally forced next A/B turn. In the four-coupling
stress family, the analogous rotation order would be
\`lcm(729,162,36,8,16)=11664\`; this too would be
closure only for that chosen constructor.

### Stronger stopping result: no universal *finite depth* in this family

There is a direct algebraic obstruction, not merely a trend in the
class counts. For ANY finite triangular B construction at depth d,
let \`z(f)\` count the zero inputs of the coupling increment function.
The total number of B-fixed states in the **full** F_3^d space is

~~~text
F_d = 3 * product_(i=2 to d-1) z(r_(i-2))
~~~

The first coordinate of a B-fixed state must be 2; each intermediate
coordinate is independently restricted to the zero set of the
coupling feeding the next coordinate, and the final coordinate is
free (three choices). In particular \`F_d > 0\`.

Now admit either of these independently constructed functions at
the next coordinate:

~~~text
zero function:      r_new(u)=0         z(r_new)=3
identity function:  r_new(u)=u         z(r_new)=1

F_(d+1,zero)     = 3*F_d
F_(d+1,identity) =   F_d
~~~

**B-fixed-point counts are preserved by every bijective
B-equivariant state alignment.** The two extensions therefore
cannot be the same full-state A/B world, even though they share
the exact same d-dimensional projection. This argument works at
every finite depth in the admitted construction family.

Result: **there is no terminal finite dimension under unrestricted
independent coupling extension.** We can close the operator orbit
inside an explicitly admitted quotient, but permitting arbitrary
new couplings always gives us another distinguishable full-state
construction. This does not prove anything universal about A/B
outside this model.

### Checks and next movement

Run:

~~~bash
python -m unittest network.tests.test_arc_like_third_coupling -v
~~~

The 12 focused tests cover all 729 rooted graphs, unchanged
classification at depth six, exact scaling maps for 80 classes,
dormant-orbit/full-space separation, the 648-turn class rotation,
a fourth-coupling exhaustive stress test (6,561 worlds),
coordinate inverses/projection, symbolic fixed-point counts,
and the finite-terminal-depth obstruction.

**Next conceptual boundary:** if the goal is a relationally closed
world-construction *process*, specify the admissible construction
operators or the quotient that identifies their movements. Otherwise
the unrestricted rule family is open by the fixed-point argument.
Do not keep adding finite dimensions hoping for an accidental
universal stopping point.

## One layer above worlds — closed A/B construction processes

A count of reachable states, a finite dimensional return, or a chosen
rotation of parameter descriptions does not establish that construction
itself has closed. We now construct and compare **entire unbounded
sequences of coupling relations**, with the declared scope explicit.

[process_alignment.py](process_alignment.py) represents a process as
a finite stem of F_3 coupling tables followed by a nonempty repeating
sequence. For a process P with rules (p_0,p_1,...), its depth-d
world applies p_i at the coordinate x_(i+2). Every finite world
is a projection of the full infinite rule-generated system.
This is a mathematical blueprint, not a player action or an ARC solve.

### Same relation through different turns

Two processes P and Q have a **projectively compatible diagonal
A/B alignment** if there is a sequence of nonzero scalars
s_0,s_1,... in F_3, with s_(-1)=1, such that

~~~text
q_i(s_(i-1) * u) = s_i * p_i(u)     for all i >= 0, all u in F_3
~~~

Define the whole-state map

~~~text
F(x_0,x_1,x_2,x_3,...) =
  (x_0,x_1,s_0*x_2,s_1*x_3,...)
~~~

These equations guarantee for EVERY dimension

~~~text
F(A_P(x)) = A_Q(F(x))
F(B_P(x)) = B_Q(F(x))
pi_d(F(x)) = F(pi_d(x))
~~~

and F is invertible because every s_i is nonzero. This is full
coordinate-space equivalence, **not just matching behavior on the
orbit reached from the origin**.

For example, let r_+(u)=u and r_-(u)=-u, modulo 3.
The two repeating constructions are

~~~text
P:  r_+, r_-, r_+, r_-, ...
Q:  r_-, r_+, r_-, r_+, ...
s:    2,   1,   2,   1, ...
~~~

Every coupling rule changes after one process shift, but the
indefinite A/B relations align. After two shifts the original
rule blueprint returns. Both adjacent phases have explicit
all-depth compatible alignments. Thus this is a **genuine
two-turn closed construction-process orbit** even though the
intermediate world template differs.

Important distinction: shifting a rule *template* re-roots
the construction process. It is not itself the projection
of an already constructed higher-dimensional state.

### Finite certificate for an infinite process

For eventually periodic P and Q, the diagonal equations can
be decided using only a **finite automaton**.

After both finite stems end, the rule-pair has period
L=lcm(period(P),period(Q)). Each proof state contains:

~~~text
(periodic phase in 0..L-1, previous coordinate scale in {1,2})
~~~

There are at most 2L states. A transition is admitted only
when the next scalar satisfies the A/B equation for all
three inputs. Repeatedly discard states with no viable
successor (a greatest fixed point), then connect the finite
stem to the surviving states. If a path remains, a repeated
finite automaton state gives a **lasso**: a finite scalar
prefix followed by an exact scalar cycle. Repeating that
finite state proves the alignment for *all future*
dimensions, by induction—not by extrapolating a finite test.

If no path survives, the finite branching relation supplies
a finite-coordinate counterexample and reports the first
depth where no admitted diagonal alignment remains.
This is an **OPEN_DIAGONAL_ALIGNMENT**, not a proof that no
more general non-diagonal state conjugacy could exist.

For example, two processes can agree on their first 75
couplings and fail at coordinate depth **78** when a
new nonlinear rule is introduced. Finite prefix agreement
is not an infinite closure certificate.

The lasso verifier checks that the rule phases and previous
scalar all recur together; a false, truncated, or
self-inconsistent proposed lasso is rejected.

### Exhaustive two-rule process classification

[process_family.py](process_family.py) enumerates all
9×9 two-phase repeating process templates formed from
the nine allowed tables r(0)=0:

| Constructed templates | Diagonal process classes | Shift-closed templates |
|---:|---:|---:|
| 81 | 34 | 13 |

Exact class-size distribution:

| Descriptions per process class | Classes | Descriptions |
|---|---:|---:|
| 1 | 1 | 1 |
| 2 | 26 | 52 |
| 4 | 7 | 28 |

Nine of the 13 shift-closed templates simply repeat the
same rule every turn. **Four alternate two genuinely
different but aligned rules.** The process-level
classification uses the *all-depth* coinductive criterion,
so it is not interchangeable with the earlier
finite-dimensional rooted graph partitions (5, 21, 85,
341).

The periodic shift-orbit certificate explicitly checks
every distinct neighboring template pair in the cycle;
a single aligned edge is not enough. A nonperiodic
finite stem is currently marked UNKNOWN for a
cycle starting at the initial template, rather than
being silently promoted to periodic closure.

Run both focused test suites from the repository root:

~~~bash
python -m unittest network.tests.test_arc_like_process_alignment network.tests.test_arc_like_process_family -v
~~~

### The actual stopping boundary reached

**CLOSED:** a repeating construction process has a fully
verified cyclic orbit of templates, with exact all-depth
diagonal A/B conjugacies along *every* edge of the orbit.
States and concrete coupling laws can keep changing
while their higher-order relationship is established.

**OPEN in this quotient:** other freely admitted rule
sequences, such as alternating a linear rule with a
nonlinear rule, fail the diagonal alignment. The older
B-fixed-point theorem independently shows why
arbitrary finite-dimensional extensions cannot share
one terminal finite state-space class.

**UNKNOWN beyond this contract:** nonperiodic or
arbitrary-oracle processes, non-diagonal conjugacies,
and a universal criterion for which mathematical
construction rules should be admitted. This is a
scoped **process-level loop**, not a universal theorem
that no new A/B relation can ever be constructed.

Next mathematical referent: specify a justified family
of permissible *process transformations* (rather than
one chosen shift), and test whether the resulting
relational quotient is itself closed under composition
and further construction. Do not return to endlessly
adding dimensions to hunt for a finite stopping point.


## One layer above processes — which construction operators preserve alignment?

The previous coinductive solver compared two complete, eventually periodic
coupling-rule streams. Now the referent is **a transformation of those entire
streams**. It must be well-defined on their A/B equivalence classes, not
merely reversible on textual rule descriptions.

[process_operators.py](process_operators.py) admits periodically varying
coordinate gauges with scales \`s_i in {1,2}\`, acting on every
coordinate \`x_(i+2)\`. A chosen gauge constructs a new coupling stream Q
from a source stream P by the exact equation

~~~text
Q_i(s_(i-1)*u) = s_i*P_i(u)          for all i >= 0, u in F_3
s_(-1) = 1
~~~

The coordinate map is invertible because each s_i is a unit. The
equation guarantees exact, full-state, origin-preserving A/B
conjugacy at every finite depth, with commuting dimensional
projections. In other words, the transformation changes concrete
rules but stays inside the coinductively verified relational class.

### Closure of the process-operator layer

Gauge schedules compose by coordinatewise multiplication:

~~~text
G_s compose G_t = G_(s*t)
(G_s)^-1 = G_(s^-1)
G_1 = identity
~~~

All ultimately periodic unit-gauge sequences form a closed
group under pointwise multiplication; the same equation proves
closure algebraically for the class of admissible schedules.
The implemented, exhausted **period-two subgroup** has four
members, the four assignments \`(1,1),(1,2),(2,1),(2,2)\`.
This is a group isomorphic to \`C2 x C2\`.

The test instantiates all 81 strict two-rule repeating
construction templates, generates their gauge-transformed
**eventually periodic** streams, and verifies exact
coinductive A/B alignment for all 324 (81 x 4)
transformed pairs. It checks all 1,296 (81 x 4 x 4)
compositions against the directly composed gauge.
Nontrivial first-rule stems are intentionally preserved:
the initial input-coordinate scale is 1, whereas later
scales can vary. It would be incorrect to assume the
transformation always yields a strict two-rule period again.

A useful distinction: a gauge sends each entire process
to an equivalent process; consequently it also preserves
equivalence between *any two* aligned inputs by
transitivity. The group therefore acts trivially on the
coinductive equivalence classes, even when it changes
the concrete rule streams. This is a justified
**operator-level relational closed loop**, not just a
finite returned state.

### Operators which do NOT descend to the quotient

Even a reversible operator on process descriptions may
fail to define a consistent transformation of their
relational classes.

**1. Shift the rule sequence.** Consider two period-two
streams with the exact pair of tables:

~~~text
P = [(0,0,0), (0,0,1)] repeated
Q = [(0,0,0), (0,1,0)] repeated
~~~

P and Q admit an all-depth diagonal A/B conjugacy.
Their first zero rule leaves the next coordinate
scale free, allowing the later nonzero tables to
align after their inputs are rescaled.

After moving forward one rule:

~~~text
shift(P) = [(0,0,1), (0,0,0)] repeated
shift(Q) = [(0,1,0), (0,0,0)] repeated
~~~

The leading tables cannot be related by the required
rooted input scale \`s_-1=1\`. The alignment fails
at coordinate depth three. On the raw period-two
descriptions this shift is a reversible involution,
but it does **not** descend to their coinductive
diagonal equivalence classes.

**2. Add a fixed coupling term.** Define the reversible
rule-table operation \`R(P)_i(u)=P_i(u)+u\` mod 3.
Its third power is the identity on the descriptions.
Yet

~~~text
P_i(u) = u          (all i)
Q_i(u) = -u         (all i)

P ~ Q               (alternating diagonal scales)
R(P)_i(u) = -u
R(Q)_i(u) = 0        -> inequivalent at depth three
~~~

An operator can have a closed algebra on raw rule
strings and still break the relational quotient.
**Invertibility is not an alignment witness.**

### Exact stopping criterion and boundary

**CLOSED:** the admitted nonzero coordinate-gauge
transformations preserve all-depth A/B equivalence,
are invertible, and are closed under composition.
Any sequence of these operators remains within
its starting relational class, even if each
constructed stream looks different. The four-element
period-two subgroup has been exhaustively checked.

**OPEN on the same quotient:** unrestricted re-rooting
by shift and nontrivial pointwise rule addition are
not globally relation-preserving. They cannot be
declared admissible to the same operator-level
quotient without changing or enriching its contract.

**UNKNOWN:** a maximal family of *all* possible
non-diagonal construction operators, equivalences
of arbitrary nonperiodic rule oracles, and closure
of a new enlarged quotient admitting shifts and
rule additions. Nothing here proves universal
construction closure for A/B beyond the
defined mathematical model.

Run:

~~~bash
python -m unittest network.tests.test_arc_like_process_operators -v
~~~

**Next referent:** either retain the proven
gauge-construction quotient as the scoped stopping
certificate, or construct a richer equivalence
that handles a shifting root and test it against
the same counterexamples. Do not erase the
root boundary by declaring every turn identical.


## Root transport — preserving the relation when the process shifts

**Current referent:** process-level A/B equivalence under shifted coupling-rule
templates. The former coinductive comparison fixed the incoming scale to 1.
That condition is valid at the original root but can fail after a simultaneous
rule shift, even when the full underlying alignment previously existed.

**Construction:** [root_transport.py](root_transport.py) shares the existing
`PeriodicProcess` and `next_scales` API. Its separately named boundary-aware
witness carries `b=s_(k-1)` when both processes shift by `k` rules. A marked
world explicitly changes the first B boundary coupling to
`B_g(x)_1=x_1+g(x_0+1)`; marking is essential—merely changing the boundary
witness does not conjugate the old unmarked worlds.

**Evidence:** exact coinductive lasso checks, full-state marked A/B transition
comparisons at finite depths, explicit witness composition/inversion, a
75-rule delayed break, and complete pairwise comparison of the 81 strict
two-phase rule templates. Allowing transported boundary scales gives
**23 classes** (sizes 1×1, 4×2, 18×4) instead of the original
root-normalized **34**. Simultaneous one-step shift acts on the 23-class
quotient with **five fixed classes and nine two-class cycles**. The
root-transport prototype's **14 focused regression tests** check
these conditions.

**Preserved boundary:** This is a new marked-root representation, not an
identity between shifted unmarked states or a claim about arbitrary
nonperiodic, non-diagonal, or native ARC behavior. Reversible addition of
coupling terms can still break the marked equivalence. Plain shift on
processes with nonempty arbitrary stems is not invertible in general.

**Artifacts:** [research report](ROOT_TRANSPORT.md),
[implementation](root_transport.py), and
[tests](../../network/tests/test_arc_like_root_transport.py).

**Reproduction:** `python -m unittest network.tests.test_arc_like_root_transport -v`

**Next referent:** test the combined action of boundary-aware shifts
and admissible gauges on marked process objects, preserving both
composition witnesses and counterexamples to unrestricted operations.

## Marked process operator interchange — gauge × transported shift

[Detailed witness and proof](MARKED_OPERATORS.md) ·
[implementation](marked_operator_system.py) ·
[11 regression tests](../../network/tests/test_arc_like_marked_operator_system.py)

**Current referent:** operations on complete eventually periodic A/B construction
processes, one layer above individual shifting or rescaled worlds.

A **marked arrow** contains both processes, their incoming root gains, and the
exact coinductively verified scalar alignment. The new construction combines
two operations:

- A boundary-aware coordinate gauge `U=(u_-1,u_0,u_1,...)` is invertible and
  acts by explicit A/B conjugacy on every coordinate.
- A process shift carries the *existing witness tail*, with new incoming scale
  `s_(k-1)`, instead of resetting the boundary or recomputing a different
  witness when zero rules permit several choices.

They satisfy a witnessed **interchange square**: shifting and then applying
shifted gauges agrees with gauging and then shifting, *provided* the source
gain is transported as `u_(k-1)`. This equality checks both process streams,
both marked gains, and the entire aligned scalar sequence, not just a quotient
class or a finite return time.

The eight period-two boundary gauges form a closed `C₂ × C₂ × C₂` group.
The finite audit checked **5,184** gauge compositions over the 81 two-rule
templates and **256** gauge/shift squares over one genuine nonidentity
marked morphism. Eleven local regression tests additionally cover
stemmed processes, full-state A/B transitions through depth seven,
composition/inversion, ambiguous witness choice, and known counterexamples
to unrestricted rule addition.

**CLOSED for the admitted relation:** coordinate gauges preserve exact
coinductive alignment and commute with *witness-aware marked shifts*.
The statements extend algebraically to the declared periodic gauge
schedules and eventually periodic process rules.

**NOT CLOSED as an unrestricted group of all constructions:** plain shift
of an unmarked process can still break equivalence; arbitrary finite stems
need not admit inverse shifts; coupling-rule addition still breaks some
marked alignments. No universal A/B stopping point or native ARC solve follows.

**Next referent:** characterize admissible operators on *marked arrows*,
rather than forgetting root gains and witnesses and reintroducing the
same quotient failure.

## Witness-complete quotient — the missing finite-head arrows

[Research report](MARKED_QUOTIENT.md) ·
[implementation](marked_quotient.py) ·
[14 regression tests](../../network/tests/test_arc_like_marked_quotient.py)

The marked gauge/shift interchange work showed that the **witness
must travel**. The next question is whether the eight period-two
gauges actually exhaust the diagonal marked equivalences they were
being used to represent.

We first close all 81 strictly two-rule process templates, each with
either root gain, under the eight marked boundary gauges. **162 seed
objects become 270 distinct marked objects:** 108 objects acquire a
genuine one-rule stem because incoming root gain and periodic gauge
phase are independent.

The eight operators give **36 exact group-action orbits** of sizes
2 (one orbit), 4 (three orbits), and 8 (32 orbits). But the previously
defined full coinductive diagonal A/B witness regards the same 270
objects as only **34 aligned classes**: one size-2, three size-4,
28 size-8, and two size-16 classes.

The discrepancy consists of **two verified bridges**, each joining
two periodic-gauge orbits of eight objects. Their witnesses have a
finite prelude before their periodic scale, so no strict period-two
gauge captures them. A concrete bridge has source scales
`(1,2,2,2,...)`, rather than any `(a,b,a,b,...)`. Those are
different *operator-level* witnesses even though both
mathematically preserve marked A/B transitions.

**CLOSED:** all 270 objects are preserved by the eight selected
gauges; the finite coinductive marked-diagonal partition is complete
for those objects under that specified equivalence.

**OPEN:** treating the eight-element periodic gauge group as
a *complete* description of all marked-diagonal arrows. It misses
two finite-head bridges. **Those bridges are already admitted by
the separate finite-stem gauge system below.** The new
`MissingGaugeBridge.stem_gauge()` produces each exact finite-stem
operator from its original certified witness, verifying full
process equality and the root mark; new regression checks exercise
gauge-arrow realization and witness-preserving shifts.

**Next:** independently admit or reject a **non-diagonal** operator
using a full-state witness or a concrete obstruction. Do not
revisit the solved finite-head diagonal bridge layer.

No universal inverse A/B closure or native ARC result is implied.



## Finite-stem gauges and composite operator normal forms

[Research report](STEMMED_OPERATOR_SYSTEM.md) ·
[implementation](stemmed_operator_system.py) ·
[regression tests](../../network/tests/test_arc_like_stemmed_operator_system.py)

The marked gauge/shift construction extends from strictly periodic gauge
schedules to a **finite gauge stem followed by a repeating tail**.
Its scalar equation preserves full-state A/B alignment, including the
explicit marked incoming root. The original witness tail survives a shift
without being recomputed at ambiguous zero couplings.

Exact algebraic interchange gives a normal form for any finite word in
the *admitted* language of gauge changes and forward root shifts:

```text
arbitrary admitted gauge/shift word
    = total forward shift + combined endpoint gauges
```

The normal form includes both root marks and the entire ultimately periodic
scalar witness, not merely a matching process quotient label. Local checks
tested 12 gauge schedules against 81 rule templates (11,664 composition
cases), 864 interchange squares and 340 short mixed operator words.
Nine focused local tests passed with the existing marked-arrow API fixture.

**CLOSED:** this chosen eventually periodic diagonal-gauge system and its
witness-carrying forward shifts are coherent. **OPEN:** unrestricted rule
addition and non-diagonal processes. A shift that drops a finite prefix is
not invertible; the normal form does not claim to restore it.

**Next:** probe an independently justified operator beyond the diagonal
gauge family, retaining full-state evidence or a precise break witness.

## Non-diagonal state construction — closed relation, open old schema

[Mathematical report](NONDIAGONAL_TRANSPORT.md) ·
[implementation](nondiagonal_transport.py) ·
[12 focused tests](../../network/tests/test_arc_like_nondiagonal_transport.py)

**Current referent:** The marked finite-stem diagonal system has
been constructed and its rooted witnesses preserved. Rather
than repeating the existing diagonal gauges, construct a
different state-space operation and check both relational
preservation and its representation boundary.

A nonlinear shear `H_c(x)_2=x_2+c*x_1^2` over `F_3` fixes
the origin, is invertible, and commutes with all finite-depth
projections. Conjugating the marked A/B actions by this map
gives constructed laws `T_c=H_c T H_-c`. The rule `c->c+1`
generates three **concretely different** B laws with an exact
three-turn return. Their all-depth relations align via
`H_(e-c)`; therefore, this is a **valid non-diagonal
construction**, not a newly inequivalent A/B class.

It also reveals a hard schema boundary: every old
`Process` has `B(0,0,0)_2=0`, while the sheared construction
has `B_c(0,0,0)_2=c` for c=1,2 (for both allowed root
gains). No old table `p_0(x_1)` satisfying `p_0(0)=0`
can represent those concrete actions. Being outside the
old description **does not** mean the worlds are
mathematically non-equivalent: their exact H-conjugacies
are explicitly known.

The marked-arrow representation now carries this general
alignment as `H_target * M_witness * H_source^-1`,
retaining the literal coinductive scalar witness inside
the overall nonlinear map. Compatible arrows compose
and invert. Re-rooting transports the marked boundary
and the original witness tail; arbitrary deleted stems
are not claimed to be recoverable.

Independent finite arithmetic checked 58,806 conjugacy
comparisons, 9,801 inverse identities, and 9,720
projection identities through depth seven for a
nontrivial marked-rule case. This is different from
running the 12 committed Python regression tests; those
tests require explicit execution for a PASS assertion.

**CLOSED** for this chosen three-element shear-conjugacy
group. **OPEN** for the old process-rule schema.
**UNKNOWN** whether other admitted non-diagonal
constructions introduce genuinely new relational
classes or can be described by a minimal extended
coupling system.

**Next:** define a justified broader transition-law
schema that carries the new x0 dependence rather than
silently suppressing it. Test independent non-diagonal
operators against it. This remains math-first,
not an ARC game implementation.

## Two-predecessor construction: preserve alignment, expose new relation

[Detailed mathematical record](WINDOW_TWO.md) ·
[standalone rule engine](window_two.py) ·
[12 regression tests](../../network/tests/test_arc_like_window_two.py)

The non-diagonal shear `H_c(x)_2=x_2+c*x_1²` showed the old
one-input coupling representation was too narrow. The smallest
**bounded-width extension needed for this witness** allows a
nine-entry `q_i(u,v)` table for each B-coordinate increment:

~~~text
B(x)_(i+2) = x_(i+2) + q_i(x_i,x_(i+1))
~~~

The old native `p_i(v)` embeds as `q_i(u,v)=p_i(v)`,
and the earlier nonlinear shear compiles *directly* to two
finite-prefix tables plus the unchanged eventually periodic tail:

~~~text
q_0(u,v)=p_0(v)+c*((v+g*(u+1))²-v²)
q_1(u,v)=p_1(v-c*u²)
q_i(u,v)=p_i(v), i>=2
~~~

The standalone transition engine does not rely on the
previous coordinate-shear implementation at runtime.
By triangular dependence, every such B update is
reversible and commutes with all coordinate projections.
The former shear-conjugate worlds therefore remain
**equivalent, now expressible within the enlarged grammar**.

A separate single-entry construction `q_0(2,0):0→1`
on the zero-coupling world with root gain one changes
the number of **full depth-three B-fixed states
from 9 to 6**. That invariant rules out *every* bijective
action-label A/B conjugacy; it is **a genuinely new
relation**, not another representation of the same world.

Independent arithmetic verified 117,612 exact compiled
transition matches, 235,224 inverse identities and
116,640 projection identities across full finite states
at depths 3–7. These are not Python CI results.
Twelve Python regression tests are committed to
reproduce the extended-schema construction and
witness boundaries.

**CLOSED:** admitted triangular two-input actions are
invertible and dimensionally coherent; existing sheared
A/B arrows retain exact alignment when recompiled.

**OPEN:** treating all independently generated two-input
rules as equivalent; the fixed-point counterexample
explicitly breaks such a claim.

**Next:** classify a finite justified collection of
two-input couplings under witnessed full-state A/B
equivalence, keeping the conjugated shear family
separate from truly new rule classes.

## A constructed full-state family — four classes, three turns each

[Mathematical proof and independent audit](WINDOW_FAMILY.md) ·
[construction and exact relation certificates](window_family.py) ·
[13 regression tests](../../network/tests/test_arc_like_window_family.py)

The next bounded two-input construction separates **relation-preserving
movement** from genuinely **new relations** without treating every
description as a distinct class. The family fixes the root gain
at one and sets all couplings beyond x2 to zero. For
k in {0,1,2,3} define a q0 increment D_k(u,v)=1 when
u=2 and v<k, otherwise zero. For c in F3 conjugate that
world by the non-diagonal H_c shear:

~~~text
q_(k,c)(u,v) = D_k(u,v)+c*((v+u+1)^2-v^2)    (mod 3)
~~~

There are 12 distinct concrete q0 tables. The mapping
H_(e-c) explicitly conjugates any two worlds with
the same k at **every** dimension. It fixes the root
and preserves all coordinate projections.

At depth three the four k levels have B-fixed
state counts **9, 6, 3, and 0**. Those quantities
must be preserved by any bijective B-labeled
state correspondence. Consequently the 12
constructed worlds divide into exactly **four
full-state A/B classes**, three aligned worlds
per class. This is stronger than a rooted-orbit
classification and does not require assuming
all state maps are diagonal.

Two independent construction operators now
make the distinction operational:

- Shear S: (k,c)→(k,c+1 mod3) is an exact three-turn
  cycle preserving the class; all three laws are
  concretely different.
- Support E: (k,c)→(k+1,c) for k<3 changes the
  class at every turn, with a new fixed-point count.
  E commutes with S wherever both are defined.
  At k=3, E reaches an explicit **WALL**, not a
  forced return to an unrelated class.

The inverse and projection laws remain exact
because the coupling is triangular. The independent
finite implementation checked 235,224 conjugacy
assertions and 233,280 projection assertions
through depth seven, with no failures. The new
13-test Python module is committed but is not
recorded as CI-passing without a runner.

**CLOSED:** the selected 12-world family under S.
**OPEN:** attempts to identify its four distinct
full-state classes.
**UNKNOWN:** arbitrary nine-entry coupling
tables and nonzero couplings in later coordinates.

**Next referent:** construct an independent
two-input coupling outside the chosen support row.
Check whether the old invariant suffices to
separate it or whether a new witness is needed.

## Second independent two-input relation — a word-fixed witness

[Detailed proof and arithmetic audit](WINDOW_BRANCH.md) ·
[24-world constructor and pairwise certificates](window_branch.py) ·
[13 regression tests](../../network/tests/test_arc_like_window_branch.py)

The earlier support axis k=0..3 exhausted one selected
row of `q0(u,v)`. The next actual construction changes
a **different row**: add one pulse `e` at `q0(0,0)`,
independently of the support values `q0(2,v)` and
the non-diagonal shear chart `c`:

~~~text
q_(k,e,c)(u,v) =
    [u=2 and v<k]
  + e*[u=0 and v=0]
  + c*((v+u+1)^2-v^2)            mod 3
k in {0,1,2,3}, e in {0,1}, c in {0,1,2}
~~~

This produces **24 distinct** two-predecessor B laws.
The old B-fixed state count is **unchanged** by e,
and so the previous invariant cannot classify the
new family. The stronger relation witness is the
action word `BBB`.

For all constructed worlds and every depth d>=3:

~~~text
#Fix(B)   = (3-k)*3^(d-2)
#Fix(BBB) = 3^d                if e=0
            2*3^(d-1)         if e=1
~~~

At depth three the second count is **27 versus 18**.
This is a **conjugacy-invariant obstruction** despite
equal single-B fixed-point counts. For example,
`BBB` returns the zero origin in the e=0 world but
changes x2 by one in the e=1 world at k=c=0.

Within each fixed (k,e), the explicit nonlinear
`H_(target_c-source_c)` gives an invertible
projectively compatible A/B conjugacy across all
depths. Different k values are excluded by Fix(B),
while equal k but different e are excluded by
Fix(BBB). Therefore the admitted finite family
contains exactly **eight full-state A/B classes**
of three concrete laws each.

The constructive axes have separate meanings:
S (shear) closes after three turns and preserves
the relation; E (support) or P (pulse) move to
genuinely different relational classes until their
declared finite domains reach walls. S, E and P
commute wherever defined, but a common square is
not proof that all their arrows are alignments.

Independent arithmetic verified 470,448 shear
conjugacy comparisons, 156,816 inverse assertions,
155,520 projection assertions and 156,816 B/BBB
fixed-count checks through depth seven. Thirteen
committed Python tests additionally specify exact
regression witnesses; their CI execution status
must be verified separately.

**CLOSED:** exactly eight classes for this declared
24-world family. **OPEN:** sufficiency of Fix(B)
alone. **UNKNOWN:** completeness of the pair
(Fix(B),Fix(BBB)) for any wider arbitrary table
family or universal A/B construction.

**Next:** independently change another q0 entry
while preserving *both* known word-fixed counts.
Look for a stronger word invariant or an exact
non-diagonal alignment rather than assuming that
colliding invariants imply equivalence.

## Third independent two-input relation — five-letter word obstruction

[Mathematical proof](WINDOW_WORD_COLLISION.md) ·
[36-world construction and exact classifier](window_word_collision.py) ·
[14 regression tests](../../network/tests/test_arc_like_window_word_collision.py) ·
[independent arithmetic audit](window_word_collision_arithmetic_audit.py)

The first additional coupling after the 24-world branch is
a *balanced* edit outside the old support row:

~~~text
q0(1,0) += 1
q0(1,1) -= 1                        (mod 3)
~~~

The edits preserve both previously established
invariants, **Fix(B)** and **Fix(BBB)**. A
shortest distinguishing fixed-point-count word is
`AABAB`, whose depth-three fixed-state count
changes **9 → 3**. Exhaustive enumeration shows
no different fixed-point count for any A/B word
of length one to four in the compared worlds.
This is minimal for *fixed-word counts*, not
for all possible trajectory observations.

Constructing across the four support levels, three
shear charts, and three explicitly admitted
pulse/balance branches yields **36 distinct full-state
A/B laws**. Their relation quotient is exactly
**12 classes of three worlds each**. Every ordered
pair is classified with an explicit shear witness
(108 pairs) or a word-fixed obstruction from B
(972), BBB (144), or AABAB (72).

The balanced edit and the previous pulse edit are
competing extensions of the ordinary world. The
simultaneous (pulse=1, balanced=1) construction
remains explicitly **UNKNOWN**, rather than
silently adding it to the same quotient.

The independent arithmetic audit checked 705,672
state conjugacy comparisons, 235,224 inverse
identities, 233,280 projection identities and
540 word-formula checks over complete state
spaces through dimension seven. Fourteen Python
tests and a targeted GitHub workflow were added;
CI success must be observed separately.

**CLOSED:** these twelve full-state classes in
the declared 36-world family and their exact
all-depth non-diagonal shear witnesses.
**OPEN:** sufficiency of the earlier two-word
signature; AABAB provides its counterexample.
**UNKNOWN:** the withheld combined pulse/balance
edit and arbitrary further couplings.

**Next referent:** construct the withheld (1,1)
branch and test full-state *and rooted* A/B
relations separately. A collision of all three
known word counts must not be treated as an
automatic alignment.

## Completed two-edit family — full-state equivalence versus rooted history

[Exact mathematical record](WINDOW_COMBINED.md) ·
[48-world construction and pairwise certificates](window_combined.py) ·
[15 regression tests](../../network/tests/test_arc_like_window_combined.py) ·
[independent arithmetic verifier](window_combined_arithmetic_audit.py)

The previously withheld (pulse=1, balanced=1)
coupling is now admitted, completing a **48-world**
finite two-predecessor construction:
four supports × two pulses × two balanced edits
× three nonlinear shear charts.

The earlier one-letter, three-letter, and five-letter
fixed-word invariants all collide between pulse-only
and combined worlds at the same support. A new
six-letter word, `ABABAB`, separates them at
the two **middle** support levels:

~~~text
support k     pulse-only Fix(ABABAB)    combined
    0                     18               18
    1                     18                9
    2                      9                0
    3                      0                0
~~~

At k=1,2 this proves full-state inequivalence.
At k=0,3, the systems are instead exactly
conjugate by an additional nonlinear state
translation that *moves the origin*:

~~~text
R(x0,x1,x2,tail) = (x0,x1+2,x2+f(x1),tail)
f(1)=2, f(0)=f(2)=0                in F3
F_(c->d)=H_d R H_(-c)
~~~

The inverse uses R^-1. Direct substitution
proves full-state A/B alignment at all
depths for these two support levels.
But R sends the zero origin to a different
state. More strongly, two explicit A/B
words reach the same state in the source
rooted world and different states in
the target. **No rooted conjugacy exists.**

Thus the same 48-world family has two
provably distinct quotients:

- **14 full-state classes:** 12 classes of
  three worlds; two classes of six.
- **16 origin-preserving classes:** 16
  classes of three worlds.

All 2,304 ordered pairs are certified
by exact rooted (144) or nonrooted (36)
state maps, or fixed-word obstructions
from B (1,728), BBB (288), AABAB (72),
and ABABAB (36). The 36 nonrooted
maps have literal root-collision witnesses.

The independently computed finite audit
checked 311,040 shear conjugacy comparisons,
103,680 inverse identities, 101,088 projection
identities, and 768 fixed-word formula checks
over all 48 worlds through depth six.
Fifteen new regression tests and a targeted
GitHub workflow are committed, but they
must not be labeled CI-passing without
a confirming run.

**CLOSED:** both full-state and rooted
classifications for this declared 48-world
family. **PRESERVED:** the marked
difference between a conjugacy that
moves the root and a root-preserving
alignment. **UNKNOWN:** additional
unbounded coupling constructions and
universal inverse A/B closure.

**Next referent:** represent the root-changing
map as a distinct *marked arrow* with explicit
source-image mark and literal word collision;
check composition and prevent its accidental
use as an origin-preserving equivalence.

## Pointed A/B arrows — the origin is an actual witness

[Mathematical record](WINDOW_MARKED_ARROWS.md) ·
[pointed-arrow implementation](window_marked_arrows.py) ·
[14 focused regression tests](../../network/tests/test_arc_like_window_marked_arrows.py)

The 48-world result exposed **36 full-state
conjugacies that do not preserve the original
marked zero state**. The operator layer now
represents these as `StateArrow` objects whose
endpoints are `PointedWorld(world, mark)`
objects, with the literal H/R map factors
retained through inversion and composition.

Promotion to a `MarkedArrow` requires the
checked equality

~~~text
F(source.mark) = target.mark
~~~

All 144 direct canonical-origin conjugacies
pass this check. The 36 other full-state
conjugacies explicitly fail it. The new
`transport_target_mark` is a separate
mathematical operation: it creates a **new
pointed target**, retaining the previous
target zero mark and the positive-word
root collision proving the originals
were not rooted-equivalent.

For a pulse-only to combined transition
at support 0 or 3, the target changes from
the original mark `(0,0,0)` to the
transported mark `(0,2,d)`, where d is
the target shear chart. No existing
world law changes, and no earlier
rooted incompatibility is overwritten.

Of 2,304 ordered world pairs, 2,124
are still obstructed; 144 directly admit
a marked arrow; 36 require explicit
target re-marking. All 180 admitted
marked arrows have tested inverses
and compositional mark conservation.
The two original full-state quotient
counts remain **14 unmarked classes
versus 16 canonical-root classes**.

The exact new module and test bytes
match their locally tested Git blobs.
Fourteen focused tests passed in a
local reproduction of the existing
coordinate laws; the GitHub workflow
must independently confirm repository
integration before claiming CI passed.

**CLOSED:** explicit mark conservation,
witness-preserving inversion and
composition for this declared family.
**WALL:** a moved origin is not the same
pointed world. **UNKNOWN:** general
marks and non-H/R state operators.

**Next:** admit a separate witnessed
root-changing construction without
ever silently identifying the two
original canonically marked objects.

## Independent central root translation — witnessed pointed paths

[Mathematical report](WINDOW_ROOT_TRANSLATION.md) ·
[operator implementation](window_root_translation.py) ·
[14 regression tests](../../network/tests/test_arc_like_window_root_translation.py)

The pointed-arrow contract now admits an independently
constructed operator `T_r(x)_2=x2+r` (over F3).
It changes the chosen point but **not** the world's
A/B transition laws. Because the declared 48-world
family's increments depend only on x0,x1 and all
higher couplings are zero, `T_r` commutes with
both A and B. It also commutes with the earlier
H shears and R fiber-shifts and has an exact
three-turn return `T_1^3=id`.

New `TranslationFactor` witnesses coexist
with exact `ConjugacyFactor` H/R witnesses.
`OperatorPath` retains their literal sequence;
`PointedOperator` admits a path only when
the **source mark is mapped exactly to the target
mark**. Inversion reverses the factor order,
while composition requires equal pointed
middle endpoints.

The previously established 36 nonrooted
H/R bridges cannot be silently promoted.
After an **explicit** target re-marking,
each can be composed with the three
independent T shifts while preserving the
original positive-word collision proof.
Across the verified 48-world family:

- 48×3 = **144** distinct pointed marks
  at the same original world laws.
- 144 existing canonical-rooted pair
  alignments give **432** translated routes.
- 36 original unrooted alignments give
  **108** pointed routes after explicit
  mark transport, never with the original
  canonical target mark.
- Total **540** route certificates, without
  changing the previous 14 full-state
  versus 16 canonical-root class counts.

The exact new module and test file hashes
match 14 locally passing tests, alongside
14 earlier pointed-arrow tests (28 in all)
against reproduced existing world equations.
The GitHub workflow now includes the new
checks; CI result remains separate.

**CLOSED:** A/B central translation symmetry
and witnessed composition in this **zero
higher-coupling** family. **UNKNOWN:** whether
the translation survives nonzero rules that
read x2 or general infinite state marks.

**Next:** construct the first higher
coupling that reads x2, then check at what
depth the previously proved central
translation stops commuting with B.
Preserve its scope rather than declaring
universal closure.

## Coordinate-translation centralizer of two finite-field generators

[Standard mathematical terminology](TERMINOLOGY.md) ·
[Centralizer theorem and counterexamples](TRANSLATION_CENTRALIZER.md) ·
[Exact table criterion](translation_centralizer.py) ·
[13 regression tests](../../network/tests/test_arc_like_translation_centralizer.py)

The original labels **A** and **B** are retained only as
the two explicitly defined *generating transformations*.
Their serialized compositions are documented with
standard right-to-left functional notation; historical
project shorthand is not the name of the mathematics.

For the triangular two-predecessor system over
`F3`, the coordinate translation
`T_r(x)_2=x2+r` belongs to the **centralizer of the
generated action** (for nonzero r) if and only if:

~~~text
q1(u,v+r) = q1(u,v)     for all u,v
q2(u+r,v) = q2(u,v)     for all u,v
~~~

Equivalently, q1 is independent of its second
argument and q2 of its first. The only other
rules cannot read x2 and impose no condition
on this particular coordinate translation.

A coupling `q1(u,v)=v` breaks commutation with
the second generator **first at dimension four**.
The independent coupling `q2(u,v)=u` breaks
it **first at dimension five**, even though
all lower-dimensional checks agree. Nonzero
couplings `q1(u,v)=u` and `q2(u,v)=v`
*preserve* the translation symmetry, proving
that a nonzero higher coupling alone does
not constitute an obstruction.

The translation subgroup is either
`{T0,T1,T2}` (order three) or `{T0}`
(trivial), with an exact table-level
certificate. The new pointed-system adapter
refuses a nonidentity translation when its
commutation certificate fails, and requires
the chosen point to be transported explicitly.

The 13 tests passed locally against the exact
newly committed source and test files plus
a local reproduction of the existing
two-predecessor dependency. GitHub workflow
results remain separately verifiable.

**Next:** test a possible higher-coordinate
correction to a broken translation and
require an explicit bijective conjugacy
or a finite periodic-orbit obstruction.

## Compensated coordinate translation — exact symmetry or fiber obstruction

[Proof and counterexamples](CORRECTED_TRANSLATION.md) ·
[finite-field construction](corrected_translation.py) ·
[13 focused tests](../../network/tests/test_arc_like_corrected_translation.py)

The uncorrected coordinate translation `x2 -> x2+r`
can fail to belong to the centralizer of the two
generating transformations when a higher coupling
reads `x2`. This does **not** automatically mean
no corrected symmetry exists.

In the declared linear family `B(x2)=x2+a`,
`B(x3)=x3+b*x2`, `B(x4)=x4+c*x2`
(with all further increments zero), the exact
answer depends on the lower-coordinate drift:

- If `a != 0`, define
  `K_r(z)=a^(-1)*(r*z+binom(r,2))`.
  The map translating x2 by r and translating
  x3 by b*K_r(x2) and x4 by c*K_r(x2)
  **commutes with both generators**, is
  invertible at every depth and defines
  an order-three centralizer action.
- If `a=0` and `b=c=0`, the original
  coordinate translation is already central.
- If `a=0` with a nonzero higher
  coefficient, an explicit B-fixed-fiber
  mismatch blocks *any* equivariant lift
  that preserves x0,x1 and adds r to x2.
  The first obstruction occurs in dimension
  **four** when b is nonzero, or **five**
  when only c is nonzero.

The fixed-fiber obstruction concerns the
prescribed class of lifts, not all conceivable
state conjugacies. The pointed-system
implementation requires a full five-coordinate
distinguished point and retains individual
correction factors through inverses and
composition.

The exact new source and regression files
match **13 locally passing Python tests**,
executed against a local copy of the existing
two-predecessor interpreter. GitHub CI
status remains a separate verification.

**Closed:** this declared linear centralizer
lifting problem with either a constructive
conjugacy or exact fixed-fiber obstruction.
**Unknown:** the corresponding cohomological
equation when `q0(x0,x1)` is nonconstant.

**Next:** test nonconstant lower-coordinate
couplings by solving or obstructing the
correction equation along full orbits of
the induced lower-coordinate B action.

## Boundary and next movement

- **Evidence depth:** mathematical model + executable finite checks, not empirical ARC performance.
- **Preserved:** candidate source rule, labeled transition graph, proposed alignment, full reachable-state witness, counterexample on break.
- **Unknown:** an A/B-general inverse-construction definition, a canonical alignment generator, a sound unbounded stopping theorem, an ARC-like gameplay realization.
- **Next:** solve or obstruct the corrected-translation equation for a nonconstant lower-coordinate coupling by its full finite-state orbit structure, preserving the pointed witness.

Related but separate: [runtime/ARC_NATIVE_OBSERVATIONS.md](../../runtime/ARC_NATIVE_OBSERVATIONS.md) captures observed native ARC moves; it does not generate these worlds. Repository-wide A/B evidence boundaries remain in [AB_CONTRACT.md](../../AB_CONTRACT.md).
