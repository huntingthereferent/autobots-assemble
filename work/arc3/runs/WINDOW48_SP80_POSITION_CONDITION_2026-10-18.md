# SP80 — position-only repair fails on new native histories

October 18, 2026. The original 48-law F3 mathematics and canonical agent are unchanged.

## Predeclared question

Does suppressing predicted native 9-to-12 changes at context step seven and later repair the frozen stage-transfer relation? The condition was fixed before this native run. Four new words were fixed: 55555544, 55555444, 44555544, 55445544, each with two independent level pairs. Native level changes interrupt comparisons and remain UNKNOWN.

## Observed execution

[Native PR run 39177027549](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39177027549) completed successfully at source commit f827413e51b853a4f43bca1adb614363aeb3c8b9. It executed 160 native actions across 16 native resets and admitted 16 paired ACTION4 comparisons per model. These comparisons are a subset of the attempted words; interrupted steps are not counted as failures or successes.

[Raw native frame stacks and complete comparison records](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39177027549/artifacts/12154484002) are retained for 14 days. ZIP SHA-256: bfd93203c46f9f46e7aeb4481186d028e8e7579d150a5fcad08f125bcd860648.

| Model | Exact complete effects | Extra changes | Missed changes | Wrong colors |
| --- | ---: | ---: | ---: | ---: |
| Frozen translation baseline | 12/16 | 4 | 0 | 0 |
| Translation plus position condition | 8/16 | 4 | 128 | 0 |
| Frozen reflection baseline | 12/16 | 4 | 0 | 0 |
| Reflection plus position condition | 8/16 | 4 | 128 | 0 |
| Identity control, with or without condition | 0/16 | 260 | 512 | 0 |

## Decision and next handoff

Reject this position-only repair: it deletes native changes that actually occur and does not eliminate the four baseline extras. The original frozen baseline remains explicitly partial. Do not add this failed condition to the canonical agent or claim an exact history model.

Next inspect retained pre-action frames for the 128 wrongly removed changes and compare them with the earlier absent 9-to-12 block. Derive any proposed discriminating observable from those records, predeclare a new held-out test before collecting observations, and preserve counterexamples. Do not silently tune the step threshold or reuse these outcomes as held-out validation.

The workflow succeeded as an experiment. The proposed condition failed. No native F3 action mapping, autonomous solving policy, or full-game win was established.
