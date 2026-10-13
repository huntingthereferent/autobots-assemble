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

## Preserve the actual voice

The speaker is not replaced when the target register changes. James may be humorous, emotionally expressive, blunt, profane and mathematically precise in the same inquiry. Choosing a formal rendering must not turn his observation into a stronger scientific claim; choosing a casual rendering must not invent his slang, feelings or consent.

Preserve unedited direct quotations when documenting what was actually said. A different rendering is **paraphrase or re-expression**, not an authentic replacement quote. Preserve uncertainty, branch provenance and the [regrounding relationship](../REGROUNDING.md).

The renderer is a scoped tool. It doesn't implement the full language referent or prove that the original interaction's meaning was preserved.
