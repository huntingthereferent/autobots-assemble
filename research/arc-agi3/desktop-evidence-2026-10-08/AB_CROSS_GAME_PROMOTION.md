

# Cross-game A/B promotion

A/B has now been applied as the same trace-to-state operation across multiple unrelated ARC environments.

The operation does not contain game-specific semantics.

Input witness form:
- current public referent
- available witnessed relations such as prior observations and prior actions
- observed continuation vector under tested actions

A/B family closure:
- collapse when continuation agrees;
- otherwise retain the smallest relation-set that restores continuation closure;
- preserve every equally-minimal witness set as provenance;
- return the surviving continuation class as the reusable state.

## Proven spectrum

### BP35
Shallow public tree:
- raw referents: 13
- A/B states: 13
- extra states: 0
- no retained relation required.

This is the collapse case.

### DC22
Shallow public tree:
- raw referents: 10
- A/B predictive states: 23 in the single-witness implementation
- split referents: 5

When all candidate sources are exposed, every split has three equally-minimal one-relation witnesses:

- prev_action2
- prev_obs1
- prev_obs2

A/B now preserves all three as witness provenance instead of choosing one by lexical order.

### CN04 Level 6
Public trajectories:
- raw public referents: 132
- A/B states: 140
- exactly 8 necessary extra states
- 124 referents collapse directly
- 8 retain prev1

All observed five-action continuation vectors are deterministic from the A/B states.

### CD82
Depth-4 public tree:
- witnesses: 151
- raw public referents: 27
- A/B predictive states: 65
- extra states: 38
- split referents: 10

Seven split referents need one relation:

- prev_action1

Three split referents require a genuine joint two-relation witness.

For each of those three, the complete equally-minimal witness family is:

- (prev_action1, prev_action2)
- (prev_action1, prev_obs1)
- (prev_action1, prev_obs2)

No one relation closes those three referents.

All three joint source paths predict the same continuation classes.

### Additional shallow controls

ft09:
- raw 3
- split 0

g50t:
- raw 5
- split 4
- maximum retained arity 1

ka59:
- raw 15
- split 0

lf52:
- raw 4
- split 2
- maximum retained arity 1

lp85:
- raw 2
- split 0

## All-sources correction

Earlier A/B family code selected the first minimum separator by relation-name ordering.

That was accidental structure.

The corrected layer returns all equally-minimal separator sets.

State identity is the witnessed continuation-equivalence class.

Minimal separator sets are provenance/sources for that state.

Prediction succeeds only when the applicable minimal source paths agree.
If they disagree, A/B has not closed and recursion continues.

Evidence:
- ab_family_all_minima.py
- test_ab_family_all_minima.py
- ab_trace_machine_v2.py
- test_ab_trace_machine_v2.py
- dc22_ab_all_minima.py
- cd82_ab_all_minima.py
- test_ab_trace_machine_v2_real.py
- ab_cross_game_shallow_tree.py
- ab_cross_game_relation_edge_scan.py

## Current movement

There is no separate memory algorithm, source algorithm, or predictive-state algorithm.

The observed shapes are consequences of repeated A/B:

witness family
-> A/B
-> continuation class
   + every minimal surviving witness source
-> reusable output
-> A/B again

A/B may:
- collapse the referent unchanged;
- retain one relation;
- retain a joint relation-set;
- retain several equivalent minimal source sets;
- recursively split its own prior output when later evidence requires it.


# Source-family recursion promotion

A/B has now been applied one layer above individual retained relations.

DC22 minimal witness family:

    { prev_action2
    | prev_obs1
    | prev_obs2 }

CD82 joint minimal witness family:

    { prev_action1 + prev_action2
    | prev_action1 + prev_obs1
    | prev_action1 + prev_obs2 }

A/B over these two source families preserves the shared residual family:

    R = { prev_action2 | prev_obs1 | prev_obs2 }

