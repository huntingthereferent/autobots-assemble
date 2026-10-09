# CN04 causal operator discovery and solve

## Result

CN04 is solved from a fresh environment:

- levels_completed = 6
- state = WIN
- no predeclared reflection family
- no predeclared affine transform family in the solve loop
- action-5 semantics are discovered empirically per object
- completion is solved as typed latent-marker exact cover

## Why CN04 matters

AR25 established:

intervention -> causal affine relation -> commuting operator orbit -> target coverage.

The open question was whether intervention-first discovery could handle a different operator family without being told the transform class in advance.

CN04 answers yes.

## Operator discovery

On Level 1, action 5 changes the selected object's local shape.

A labeled-grid adjacency isomorphism was computed between the before and after states without assuming rotation/reflection/affinity.

One-step structure alone admitted two graph isomorphisms because the object had an internal symmetry.

Repeated intervention resolved the ambiguity:
the only coordinate rule consistent across the full four-step cycle had linear part

(r,c) -> (c, H-1-r).

The same learned structural map transferred to a previously unseen second object after canonicalizing presentation colors.

This established an order-4 geometric operator from adjacency + continuity rather than from a predeclared transform class.

## Latent versus presentation state

A failed raw-color transfer exposed a separate rendering layer.

Selection can remap ordinary material colors while preserving the structural roles:
- empty
- ordinary material
- special marker

A later mismatch exposed an even stronger distinction:
rendered markers can collapse semantic marker types.

The completion algebra therefore cannot use rendered color directly.

The retained semantic state is:
- latent marker type (8 or 13)
- current action-5 state
- current transform/rendered geometry
- position

Semantic marker coordinates are obtained by rendering the latent base mask through the object's current state.

## Completion contract

For every visible object, special marker cells are projected into global coordinates.

Completion requires every typed marker key

(x, y, marker_type)

to occur with multiplicity exactly 2.

Position-only matching is insufficient: Level 2 produced a false structural solution in which marker positions aligned but types 8 and 13 were swapped.

## Empirical action-state cycles

The solver does not assume that action 5 always means rotation.

For each visible logical object:
1. select it in a copied environment;
2. repeatedly apply action 5;
3. record the reachable semantic state;
4. stop when the full state repeats.

The discovered cycles across the six levels were:

Level 1: [4, 4]
Level 2: [4, 4, 4, 4]
Level 3: [4, 4, 4]
Level 4: [4, 4, 4, 4]
Level 5: [9, 4, 4, 4]
Level 6: [11, 4, 7, 4, 4]

The Level-5 9-state cycle and Level-6 11-state / 7-state cycles include discrete sprite-variant transitions rather than a single geometric rotation family.

The same solver handles both because action 5 is represented as an empirically discovered state-transition cycle.

## Search

For every discovered action-5 state, the solver enumerates legal translations and records the resulting global typed-marker set.

The search is exact cover with multiplicity 2.

A marker-driven branching strategy is used:
- choose an unmatched typed marker;
- branch only on remaining object states that cover it;
- reject any branch that raises a marker multiplicity above 2;
- use action-count cost for branch-and-bound.

Fresh-run search results:

Level 1:
- cycles [4,4]
- nodes 2,422
- best cost 12

Level 2:
- cycles [4,4,4,4]
- nodes 59,730
- best cost 27

Level 3:
- cycles [4,4,4]
- nodes 8,800
- best cost 18

Level 4:
- cycles [4,4,4,4]
- nodes 409,504
- best cost 26

Level 5:
- cycles [9,4,4,4]
- nodes 672,482
- best cost 41

Level 6:
- cycles [11,4,7,4,4]
- nodes 2,154,680
- best cost 34

Final:
- levels_completed = 6
- state = WIN

## Promotion

The promoted abstraction is now:

intervention
-> empirical action-state graph
-> latent semantic projection
-> relational completion contract
-> constrained search
-> action execution

This is strictly more general than the prior AR25 reflection-orbit kernel.

The solver does not need to assign a semantic name such as "rotation" or "variant switching" to action 5 before using it.

The action's reusable meaning is its observed transition structure.

## Evidence files

- cn04_graph_operator_discovery.py
- cn04_operator_cycle_consistency.py
- cn04_transfer_learned_operator_object2_structural.py
- cn04_l2_latent_marker_diagnostic.py
- cn04_l3_direct_latent_render_solver.py
- cn04_l5_marker_driven_search.py
- cn04_final_level_search.py
- cn04_empirical_cycle_full_solver_v2.py

## New unresolved edge

The remaining abstraction boundary is no longer operator-family discovery.

