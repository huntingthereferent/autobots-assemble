# Inverted A/B — First word-invariant collision beyond the support row

**Current referent:** [The twelve-world full-state construction](WINDOW_FAMILY.md)
was partitioned into four exact A/B classes by counting states fixed under B.
Its independent support extension reached a scoped wall only because that
selected row of the two-predecessor table was exhausted. The next admissible
construction should leave that row, then check whether the old invariant is
complete. It is not.

**Solved condition for this movement:** construct a new B increment outside
the old support row, find a *same-count* counterexample, upgrade the
witness criterion to fixed points of an A/B **word**, and prove an exact
partition of a clearly delimited finite new family.

## Declared construction and witnesses

Work over F3 with the same marked root gain one:

~~~text
A(x) = (x0+1, x1, x2, x3, ...)
B(x) = (x0, x1+x0+1, x2+q0(x0,x1), x3, ...)
~~~

All additions are modulo three. Every higher coupling q_i (i>=1)
is identically zero. These are genuine *full-state* transition laws,
not just reachable paths from the origin.

There are three **independent** parameters:

1. k ∈ {0,1,2,3} is the previously witnessed support level:
   D_k(u,v)=1 when u=2 and v<k, zero otherwise.
2. e ∈ {0,1} is a new pulse, supported only at the cell (u,v)=(0,0),
   outside the old support row u=2.
3. c ∈ {0,1,2} is the earlier nonlinear coordinate shear chart.

The new coupling q0 is the exact nine-entry table

~~~text
q_(k,e,c)(u,v) =
    D_k(u,v)
    + e*[u=0 and v=0]
    + c*((v+u+1)^2-v^2)
                mod 3
~~~

The first two terms are independently created coupling relations.
The last term is the established H_c state conjugacy; it is **not**
an arbitrary extra relation. This yields 4×2×3=**24**
distinct concrete transition tables, all representable by
the existing [two-predecessor interpreter](window_two.py).

## The old invariant collides

B can fix x1 only when x0=2. In that row the shear
term disappears, because x0+1=0 in F3, and the new pulse
disappears because it is supported exclusively at x0=0.

Consequently **both pulse values have the exact same
number of B-fixed states** for any finite depth d≥3:

~~~text
# Fix(B; W_(k,e,c), depth d) = (3-k)*3^(d-2)
~~~

Thus neither that count nor the earlier four-class
classification can distinguish W_(k,0,c) from W_(k,1,c).

Take the origin and k=c=0:

~~~text
x = (0,0,0)
Original: B^3(x) = (0,0,0)
Pulse:    B^3(x) = (0,0,1)
~~~

This is a concrete, rooted three-turn counterexample
to identifying the two constructed worlds. The old
single-B *fixed-state count* fails; the full action
word B^3 succeeds.

## The stronger word-fixed invariant

Consider three consecutive B transitions.

- For x0=0, B increments x1 by 1, so x1 visits
  all three F3 values exactly once. The new
  pulse occurs exactly once, incrementing x2
  by e. The shear contribution telescopes.
- For x0=1, x1 advances by 2, again visiting
  each value, but the pulse does not apply.
  The shear contribution telescopes.
- For x0=2, x1 never advances; B adds the same
  q0(2,x1) to x2 three times, totaling 0 mod 3.

All x_i for i≥3 remain unchanged.

Therefore **B^3 is the identity map** on the complete
state space when e=0. When e=1, the states
with x0=0 are moved by B^3, and precisely those
with x0∈{1,2} are fixed:

~~~text
# Fix(B^3; W_(k,0,c), depth d) = 3^d
# Fix(B^3; W_(k,1,c), depth d) = 2*3^(d-1)
~~~

At depth three these values are **27 and 18**,
independent of the support level k or shear chart c.

Fixed-point counts of every word in {A,B} are invariant
under *every* bijective, action-labeled A/B conjugacy:
if F B = B' F, then F B^3 = (B')^3 F.
They are not specific to the diagonal gauge or a
prescribed form of state map.

This gives a strict and complete two-stage decision
for the admitted 24 worlds:

~~~text
if support differs:
    B fixed-count mismatch -> inequivalent at depth 3
