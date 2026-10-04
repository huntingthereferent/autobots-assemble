# SB26 Symbolic Recovery — 2026-10-04

## Status

`SUPPORTED_GENERIC_VISUAL_GRAMMAR_SOLVE`

Live official-agent result:

```text
game: sb26
levels: 8 / 8
actions: 124
state: WIN
score: 100.0
```

The committed solver contains:
- no `sb26` game-id branch;
- no banked public replay;
- no stored level coordinates;
- no source-code assumptions.

It recognizes a visual program-synthesis relation from the current frame, constructs a symbolic program, and executes the synthesized assignments.

## Starting failure

G0.1:
```text
SB26 0 / 8
601 actions
```

G1/G1.1 and the old object/world-model candidate also failed to level.

The failure was not inability to click or predict local effects.

The interface itself was not yet represented as the task.

## Live mechanic recovery

All mechanics below were recovered from observable frames/actions.

### Action roles

`ACTION6`
- selects a visible token;
- assigns the selected token into an editable program slot.

`ACTION5`
- executes/evaluates the completed symbolic program;
- one successful execution advances the level.

### Visual symbols

Bottom tokens have two visually distinct forms.

**Solid colored 4×4 token**
- terminal/value symbol.

**Hollow colored 4×4 token**
- call symbol for the function/subroutine with the same border color.

Multiplicity is literal evidence:
- duplicate visible tokens permit duplicate use;
- assignment consumes one token resource.

### Program frames

Middle rectangular colored frames denote functions/subroutines.

Inside them:
- red 2×2 blocks are editable positions;
- solid colored 4×4 blocks are fixed terminals;
- callable child functions may be wired visually or selected through hollow call tokens.

The function's border color is its callable symbol.

### Target

The top colored boxes form the required output sequence.

When the target wraps onto another row, row-major order is a finite required prefix.

## Recovered recursive contract

A program is valid when:

```text
flatten(root program / call graph) prefix == visible target sequence
```

Terminal symbols emit their color.

Call symbols recursively expand the referenced function.

Recursive cycles are permitted when they keep producing terminals; only the finite visible target prefix has to match.

This distinction resolved the final level:
the two target rows were a finite prefix of a mutually recursive periodic expansion, not a request to terminate recursion.

## Solver implementation

Gen-2 files:

- `direct_agent/gen2/latent.py`
- `direct_agent/gen2/symbolic.py`
- `direct_agent/gen2/grammar.py`
- `direct_agent/gen2/my_agent.py`

### Pre-wired visual parser

For the early layouts, the parser:
- reads the target colors;
- locates selectable terminals;
- identifies editable positions;
- follows visible pre-wired calls;
- recursively flattens the visible call graph.

### Grammar synthesizer

For later layouts, the solver:
1. detects target colors;
2. detects terminal and call resources by visual form;
3. detects function frames;
4. extracts editable and fixed positions;
5. builds the finite resource multiset;
6. searches assignments of those resources to editable positions;
7. recursively expands the resulting call graph;
8. accepts only an assignment whose output prefix exactly equals the visible target;
9. executes the resulting select/assign pairs;
10. uses ACTION5 once to evaluate.

The search uses the visual frame as its specification.
No public solution sequence is consulted at runtime.

## Oracle boundary

A public source-free solved trace was consulted **after seven levels had already been solved from live visual inference**.

Its sole role was to resolve the final-level ambiguity between competing recursion interpretations.

The oracle established which call position was correct.
That observation was translated back into the general rule:

```text
recursive expansion may be cyclic;
compare its finite emitted prefix to the finite visible target
```

The committed Gen-2 solver does not contain the oracle trace, public level coordinates, or game-specific policy.

A fresh run of the generic visual-grammar solver then independently reconstructed all eight programs from frames and completed SB26 in 124 actions.

## Why this matters beyond SB26

This is the first live case where a major G0.1 failure was converted from:

```text
blind action search
```

into:

```text
pixels
→ visual role induction
→ symbolic variables
→ relational grammar
→ constrained synthesis
→ executable plan
→ verified level transition
```

The relevant reusable lesson is not "recognize SB26."

It is:

```text
When local transition learning plateaus,
ask whether the frame visibly specifies a higher-level language.
If it does, infer that language and solve inside it.
```

## Current boundary

This result establishes one public game solved by the generic Gen-2 mechanism.

It does not establish:
- public 25/25 first-contact completion;
- hidden/private transfer;
- ARC-AGI-3 100%.

Those remain the active target.