and retains only the difference:

    DC22 core = {}
    CD82 core = { prev_action1 }

Therefore:

    DC22 = R
    CD82 = prev_action1 + R

The residual family R is itself now a valid reusable A/B referent.

This is not a new source-family algorithm.
It is the same operation one layer up:

individual witnesses
-> A/B
-> minimal source family
-> A/B
-> shared residual family + surviving core
-> reusable output
-> A/B again

Evidence:
- ab_cross_game_source_factor.py
- ab_source_family_recursive_object.py

Current movement:
A/B the higher-order source-family objects themselves.


# Witness-antichain and atom-quotient promotion

The minimal witness source families admit a canonical antichain representation.

Each minimal sufficient relation-set is one antichain edge.

Semantics:
- relations within an edge are jointly required;
- separate edges are alternative sufficient witnesses.

Observed examples:

    G   = A1

    R   = A2 OR O1 OR O2

    S   = A1 OR A2 OR O1

    CD  = (A1 AND A2)
       OR (A1 AND O1)
       OR (A1 AND O2)

and CD factors exactly as:

    CD = A1 AND R

A/B across R and S preserves the reusable subfamily:

    K = A2 OR O1

with:

    R = K OR O2
    S = A1 OR K

K is a valid recursive A/B output even though no scanned environment had to instantiate K as a whole source family.

The antichain witness algebra was tested for:
- idempotence
- commutativity
- absorption
- associativity on representative closure states
- distributivity on representative closure states
- top/bottom boundary behavior

With four named relation atoms:

    A1 = prev_action1
    A2 = prev_action2
    O1 = prev_obs1
    O2 = prev_obs2

the complete canonical witness-antichain space contains 168 states when the empty witness-set boundary element is included.

## A/B over the relation atoms themselves

Across the real higher-order source families witnessed so far:

    G, R, S, CD

the atom role signatures are:

    A1  distinct
    A2  equivalent to O1
    O2  distinct

Thus current evidence yields the A/B quotient:

    [A1], [A2/O1], [O2]

Important:
this is not a permanent declaration that A2 and O1 are identical.
It is the current witness-equivalence class.
Future evidence that gives them different continuation roles must split the class by A/B again.

Quotienting the full 168 four-name witness space by A2 ~ O1 produces exactly 20 canonical states.

An independently generated three-generator witness space also contains exactly 20 states, and the two sets are equal.

Therefore under current cross-game evidence:

    168 named witness states
    -> A/B atom quotient
    -> 20 evidence-distinct witness states

This is recursive compression at the relation-vocabulary layer itself.

Evidence:
- ab_witness_antichain.py
- test_ab_witness_antichain.py
- ab_witness_algebra.py
- test_ab_witness_algebra.py
- test_ab_witness_algebra_laws.py
- test_ab_witness_lattice_168.py
- ab_atom_role_quotient.py
- test_ab_atom_quotient_lattice.py
- ab_g50t_lf52_sources.py
- ab_remaining_games_source_shapes.py

# Recursive information-closure correction

Later evidence corrected two earlier promotions without invalidating them as evidence.

## 1. The shallow atom quotient was not permanent

At shallow depth, A2 and O1 had identical witnessed higher-order roles:

    A2 ~ O1

and the 168 four-name witness states quotiented to a complete 20-state
three-class witness space.

Depth-5 evidence split that equivalence.

DC22 introduced witness families containing O1 without A2, so:

    A2 != O1

under the deeper witness contract.

The shallow 168 -> 20 quotient remains valid evidence for the shallower layer.
It is not the current promoted relation vocabulary.

The same deeper scan introduced A3, A4, O3, O4.
Across the depth-5 source-family roles there are 8 names and 7 current
role classes; A4 and O4 remain role-equivalent under that specific evidence.

However, source equivalence is referent-local rather than globally semantic.
Real SK48 witnesses show, for example:
- A4 and O4 can induce the same occurrence partition at one referent;
- A3 and O2 can be aliases at another;
- A1, A2, O1 can all be aliases at another;
- A1 and O1 can be distinct proofs elsewhere.

