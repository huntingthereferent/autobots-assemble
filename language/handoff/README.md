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

A receiver validates the packet before resuming. It does not blindly inherit the sender's conclusions.
