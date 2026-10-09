# Inverted A/B — A full-state equivalence that does NOT preserve the origin

**Current referent.** [The 36-law word-collision experiment](WINDOW_WORD_COLLISION.md)
held the pulse-plus-balanced table combination out of scope. It established
12 full-state classes for its three-branch fork and showed that equal
Fix(B) and Fix(BBB) counts can hide a five-letter word obstruction.
The next movement is to admit the actual missing combination, rather
than extend a closed support row artificially.

**Solved condition.** Admit (pulse,balanced)=(1,1); decide all pairwise
full-state labeled A/B relations with explicit state maps or
action-word obstructions; check the **separate origin-preserving relation**
using paths from the marked origin. Preserve the exact witness, including
where a world is equivalent only after moving the origin.

## One full two-edit grid

At each depth d>=3, all arithmetic is in F3. As in the preceding
constructed models:

~~~text
A(x)_0 = x0+1, A(x)_i = x_i   i>=1
B(x)_0 = x0
B(x)_1 = x1+x0+1
B(x)_2 = x2+q0(x0,x1)
B(x)_i = x_i               i>=3
~~~

Declare:

~~~text
q_(k,e,t,c)(u,v) =
    [u=2 and v<k]                 support
  + e*[u=0 and v=0]               pulse
  + t*([u=1 and v=0]-[u=1 and v=1])  balanced edit
  + c*((v+u+1)^2-v^2)             nonlinear shear
                              mod 3

k∈{0,1,2,3}; e,t∈{0,1}; c∈{0,1,2}.
~~~

All 4×2×2×3=**48 concrete B transition tables** are different.
All have exact triangular inverses and commute with truncation to
lower coordinate depths. Unlike the earlier fork, *both* independent
edits may be applied, in either order. Their construction squares
commute on the admitted parameter set.

The coefficient c remains a three-turn, relation-preserving
nonlinear chart: H_c(x)_2=x2+c*x1², other coordinates unchanged.
Within each fixed (k,e,t), all three chart worlds are related
by H_(target_c-source_c), which fixes the origin.

## Why the combined edit is a new test

Compare the **pulse-only** world (e,t)=(1,0) with the
**pulse-plus-balance** world (e,t)=(1,1), at the same k,c.

Their full-state counts of the first three previously discovered
invariants agree at every depth:

~~~text
Fix(B)       = (3-k)*3^(d-2)
Fix(BBB)     = 2*3^(d-1)
Fix(AABAB)   = 6*3^(d-3)
~~~

Thus equality of the established three-number signature
does NOT constitute proof of an alignment.

The next action word ABABAB distinguishes these worlds
at the *middle two support levels*:

| Support k | Fix(ABABAB), pulse only | Pulse plus balanced |
|---|---:|---:|
| 0 | 18 | 18 |
| 1 | 18 | 9 |
| 2 | 9 | 0 |
| 3 | 0 | 0 |

At k=1,2 this is a complete-state fixed-word obstruction
to **every** bijective action-label-preserving A/B conjugacy,
including non-diagonal ones. Deterministic enumeration of
all positive A/B words of lengths 1–5 finds no differing
fixed-state count for those compared worlds; ABABAB is
the first such length-six witness (lexicographic A before B).

The count is algebraic for all d>=3: the word includes
three A and three B actions; x0 and x1 return to their
original coordinates. Sum q0 over its three sampled
(x0,x1) pairs, then count the zero sums across the nine
possible base-coordinate states. Each allowed pair has
3^(d-2) choices of the remaining coordinates.

## A stronger discovery: full-state isomorphism without a rooted one

For k=0 and k=3, the two constructed systems are instead
**exactly conjugate on the full state space**. The conjugacy
is not a scalar gauge and it is not rooted.

At chart c=0, the map from pulse-only to combined is:

~~~text
R(u,v,z,tail) =
    (u, v+2, z+f(v), tail)
f(v) = 2 if v=1, else 0              (mod 3)
~~~

It is a bijection. Its inverse recovers old_v=new_v+1
and subtracts f(old_v). It commutes with A because
A changes only u and R does not depend on u.

For B, direct substitution gives the needed identity

~~~text
q_combined(u,v+2) - q_pulse(u,v)
  = f(v+u+1) - f(v)                 (mod 3)
~~~

at k=0 or k=3, and **not** at k=1,2.
The support row causes this distinction: when k=0
the row is empty, and when k=3 it is constant;
both survive translation of v. The partial support
rows k=1,2 do not survive.

For arbitrary source chart c and target chart d
compose the already proved coordinate changes:

~~~text
F = H_d ○ R ○ H_(-c)
~~~

The reverse alignment uses R^-1.
This gives an explicit invertible full-state
A/B conjugacy at **every depth**, with compatible
projection onto lower depths.

However:

~~~text
R(0,0,0) = (0,2,0)
F(0,0,0) = (0,2,d)
~~~

