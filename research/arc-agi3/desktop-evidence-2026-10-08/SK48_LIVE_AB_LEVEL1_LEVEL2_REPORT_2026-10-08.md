# SK48 A/B — single-stream native continuation, October 8, 2026

## Verified movement: independently generated Level 1

The search in `_tmp_sk48_single_stream_live_bfs.py` uses exactly **one** native `Arcade.make("sk48")` game instance, native `RESET` and actions 1–4, public SDK frames, and public `levels_completed`.

It does **not** use `copy.deepcopy`, private `_game` access, or a saved route. A/B collapses replay histories to the same observed complete public frame before expanding the next native actions.

A successful Level 1 route was independently discovered:

`1,1,1,4,4,4,4,3,2,2,4,3,1,4`

- Native Level 1 completion at action 14.
- 1,031 distinct public-frame states.
- 2,488 expanded native successor branches.
- 30,540 total native actions including resets and path replays.
- 0 replay mismatches.
- Freshly generated path happens to agree with the earlier local cloned-game BFS result, which was **not loaded**.

The 30,540-action research score is not a competition-quality result.

Raw evidence: `sk48_live_single_stream_bfs.json`.

## Corrected Level 2 RESET boundary

The first Level 2 search was stopped on a mismatch: after issuing an action on Level 2, one `RESET` did not necessarily return to Level 0.

Controlled experiment:

- L1 14-action completion -> new L2 entry public frame SHA256 `9a357142...`.
- Without an intervening L2 action, `RESET` was acknowledged and replayed L1 produced the same L2 frame.
- With an intervening L2 action (1, 2, 3, 4, or 7), the first `RESET` returned `levels_completed=1` and did **not** establish reset completion. Treating the subsequent actions as a fresh L1 replay created an erroneous 196-pixel difference.
- Requiring native acknowledgement (`levels_completed=0`) before replay, and retrying up to a bounded limit, restored the original L2 entry frame **exactly in all five controls**. Two RESET attempts were required for each of the five tested actions.

This evidence corrects the provisional interpretation of hidden state persistence. The observed difference was caused by **unacknowledged reset**, not proof of a hidden state that survives a properly acknowledged reset.

Raw tests:
- `_tmp_sk48_l2_reset_history_ab.py`, `sk48_l2_reset_history_ab.json`
- `_tmp_sk48_reset_ack_handshake.py`
- `_tmp_sk48_l2_reset_ack_verify.py`, `sk48_level2_reset_ack_verified.json`

## Level 2 independent search frontier

The corrected single-game native BFS uses the previously independently found Level 1 path to reenter Level 2. It still uses no saved Level 2 moves, no clone, and no private game state. It checks native RESET acknowledgement first, then requires the full replayed parent public frame to match before each branch.

Verified fully finished frontiers:

| Level 2 search depth | Total distinct public states | Expanded edges | Native actions including resets | Extra RESET attempts |
|---:|---:|---:|---:|---:|
| 1 | 4 | 4 | 82 | 3 |
| 7 | 77 | 192 | 4,074 | 191 |
| 8 | 127 | 308 | 6,858 | 307 |
| 9 | 212 | 508 | 11,858 | 507 |
| 10 | 444 | 848 | 20,698 | 847 |
| 11 | 875 | 1,776 | 45,754 | 1,775 |

- Level 2 not yet completed by this independent search.
- 0 replay mismatches in the fully finished depths.
- The active process passed its operational run budget while expanding depth 12; it was stopped. No claim of exhaustive depth 12 or later.
- The killed script did not emit its end-of-run JSON, so the depth 11 table is preserved from its actual captured stdout and should not be mistaken for a complete persisted search frontier.
- Native Level 2 operator probes separately showed action-dependent public-frame changes for actions 1–4.
- The older saved 8/8, 280-action SK48 replay remains available **as regression evidence only**, not as independent Level 2 discovery.

Evidence:
- `_tmp_sk48_single_stream_level2_bfs.py` — bounded search with verified native reset handshake.
- `_tmp_sk48_l2_public_operator_probe.py` — native Level 2 response.
- This report — explicit depth 11 stdout checkpoint; do not claim JSON result exists from interrupted run.

## Current operation and next edge

The reusable A/B operation remains:

native current referent -> available action -> actual public continuation -> compare prediction/observation -> preserve shared relations, split counterexamples -> retain native provenance -> recursively use resulting state.

Two boundaries now matter: (1) transition actions require **positive RESET acknowledgement** and (2) naive complete-frame BFS is too expensive across Level 2. The next solver move is evidence-grounded **action/state factoring** (public control object, moving color sequence, target relation, action phase) and check its predictive closure, rather than re-run the unbounded 4-way tree.

This is not a new solver architecture: it is an A/B refinement of the existing observed-continuation state and action effects.

No GitHub repo/competition agent edit or official submission was made by this continuation.
