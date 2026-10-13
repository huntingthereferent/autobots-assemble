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

## Example — observation, not a command

James has described "swallowing" observations from several situations at once. The same word also occurs in the repository's technical `swallow X` operator. If the conversation is about what he is observing, selecting `LAYER.ABSORB` would be the wrong operation. Preserve the words and their context, then return UNKNOWN or candidates where necessary.

Likewise, "yes surfing :)" followed an explanation of *regrounding* in conversation. It is a metaphor and confirmation in that context, not an automatic instruction to move an engine. "Isn't that math?" introduces mathematics into the conversation and can itself be examined; a decoder should not require an external mathematics step to recognize that relation.

**Reground instead of guessing:** recover the continuing relationship, what changed on the branch, and the intended return point. [Regrounding](../REGROUNDING.md). A decoder's selected shape remains one scoped interpretation, not the full human observation.
