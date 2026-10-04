# Witness Compression Selector

The selector ranks ARC3 actions **after** the forward-match layer has produced exact, evidence-admissible predictions.

It does not infer action meaning and does not manufacture correspondence.

## Pair-separation score

For `n` live candidate models there are:

```text
n(n-1)/2
```

candidate pairs.

For a proposed action, two candidates are separated when they predict different exact observable outcomes.

```text
separation_rate =
  separated candidate pairs
  / all live candidate pairs
```

A candidate with no admissible exact prediction is represented as `None`; pairs touching it remain unresolved rather than being counted as informative.

## Ordering

Actions are ranked by:

1. separation rate;
2. number of separated candidate pairs;
3. prediction coverage;
4. supported goal-progress score only as a tie-breaker.

Goal value therefore cannot turn an unsupported action prediction into evidence.

## FM-004 fixture

FM-004's ACTION2 has two live candidates with different exact glyph predictions:

- H_flip
- H_rotate

so:

```text
1 candidate pair
1 separated pair
separation_rate = 1.0
```

That reproduces the witnessed LS20 compression event in a reusable selector shape.

## Boundary

This is an action-selection lens over already-admissible relations.

It is not A/B itself.
