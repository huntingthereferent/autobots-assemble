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
