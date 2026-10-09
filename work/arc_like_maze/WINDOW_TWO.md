# Inverted A/B — Two-predecessor coupling construction

**Current referent:** The verified non-diagonal shear
\`H_c(x)_2=x_2+c*x_1²\` creates transition laws that the previous
one-variable Process coupling tables cannot express, although the
worlds remain exactly conjugate. We need a mathematical description
that preserves the new dependence without declaring an artificial
inequivalence.

**Definition of solved in this movement:** Construct a small explicit
eventually periodic coupling language that can represent the sheared
marked worlds *exactly at every depth*. Verify its transitions, inverses,
projections, and previously certified marked-arrow state maps. Construct
a genuinely different coupling within the same language and produce
an invariant separating it from the base world.

## The new mathematical language

Every increment remains triangular over F_3. The A and incoming B
coordinates retain their marked-root definitions:

~~~text
A(x)_0 = x_0 + 1               ; all other coordinates unchanged
B(x)_0 = x_0
B(x)_1 = x_1 + g*(x_0 + 1)     ; g in {1,2}
~~~

The constructed extension admits two-variable rule tables
\`q_i:F_3² -> F_3\`, represented by nine entries in row-major
order, \`q_i(u,v) = table[3*u+v]\`:

~~~text
B(x)_(i+2) = x_(i+2) + q_i(x_i,x_(i+1))       i >= 0
~~~

The arguments of each rule refer to the **old** state, not to
coordinates already updated by B. This detail is necessary for
the exact formula and for reversing B.

The rule stream consists of a finite stem followed by a nonempty
period, just as the earlier complete process model did. An
arbitrary stream oracle is **not** silently admitted.

This is a **two-predecessor** generalization sufficient for the
present construction, not a proof of global minimality among every
possible transition grammar.

### Exact mathematical guarantees

Every output coordinate only depends on an equal or shorter
input prefix. Therefore all dimensional projections commute with
the A and B laws for **every** finite depth, including the full
inverse limit.

A changes only x0 and is reversed by subtracting one. The
inverse of B recovers x1 from x0, then recovers x2, x3, ...
in order:

~~~text
old_x1 = new_x1 - g*(x0+1)
old_x_(i+2) =
  new_x_(i+2) - q_i(old_x_i,old_x_(i+1))
~~~

All arithmetic is mod 3. This is a constructive all-depth
inverse for **every admitted nine-entry rule stream**, not
merely one experimentally chosen world.

## Embedding the old world, compiling the shear

A native one-input coupling rule p_i(v) becomes the
two-input rule q_i(u,v)=p_i(v) for every u.

The reverse conversion exists precisely when *every*
nine-entry q_i is independent of u and satisfies q_i(u,0)=0
on the complete eventually periodic stream. The
\`WindowProcess.native()\` check is exact, rather than a
bounded prefix assumption.

For the sheared marked world \`H_c T H_-c\`, the first two
rules are derived algebraically:

~~~text
q_0(u,v) =
  p_0(v) + c*((v+g*(u+1))²-v²)

q_1(u,v) =
  p_1(v-c*u²)

q_i(u,v) = p_i(v)                     i >= 2
~~~

Coordinates are taken modulo three throughout. The
first two q rules must be preserved as a **finite stem**,
even if the original p process had no stem. The
subsequent tail phase is preserved rather than
reset or guessed.

This direct nine-entry compilation reproduces the
original non-diagonal conjugated actions at **every**
depth, by substitution in the coordinate equations.
It does not merely call the old shear implementation
at runtime; \`WindowProcess\` has its own standalone
transitions and inverse.

For c=0, reverse native decoding is possible. For c=1
or 2, q_0(0,0)=c, so the compiled concrete B action
cannot be decoded into the former \`p_0(0)=0\` schema.

**That is a representation break, not an equivalence break.**
The earlier certified non-diagonal alignment
\`H_target M_witness H_source^-1\` still conjugates the
compiled source and target B laws exactly. The new
test suite verifies that witness against **independent
compiled transition tables**, rather than only the
original sheared-world implementation.

## Independently constructed new relation

The expanded grammar also permits independent local
rule-table changes. From the zero-coupling
marked world with g=1, modify precisely one entry:

~~~text
q_0(2,0): 0 -> 1
~~~

The edit leaves every other entry and every other rule
of the infinite process unchanged. The tail is
re-phased correctly if the edited index was previously
inside a repeating segment.

At depth three, the original B law has **9** fixed
states in the full F_3³ state space. The new law has
**6**. Every bijective A/B conjugacy must give a
bijection between B-fixed state sets. Hence the two
complete systems **cannot** be globally conjugate by
any A/B-label-preserving bijection (not just the
diagonal or shear gauges). Projection to depth
three also forbids a *projectively compatible*
all-depth alignment.

This is a new relation, not merely an inadequate
representation, even though the newly edited A/B
maps remain reversible and compatible with
dimensional projection.

## Evidence

[Implementation](window_two.py) ·
[12 focused regression tests](../../network/tests/test_arc_like_window_two.py)

An **independent finite arithmetic implementation** checked
three native process types, two marked root gains, all three
shear parameters, all full states at depths 3 through 7,
and both A/B operations. It obtained:

| Check | Exact count | Result |
|---|---:|---|
| Direct sheared action vs compiled two-input table | 117,612 | Pass |
| Left and right inverse identities | 235,224 | Pass |
| Adjacent depth projections | 116,640 | Pass |
| Reverse-native conditions for c=0 | 88,614 | Pass |
| B-fixed state counts, old versus independently edited | 9 vs 6 | Distinct |

The independent implementation is **not** the exact
committed module or the GitHub test runner. The 12 Python
regression tests are committed separately and must be
executed before claiming that the code itself passed.
They additionally cover stems and period phasing, exact
marked-arrow witness compatibility, malformed input,
and arbitrary two-variable coupling reversibility.

Reproduce the Python tests from the repository root:

~~~bash
python -m unittest network.tests.test_arc_like_window_two -v
~~~

## The current stopping boundary

**CLOSED:** every previously admitted native marked
one-input process embeds faithfully, and the particular
non-diagonal shear family compiles into independently
specified two-variable laws while keeping its exact
relational alignment. All A/B laws in this defined
two-variable triangular grammar are invertible and
dimensionally compatible.

**OPEN:** the former one-variable language cannot
represent all admitted compiled laws. Moreover an
independently edited two-variable coupling gives an
invariant-based *genuine* inequivalence, so all possible
admitted q tables do not collapse to a single A/B class.

**UNKNOWN:** classification of every all-depth
two-variable process under arbitrary non-diagonal
conjugacies; a maximal family of coordinate charts;
admissibility of higher-width couplings; universal
inverse A/B closure or any native ARC solve.

**Next referent:** construct an operator-level quotient
for a justified finite collection of two-variable
rules, where the equivalence criterion uses actual
full-state A/B witnesses and explicitly separates
the proved shear-conjugate family from independently
inequivalent rule edits.
