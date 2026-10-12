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

## Audit / correction continuity

An audit, failed test, or corrected interpretation does not by itself authorize changing the referent. Preserve the original question or claim; the evidence actually inspected or run; whether a failure was reproduced, merely reported, or remains UNKNOWN; the scope of any defect; and the smallest warranted next movement. An identical answer or endpoint does not make two questions, histories, or sources identical. Apply the standing neutral-audit and evidence-scope discipline in [AI session protocol](../ai/session.md) when the current task is evaluative.

## Continuation

The selected referent is valid input to this same protocol on the next movement.
