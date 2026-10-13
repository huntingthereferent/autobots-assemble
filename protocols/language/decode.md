# Protocol — Language Decode

## Referent

The active conversational/work referent, not the words by themselves.

## Input

A surface utterance plus available context.

## Witness contract

- preserve the original surface;
- retrieve candidate movement shapes;
- preserve pragmatic/register modifiers;
- use the current referent to eliminate unsupported candidates;
- if a remaining ambiguity would change continuation, preserve alternatives and clarify.

## Output

A language-neutral shape ID (or candidate set/UNKNOWN) plus pragmatic modifiers.

Decoding is interpretive projection. It does not itself mutate the network.

## Reground before forcing a shape

When a phrase participates in a longer conversation, preserve the [language referent](../../LANGUAGE_REFERENT.md) and [regrounding context](../../language/REGROUNDING.md). Outward observation, joke, silence or reported feeling cannot automatically be treated as a work command. "Swallow" can describe observations rather than invoke layer absorption; "surfing" can describe regrounding rather than execute a movement.

Retain original utterances and speaker context. The same person may be playful, blunt, caring, or technical. Mark interpretations as interpretations, not rewritten quotes, and emit UNKNOWN when the relevant meaning is unresolved.

## Reground before forcing a shape

When a phrase participates in a longer conversation, preserve the [language referent](../../LANGUAGE_REFERENT.md) and [regrounding context](../../language/REGROUNDING.md). Outward observation, joke, silence or reported feeling cannot automatically be treated as a work command. "Swallow" can describe observations rather than invoke layer absorption; "surfing" can describe regrounding rather than execute a movement.

Retain original utterances and speaker context. The same person may be playful, blunt, caring, or technical. Mark interpretations as interpretations, not rewritten quotes, and emit UNKNOWN when the relevant meaning is unresolved.
