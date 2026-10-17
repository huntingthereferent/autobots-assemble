# WORLD W13 — Movement 1: an explicit two-world continuation

**Authority:** WORLD's next bounded game-rule declaration, routed by COORDINATOR after the independent W12 local-candidate witness.  
**Status:** WORLD RULE DECLARED / BUILD NOT YET VERIFIED / WITNESS NOT YET RUN.  
**Contract version:** `game-w13-multiworld-v1`.  
**No existing W12 source, native verifier, browser receipts, or W1–W12 witnesses are replaced.**

## CURRENT REFERENT

Continue the **actual playable game** from W12 into a second, separately
declared world while preserving the already-observed first world. The
`advance` action crosses one explicit boundary between completed worlds;
it does not reclassify a game, the language referent, or an NIH checkpoint
as the same system.

This movement reuses the **already existing** unadmitted
`WORLD_W13_PROPOSAL.md` from the recovered
`game_nih_complete_stack_bridge_v1.zip` and the October 15
`_game_w13_publish_20261015` BUILD/worker candidate. It is not a
second W13 design. In particular, the candidate's
`game-w13-multiworld-v1` and `advance` vocabulary are preserved.

## PRESERVE — W12 LOCAL SEMANTICS

Every world runs the unchanged W12 `GameSpec` and `transition`:

- Cardinal `up/down/left/right` movement is bounded by the local grid.
- A blocked move consumes **one local turn**, leaves position unchanged,
  and records `blocked-by-boundary`.
- `interact` consumes **one local turn** and first collects the target
  only when the actor is **cardinally adjacent**, not diagonal.
- Each world owns an independent local player state:
  `x`, `y`, `collected`, `turns`; its own exact `spec`, action
  sequence and native trace.
- Once the target is collected, the local state is retained for evidence.
  Changing world must never rewrite previous actions, before/after states,
  receipts, head hashes, or the W12 strict verifier.

The original 4×3 W12 trace `right → interact` and C1
`left → right → interact` remain separate preserved witnesses.

## WORLD RULE — one explicit cross-world action

The initial W13 WORLD scope is **exactly two specified worlds in order**,
not yet the candidate worker's broader ability to accept two–four worlds.

| World ID | Width × height | Start | Target | Exact required successful local actions |
| --- | --- | --- | --- | --- |
| `first-room` | 4×3 | (0,1) | (2,1) | `right, interact` |
| `second-room` | 3×3 | (0,0) | (1,1) | `right, interact` |

The bounded global action path is:

```text
first-room:  right → interact [collected = true]
SESSION:     advance
second-room: right → interact [collected = true]
```

`advance` is **only** a session boundary: it is not passed to W12
`transition`, does not increment either world's local turn count,
does not mutate the saved prior world, and cannot run unless the current
world is collected and an unused next declared world exists.

On accepted `advance`, set session cursor to `second-room`,
start that world at its *declared* `(0,0)` with `collected=false`,
`turns=0`, retain the completed first world's evidence, and record
the explicit from-world/to-world relation.

W13 session `solved=true` requires all declared worlds completed;
a first-world collection or one admitted transition **alone**
cannot mark the W13 session solved.

## EXPECTED WITNESS — precise before/action/after

The original W12 native `run_actions` was evaluated on both
declared local specs. The following are **contract expectations** for
BUILD and independent WITNESS, not a claim of W13 BUILD completion.

| World | Before | Action | After | W12 verdict |
| --- | --- | --- | --- | --- |
| first | (0,1,false,0) | right | (1,1,false,1) | moved |
| first | (1,1,false,1) | interact | (1,1,true,2) | collected |
| boundary | first-room completed | advance | second-room starts (0,0,false,0), first preserved | advanced (W13 only) |
| second | (0,0,false,0) | right | (1,0,false,1) | moved |
| second | (1,0,false,1) | interact | (1,0,true,2) | collected |

Tuple convention: `(x,y,collected,turns)`.
The expected **final session** is world `second-room`,
local `(1,0,true,2)`, `worlds_completed=2`, `solved=true`,
with both world traces independently valid.

The preserved data-only request is recorded as
`network/tests/fixtures/world_w13_movement_01.json`. Its bytes
represent the **existing W13 candidate example**, not a claim that
that candidate has passed the new browser verification conditions.

