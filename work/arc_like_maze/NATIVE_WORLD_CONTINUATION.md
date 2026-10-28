# Native A/B mathematical world continuation — first measured feed

This experiment **continues the existing** `window_combined.CombinedWorld` laws. It does not introduce a replacement A/B mathematics or claim that the language referent is a generator.

## Actual operation

Select two or more original law IDs, choose an exact A/B action word, and repeat that word under an explicit step budget. Each move calls the **original source's** `CombinedWorld.step` for every world. The receipt records exact before/after states, first coordinate divergence, first visits, and distinct labeled edges. A separate replay checks the complete event record against the unchanged native source.

```bash
python -m work.arc_like_maze.native_world_continuation --laws 0 1 --word ABBA --repeat 10000 --out /tmp/ab-feed.json
python -m work.arc_like_maze.native_world_continuation --verify /tmp/ab-feed.json
python -m unittest -v network.tests.test_arc_like_native_world_continuation
```

## What is and is not open

The **observation sequence** can continue with larger explicit budgets, and the source has 48 distinct existing laws to compare. The law grammar, depth-three state domain, and input alphabet remain **fixed**. Repeated inputs do not invent or admit new relationships. Novelty means a state or labeled edge not previously visited in that run; it does **not** establish new mathematics. Fast feeding cannot enlarge the 27-state space per law.

## Next actual boundary

To meet James's proposed *open world with new relationships*, first identify an admitted native mathematical construction rule that can extend the existing law/relationship grammar, specify its exact source, domain, transition and independent witness, then compare preservation and breakage against earlier worlds. **Do not silently use random graph edges or relabel a fixed-law replay as an open world.** This instrument is a baseline for testing that future extension.

Evidence levels: implementation committed; execution and CI results must be checked separately. The SHA-256 receipt checksum is an integrity aid, not third-party attestation.
