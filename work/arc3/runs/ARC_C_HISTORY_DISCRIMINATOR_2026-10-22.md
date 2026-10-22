# ARC-C — History discriminator (2026-10-22)

Status: experiment specification; native execution pending.

## Existing evidence
- Equal-interior history experiment: 42 ACTION5 observations with matched pre-action interior and identical 22-frame animation series, despite varying histories/boundaries.
- Other original-native factorial and temporal studies observed 22, 23, 26 and 28 frames.
- Longer-history ACTION4 results falsify an earlier universal transition prediction.

## Next discriminating test
Use original native SDK resets only. Pair trials by exact pre-action 64x64 frame hash, selected-bar coordinate, stage, and SDK action age where possible. Vary earlier action order and ACTION5 count independently. Keep unmatched pairs explicitly unmatched.

Record full pre-action frame, full native animation stack, legal actions, coordinate payload, action history, stage counters, terminal state, frame count, pixel-change mask and hashes.

Compare: (1) same visible frame/different history; (2) same history age/different geometry; (3) same geometry/different action age. Report negative controls and counterexamples.

## Decision rule
A history-dependent claim requires a genuinely matched visible state and identical next action producing reproducibly different native consequences. Differences in row63, selected-bar state, action age, or animation frames must not be silently discarded. No inference of hidden-state equivalence from matched interior pixels alone.

## Boundary
This is a research plan, not a completed experiment or an ARC win. Keep existing canonical agent, source-owned evidence, and prior run records unchanged.
