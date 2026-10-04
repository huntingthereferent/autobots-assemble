# FM-004 — LS20 Witness Compression by Prediction Partition

**Type:** within-environment discriminating-action test  
**Status:** supported witness compression  
**Purpose:** test whether one environment action can resolve multiple live candidate relations because those candidates predict different observable outcomes.

## Source

Official ARC Prize LS20 replay:

https://arcprize.org/replay/8314341d-c2e5-4b75-af8a-a085eddd8165

Relevant replay states:

- frame 18: pre-discrimination model and planned ACTION2
- frame 19: post-action correction

## Ground before the discriminating action

By frame 18, the replay had already supported:

- ACTION2 moves the block downward;
- the block was positioned above the marker;
- landing/crossing the marker had previously changed the bottom-left glyph;
- an immediately preceding off-marker move did not change that glyph.

The current glyph before the next marker landing was represented as:

```text
X.X
..X
XXX
```

Two live transformation models were distinguishable.

### Candidate H_flip

Action-specific interpretation:

```text
ACTION2 + marker landing
→ vertical flip
```

Exact prediction:

```text
X.X        XXX
..X   →    ..X
XXX        X.X
```

### Candidate H_rotate

Action-independent marker interpretation:

```text
any valid marker landing
→ glyph rotates 90° clockwise
```

Exact prediction:

```text
X.X        X.X
..X   →    X..
XXX        XXX
```

The two candidates therefore partitioned the next observation cleanly.

## Discriminating action

```text
ACTION2
```

This action was useful for task progress, but it also had high information value because the live candidates predicted observably different glyph states.

## Witness

Frame 19 reports the post-action glyph as:

```text
X.X
X..
XXX
```

and corrects the mechanic to:

```text
marker landing
→ rotate glyph 90° clockwise
```

## Result

`SUPPORTED_WITNESS_COMPRESSION`

One environment action resolved at least two live model relations:

1. `H_flip` — **FALSIFIED**
2. `H_rotate` — **SUPPORTED** for the observed marker-landed transitions

It also preserved the existing marker-overlap gate rather than requiring a new trigger rule.

## Compression metric

For this bounded event:

```text
environment actions spent = 1
candidate models separated = 2
direct model-resolution ratio = 2 / 1
```

Do not interpret this as a benchmark-wide speedup yet. It is one witnessed compression event.

A stricter metric for future runs should count independent relation edges whose status changes because of the action.

## A/B-forward interpretation

The one-layer-up movement is:

```text
current witnessed graph
→ generate admissible candidate continuations
→ project exact observable consequence of each
→ partition candidates by predicted outcome
→ choose one action crossing the most partitions
→ observe once
→ update several relation states
→ recurse
```

The action is not selected merely because it “looks promising.” Its value comes from how many current relation candidates it can discriminate under explicit predictions.

## Important distinction

This is stronger than FM-003's repeated prediction reuse.

FM-003 showed:

```text
one supported relation
→ recursive predictions in corresponding contexts
```

FM-004 shows:

```text
multiple live relations
→ one selected witness
→ several relation statuses updated
```

That is the first direct evidence for **witness compression**.

## Next seam

Automate the partition calculation.

For every available action:

1. enumerate current admissible candidate models;
2. predict the observable delta under each;
3. partition models by predicted delta;
4. score how many unresolved distinctions the action can resolve;
5. discount actions whose prediction depends on unsupported correspondences;
6. prefer high-discrimination actions that also preserve supported task progress.

The next test should compare this selector against a simpler exploratory policy on held-out replay segments or live public play.
