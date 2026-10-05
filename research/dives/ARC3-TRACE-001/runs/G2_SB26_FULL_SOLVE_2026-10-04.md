# G2 Relational Construction — SB26 Full Solve — 2026-10-04

## Result

A generic visual/latent-state mechanism completed the public SB26 game:

```text
state: GameState.WIN
levels completed: 8 / 8
environment actions: 530
aggregate local score: 20.800753929040518
agent SHA-256: c915f36adb1e81c78defc45288f6b2d2dd0c88c9cfa9ee94f00254b665ce0f8b
```

The agent contains:
- no game ID branch;
- no fixed SB26 coordinates;
- no fixed SB26 colors;
- no banked public action path.

This is **not** a clean first-contact benchmark witness. Public game source was consulted during iterative diagnosis after source-free hypotheses failed. Treat the source as oracle evidence that identified missing relation classes. The resulting mechanism must be tested for transfer and must not be represented as an untouched competition result.

## Movement from G0.1

G0.1 spent 601 actions on SB26 and completed 0/8 levels.

Action-score balancing, exact-state DFS, undo/backtracking, directional momentum, edit→commit, and the prior Gen-1 object transition model all failed to level.

The successful movement was one layer up:

```text
pixels
→ selectable/movable object relation
→ destination-slot relation
→ framed ordered containers
→ colored frame links
→ recursive graph execution
→ finite visible reference as stopping witness
```

## Relations recovered from observation

### Second-order interaction

ACTION6 could not be modeled as a unary click effect.

Observed protocol:
1. first click establishes a selected object;
2. second click establishes a target;
3. selected-object + target relation determines whether a structural move occurs.

Bottom colored tokens moved into central empty slots only under the two-click relation.

### Reference / construction / palette separation

The visible board supplied three roles:
- top: reference sequence;
- middle: construction graph;
- bottom: movable token vocabulary.

The roles were inferred from repeated visual geometry and interaction effects rather than game ID.

### Recursive framed traversal

Middle frames encode ordered containers.
- entries are traversed left-to-right;
- solid data entries emit a color;
- link entries invoke another frame and then return;
- sibling frames may occur at the same depth;
- a child frame may be invoked more than once;
- final level requires bounded recursion/cyclic graph calls.

### Shared subroutine

A later level had:
- 9 target outputs;
- 8 physical tokens;
- two hollow links to the same child frame.

The only consistent latent model was construction-once / invoke-many: physical state is assigned once, traversal may reuse a child frame multiple times.

### Bounded recursion

Final level exposed a wrapped 12-token reference and hollow link tokens for both frame colors.

The latent program can recurse. The finite visible reference provides the stopping witness: execution is accepted when the emitted sequence reaches the complete target, rather than requiring the graph itself to be acyclic.

## Generic G2 detector

The frozen implementation:
`research/dives/ARC3-TRACE-001/direct_agent/gen2/my_agent.py`

It detects:
- wrapped reference tokens in row-major visual order;
- movable solid and hollow palette tokens;
- repeated empty slot lattices;
- individual framed containers from their border runs;
- fixed data;
- fixed links;
- movable links;
- sibling frames;
- shared child frames;
- bounded recursive calls.

It synthesizes an assignment over the compact latent graph, then executes the inferred physical moves.

## Important boundary

This is one solved public game and one reusable mechanism, not ARC3 100%.

The mechanism is strongly supported for the relation class:

```text
visual reference
+ physical token vocabulary
+ framed construction graph
+ data/link semantics
→ synthesize graph program matching reference
```

It has not yet been shown to transfer to unrelated control, navigation, temporal-history, autonomous-world, or other ARC3 game classes.

## Next movement

Freeze G2 as a solved-mechanism module.

Return to the full public failure set and choose the next unresolved relation class from live evidence. Integrate mechanisms by witness detection rather than by game ID.
