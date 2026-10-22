# Handoff Language

Handoff language is the stable continuation spine between AI, human, tool, repository, and future-session surfaces.

The canonical packet is **language-neutral**. English, future languages, terse tool encodings, and human summaries are renderings of the same packet.

Required spine:

1. referent
2. goal
3. state
4. evidence
5. witnesses
6. movement
7. walls / unknown / partial
8. artifacts
9. do-not-upgrade constraints
10. next referent
11. return target

See `packet.schema.json`.

[Continuous Handoff — observational determination](CONTINUOUS_HANDOFF.md) describes how backward construction and branch openings can continue without deciding the evidence; native observational layers determine what is supported. [Runnable read-only example](../../runtime/examples/continuous_handoff/README.md).

A receiver validates the packet before resuming. It does not blindly inherit the sender's conclusions.

## Regrounding across the handoff

The [language referent](../../LANGUAGE_REFERENT.md) survives a change of speaker, tool or file only when the current relation is recovered, not merely because the packet repeats the same word. Preserve the actual correction and the path traveled when they matter. A branch need not be erased in order to return.

For human attribution, carry an exact quotation and mark AI-authored interpretation separately; changing tone or technical register cannot silently rewrite the speaker. James's playfulness, frustration, swearing, care and mathematical questions are not separate authored identities. See [Regrounding](../REGROUNDING.md).

The packet doesn't establish the receiver's understanding, actor identity, or consent. Validate actual evidence and authorization within the target system.


**Source withdrawal boundary:** Do not republish, reconstruct, or attribute quotations removed from the current [writing archive](https://github.com/huntingthereferent/huntingthereferent/blob/main/writing/README.md). Retain the distinction between an authorized quote, a technical example, and an AI paraphrase.