It is:

Can the system discover the latent semantic projection and completion relation itself from interventions, without being given privileged access to the engine's latent marker mask or completion bookkeeping?

That is the next layer.


## Public-only semantic discovery promotion

A stricter experiment removed privileged semantic reads from the discovery loop.

Forbidden for this layer:
- hlxyvcmpk latent marker masks
- iahpylgry matched-marker bookkeeping
- direct reading of hidden marker type
- assuming public color directly equals semantic class

The learner used only:
- public result.frame
- public actions
- levels_completed / game-state outcome
- intervention history

### Public board reconstruction

The public frame is a 64x64 raster.
For CN04 the logical 20x20 board can be sampled from the visible 3x3 cell lattice.
Object/background colors are not fixed across levels, so background is inferred as the modal board value and foreground is segmented relationally.

### Level 1: hidden class discovery from success/failure

Both latent marker types render publicly as 8.

An isolated one-marker overlap changes the visible overlap cell to public color 3 regardless of hidden compatibility.
Therefore:

visible 3 = geometric overlap

not:

visible 3 = semantic compatibility.

Two full two-marker alignments were then tested.

Alignment A:
- both markers geometrically overlap
- level completes

Alignment B:
- both markers geometrically overlap
- public board shows two overlap cells
- level does not complete

The untyped completion hypothesis is therefore falsified.

Enumerating binary marker labels consistent with the two public outcomes yields exactly two assignments related by global label swap.
Thus the two latent marker classes are identifiable from public intervention up to renaming.

Evidence:
- cn04_public_grid_decode.py
- cn04_public_marker_compatibility.py
- cn04_public_full_alignment_tests.py
- cn04_public_hypothesis_elimination_l1.py

### Observation is not free

Using ACTION7 as a passive observation consumed the game's action budget and produced GAME_OVER during candidate testing.

The execution model was corrected:
- discovery runs may spend actions to inspect state;
- execution runs use frames returned by required actions;
- candidate execution is open-loop where the learned state model is sufficient.

This distinction is now part of the evidence contract.

### Level 2: active semantic discovery

From public frames only, Level 2 exposed:
- four foreground objects;
- four empirical action-5 cycles;
- 318 purely geometric marker-pairing candidates in the bounded search.

Candidates were tested in cost order using only public actions and the public completion signal.

Result:
- candidate 0 failed;
- candidate 1 succeeded;
- both had the same geometric cost 27.

Therefore success/failure supplies semantic information not present in the geometric projection.

The first public-only accepted Level-2 plan was:

public object 0: k=0, position (3,3)
public object 1: k=0, position (8,6)
public object 2: k=0, position (4,5)
public object 3: k=3, position (12,8)

Evidence:
- cn04_public_l2_untyped_solutions.py
- cn04_public_l2_active_discovery.py
- cn04_public_l2_success_control.py

### Level 3: public role inference and active learning

Level 3 showed two additional observation effects.

1. Selected style is not a fixed color.
   The selected object was inferred as the unique foreground component not flattened to public material color 4.

2. Connected components are not stable object identities.
   After an action-5 transform, one controlled object can touch another and merge into one public connected component.

Selection-induced rendering changes and intervention history are therefore required to track controlled state.

A public-only geometric search produced 1,631 candidate covers.

Active trials:
- candidates 0 through 35 failed;
- candidate 36 succeeded;
- successful geometric cost = 18.

Successful public configuration:

object 0: k=0, position (9,9)
object 1: k=0, position (5,4)
object 2: k=2, position (9,3)

### Recovering the latent Level-3 marker partition

The first 37 public outcomes were converted into binary-label constraints.

After quotienting away global label renaming, two hidden-class hypotheses remained.

A discriminating intervention was synthesized automatically:

k tuple: (2,0,0)
positions:
- object 0 -> (10,4)
- object 1 -> (11,4)
- object 2 -> (9,5)

Hypothesis H1 predicted failure.
Hypothesis H2 predicted completion.

Observed result:
- levels_completed remained 2
- therefore H2 was eliminated.

The surviving hidden partition is, up to class-name swap:

a0 = a1 = b1 = c0
b0 = c1
and the two groups differ.

This matches the engine's latent 13/8 split, but that engine state was not used to infer the partition.

Using the learned partition to prune geometry produced the minimum typed-compatible Level-3 plan directly at cost 18.

A fresh execution of that predicted plan produced:

levels_completed = 3

without latent semantic reads.

