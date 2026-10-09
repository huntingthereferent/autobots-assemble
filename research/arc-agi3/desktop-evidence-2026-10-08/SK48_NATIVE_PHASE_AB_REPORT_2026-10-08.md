# ARC / SK48 — observed directional phase A/B, 2026-10-08

## Status and correction

- **Independent native Level 1**: solved from one live SDK game instance through public frame/action observations, 14 directional actions, without a saved solution or cloned engine.
- **Independent native Level 2**: still open. The earlier full-frame BFS reached a fully tested depth-11 frontier (875 public-frame keys, 1,776 branches), but was too expensive to continue blindly.
- **Existing 8/8 SK48**: still a separate saved-route replay witness (280 actions), not an independently planned all-level solver.
- **No GitHub or official ARC submission** in this continuation.

### Why the naïve frame quotient fails

A public frame can be identical while its following native action transition differs.

At the exact same Level 2 public frame:

- Fresh action 4 produced SHA256 prefix `59a8a28d1abf572a`.
- Action histories `1,7,2,7,3,7,4` produced `582802a68ff65ca0`, where action 7 is native undo.
- The three rollback cycles individually returned to the identical public frame.
- Exhaustive ordered subsets of the three prior cycles showed the counterexample only after all three cycles under the originally tested sequence.
- Fourteen alternative three-cycle histories (permutations, repetitions, different direction actions) all produced the **same altered native response vector** for next actions 1–4.
- Twenty isolated one-step undo-followed-by-action controls had passed. The failure appeared only on a longer horizon. Thus a locally correct one-step undo shortcut was not compositionally safe.

Evidence: `sk48_l2_chained_undo_counterexample.json`, `sk48_l2_chained_undo_minimal_ab.json`, `sk48_l2_undo_history_higher_order_ab.json`.

### Directional action, not undo, is the relevant source

Native controls distinguished the available causes:

- 0, 1, 2, 3 repeated ACTION2 movements returned the same public frame at the Level 2 entry state, but the fourth test action (ACTION4) changed its result once 3 ACTION2 actions had occurred.
- After 4 ACTION2 actions, the current public frame itself changed.
- Repeated ACTION7 without directional action did not change the public frame or subsequent ACTION4 result in 0–7 repetitions.
- Eight held-out Level 2 parent paths showed the changed result after **3 additional rollback cycles from a zero-move parent, 2 cycles from a one-move parent, and 1 cycle from a two-move parent**.

The conservative promoted hypothesis is a **witnessed directional-action history/phase** in the native environment. It is **not** proven that a single universal counter describes every SK48 state, nor that all actions advance a phase.

Evidence: `sk48_l2_native_noop_action_count_ab.json`, `sk48_l2_rollback_phase_heldout_parent_ab.json`.

## A/B over the evidence families

All testing below uses actual native SDK steps and public frames. No private engine members, copied game object, or saved Level 2 solution is required. Positive native RESET acknowledgment to Level 0 was required before every fresh Level 1 replay.

Four evidence classes have the **same initial Level 2 public frame** but different witnessed directional phase counts 0, 1, 2, 3. For each phase count, three different history sources were tested:

- visually unchanged ACTION2 repeated 0–3 times;
- paired ACTION1/ACTION7 intervention histories;
- paired ACTION4/ACTION7 intervention histories;
- for phase zero, repeated ACTION7 alone was included as a negative control.

The native experiment executed **64 three-action suffixes × 4 phase counts × 3 history-source variants = 768 continuations**, comparing the **entire returned trace** of three native frames. There were **zero within-phase counterexamples**.

The recursively refined continuation quotient:

| Prediction horizon | Minimal witnessed classes |
|---|---|
| One native future action | {0,1,2} / {3} |
| Two native future actions | {0,1} / {2} / {3} |
| Three native future actions | {0} / {1} / {2} / {3} |

First separating future action for all 64 suffixes: 0 vs 1 splits at step 3, 0 vs 2 at step 2, 0 vs 3 at step 1, 1 vs 2 at step 2, 1 vs 3 at step 1, 2 vs 3 at step 1.

Important: comparing **only the final frame after three steps** incorrectly merges the 1/2/3 phase classes even though their earlier native continuations differed. Full trajectory preservation is required; later convergence does not erase observed differences.

Evidence:
- `sk48_l2_native_trajectory_horizon3_ab.json` — two representative histories per class and all 64 three-step suffixes.
- `sk48_l2_directional_phase_cross_source_ab.json` — three different source histories per class, 768 witnessed continuations.
- `sk48_l2_ab_recursive_phase_quotient.json` — automatically reconstructed partition and minimal separation depth, assertions passed.
- `_tmp_sk48_l2_ab_recursive_phase_quotient.py` — pure evidence-only quotient checker.

## Relation to the one-agent Continuity runtime

This is **an A/B state correction, not a second agent architecture**.

A native continuation key `(public_frame_hash)` is insufficient wherever the same frame has incompatible future outcomes.

For the tested referent family, A/B retains `(public_frame_hash, native-witnessed directional phase relation)`. A phase must be grounded in admitted native action and return witnesses; when the relevant phase is not grounded, the correct evaluator result is `UNKNOWN`, not an invented frame equivalence.

Unnecessary action identity and order are discarded when all three source families prove identical future continuation. Later counterexamples can always split the quotient again. Existing `AgentMove`, `AgentLineage`, and observation provenance remain the integration boundaries.

**Do not resume the previous undo-optimized BFS checkpoint.** It admitted a false child state after chained rollbacks, before this counterexample was understood. Full native reset/replay remains valid when acknowledgment and parent frame are checked; the prior undo shortcut is only a bounded experimental witness.

## Next native continuation

Before trying a costly all-direction Level 2 search again:

1. Test the new phase-aware state relation on **held-out Level 2 parent states with full three-step continuation**, not only the shared initial frame.
2. Introduce the smallest frame-plus-witnessed-phase key inside the existing A/B search, rejecting ungrounded aliases instead of silently merging them.
3. Use witnessed visual reference/goal relations and action equivalences to reduce search branching before re-running the full level; keep the native action budget explicit.
4. Replay any newly discovered Level 2 solve from a fresh game and require the actual `levels_completed >= 2` signal.

The current **independent Level 2 solve status remains UNKNOWN**. This report establishes the predictive-state boundary and a tested family-local A/B correction, not a competition win.

All files are local in `C:\Users\teepa\arc3\AB_ARC_EVIDENCE`. Nothing here changed GitHub `main` or the competition agent.
