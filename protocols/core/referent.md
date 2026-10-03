# Core Protocol — Referent

## Input

- current referent
- explicit user instruction, current task state, or supported relation proposing movement

## Witness contract

A referent change is admitted only when at least one is true:

- the user explicitly changes the referent;
- the current task reaches a necessary sub-referent;
- the current referent is solved and its recorded continuation points to the next referent;
- an explicit wall routes to a named dependency.

## Movement

Preserve the old referent as evidence. Record the new referent and the reason/witness for the transition.

## Wall

If several candidate referents exist and no witness selects one, preserve the current referent and record \`UNKNOWN\` rather than choosing by convenience.

## Continuation

The selected referent is valid input to this same protocol on the next movement.
