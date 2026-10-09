# Marked A/B arrows — explicit root transport

## Current referent

The [48-world construction](WINDOW_COMBINED.md) has 14 full-state A/B classes but 16 classes when the origin is preserved. The difference consists of 36 ordered maps that intertwine both A and B but move the zero origin.

## Mathematical movement

[Implementation](window_marked_arrows.py) and [14 regression tests](../../network/tests/test_arc_like_window_marked_arrows.py) introduce three distinct objects:

- `PointedWorld(W, m)`: a world and a coherent finite-support mark; its first three coordinates are explicit and its higher coordinates are zero.
- `StateArrow`: an invertible map intertwining labeled A/B actions, plus its complete ordered list of original state-map witnesses. It may move marks.
- `MarkedArrow`: a state arrow satisfying the separate equation `F(source.mark)=target.mark`. Construction rejects any mismatched mark.

For a pulse-only to combined world at support 0 or 3, the existing non-diagonal full-state map is `F = H_d R H_-c`, where `H_c` is the coordinate shear. In the forward direction:

```text
source original mark: (0,0,0)
target original mark: (0,0,0)
F(source mark):       (0,2,d)
```

This map is **not** a marked arrow between the original pointed objects. An explicit `transport_target_mark` creates a *different* pointed target with mark `(0,2,d)`. It preserves the original target mark and two positive A/B words witnessing why the two canonical origins cannot be identified. The reversed transformation similarly moves the mark to `(0,1,1+d mod 3)`.

Composition requires identical **pointed** middle objects, not just equivalent underlying worlds. Inversion reverses the actual witness factors. Composed factors are retained even when two origin moves happen to cancel. The same full-state map cannot silently be promoted to an origin-preserving equivalence.

## Witness result and verification boundary

| Ordered world-pair status | Count |
|---|---:|
| Invariant-obstructed state maps | 2,124 |
| Direct origin-preserving maps | 144 |
| Full-state but origin-moving maps | 36 |
| Explicit target re-markings | 36 |

The 14 new Python regression tests passed locally against a reproduction of the existing 48-world transition/classifier formulas; the exact new source and test file bytes matched their committed Git blob hashes. **This is not confirmation of a run against the complete GitHub repository or CI.** The local tests include explicit target-image checks, both inverse directions, full-state A/B squares through dimension six, composition, mark mismatch rejection, and original rooted word-collision preservation.

**Closed:** the pointed-arrow contract for the 48-world family and its existing H/R witnesses.

**Unknown:** arbitrary marks with nonzero higher coordinates, arbitrary window processes and state maps beyond H/R, universal A/B stopping, and native ARC execution.

**Next:** admit another independently justified root-changing operation through this witnessed pointed-arrow contract, preserving the mark and the actual alignment through composition.
