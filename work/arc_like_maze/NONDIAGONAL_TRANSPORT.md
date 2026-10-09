# Inverted A/B — Non-diagonal witness transport

**Current referent:** The marked diagonal A/B quotient is complete for its
declared periodic / finite-stem gauge relation, but there may be meaningful
world constructions that are *exactly aligned* without fitting the
one-variable coupling-rule representation.

**Definition of solved in this movement:** construct a reversible
non-diagonal all-depth coordinate transformation; prove it transports exact
marked A/B alignment, including the original coinductive witness; and give
a concrete obstruction showing why the constructed world does not fit
the preexisting process schema. Do **not** confuse schema nonclosure
with mathematical inequivalence.

## Construction

Let a marked process world have root gain g in {1,2} and rule stream
P=(p_0,p_1,...), each p_i a table F_3 -> F_3 with p_i(0)=0:

~~~text
A(x)_0 = x_0+1                     ; other coordinates unchanged
B(x)_0 = x_0
B(x)_1 = x_1+g*(x_0+1)
B(x)_i = x_i+p_(i-2)(x_(i-1))      ; i >= 2
~~~

Define a new *non-diagonal* invertible map for each c in F_3:

~~~text
H_c(x_0,x_1,x_2,x_3,...)
 = (x_0,x_1,x_2+c*x_1^2,x_3,...)
~~~

All arithmetic is modulo 3. The explicit inverse is H_(-c).
Composition is H_c H_e = H_(c+e). The origin is preserved.

The formula for coordinate i never reads any later coordinate, so
H_c commutes with every forgetful projection of depth >= 3.
It induces a continuous all-depth inverse-limit homeomorphism.

Construct *new* marked world operations, not a new display:

~~~text
A_c = H_c A H_(-c)
B_c = H_c B H_(-c)
~~~

The conjugacy H_(e-c) transports the complete action from the world
with parameter c to the world with parameter e:

~~~text
H_(e-c) T_c = T_e H_(e-c)           for T in {A,B}
~~~

These equations hold algebraically for every admitted depth.
The construction c -> c+1 cycles through the exact law order

~~~text
0 -> 1 -> 2 -> 0
~~~

and has three different concrete B transition laws already at depth 3.

## What the old process representation cannot say

For any native admissible process and any gain, the B transition
from the zero state changes x_1 but leaves x_2 equal to zero,
because the first coupling table satisfies p_0(0)=0.

For the new constructed world:

~~~text
B_c(0,0,0) = (0,g,c*g^2)
           = (0,g,c)             because g^2=1 in F_3
~~~

Thus for c=1 or c=2, **no** native process satisfying
p_0(0)=0 can have exactly the same action on that *concrete state*.

The transformed action can also depend on more than one earlier
coordinate. Writing the input in transformed coordinates,
with x_0 and x_1 unchanged:

~~~text
(B_c(x))_2 =
    x_2 + p_0(x_1)
        + c*((x_1+g*(x_0+1))^2-x_1^2)
~~~

The extra x_0 dependence is not a permitted one-variable
coupling p'_0(x_1).

**This is a failure of closure of the old canonical representation,
not an A/B invariant that separates two worlds.** An exact
non-diagonal state alignment H_c exists. Therefore describing c=1,2
as genuinely inequivalent *worlds* would be false.

## Transport the whole marked arrow, not just its scalar label

A previously certified marked diagonal arrow includes both complete
processes, both incoming root gains, and the exact coinductive witness
w=(b,s_0,s_1,...). Let M_w be its coordinate-diagonal A/B alignment.

For arbitrary independent source and target shears c and e,
the exact constructed-world alignment is:

~~~text
F_(c,e,w) = H_e M_w H_(-c)
F_(c,e,w) A_c = A_e F_(c,e,w)
F_(c,e,w) B_c = B_e F_(c,e,w)
~~~

It is reversible; its inverse is H_c M_(w^-1) H_(-e).
This retains the **original** witness and its potentially ambiguous
choices at zero couplings. It does not pretend a single scalar
witness is the whole non-diagonal state map.

Composition is admitted **only if** the sheared middle objects,
full streams and marked gains match. The H_e and H_(-e)
cancel algebraically at a compatible middle object, leaving
the already-certified marked-arrow composition.

A simultaneous forward process shift is represented by re-rooting
each marked process and its local shear chart, carrying the
original witness tail and incoming scalar through the
existing shift-arrow contract. This is **not** a claim that
discarded global process prefixes become invertible.
Diagonal gauge changes are conjugated through the same
source/target local charts; the old witnessed gauge/shift
interchange equality therefore survives for these new
constructed arrows.

## Evidence and verification

[Implementation](nondiagonal_transport.py) ·
[12 regression tests](../../network/tests/test_arc_like_nondiagonal_transport.py)

An independent finite arithmetic check (separate from the Python
suite) covered **58,806** concrete conjugacy comparisons,
**9,801** inverse checks, and **9,801** projection checks
across depths 3–7 for a nontrivial marked-rule example.
It found no violations, and witnessed two non-native action
laws at the origin. The exact all-depth statements rely on
the displayed invertible conjugacy formulas, not on the bounded
checks alone.

The 12 added Python regression tests exercise three-turn law
return, all-state A/B conjugacy, complete inverse maps,
projection compatibility, native schema obstruction,
marked-arrow composition/inversion, root shifts and
witness retention under zero-rule ambiguity, and
gauge/shift interchange in the sheared chart. **Do not label
these Python tests as executed until a runtime has
actually executed the committed files.**

Run from repository root:

~~~bash
python -m unittest network.tests.test_arc_like_nondiagonal_transport -v
~~~

## Status / wall / next referent

**CLOSED for the admitted shear family:** three different concrete
transition laws form an invertible group of coordinate
conjugacies, and exact marked A/B arrows transport
through these non-diagonal maps at all depths.

**OPEN in the old representation:** the two nontrivial
conjugated B laws are not expressible by an existing
table p_0(x_1) with p_0(0)=0. We must not force them
back into the diagonal Process schema or discard x_0
dependence.

**UNKNOWN:** which independent non-diagonal constructions
preserve the *larger* combined equivalence, whether any
such transformations connect formerly unaligned
marked process objects, a complete classification of
general triangular homeomorphisms, and native ARC execution.

**Next:** define the smallest justified general transition
schema admitting the extra dependence on x_0, then
test its full-state relational equivalences and
counterexamples. This should remain a mathematical
construction exercise until the user changes the referent.
