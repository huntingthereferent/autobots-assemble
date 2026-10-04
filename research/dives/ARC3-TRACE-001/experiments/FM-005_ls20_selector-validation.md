# FM-005 — LS20 Retrospective Selector Validation

**Type:** held-out action-ranking replay test  
**Status:** supported selector validation  
**Purpose:** verify that the generic witness-compression selector ranks the replay's discriminating action highest using only pre-action candidate predictions.

## Source

Official ARC Prize LS20 replay:

https://arcprize.org/replay/8314341d-c2e5-4b75-af8a-a085eddd8165

Decision boundary:

- pre-action state: frame 18
- held-out witness: frame 19

## Live candidates before action

Current glyph:

```text
X.X
..X
XXX
```

Two live candidate models:

### H_flip

```text
ACTION2 + marker landing
→ vertical flip
```

### H_rotate

```text
valid marker landing
→ 90° clockwise rotation
```

The block is immediately above the marker. So ACTION2 is the only available move in this local state whose marker interaction gives the two models different exact glyph predictions.

## Prediction matrix

Discriminating observable: **bottom-left glyph**.

| Action | H_flip | H_rotate | Separated? |
|---|---|---|---|
| ACTION1 | unchanged | unchanged | no |
| ACTION2 | `XXX / ..X / X.X` | `X.X / X.. / XXX` | **yes** |
| ACTION3 | unchanged | unchanged | no |
| ACTION4 | unchanged | unchanged | no |

The non-ACTION2 moves do not land on the marker in this state, so both live transformation models predict no glyph change.

## Selector score

With two live candidates there is exactly one candidate pair.

```text
ACTION1: separated_pairs = 0 / 1
ACTION2: separated_pairs = 1 / 1
ACTION3: separated_pairs = 0 / 1
ACTION4: separated_pairs = 0 / 1
```

Therefore the generic selector ranks:

```text
ACTION2 > ACTION1 = ACTION3 = ACTION4
```

before the held-out frame is inspected.

## Held-out witness

Frame 19 shows the glyph as:

```text
X.X
X..
XXX
```

which matches H_rotate and falsifies H_flip.

The replay agent also selected ACTION2 at this point, so the selector's top-ranked action agrees with the actual useful action without using frame 19 as input.

## Result

`SUPPORTED_SELECTOR_RETROSPECTIVE_VALIDATION`

The generic partition selector successfully identifies the one action that resolves the active model ambiguity.

## What this establishes

Supported:

- candidate predictions can be converted into an action-ranking matrix;
- pair separation is sufficient to recover the discriminating LS20 action;
- unsupported/missing predictions need not be treated as evidence;
- the selector can remain separate from game semantics and from A/B itself.

Not established:

- benchmark-wide action savings;
- superiority to the replay agent on this event;
- live unseen-game performance;
- cross-environment action-semantic transfer.

## Next test

Find a held-out decision where the recorded agent chose a low-information exploratory action while another admissible action would have separated more live candidates.

That is the first retrospective test capable of demonstrating **counterfactual action savings**, rather than merely reproducing a good choice.
