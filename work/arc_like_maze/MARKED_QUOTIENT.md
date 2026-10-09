# Inverted A/B — Witness-complete quotient of a marked operator family

**Current referent:** The marked-arrow construction has an eight-element
period-two coordinate-gauge group and exact witness-carrying root transport.
Does that *operator group* already identify every diagonally equivalent marked
process, or are there verified arrows that it misses?

**Goal / solved condition:** Build the smallest explicit universe closed
under those eight gauges, partition it twice (by actual gauge orbits and by
coinductively certified marked A/B alignment), and retain a valid witness for
every merger of distinct gauge orbits.

## Construction and evidence

Each coupling rule is a table \`r=(0,a,b)\` over \`F_3\`.
We begin with every strictly two-periodic rule stream \`(r,s,r,s,...)\`
at either incoming marked gain \`g∈{1,2}\`: \`9×9×2=162\` marked objects.

The eight admitted \`BoundaryGauge\` constructions are

~~~text
U = (u_-1, (u_0,u_1))             each scalar is 1 or 2
g' = u_-1 * g
P'_i(u_(i-1) * v) = u_i * P_i(v)
~~~

For \`i=0\`, the previous scalar is \`u_-1\`; subsequently the
period-two schedule applies. Crucially, **\`u_-1\` need not equal \`u_1\`**,
so transforming a strictly periodic stream may create a *one-rule stem*.
Discarding that stem would silently erase the root boundary.

Every resulting process has an exact canonical representation

~~~text
P' = (r_0,) + periodic_tail(r_1,r_2)
~~~

and the eight gauges preserve the entire set of these transformed
processes, including the root gains. The closed set has **270** distinct
marked objects: 162 strictly periodic ones plus 108 with a genuine
one-rule stem.

The operator's complete finite gauge orbits partition these 270 into:

| Gauge orbit size | Gauge orbits | Objects |
|---|---:|---:|
| 2 | 1 | 2 |
| 4 | 3 | 12 |
| 8 | 32 | 256 |
| **Total** | **36** | **270** |

This is an exact group-action quotient for **the eight selected gauges**.

## A stronger quotient: keep the actual diagonal A/B witness

A marked arrow \`(P,g) -> (Q,h)\` must carry an eventually-periodic
scalar sequence \`s_i\` and an incoming scalar \`b=h/g\`. At every rule:

~~~text
Q_i(s_(i-1) * v) = s_i * P_i(v)     for all v in F_3
s_-1 = b
~~~

The existing \`root_transport.find\` constructs a finite-head/periodic-tail
witness using a finite-state coinductive decision procedure;
\`root_transport.verify\` certifies the entire infinite stream.
Our quotient does **not** re-solve an arrow during later operator
transport; the witness itself remains a mathematical referent.

Under that complete **diagonal, marked-root** equivalence, the same
270 objects form **34 classes**:

| Aligned class size | Classes | Objects |
|---|---:|---:|
| 2 | 1 | 2 |
| 4 | 3 | 12 |
| 8 | 28 | 224 |
| 16 | 2 | 32 |
| **Total** | **34** | **270** |

There are exactly **two** classes in which *two distinct period-two
gauge orbits* become equivalent. The Python implementation returns
a certified arrow for each bridge, not merely a list of class labels.

A concrete example (root gain 1 on both ends):

~~~text
P = (0,1,2), (0,1,1), (0,1,2), (0,1,1), ...
Q = (0,1,2), (0,2,2), (0,1,2), (0,2,2), ...

incoming b = 1
scalar witness s_0,s_1,s_2,s_3,... = 1,2,2,2,...
~~~

This scalar stream cannot be the repetition of a two-element
gauge period from the root: \`s_0 ≠ s_2\`.
It **is** an exact eventually periodic witness, preserving marked
A/B transitions in every dimension. The prelude is mathematically
necessary, not formatting noise.

Therefore:

- The **eight-gauge action is closed**, a proved group of constructions.
- Its **36-orbit quotient is not complete** for the broader admitted
  family of fully verified marked diagonal A/B arrows.
- The latter finite universe has exactly **34** equivalence classes.
  In this *declared* universe, its coinductive quotient is complete
  for the diagonal marked-arrow definition, not for arbitrary
  conjugacies or arbitrary external constructions.

## Verification contract

[\`marked_quotient.py\`](marked_quotient.py) stores each entire process
through a representation that is exact for this one-stem/two-tail
family. Its orbit partition is constructive; its coinductive
classification only compares the 36 orbit representatives, using
the provable transitivity of exact diagonal alignment.

The 14 new [regression tests](../../network/tests/test_arc_like_marked_quotient.py)
are designed to verify: 162→270 closure and the 108 new stems; the
36-orbit gauge action and all 64 ordered gauge compositions on
every object; 34 full-alignment classes and cross-class witnesses;
the two nonperiodic bridges; full-state A/B alignment at depths 3–7;
composition and inversion of the actual marked arrows; and
witness-carrying gauge/shift interchange on the bridges.

An independent finite arithmetic classification was completed before
writing this implementation: 270 distinct objects; 36 gauge orbits;
34 coinductive classes with the above histograms; all objects assigned;
no inconsistent within-class or representative cross-class matches.
**This does not by itself assert GitHub CI or Python regression success.**

Run the exact committed tests from the repository root:

~~~bash
python -m unittest network.tests.test_arc_like_marked_quotient -v
~~~

## Connection to the existing finite-stem operator extension

The separate [finite-stem operator](stemmed_operator_system.py) already
admits gauges whose scalar schedule has a finite head before a repeating
tail. The two bridges above are **not missing** from that enlarged
operator family. The new `MissingGaugeBridge.stem_gauge()` builds an exact
`StemGauge` from the already certified arrow's head, period and incoming
gain. It verifies that the full target process is reached and the marked
root is preserved. No new alignment is silently chosen.

The regression suite checks that each bridge is reproduced as the actual
marked arrow by the finite-stem gauge interface, then survives exact
gauge/shift interchange with its witness transported. Thus we can
separate three precise levels:

1. **Closed eight-gauge group:** 36 orbits on the 270 objects.
2. **Complete diagonal marked-equivalence quotient:** 34 classes,
   which are strictly coarser than the eight-gauge orbits.
3. **Existing finite-stem gauge extension:** supplies the additional
   arrows needed to bridge those two quotient differences.

These are statements about complete *marked diagonal* A/B witnesses in
this finite object universe. They do not imply that every conceivable
marked-process operator is admitted, or that the finite-stem group is
exhaustive for arbitrary non-diagonal transformations.

## The wall and next referent

**CLOSED:** finite eight-gauge action on the 270-object universe, with
explicit canonical root-stem preservation.

**CLOSED for the specified equivalence:** complete finite quotient under
the existing coinductively decided *diagonal marked A/B* relation. The
two additional bridges have exact witnessed arrows.

**NOT the same:** a finite group action and the full diagonal groupoid.
Allowing an eventually periodic gauge witness enlarges the morphism
family, even without adding new source objects.

**UNKNOWN:** transformations with nonperiodic gauge oracles, arbitrary
non-diagonal marked A/B conjugacies, admission of new rule tables or
root operations, and any native ARC solving / universal construction
stopping principle.

**Next mathematical referent:** test an independently justified
**non-diagonal** operator on marked A/B process worlds, or provide a
precise invariant-based counterexample. The finite-stem diagonal
family already realizes the two missing eight-gauge bridges, so do
not repeat that solved layer. Do not equate completeness of the
34-class diagonal marked-object quotient with completeness of
arbitrary arrow composition or universal A/B closure.