Evidence:
- cn04_l3_first37_pairings.py
- cn04_l3_discriminating_experiment_design.py
- cn04_l3_discriminating_experiment_execute.py
- cn04_l3_public_typed_prune.py
- cn04_l3_public_typed_prediction_execute.py

## Current promoted statement

For CN04, the hidden semantic projection is not merely recoverable from privileged engine state.

It can be reconstructed behaviorally from:

public observation
-> intervention
-> geometric overlap response
-> global success/failure
-> hypothesis elimination
-> latent equivalence classes
-> typed completion prediction.

This closes the previous unresolved edge for Levels 1-3.

## New unresolved edge

The next boundary is predictive state itself.

Later CN04 levels contain action-5 variant paths with repeated visible forms but different continuation behavior.

Therefore the public frame alone may cease to be Markov.

The next question is:

Can intervention history be automatically refined into the minimal predictive hidden state when two identical public observations have different future transitions?

This is the next layer.


## A/B placement at the predictive-state boundary

The causal/predictive-state work above must not replace A/B with a domain-specific label.

A/B remains the recursively reusable operation.

At this layer the witness is especially clean:

Two occurrences have the same current public observation O:

    O_A = O_B = b8e5aebd8004

but their valid continuations differ under the same tested actions.

Therefore the current public observation is not a sufficient referent for recursive reuse.

A/B acts on the two witnessed occurrences under the same evidence contract:

A:
    predecessor = c785f27b0ec2
    current     = b8e5aebd8004
    continuation under action 5 = 1b8305baa319

B:
    predecessor = 1b8305baa319
    current     = b8e5aebd8004
    continuation under action 5 = d00943ccf2e2

The visible current term is preserved because it is shared.
The predecessor distinction is retained because removing it destroys predictive closure.

The A/B output is therefore not merely the frame O.
It is the refined relation-state:

    (previous observation, current observation)

for this ambiguous equivalence class.

Crucially, that output remains a valid input to the same operation.

The next comparison can be:

    AB(A,B) versus C

under the same witness requirement:
if two refined states have the same evidence-bearing relation and the same future behavior, they may collapse;
if a future action separates them, the separating relation is retained and the output is lifted again.

So the movement remains:

    candidate states
    -> A/B under witness contract
    -> preserve shared relation
    -> retain only differences that change valid continuation
    -> output refined state
    -> reuse output as next A/B input

The domain-specific phrase "predictive-state refinement" describes what A/B produced here.
It is not a replacement for A/B.

Older representations remain evidence:
- rendered-frame equality was evidence;
- geometry was evidence;
- causal operator response was evidence;
- semantic class partitions were evidence;
- predecessor-conditioned state is the current promoted output only because it preserves the observed continuation distinction.

Do not promote a vocabulary layer over the operation.


## A/B restored as the operation

The predictive-state work is not a replacement for A/B.

A/B is the recursively reusable operation that produced the predictive state.

For each witnessed referent family:

1. hold the current referent fixed;
2. compare witnessed continuations;
3. if continuations agree, collapse;
4. if continuations differ, A/B the available relations;
5. retain the smallest relation-set that restores continuation closure;
6. treat that output as a valid next referent;
7. repeat under the same witness contract.

### Real CN04 Level-6 result

The generic family A/B kernel was applied directly to the public Level-6 trajectories.

Across all five objects:

- raw public states = 132
- A/B refined states = 140
- only 8 additional states were introduced
- all observed action continuations became deterministic

Breakdown:

- object 0: 26 raw -> 28 A/B states; 2 witnessed splits
- object 1: 28 -> 28; no split
- object 2: 22 -> 28; 6 witnessed splits
- object 3: 28 -> 28; no split
- object 4: 28 -> 28; no split

Every required split retained exactly one witnessed relation:

    prev1

This is not because "previous observation" is privileged in the operation.
The generic family kernel was also tested on a witness family where neither relation alone was sufficient.
A/B retained the joint relation-set (x,y), then successfully reused that output as the next referent and split it again on a new relation z.

Therefore:

predictive memory = one domain-specific consequence of A/B.

The operation remains:

    evidence family
    -> A/B
    -> minimum surviving relation-set
    -> reusable output
    -> A/B again

### Current promoted edge

Do not ask whether A/B can proceed.

Run A/B.

If one relation closes the continuation, retain one.
If several are jointly required, retain the minimum joint set.
If the resulting output later develops incompatible continuations, A/B that output again.

Current evidence files:

- ab_recursive_closure.py
- test_ab_recursive_closure.py
- ab_family_closure.py
- test_ab_family_closure.py
- test_cn04_l6_generic_ab_family.py
- test_cn04_l6_ab_predictive_table.py
