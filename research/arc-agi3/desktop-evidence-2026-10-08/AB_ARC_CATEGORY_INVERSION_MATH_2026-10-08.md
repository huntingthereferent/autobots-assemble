# ARC / A/B — Complete-category swallow -> inverted mathematical projection

Date: 2026-10-08
Status: RESEARCH CONTINUATION, NOT AXIOM OR GENERAL GAME RULE
Workspace: C:\Users\teepa\arc3\AB_ARC_EVIDENCE
No GitHub changes. No game submission.

## 0. Provenance order (CRITICAL)

Our work began from observed MOVEMENT. We used A/B to compare and
categorize actual observed continuations. We then translated the
surviving categories into formal mathematical representations.
This report now inverts those earned representations as a deliberately
new PROJECTION. It does not silently treat those projections as
additional observations.

    native states + witnessed actions
      -> A/B categories, corrections, unknowns
      -> formal mathematics of preserved distinctions
      -> inverse correspondences (candidate prior states)
      -> optional generated refinements (hypotheses)
      -> new witnessed action to earn/reject a projection

This respects "language first, then math one layer up, then implementation".
Boundary Math is a distinct WATCH formalism, not a definition of A/B.

## 1. Swallowed ARC evidence families, not a single game

AR25: The complete returned 64x64 board is the referent. Native action
triples make each movement witnessed. Level 2 completed after retaining
the exact 8-cell held 11->4 counterpart exchange across whole board
returns; 136 distinct whole boards at that watched referent admitted
two observed outcomes: 8 held or 8 restored. This is a target-relative
reduction, not the assertion that an 8-cell binary field *is* a board.
Level 3 exact returned-state first-action quotient was
{1},{2},{3,4,7},{5}; 100 walls gave 55 distinct boards. Its older
2/8 report must not be confused with the later SK48 8/8 result.

SK48: Pixels distinguish attached colored objects from mere alignment.
Native action phase and history matter: equal visible frames can have
different next responses. A/B retains the relevant history witness.
Moving the active 6x6 control sprite is different from action-button
identity; multiple controls coexist. Every level's returned completion
must close the current action list at first completion, with unused
candidate moves preserved but not applied to the next stage.
Full SK48: 8/8 native WIN from saved-reference-assisted alternatives.
Later the local Level2 controller found a distinct 30-action path using
native public observations without loading the old Level2 positive
action history. Other levels remain reference-assisted.

BP35 / DC22 / CD82 / CN04 and control environments:
A/B can have no extra memory (BP35), one necessary relation, several
equivalent minimal source families, jointly required source relations
(CD82), and recursive splits of initially similar observations (CN04
and deeper CD82). "Fewest variable names" was falsified as the global
information-minimal criterion. A/B instead seeks the coarsest sufficient
witnessed occurrence partition. An old source vocabulary may be too
fine: CD82-shaped old proof partition 8 blocks, continuation partition
4 blocks. Synthesizing that class as a relation was the correction.

Recursive bounded refinements reach stable partitions in observed
horizons; deeper continuation evidence can split shallow categories.
Shallow global A2~O1 atom quotients did NOT survive deeper DC22
evidence. Therefore all category equalities remain W- and
horizon-relative; no cross-game permanent atom identity.

Provenance documents: AR25_SOLVE_DOCUMENTATION.md,
ARC_ar25_AB_Progress_Report.pdf,
AB_CROSS_GAME_PROMOTION.md,
SK48_NATIVE_PHASE_AB_REPORT_2026-10-08.md,
SK48_PUBLIC_AB_CONTINUATION_2026-10-08.md,
SK48_ROUTE_BLIND_LEVEL2_DISCOVERY_2026-10-08.md,
SK48_FULL_NATIVE_ALTERNATIVE_8OF8_REPORT_2026-10-08.md.

## 2. Forward mathematics: witnessed state transition AND A/B quotient

Let O_W be the collection of *witnessed occurrences* under
contract W (including public referent, admitted action/history
relations, and tested continuations). A generic native transition
witness is (x,a,y) in E_W, and the earlier AR25 working kernel was:

    x_(n+1) = AB_W(x_n)

This is shorthand for a witness-gated continuation, not proof that the
physical environment has a single invertible map on visible x alone.
Concretely, under finite observed continuation horizon h, let
C_W,h(o) be the actual tested action-labelled future trajectory
signature for occurrence o.

    o_i ~_(W,h) o_j
       iff C_(W,h)(o_i) = C_(W,h)(o_j)
       on the tested, applicable continuations.

Missing tests are UNKNOWN. Equal visible pixels do not suffice.

The A/B categorization quotient is

    q_(W,h): O_W -> Q_(W,h) = O_W / ~_(W,h)
    q_(W,h)(o) = [o]_(W,h)

An evidence relation subset S is sufficient if each S-partition
block is continuation-pure. Retain coarsest sufficient induced
partition(s), their minimal realization sources, and provenance.
If the old relations cannot achieve the actual continuation
partition, synthesize the quotient as a new relation and A/B again.

