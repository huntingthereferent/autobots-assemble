# Inverted A/B — first five-letter fixed-word obstruction

**Current referent:** The 24-world two-input family is classified by
Fix(B) and Fix(BBB). Extend it with a genuinely independent edit
that preserves both invariants; retain full-state A/B witnesses.

## Constructed law

At every depth d>=3 over F3:

~~~text
A: x0 -> x0+1; all other coordinates unchanged
B: x1 -> x1+x0+1
   x2 -> x2+q0(x0,x1)
   xi -> xi                   (i>=3)
~~~

Build q0 from four explicitly bounded parameters:

~~~text
q_(k,e,t,c)(u,v) =
    [u=2 and v<k]
  + e*[u=0 and v=0]
  + t*([u=1 and v=0]-[u=1 and v=1])
  + c*((v+u+1)^2-v^2)          (mod 3)
k=0,1,2,3 ; c=0,1,2
(e,t) in {(0,0),(0,1),(1,0)}
~~~

The last term is the established reversible nonlinear shear
H_c(x)_2=x2+c*x1². The new balanced edit t changes two
independent q0 cells: q0(1,0) increases by one and
q0(1,1) decreases by one. It does NOT alter the old
support row x0=2 and cancels over three B turns.

There are **36 distinct concrete laws**. The simultaneous
combination (e,t)=(1,1) is **not admitted** in this
finite experiment. This is a three-branch fork at
each support k, not a falsely complete 4×2×2 grid.

## The fixed-point count collision

The balanced t=1 construction, compared against
t=0 with the same k,e=0,c, has:

| Word | Old | Balanced |
|---|---:|---:|
| B | 9 | 9 |
| BBB | 27 | 27 |
| AABAB | 9 | 3 |

All numbers above count the complete F3³ state
space, not just its origin-reachable subset.
An exhaustive enumeration of all words of lengths
one through four found **no fixed-state-count
difference**. AABAB is the first separating
length-five word in lexical A-before-B order.
This is *minimal for this numerical witness*,
not minimal for every possible kind of state observation.

### All-depth invariant proof

B fixes x1 only when x0=2. Neither the balanced
row-one edit nor the old row-zero pulse applies
there. Thus Fix(B)=(3-k)*3^(d-2).

For BBB, x0=0 and x0=1 each cycle x1 through
all three values; the balanced row-one edits
sum to zero. x0=2 does not move x1 and triples
the same x2 increment to zero. The old row-zero
pulse contributes one net x2 step over BBB
exactly when x0=0. Hence Fix(BBB) is 3^d
for e=0 and 2*3^(d-1) for e=1.

For AABAB, a state returns in its first two
coordinates only when x0=1. Its two B increments
sample q0(0,v) and q0(1,v+1). For e=0,t=0,
all three choices v are valid. For e=0,t=1,
only v=1 cancels the increment; for e=1,t=0,
two choices are valid. The nonlinear shear
term telescopes because x1 returns.

Every higher coordinate x_i (i>=3) is unchanged,
so each depth-three count multiplies by 3^(d-3):

~~~text
#Fix(B)       = (3-k)*3^(d-2)
#Fix(BBB)     = (27 if e=0 else 18)*3^(d-3)
#Fix(AABAB)   = (9 if (e,t)=(0,0)
                 else 3 if (e,t)=(0,1)
                 else 6)*3^(d-3)
~~~

Fixed sets of **every action word** are invariant
under any bijective A/B-labeled state conjugacy,
not merely diagonal gauges. These count
differences are therefore concrete obstructions.

## Complete classification in this declared family

Within a fixed (k,e,t), all three chart coefficients
c=0,1,2 are related by the explicit invertible,
root-preserving, projection-compatible shear
H_(target_c-source_c). At different (k,e,t),
one of the three counts above differs.

Thus the 36 worlds form **exactly 12 full-state
A/B equivalence classes** of size three.

| Ordered pairs | Count | Evidence |
|---|---:|---|
| Equivalent | 108 | Explicit nonlinear shear |
| Different k | 972 | Fix(B) obstruction |
| Different e | 144 | Fix(BBB) obstruction |
| Different t, same k,e | 72 | Fix(AABAB) obstruction |
| **Total** | **1296** | One certificate per pair |

The earlier 24-world family embeds unchanged
at t=0. Shear moves around a closed three-turn
orbit inside a class. The support, pulse, and
balanced edits can change the class, but their
finite domain boundaries do not establish
unrestricted mathematical closure. Pulse and
balance are **alternative extensions**, not
two freely commuting updates.

## Evidence and reproducibility

[Construction and classifier](window_word_collision.py) ·
[14 regression tests](../../network/tests/test_arc_like_window_word_collision.py) ·
[independent arithmetic checker](window_word_collision_arithmetic_audit.py) ·
[GitHub Actions workflow](../../.github/workflows/arc-window-branch.yml).

An independent implementation of the coordinate arithmetic
was exercised over complete state spaces at depths 3–7
for all 36 worlds:

| Bounded check | Assertions | Result |
|---|---:|---|
| State-level conjugacy | 705,672 | Pass |
| Inverse identities | 235,224 | Pass |
| Projection identities | 233,280 | Pass |
| Full-depth formulas for B, BBB, AABAB | 540 | Pass |

The committed 14 Python regression tests were added
separately. Do not report a GitHub CI pass until a
workflow check actually completes successfully.

~~~bash
python -m unittest network.tests.test_arc_like_window_word_collision -v
python -m work.arc_like_maze.window_word_collision_arithmetic_audit
~~~

**CLOSED:** exact twelve-class partition within this
36-world construction, with full-state maps or
finite-depth fixed-word obstructions.

**NEW:** Fix(B) and Fix(BBB) collide; the first
separating fixed-point count requires a five-letter
word, AABAB.

**UNKNOWN:** the withheld pulse-plus-balance edit
(e,t)=(1,1), arbitrary two-input rules, later
nonzero coupling coordinates, general non-diagonal
conjugacies, universal inverse A/B closure and
native ARC execution.

**NEXT:** admit (e,t)=(1,1) independently, inspect
the actual marked/rooted A/B transition relation,
and use new word witnesses or exact conjugacies
rather than concluding equivalence from matching
three fixed-word counts.