The map moves the marked origin. One must **not**
promote this full-state equivalence to a rooted one.

The stronger rooted counterexample does not merely
inspect this particular chosen map: two positive
action words reach the **same state from the source
origin** but **different states from the target origin**.
No origin-fixing labeled conjugacy can exist.

At chart c=d=0, pulse-only -> combined:

| Support | Same source from words | Different target |
|---|---|---|
| 0 | BAB and BBBA | (1,0,0) versus (1,0,1) |
| 3 | AAB and BABA | (2,0,1) versus (2,0,0) |

Those positive-word collision witnesses are preserved
across source and target shear charts because H_c
and H_d both fix the origin. The code constructs
an actual BFS collision for each nonrooted pair
instead of assuming that the presented R map is
the only possible alignment.

This difference is substantive: **the whole-world
dynamics align at k=0,3, but their marked entrances
do not**.

## Two certified quotients of the same 48 worlds

For every ordered world pair:

1. Different k -> distinct Fix(B).
2. Same k, different pulse e -> distinct Fix(BBB).
3. Same k, e=0, different balanced t -> distinct Fix(AABAB).
4. Same k, e=1, different t, k in {1,2} -> distinct
   Fix(ABABAB).
5. Same k, e=1, different t, k in {0,3} -> exact
   nonrooted R conjugacy, with a rooted collision.
6. Same (k,e,t) -> exact origin-preserving H shear conjugacy.

This proves completeness **only for the declared 48 laws**.

| Quotient | Classes | Class size distribution |
|---|---:|---|
| Full-state action-preserving conjugacy | **14** | 12 classes of 3; 2 classes of 6 |
| Origin-preserving action conjugacy | **16** | 16 classes of 3 |

All 48²=2304 ordered pairs receive a concrete witness:

| Pair status | Count |
|---|---:|
| Rooted exact state conjugacies | 144 |
| Full-state but NONROOTED exact conjugacies | 36 |
| Fix(B) obstruction | 1728 |
| Fix(BBB) obstruction | 288 |
| Fix(AABAB) obstruction | 72 |
| Fix(ABABAB) obstruction | 36 |
| **Total** | **2304** |

This is not a general claim that arbitrary full-state
conjugacies may be freely treated as rooted A/B
witnesses. The 36 nonrooted ordered alignments are
marked explicitly and carry 36 positive-word
root-counterexamples.

The nonlinear shear still returns after three turns
inside each parameter block. The support, pulse
and balanced edits commute as **parameter
constructions**, but generally change the
relational class. A commutative construction
square is not a conjugacy square.

## Reproducibility and provenance

[Implementation](window_combined.py) ·
[15 focused regression tests](../../network/tests/test_arc_like_window_combined.py) ·
[independent arithmetic checker](window_combined_arithmetic_audit.py) ·
[targeted workflow](../../.github/workflows/arc-window-branch.yml)

The independent finite arithmetic verification used
**all 48 laws at every state and both actions through
depth six**, independently of the repository's
WindowProcess interpreter:

| Check | Assertions | Result |
|---|---:|---|
| Shear edge comparisons | 311,040 | Pass |
| Triangular inverse identities | 103,680 | Pass |
| Projection identities | 101,088 | Pass |
| Fixed-word formula checks | 768 | Pass |
| Ordered relation comparisons at depth 3 | 2,304 | Complete |
| Nonrooted positive-word root counterexamples | 36 | Found |

The algebra above proves the extension to all finite
depths for these explicit formulas; the bounded tests
remain bounded evidence. The 15 committed Python
tests and new workflow steps must not be called
CI-passing until a runner has actually reported it.

~~~bash
python -m unittest network.tests.test_arc_like_window_combined -v
python -m work.arc_like_maze.window_combined_arithmetic_audit
~~~

## Boundary / next movement

**CLOSED:** Complete full-state (14 classes) and
origin-preserving (16 classes) classification for
this expressly admitted 48-world family, with
exact state maps, action-word obstructions, and
literal root-collision witnesses.

**PRESERVED:** Old 36 worlds remain intact;
three-turn shear equivalences and the earlier
B, BBB, AABAB witness layers all survive.
A new sixth-letter word ABABAB supplies an
obstruction for partial supports.

**IMPORTANT NONCLOSURE:** Full-state equivalence
does not imply *root-preserving* equivalence.
The marked boundary is a genuine mathematical
referent and cannot be erased by quotienting.

**UNKNOWN:** arbitrary nine-entry rule processes,
nonzero higher-depth couplings, general finite-head
root transports and arbitrary action conjugacies
outside this finite family, universal inverse A/B
closure and native ARC gameplay execution.

**NEXT:** build a witness-carrying relation operator
that makes the marked/unmarked distinction explicit.
Composition must retain the mark and fail safely
when only an unrooted conjugacy is available. Test
whether a change of root can be represented as a
separate admitted operation rather than as a
silent quotient merger.
