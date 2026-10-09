# Inverted A/B — Four full-state classes from twelve constructed worlds

**Current referent:** The two-predecessor A/B grammar can both (1) represent
the earlier non-diagonal shear exactly and (2) admit genuinely new
couplings. We now need a bounded complete classification by witnessed
**full-state** A/B relations, without mistaking a chosen finite family
for all possible nine-entry coupling tables.

**Goal:** Construct one finite family closed under an explicit nonlinear
shear; prove a complete classification of its members without guessing
arbitrary graph isomorphisms; and identify the stopping condition for the
family's *independent* relation-changing operation.

## Language first — define the independent constructions

Work over F_3 with marked root gain g=1 and the two-predecessor
law (all additions are mod 3):

~~~text
A(x)_0 = x_0 + 1,       A(x)_i = x_i, i>=1
B(x)_0 = x_0
B(x)_1 = x_1 + x_0 + 1
B(x)_2 = x_2 + q0(x_0,x_1)
B(x)_i = x_i,          i>=3
~~~

All other coupling tables are explicitly **zero**. This is a
declared subfamily of the larger window process space, not a
claim that later dimensions can never carry a nonzero coupling.

For each support level k∈{0,1,2,3}, define one primitive table:

~~~text
D_k(u,v) = 1 if u=2 and v<k, else 0
~~~

At k=0 it is the native zero-coupling world. Increment k from
zero to three to add precisely one new nonzero entry at
(2,k-1), without moving the earlier entries.

Separately, for each shear coefficient c∈{0,1,2}, construct
the same nonlinear coordinate conjugacy as in the last layer:

~~~text
H_c(x)_2 = x_2 + c*x_1^2
H_c(x)_i = x_i elsewhere
q_(k,c)(u,v) =
    D_k(u,v) + c*((v+u+1)^2-v^2)
~~~

The q table is represented by all nine entries, as admitted
in [window_two.py](window_two.py). Note that the added nonlinear
term is the **actual** difference of the squared old and new
x1 coordinates after B, not a substitution into an unrelated
linear-gauge formula.

The family has **4×3=12** concrete action laws
\`W_(k,c)\`, each independently executable by \`WindowProcess\`.

## Mathematical classification — exactly four A/B classes

**Inside a support level:** the explicit invertible map
\`H_(e-c)\` conjugates \`W_(k,c)\` to \`W_(k,e)\`
at every depth. The transform fixes the origin, preserves
all coordinate projections, and has inverse \`H_(c-e)\`.
This proves full-state, action-label-preserving equivalence,
not merely origin-orbit equivalence.

**Between support levels:** count the states fixed by B.

For B to fix the x1 coordinate, \`x0+1=0\`,
so x0 must equal 2. At that value, the shear's
extra term is zero:

~~~text
q_(k,c)(2,v) = D_k(2,v)
            = 1 if v<k, else 0
~~~

Thus precisely \`3-k\` possible x1 coordinates remain
fixed, and all coordinates x2,...,x_(d-1) are free.
The exact count at depth d≥3 is therefore

~~~text
#Fix(B | depth d, W_(k,c)) = (3-k) * 3^(d-2)
~~~

At depth 3 the four support levels give **9, 6, 3, 0**
fixed states respectively, regardless of c.

Any bijective conjugacy F intertwining the B operations
must biject their fixed-state sets. Consequently worlds
at *different* k cannot have a bijective B-preserving
state alignment even at depth 3, and no projectively
compatible all-depth A/B conjugacy exists between them.

Combining the explicit witnesses and the invariant
obstructions proves **exactly four full-state A/B
classes among the twelve specified worlds**, with
three concrete construction laws in each class.

| Support k | Shear worlds | B fixed at depth 3 | Result |
|---:|---:|---:|---|
| 0 | c=0,1,2 | 9 | Exactly aligned |
| 1 | c=0,1,2 | 6 | Exactly aligned |
| 2 | c=0,1,2 | 3 | Exactly aligned |
| 3 | c=0,1,2 | 0 | Exactly aligned |
| Total | 12 | Four distinct invariants | Four classes |

This proof does not rely on an assumed completeness of the
previous diagonal-gauge solver: the alignment is given as
a concrete, reversible **non-diagonal** state map.

## Two construction motions, two different closure results

Define

~~~text
S: (k,c) -> (k,c+1 mod 3)
E: (k,c) -> (k+1,c)      provided k<3
E: (3,c) -> WALL        no next value in this family
~~~

The shear operator S is a three-turn loop in every
support class:

~~~text
W_(k,0) -> W_(k,1) -> W_(k,2) -> W_(k,0)
~~~

Every intermediate concrete B law differs, but the
**same A/B relational structure survives**.

The independent support construction E does something
mathematically different. Each E step enters a new
class; it reduces the depth-three B-fixed count by
exactly three. On all defined squares E and S commute:

~~~text
E(S(W_(k,c))) = S(E(W_(k,c)))   for k=0,1,2
~~~

At k=3 the declared support axis stops only because
this one row of three possible nonzero entries has
been exhausted. **The resulting WALL is scoped to
this chosen construction family**; it is not a
universal A/B mathematical stopping point. Additional
two-variable couplings or nonzero later rules remain
possible and are not equated to this family.

## Evidence and actual test boundary

[Implementation](window_family.py) ·
[13 focused regression tests](../../network/tests/test_arc_like_window_family.py)

An independent executable finite arithmetic model (not the
committed Python module) verified for the 12 worlds:

| Finite check | Comparisons | Outcome |
|---|---:|---|
| All conjugacies between each k's 3 shear charts through depth 7 | 235,224 | PASS |
| Triangular inverse identities in that same loop | 235,224 | PASS |
| Dimensional projection identities within that loop, depths 4–7 | 233,280 | PASS |
| Ordered world-pair classification by witness/invariant | 144 | 36 aligned, 108 obstructed |

The inverse/projection totals include repeated checks
over different *target* shear coefficients; they count
assertions executed, not mathematically independent states.
The higher-depth equivalence follows from the exact H
conjugacy equation, not from bounded testing alone.
The all-depth fixed-point formula follows from the
displayed B-coordinate equations.

Thirteen additional Python regression tests are committed
to exercise the exact repository's \`WindowProcess\`
interpreter, finite inverses, projections, support
construction, all state-level witnesses, native-shear
compatibility, and input boundaries. **No GitHub CI
pass or committed-file Python test execution is
claimed without its actual run.**

~~~bash
python -m unittest network.tests.test_arc_like_window_family -v
~~~

## Wall, preservation, next referent

**CLOSED:** this twelve-world *declared* family is
exhaustively classified by four action-preserving
full-state A/B classes, with a three-turn non-diagonal
gauge cycle inside each one. The family is closed
under S but not under unrestricted E, which ends
at a declared scope wall.

**PRESERVED:** full-state witnesses are reversible,
origin-preserving, and commute with every dimensional
projection. Four distinct B-fixed-point invariants
prevent false alignment across supports.

**UNKNOWN:** whether arbitrary nine-entry coupling
tables, other roots, nonzero couplings beyond x2,
or more general triangular conjugacies yield the
same quotient; unbounded arbitrary construction
closure; any native ARC gameplay or solution.

**Next mathematical referent:** test another *independent*
two-predecessor coupling beyond the selected x0=2
support row. Determine whether its new law is
conjugate to one of these four classes or breaks
the fixed-point signature in a way that requires
a richer invariant. Do not simply cycle the finite
support axis and declare universal closure.
