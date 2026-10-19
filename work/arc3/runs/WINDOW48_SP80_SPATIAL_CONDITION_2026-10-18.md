# SP80 — spatial condition improves pixel precision but remains incomplete

October 18, 2026. Original 48 laws and canonical agent unchanged.

## Source observation and predeclaration

Inspection of retained run 39177027549 found actual 9-to-12 blocks at x=28..35 at context steps seven/eight, whereas the earlier long-history absent block was at x=44..47. The earlier position-only suppression was therefore rejected. A new exploratory condition was fixed before this run: suppress predicted 9-to-12 changes only where target x>=44, independent of word position. Geometry, pre-color occupancy and bottom-row completion remained frozen. Four NEW words were fixed: 444445444, 445444444, 554444444, 444554444; two fresh level pairs each.

## Actual native execution

[Native run 39183806654](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39183806654), source 0dafb5caaaf5f7079f893671b43ebebdeb776be0, executed 182 actual native actions across 16 resets. There were 52 admitted matched ACTION4 comparisons per model; unmatched or interrupted steps remain UNKNOWN.

Artifact: 12156877914. ZIP digest: sha256:f8c83f6e6ba6c5b5043aa9ee19685566599126d38b687fdb0503c3e273280d3b. Raw frames and complete native comparison records are retained for 14 days.

| Model | Exact effects | Extras | Misses | Wrong colors |
| --- | ---: | ---: | ---: | ---: |
| Frozen translation baseline | 40/52 | 166 | 6 | 0 |
| Translation with spatial condition | 40/52 | 6 | 6 | 0 |
| Frozen reflection baseline | 40/52 | 166 | 6 | 0 |
| Reflection with spatial condition | 40/52 | 6 | 6 | 0 |
| Identity control (either condition) | 0/52 | 838 | 1350 | 0 |

## Decision / resume here

The candidate removed 160 extra predictions without adding misses on this new sample, but did not increase the count of completely exact effects. It is a partial empirical improvement, not an exact native transformation. Crucially the baseline now misses six actual transitions: previous all-observed-change coverage does not extend to these new histories. Both geometry hypotheses remain tied in aggregate results.

Next inspect the exact locations, color pairs, pre-action frames and histories of the SIX remaining extras and SIX misses. Keep those residuals distinct from the 160 corrected predictions. Predeclare any further condition on new native histories before testing; do not silently adjust the spatial threshold. No causal mechanism, native F3 correspondence, autonomous solver or full-game win is established.