## W13 BROWSER / SOURCE WITNESS REQUIREMENTS

BUILD receives this declared version and the exact two world specs.
A browser-facing W13 version must expose the actual current room, let
the person use W12 movement/interaction, and present an explicit
`advance` action only when admissible. The first room must not
automatically vanish when its target is collected. A reset must
restore both rooms, session cursor, and local turns to their declared
initial state.

For **each** world, an exported browser record must preserve the
actual `id`, W12 `version` (`game-construction-v0`), `spec`,
native local `actions`, all `observations` with exact
`before/action/after/verdict`, and `final` state. Additionally, a
versioned **W13 session receipt** must carry the ordered world IDs,
one global action sequence including each explicit `advance`, a
record of the boundary's from/to IDs and local pre/post state, and
the final session/world state. This defines required evidence fields,
not an already-executed browser exporter or a completed serialization
schema: BUILD must present the exact proposed JSON schema before
WITNESS can certify its acceptance.

WITNESS must independently reconstruct each world through the
byte-preserved **original** W12 native verifier and check the
W13 boundary and session-level ordering **in addition** to W12's
per-world trace. A source-owned W13 engine result must be compared
to this independent reconstruction, not accepted as its own proof.

The W12 `verify-browser` and `verify-browser-expanded` entry points
continue to accept **W12-only** objects. Neither may silently reinterpret
a W13 envelope or treat one world's proof as proof for another world.

## REQUIRED NEGATIVE OBSERVATIONS

1. `advance` before collection (including as the first action) must
   fail; cursor and existing W12 evidence cannot change.
2. `right, interact, advance, right` must **not** produce
   `solved=true`: the second room remains uncollected.
3. A second `advance` at the last room is rejected; there is no
   implicit third world.
4. A blocked `left` at `first-room` start leaves (0,1) unchanged
   but increments its local turns to 1; the later
   `right, interact, advance, right, interact` remains valid with
   3 first-world turns and 2 second-world turns.
5. Treat `interact` diagonally adjacent to the object (e.g.
   `second-room` at (0,0) and target (1,1)) as out-of-reach, not
   collected; it consumes a local turn.
6. Reject a duplicate world ID, duplicated local world specification,
   missing/extra fields, non-integer coordinate/dimension, unknown
   action, incompatible version, or changed W12 source fingerprint.
7. Reject a receipt with an altered pre-state, `spec`, boundary,
   final state or claimed solved-world count, **even when** its own
   claimed hash or W12-like local trace is internally self-consistent.
   No witness may be borrowed across worlds.
8. A W13 receipt submitted to the old strict W12 verifier must fail.
   A W12 local PASS is not an automatic W13 PASS.

## SUPPORT / ASSUMPTIONS

**Supported:** Independently verified **W12** local source/receipt
candidate (historical witness 32/32 native tests, 33/33 archive hashes,
23/23 negative probes, 10/10 headless Chromium scenarios), with original
source bytes now restored on GitHub `main` at
`dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1`.
The W13 BUILD source and worker example predate this WORLD handoff but
remain **candidate**, not independently W13 witnessed or endorsed.

**Declared now:** the single exact W13 two-world and `advance`
relation above. It is **WORLD scope**, not evidence of implementation,
browser integration, a native CP `PASS` or deployment.

## WALL

The W13 BUILD candidate's native two–four-world composition is **not**
a verified W13 playable browser or WITNESS PASS. No existing W12 receipt
proves browser origin. No autonomous agent, GitHub execution service,
general world generator, cross-lane merge or completed route is claimed.

## NEXT SINGLE MOVEMENT / COORDINATOR HANDOFF

**BUILD:** reuse the existing W13 candidate instead of starting over;
supply one versioned two-room **playable browser** and its exact
session-receipt schema and saved positive/negative exports, without
changing any archived W12 file. Return source fingerprint, native
trace, browser receipts and bounded test logs.

**WITNESS (independent):** only then assess the above WORLD rule,
including unchanged W12 native replay, two distinct local traces,
one exact `advance`, actual browser actions, invalid receipts,
and candidate-versus-independent reconstruction.

**COORDINATOR:** do not promote `GAME-W13-WORLDS` to `PASS`
until that native/source-scoped WITNESS returns verified evidence.
