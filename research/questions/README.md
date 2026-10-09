# Research question board — checkpoint contract

This is a research output. It does not replace the original questions, decide
mathematical equivalence, create tasks, or silently update the source evidence.

## Freeze and reconcile

1. A checkpoint freezes the questions **as stated at that time**. The first
   checkpoint preserves the six original questions from the October 9 public
   research notebook without guessing answers.
2. In the next pass, read the original question and current relevant evidence.
   Mark it ANSWERED only if the recorded witness settles it **for the stated
   scope**. Mark PARTIAL if evidence settles a proper portion, UNKNOWN if
   evidence remains insufficient, or OPEN when a newly derived question is
   intentionally active. REVIEW means not yet reconciled.
3. For ANSWERED or PARTIAL, include a nonempty answer, exact scope, and at
   least one independently locatable witness. Do not promote inferred
   generality or substitute a summary for a source.
4. Keep the original question ID, origin, and past checkpoint unchanged.
   Record narrower unresolved conditions and any new question IDs explicitly
   through `next_question_ids`; new records link back through `derived_from`.
5. **Create a new checkpoint file**, register it in `index.json`, then
   advance `current`. Do not edit old checkpoint files.
6. The board renders those registered snapshots. Browser controls change
   only the viewed checkpoint; they never modify mathematical conclusions.

A sample later checkpoint might record:

```json
{
  "id": "Q-001",
  "question": "Which state relations survive a change of representation?",
  "status": "PARTIAL",
  "answer": "A witnessed conjugacy survives the specifically checked change.",
  "scope": "Named finite-field family and declared state space only",
  "boundary": "Arbitrary transformations remain unclassified.",
  "witnesses": [
    {"label": "Exact conjugacy witness", "url": "https://github.com/..."}
  ],
  "derived_from": [],
  "next_question_ids": ["Q-007"],
  "origin": "https://github.com/..."
}
```

The example is a *schema illustration*, not an admitted actual answer.

## Publication boundary

The board endpoint is read-only. Results are Git-versioned source records
with attributed witness links and explicit epistemic states. A public webpage
or GitHub summary does not substitute for runnable tests. This is not a
live synchronization or multi-user editing feature.
