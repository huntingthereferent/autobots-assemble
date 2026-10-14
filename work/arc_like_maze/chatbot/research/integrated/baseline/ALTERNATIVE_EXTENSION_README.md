# Finite A/B chatbot — alternative edge-extension experiment

**Current referent:** Compare several admissible continuations from one pinned, witnessed union under changing finite A/B-labeled transformation rules. These generators are local mathematical models, not definitions of the language-level A/B referent.

## New local integration

- `UnionEdgeExtender(..., action_order='AB'|'BA')` retains the earlier `AB` default and its evidence/verifier semantics.
- `AlternativeExtensionChooser` independently advances both priorities against the same pinned local source snapshots; it preserves separate state pairings, admitted edges, rejected collision witnesses, rooted goal routes, alternative goal images, and source/wall status.
- No goal choice is finalized until both candidates finish and pass replay checks. A changed source version, corrupted edge, missing source authority, or observation budget wall prevents promoting an incomplete result.
- The candidate set is only two action priorities. It is not an exhaustive search for maximal correspondences, arbitrary semantics, or physical A/B motion.

## Concrete result

For original phi `(0,0,1)`, changed phi `(1,0,1)` and old-goal `(0,0,2)`:

| Priority | Paired states | Admitted edges | Goal |
|---|---:|---:|---|
| `AB` | 20 | 28 | Not reached in this restricted extension |
| `BA` | 25 | 37 | Reached as `(0,0,1)` via `BBBBBB` |

The chooser selected `BA` for the declared goal. The alternatives use shared observed finite laws but independent partial pairings.

## Execution and verification (local, 2026-10-12)

```sh
python run_alternative_extension_demo.py
python -m unittest -q test_ab_chatbot_alternative_extension.py
python -m unittest -q test_ab_chatbot_path_union.py test_ab_chatbot_union_extension.py
python -m unittest -q test_ab_chatbot_branch_discovery.py test_ab_chatbot_goal_selected_restrictions.py
```

Completed runs: new tests 9/9; related legacy tests 30/30 and 28/28 (67/67 total in these runs). Earlier version reported 312/312 in a prior session; the full 20-module suite was **not** independently rerun to completion for this handoff (a full grouped attempt timed out). The standalone GitHub finite reference has a separate 4/4 test result.

## Provenance and boundaries

- Base package: `ab_chatbot_union_edge_extension_2026-10-12.zip`, SHA-256 `db341642b42aa09472eae80006802ace3b23130ab5bcff9a29a7cb174432c35b`.
- The code added in this continuation includes `ab_chatbot_alternative_extension.py`, `test_ab_chatbot_alternative_extension.py`, `run_alternative_extension_demo.py`, and a backward-compatible change to `ab_chatbot_union_extension.py`.
- GitHub's `work/arc_like_maze/chatbot/` standalone witness is a **small, independently runnable reproduction** of the finite comparison. The complete local chatbot package is separately packaged in the conversation and is not claimed to have been uploaded in its entirety to GitHub.
- No physical or external-system proof; no unlimited generalization; no assertion of unique pairings outside the candidate set.

**Next referent:** Compare branching candidate extensions beyond two fixed priorities, with bounded backtracking and explicit evidence for why a rejected edge may be admitted under another pairing.