else if pulse differs:
    B^3 fixed-count mismatch -> inequivalent at depth 3
else:
    explicit H_(target_c-source_c) all-depth conjugacy -> equivalent
~~~

No cross-class pair is *assumed* inequivalent. Each has
a concrete labeled-word obstruction. No same-class pair
is *assumed* aligned. Each has an explicit invertible
projectively compatible state map.

## Complete finite classification

| Support k | #Fix(B), depth 3 | #Fix(B^3) e=0 / e=1 | Classes | Worlds |
|---|---:|---:|---:|---:|
| 0 | 9 | 27 / 18 | 2 | 6 |
| 1 | 6 | 27 / 18 | 2 | 6 |
| 2 | 3 | 27 / 18 | 2 | 6 |
| 3 | 0 | 27 / 18 | 2 | 6 |
| **Total** | | | **8** | **24** |

Each class has the three concrete shear worlds c=0,1,2.
Among all 24²=576 ordered pairs:

| Result | Ordered pairs | Witness |
|---|---:|---|
| Full-state conjugacy | 72 | H_(target_c-source_c) |
| Inequivalent by Fix(B) | 432 | Different k |
| Inequivalent by Fix(B^3) | 72 | Same k, different e |
| **Total** | **576** | Witness for every pair |

The shear constructor S increases c modulo three and
returns after three turns. The support constructor E
increases k, until the stated k=3 boundary. The
new pulse constructor P changes e=0 to e=1, once,
then reaches its own e=1 boundary. On their common
domains S, E and P commute exactly on the world
parameter descriptions.

**Only S is an equivalence-preserving construction
within each class.** E and P generally change the
relation; neither is a closed group action on one
class. Neither scoped wall is a terminal claim about
the full two-predecessor grammar.

## Evidence and reproducibility

[Implementation](window_branch.py) ·
[13 focused regression tests](../../network/tests/test_arc_like_window_branch.py) ·
[independent self-contained arithmetic checker](window_branch_arithmetic_audit.py)

An **independent** arithmetic implementation of these
coordinate formulas (not a GitHub CI run) exhaustively
checked the complete state spaces at depths 3–7,
all 24 constructed worlds and both action labels:

| Bounded check | Performed | Result |
|---|---:|---|
| Shear conjugacy comparisons | 470,448 | Pass |
| Inverse transition checks | 156,816 | Pass |
| Adjacent-depth projection checks | 155,520 | Pass |
| B/B^3 fixed-state count checks | 156,816 | Pass |
| Distinct depth-3 B transition signatures | 24 | Distinct |

The all-depth statement is separately supported by
the direct scalar field algebra and the unchanged
zero higher-coupling tail. This does not certify
arbitrary new q0 functions, later nonzero q_i,
or any real ARC solve.

The committed Python regression module covers 24
concrete rule tables, 576 relation pairs,
all-depth formulas on tested prefixes, two separate
obstruction words, inverses, projections,
operator squares, explicit return witnesses,
and malformed input. A pass of the independent
arithmetic implementation must **not** be called a pass
of the Python regression suite without actually
executing that suite.

Run from the repository root:

~~~bash
python -m unittest network.tests.test_arc_like_window_branch -v
python -m work.arc_like_maze.window_branch_arithmetic_audit
~~~

## Current boundary and next referent

**CLOSED:** the constructed 24-world family is
completely partitioned under *full-state* labeled
A/B conjugacy into eight classes, each containing
three exact non-diagonal shear charts.

**NEW WITNESS:** Fix(B) is insufficient even for
this small family; Fix(B^3) detects the first collision.

**UNKNOWN:** whether Fix(B) and Fix(B^3) remain
complete for larger two-input families. In general
they need not. Failure of these two counts to
distinguish a pair would require another word,
an actual state conjugacy, or an explicit UNKNOWN
boundary—not an automatic equivalence assertion.

**NEXT:** introduce another genuinely independent
table entry while holding the pair
(Fix(B), Fix(B^3)) constant. Search for the first
word-invariant collision and derive a new exact
obstruction or a constructive alignment. Preserve
the current finite witnesses as regression evidence.
