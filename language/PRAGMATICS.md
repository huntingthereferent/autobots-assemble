# Pragmatic Modifiers

A shape captures the continuation-relevant movement. Pragmatics capture how that movement is being performed.

Useful modifier axes include:

- `tone`: neutral, warm, annoyed, playful, sarcastic, hostile, uncertain
- `intensity`: low / medium / high
- `politeness`: blunt / neutral / deferential
- `certainty`: tentative / ordinary / emphatic
- `urgency`: none / soon / immediate
- `stance`: approving / disapproving / neutral
- `irony`: literal / ironic / unknown
- `audience`: private / public / technical / peer
- `compression`: full / ordinary / terse / telegraphic
- `register`: standard / plain / casual / slang / internet / caveman / technical

Example:

`"cook"`

may decode as:

```json
{
  "shape": "MOVE.CONTINUE",
  "pragmatics": {
    "register": "internet",
    "stance": "approving",
    "compression": "terse"
  }
}
```

while `"continue"` may produce the same movement shape with neutral pragmatics.

The shape preserves continuation. The modifiers preserve the social surface instead of pretending the two utterances are identical.

## Attribution and retired sources

A language interpretation is not evidence of a person's private thoughts. Quote only what remains intentionally published in the current writing archive, and distinguish authored material from AI paraphrase. A retired conversation, deleted page, or historical Git revision must not be used to restore quotations that have been withdrawn.

[Human Drift](HUMAN_DRIFT.md) records conceptual boundaries rather than an archive of original dialogue. [Regrounding](REGROUNDING.md) records a response to drift.