Therefore global name quotienting is evidence only.
The correct A/B quotient is local to the witnessed referent.

## 2. Minimal relation count was not minimal information

Earlier code first minimized the number of relation names and then compared
the resulting witnesses.

Real DC22 falsified that as the promoted criterion.

For the old source family:

    A2 OR O1 OR O2

all three single relations predict the continuation, but their occurrence
partitions differ.

A2 and O1 induce the same finer partition.
O2 induces a strictly coarser sufficient partition.

A/B therefore retains O2.

The current rule is:

    enumerate witnessed relation subsets
    -> compute their induced occurrence partitions
    -> keep sufficient partitions
    -> remove any partition strictly finer than another sufficient partition
    -> retain the coarsest sufficient partition(s)
    -> preserve minimal source sets that realize each surviving partition

Thus A/B minimizes distinction, not vocabulary length.

Evidence:
- ab_partition_provenance.py
- ab_information_minimal_provenance.py
- ab_information_closure.py
- dc22_partition_provenance.py
- cd82_information_minimal_provenance.py
- test_real_direct_information_closure.py

## 3. Continuation partition is the target quotient

For every tested ambiguous DC22 referent, direct information-minimal A/B
reconstructed the continuation-equivalence partition exactly.

CD82 exposed the next layer.

For referent be775c83b8f0:

    best old-relation partition: 8 blocks
    continuation partition:      4 blocks

No available raw history relation subset realizes the 4-block quotient.

Therefore A/B must create a new relation rather than continue searching the
old vocabulary.

ab_relation_synthesis.py records the witnessed merge:

    old proof blocks -> continuation classes

and the synthesized continuation class becomes a valid next A/B input.

## 4. Recursive reuse reaches a witnessed fixed point

On a bounded CD82 public tree, synthesized A/B outputs were recursively fed
back as state inputs.

Depth-5 tree:

    one-step classes: 48
    A/B pass 1:       56
    A/B pass 2:       59
    A/B pass 3:       60
    next pass:         60

Seven public referents split beyond their one-step continuation quotient.

The generic implementation is ab_recursive_partition.py.

Cross-game bounded depth-4 evidence:

    BP35: 20 -> 23 -> 25 -> 25
    DC22: 24 -> 30 -> 30
    CD82: 27 -> 31 -> 32 -> 32
    SK48: 43 -> 55 -> 56 -> 56

So recursive A/B refinement is not specific to CN04 or CD82.

## 5. A/B closure frontier

Increasing the witnessed horizon moves new distinctions through the state tree
one edge at a time while the already-closed prefix remains stable.

CD82:

    H4 -> H5: first new split at depth 1
    H5 -> H6: first new split at depth 2
    H6 -> H7: first new split at depth 3

DC22:

    H4 -> H5: first new split at depth 2
    H5 -> H6: first new split at depth 3

SK48:

    H4 -> H5: first new split at depth 3
    H5 -> H6: first new split at depth 4

The offset depends on what the existing referent/continuation evidence already
distinguishes, but each added continuation horizon advances the unresolved
A/B frontier by one tree edge in these witnesses.

Evidence:
- cd82_recursive_ab_fixed_point.py
- ab_fixed_point_cross_game.py
- cd82_ab_horizon_stability.py
- ab_horizon_frontier_cross_game.py

## Current promoted operation

A/B is currently represented by the following movement:

    witnessed occurrences
    -> compare continuation
    -> quotient by continuation-equivalence
    -> find the coarsest available evidence partition that realizes the quotient
    -> if old relations cannot realize it, synthesize the quotient as a new relation
    -> use that output as the next referent
    -> A/B again
    -> repeat as new continuation evidence arrives

Older state names, source families, antichains, and atom quotients remain evidence.
They are not promoted over the recursive operation.
