# Central coordinate-translation symmetry of a pointed finite-field transformation system

## Current referent

The [pointed-arrow contract](WINDOW_MARKED_ARROWS.md) preserved the distinction between full-state conjugacy and an alignment of **chosen marks** across the declared 48-world family. We now admit a genuinely different operator that moves a mark *within the same world* without changing either A or B.

This is a construction in finite-field mathematics, **not** native ARC execution or an unbounded inverse-A/B stopping theorem.

## New operator: a central translation

For any depth d≥3 and r in F3, define:

```text
T_r(x0,x1,x2,x3,...) = (x0,x1,x2+r,x3,...)
T_r T_s = T_(r+s)
T_r^-1 = T_(-r)
T_1^3 = identity
```

The declared family has A changing x0, B updating x1 from x0, and B updating x2 by a function **only of x0 and x1**. All higher B couplings are zero. Consequently:

```text
T_r A = A T_r
T_r B = B T_r
```

for *every admitted world* at every depth. The translation is a bijective all-depth homeomorphism and commutes with dimensional truncation. It also commutes with the prior nonlinear H shears and R fiber-shift maps, because their x2 updates are additive and depend only on x0 and x1.

This is an independently admitted **symmetry of the existing world law**, not an additional coupling, new class, or hidden way of identifying two canonical origins.

## Marks must move explicitly

Let p be any pointed world (W,m). Applying T_r creates a new pointed target:

```text
(W,m) --T_r--> (W,T_r(m))
```

For the canonical origin:

```text
(W,(0,0,0)) --T_1--> (W,(0,0,1))
             --T_1--> (W,(0,0,2))
             --T_1--> (W,(0,0,0))
```

All three pointed objects share the same world dynamics, and each connecting **marked** arrow explicitly maps its source mark onto its target mark. An attempted arrow T_1 from (W,0) *back to (W,0)* is rejected as `MARK_MISMATCH`.

## Combining independent translations with H/R witnesses

The new [implementation](window_root_translation.py) adds `TranslationFactor` beside `ConjugacyFactor`, with both witness types preserved in the full ordered `OperatorPath`. A `PointedOperator` is admitted only when:

```text
path.map_state(source.mark) == target.mark
```

Composition requires the entire pointed middle object to agree; it refuses mere equality of underlying world descriptions when the marks differ. Inversion reverses the factor list and swaps the two stored directional H/R witnesses instead of silently rediscovering a different alignment.

For an existing pulse-only → combined R bridge at support 0 or 3, retain the original `MarkChange` record and its two positive-word root-counterexamples. For the target shear chart d, its first explicit target mark is:

```text
original canonical target mark:  (0,0,0)
H_d R H_-c(source origin):       (0,2,d)
after independently applying T_r: (0,2,d+r mod 3)
```

All three target marks are distinct, and **none** is the original target origin: their second coordinate remains 2. Central translation cannot turn this full-state-but-unrooted equivalence into a false equivalence of the canonical roots.

The reverse R bridge has its own root-image mark and is handled symmetrically.

## Finite certificate and verification

| Category | Count | Meaning |
|---|---:|---|
| Constructed world laws | 48 | Unchanged from the previous experiment |
| Canonical worlds × translated marks | 144 | Three distinct explicit points per world |
| Existing canonical-rooted ordered alignments | 144 | Preserved |
| Existing full-state but nonrooted ordered alignments | 36 | Still blocked as canonical marked arrows |
| Shift-extended rooted routes | 432 | 144 pairs × 3 translation amounts |
| Shift-extended originally nonrooted routes | 108 | 36 pairs × 3, retaining original root conflicts |
| Combined witnessed translated routes | **540** | Endpoints and full factor chains conserved |

[Fourteen focused tests](../../network/tests/test_arc_like_window_root_translation.py) cover reversibility/order 3, commutation with A/B and the older H/R maps, all state prefixes to depth six (with the direct group identity checked to depth seven), pointed squares, translation into explicitly different marks, inverse/composition of mixed witness factors, rejecting forged marks, and all 540 named routes.

**Execution boundary:** the committed Python module and tests match the locally tested copies by exact Git blob hashes. The **14 new tests and 14 previous pointed-arrow tests passed locally** using a reproduction of the 48-world transition/classifier dependency. The full GitHub repository test workflow must report its own result before claiming CI success.

Run:

```bash
python -m unittest network.tests.test_arc_like_window_root_translation network.tests.test_arc_like_window_marked_arrows -v
```

## Subsequent centralizer criterion: scope sharpened

The [two-predecessor centralizer theorem](TRANSLATION_CENTRALIZER.md)
generalizes this zero-higher-coupling symmetry exactly.
A nonzero higher rule does **not** necessarily destroy it.
For the coordinate shift of x2, the full generating action
commutes with the translation precisely when q1 is
independent of its second input and q2 independent of
its first. If q1 reads x2, the first obstruction is
in dimension four; if only q2 reads x2, the first
obstruction is in dimension five.

That theorem is a separate later result. It does
not retroactively broaden the 48-world zero-tail
certificate or erase any previously recorded mark.

## Wall, preservation, next referent

**CLOSED for this operator family:** A/B-commuting central translations and H/R witness composition, with exact mark conservation and transparent factor provenance.

**PRESERVED:** 14 full-state classes, 16 canonical-root classes, and the 36 original positive-word incompatibility certificates. Three additional marks in the *same* world do not make three new world laws.

**UNKNOWN:** centralizers of A/B for arbitrary nonzero higher couplings, general infinite-support marks, arbitrary non-diagonal maps, and universal A/B stopping or ARC puzzle execution.

**Next:** admit a nonzero higher coupling depending on x2, which may **break** the T_r commutation. Find the smallest coordinate depth and an explicit action-state counterexample. Preserve the existing T_r witness as a conditional theorem valid for the zero-tail family rather than treating it as universal.