## 3. Mathematical inversion (two different operations)

A. INVERSE TRANSITION CORRESPONDENCE

    E_W^T(y) = { (x,a) : (x,a,y) in E_W }

This retrieves all witnessed predecessor/action pairs for a returned
state. A unique inverse E_W^-1(y) is NOT earned without a witnessed
one-to-one inverse map. Some actions dissipate resources, so there
may be many-to-one outcomes and no physical inverse action.

B. INVERSE A/B CATEGORY (closer to the proposed projection)

    q_(W,h)^-1(c) = {o in O_W : q_(W,h)(o)=c}

This re-expands an earned category into *all witnessed members*.
Across consecutive quotient layers:

    C_m --q_(m-1)^-1--> C_(m-1)
        --q_(m-2)^-1--> ... --q_0^-1--> original occurrences

All arrows here are set-valued fibers, not actions in the ARC game.

If q_1 and q_2 are valid nested surjections then the reverse
correspondence of their composition obeys:

    (q_2 o q_1)^-1(c) = union_{b in q_2^-1(c)} q_1^-1(b)

This is the precise one-layer-up mathematical operation: the same
comparison structure, now applied to category members/categories.

## 4. Executed test: reverse CD82-shaped category witness

Used existing code and test fixture:
- ab_relation_synthesis.py
- test_ab_relation_synthesis.py
- ab_source_family_recursive_object.py

Empirically earned in the previously saved synthetic witness test:
    11 original occurrences -> 8 old proof blocks -> 4 future classes.

Current inverse test:
    4 classes -> 8 proof blocks -> all 11 original occurrences.

Fiber sizes of the four categories over the proof blocks: [2,1,4,1].
Exact recovered original occurrence sets:
    C0: {0,1}
    C1: {2}
    C2: {3,4,6,7,9,10}
    C3: {5,8}

No original index was lost, and no occurrence was assigned to
the wrong continuation class. This validates a category inverse
against the existing CD82-shaped *fixture*, not a fresh game trace.

The same higher-order A/B source example retains:

    R = A2 OR O1 OR O2
    DC22_fam = R
    CD82_fam = A1 AND R

The reverse source expansion can recover each alternative witness
source path of R; it must not assert that A2/O1/O2 are the same
physical history or universally interchangeable.

Evidence: AB_ARC_INVERSE_CATEGORY_TEST_2026-10-08.json
Executable: _tmp_ab_arc_inverse_category_math.py

## 5. Projection beyond observed category fibers (hypothesis)

Witnessed fiber reconstruction is NOT yet creation. To GENERATE
branches beyond prior witnesses, explicitly introduce a candidate
operator family G_W(c) and preserve unknown status until tested:

    Project_(W)(c) = q_W^-1(c) union G_W(c)
    G_W(c) unverified until admitted by a new native witness.

Never silently call a hypothesized category member an observed one.
Nor is every reconstruction uniquely reversible. Some categories
cannot be de-quotiented uniquely without preserved provenance.

The mathematical branching recursion can be written

    K_(n+1) = union_{g in G} g(K_n).

This makes a true self-similar fractal only with extra structure:
e.g. contraction maps on a suitable metric space, recurring across
scales. In that setting the familiar invariant attractor obeys

    K = union_{g in G} g(K).

A small explicit TEST/DEMO (not inferred from ARC rules):

    g0(x) = x/3
    g1(x) = (x+2)/3
    K_(n+1) = g0(K_n) union g1(K_n)
    K0 = [0,1].

Repeated levels had 2,4,8,16,32,64 intervals with width 3^-n;
their total retained lengths were (2/3)^n. This is the usual Cantor
construction. It shows a mathematically feasible branching fractal,
not evidence that ARC or A/B intrinsically implements Cantor geometry.

The formal lesson is:
    reverse quotient -> possible witnessed histories/categories
    hypothesis generator -> new candidates
    native witness -> earn/split/reject
    A/B -> recategorize at the new higher layer

Without the hypothesis generator, inverse A/B is a multivalued
reconstruction; with the generator and native witness, it becomes
a testable route to building a richer, recursively projected environment.

## 6. Precise boundary

Tested now:
- Category fiber inverse recovers 11/11 fixture members: PASS.
- Recursive source family common/different factors: PASS.
- Purely mathematical Cantor-generation fixture: PASS.

Not tested/NOT earned:
- That full ARC native engine transitions are invertible;
- That a public-frame quotient can be reversed without its history;
- That an ARC game rule itself is a contractive fractal generator;
- That the inverted projection produces interesting new tasks
  or tasks consistent with native ARC physics.

Next work should use real native recorded A/B category maps (not
only test fixture) and feed predicted reverse-branch candidates into
one witnessed forward test. Retain original provenance and failed
branches. Do not create a second agent; the existing A/B evaluator
can consume this inverted candidate family one layer above.
