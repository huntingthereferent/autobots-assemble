# Correction — ARC3 Action Semantics

Earlier forward-match work treated ACTION1–ACTION4 identifiers as if they supplied no cross-game semantic information.

That was too strict.

ARC Prize's official documentation states:

```text
ACTION1 → semantically mapped to up
ACTION2 → semantically mapped to down
ACTION3 → semantically mapped to left
ACTION4 → semantically mapped to right
```

while noting that their concrete game effect varies by game.

Therefore the admissible cross-game prior is:

```text
ACTION3 has leftward directional semantics
```

but not:

```text
ACTION3 moves the same object
ACTION3 moves the same distance
ACTION3 has the same collision consequences
ACTION3 participates in the same goal relation
```

Likewise ACTION5 remains game-specific, ACTION6 is coordinate click, and ACTION7 is undo.

## Effect on FM-002

FM-002's wall should be narrowed.

The earlier rejection:

```text
same ACTION3/ACTION4 ids
→ no semantic correspondence at all
```

was incorrect.

Official docs supply a directional semantic correspondence for ACTION1–4.

The remaining wall is the **effect correspondence**:

```text
same directional semantic
!=
same affected object / magnitude / context consequence
```

So cross-environment direction priors are admissible and useful for first-contact solving, while full transition transfer still requires game-local evidence.

Official source:
https://docs.arcprize.org/actions
