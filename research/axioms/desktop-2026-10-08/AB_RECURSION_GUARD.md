# A/B Recursion Guard — experiment

Purpose: test whether drift occurs because an unwitnessed map is inserted between valid A/B applications.

## Kernel
For a fixed witness/evidence contract W:

    x[n+1] = AB_W(x[n])

Closure:
    AB_W(x) in Dom(AB_W)

No-interposition:
    No map f : x[n+1] -> y may be inserted between recursive calls
    unless f itself is witnessed under W.

Skip:
    AB_W^k(x) means repeated application of the same operation.
    A skip does not introduce a new operator or require externalizing
    intermediate representations.

Boundary:
    If the returned output does not support another application under W,
    return UNKNOWN/PARTIAL at that representation.
    Do not invent a bridge to continue.

## ARC witness contract
Referent: the complete returned game board/state.
Permitted interaction: game actions supplied by the environment.
Goal/closure witness: returned environment state, including levels_completed.
Provenance: the relation supporting movement must survive into the returned input.

A derived description (objects, hashes, components, generators, symmetry,
algebra, action labels, etc.) may be diagnostic evidence, but it cannot
replace the whole returned state as the referent unless that replacement
map is itself witnessed.

## Audit at every recursive boundary
1. INPUT: exact evidence-bearing output from the previous call.
2. RELATION: state only the relation witnessed under W.
3. MOVEMENT: execute only movement supplied by that relation.
4. RETURN: accept the complete returned state as the next input.
5. CHECK: did W survive?
   YES -> recurse immediately.
   NO  -> UNKNOWN/PARTIAL.
6. INTERPOSITION CHECK:
   If a new representation, heuristic, analogy, symmetry, generator,
   search policy, or interpretation appears between RETURN and the next
   AB call, identify its witness. No witness -> reject it.

## Failure examples already observed
- Whole board -> generator algebra -> next action:
  rejected unless the board-to-algebra map authorizes that movement.
- Solved L1 sequence -> rotations/reflections -> L2 trials:
  rejected because symmetry correspondence was not witnessed.
- Relation -> conventional semantic label -> permission to execute:
  label is unnecessary; the relation/witness contract is sufficient.

## Test criterion
This guard is useful only if it changes behavior at the transition where
drift previously occurred. Passing means recursive continuation remains
on the same evidence contract without an unwitnessed intermediate map.
It does NOT by itself prove general A/B closure.
