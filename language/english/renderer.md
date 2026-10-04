# English Renderer

The renderer takes a language-neutral movement shape plus pragmatic targets and produces English.

## Input

- shape ID
- active referent
- target register
- optional tone/intensity/politeness/stance/compression modifiers

## Rule

Choose a surface form from the requested register only if it preserves the movement and does not add unsupported force.

Examples for `MOVE.CONTINUE`:

- standard: “Continue.”
- plain: “Keep going.”
- casual: “Yeah, keep going.”
- slang: “Run it.”
- internet: “cook”
- caveman/telegraphic: “keep go”
- technical: “continue current movement”

These are not semantically identical in every social setting. They share the selected continuation shape; pragmatic differences remain visible.

## Safety against over-rendering

Do not turn:

- UNKNOWN into certainty;
- PARTIAL into completion;
- receipt into approval;
- continue into submit;
- a wall into failure;
- a narrower referent into a broader claim.
