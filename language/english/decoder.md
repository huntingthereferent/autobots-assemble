# English Decoder

## Purpose

Recover the movement that matters for continuation from ordinary, slang, internet, terse, or technical English.

## Sequence

1. Preserve the actual surface form.
2. Identify the active referent/context.
3. Retrieve candidate shapes from the bank.
4. Preserve pragmatic modifiers.
5. Eliminate candidates contradicted by the current referent.
6. If one continuation-relevant distinction remains unresolved, return alternatives and clarify.
7. Emit the selected language-neutral shape ID only when supported.

## Example — “send it”

Possible candidates:

- `MOVE.CONTINUE` — proceed with what we are already doing.
- `WORK.SUBMIT` — submit/deliver the artifact.

If the current referent is *building a prototype*, “send it” may mean continue.  
If the current referent is *a completed Freelancer proposal awaiting submission*, it may mean submit.

The words alone do not decide.

## Example — “nah”

Possible candidates:

- `CORRECT.NEGATE`
- a pragmatic disapproval modifier around some other movement

If the next action depends on which one is meant, clarify. Do not hard-code slang as one permanent meaning.
