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

## Keep the person with the words

[Regrounding](REGROUNDING.md) returns from a branch while preserving what happened there. Pragmatic tags are not a substitute for that record. In particular:

- A direct quote remains **verbatim**, including James's swearing, shorthand and jokes; an edited rendering is explicitly labeled a rendering.
- A blunt correction can coexist with care, humor, and technical precision. Do not infer a different speaker, character, intent or consent from a change of register.
- Absence of a reply is an observation only when an expected reply and an observation window are grounded; it cannot by itself establish why someone was silent or how they felt.
- Silence and speech can each help and harm. Those consequences require context, not an automatic positive/negative modifier.
- The same words can sound different after a detour. Recover the current referent before assigning tone, urgency or an action.

Modifier labels are descriptive aids, not psychological assessments or evidence that the speaker's entire meaning has been captured.
