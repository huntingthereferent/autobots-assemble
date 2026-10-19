# WORLD48: Cross-depth source observation

This is **not a completion certificate**. It is a portable, independently
replayable observation of two bounded A/B paths in the original mathematical
WORLD48 family.

## From the live game

Open `/game/`, select a challenge, build and lock both paths, and inspect the
**Cross-depth source comparison**. Select one actually recorded prefix depth per
path; click **Export research observation JSON**. The export works for
nonwinning path pairs too. Unlike **Export verified certificate**, it never
awards a challenge or claims an external result.

## Independent replay

From a checkout of the corresponding original-source repository:

```bash
python -m work.arc3.window48_cross_depth --verify world48_cross_depth_observation_03.json
```

The verifier recalculates original `work/arc_like_maze/window_combined.py`
transitions from root `(0,0,0)`, for every recorded prefix in both paths. It
verifies that the challenge ID and exact law pair are source-owned, selected
steps are within the actual word lengths, selected states are exact, total
prefix-pair count and qualifying candidate count match, and the recorded first
candidate is the deterministic minimum of `(depth_1 + depth_2, depth_1)`.

**Candidate condition:** two distinct recorded action prefixes end in the same
left-world state and different right-world states. Prefix depths may differ.
There is no padding or synthesized pause step. The selected candidate and
total candidate count are observations; neither is a win, an inferred causal
explanation, a native ARC game result or a claim of real-world physics.

The JSON is **not signed**. Source replay verifies its claims against the
original mathematical definitions, not who generated the file, when it was
recorded, or ownership of a browser session. Old
`original-window48-rooted-collision-certificate/v1` win receipts are a
different schema, with their own independent verifier
`work.arc3.window48_challenges.verify_certificate`. Their schema and
persistent browser records remain unchanged.

## CI evidence

The `WORLD48 original finite-world source and Chromium` job executes Python
adversarial tests in `network/tests/test_arc3_window48_cross_depth.py` and real
Chromium exports/replays in `network/browser_window48_challenge_check.py`.
