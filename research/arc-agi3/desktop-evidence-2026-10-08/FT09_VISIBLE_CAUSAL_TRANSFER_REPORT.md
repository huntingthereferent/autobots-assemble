# ARC A/B — FT09 visible causal policy | 2026-10-08

## Verified results
- FT09: 6/6, WIN, local SDK score 100.0.
- Frame-only agent on two independent fresh runs: 75 actions each; 69 within-level effect predictions checked each; 0 failures.
- Perturbed on-trajectory control: one exploratory click per level, two independent variations: WIN after 81 and 76 total actions; SDK score 100.0 in each; 75 and 70 predictions checked.
- Cross-game rejection controls: 9/9 unrelated initial public environment observations declined rather than issuing FT09 clicks (SK48, LS20, AR25, CN04, BP35, CD82, DC22, G50T, LF52).

## Method
- Prior source-assisted work established color constraints and the click-stencil hypothesis.
- The new policy reads only public 64x64 frame pixels for cell positions, connected board groups, palette, reference glyphs and stencils.
- It builds allowed colors from equality/inequality relations, composes visible click-effect masks, solves binary targets over GF(2), and handles independent multicolor changes by forward-cycle distance.
- It reparses the frame and checks the prior predicted effect after every action, replanning from the newly returned visual state.
- No precomputed per-level click sequence or private game object access during policy execution.
- Source-backed audit: 52/52 visible click-effect predictions matched on Levels 5 and 6.
- Pixel decoder matched all source-audited cells and references in Levels 2-6; a mirrored tutorial group at Level 1 is excluded by board connectedness and rightmost tie-break.

## Evidence scripts
_tmp_ft09_live_visual_causal_agent.py — two 75-action fresh runs
_tmp_ft09_visual_agent_offtrajectory.py — perturbed starts
_tmp_visual_causal_cross_game_gate.py — unrelated-game rejection tests
_tmp_ft09_visible_click_operator_v2.py — 52 click effect tests
_tmp_ft09_pixel_decoder_audit.py — visual geometry audit
_tmp_ft09_visible_components.py — tutorial duplicate discrimination
ft09_verified_6of6.json — independent prior replay record, not read by the live visual policy

## Boundary and next action
- This remains a specialized visual mechanic. The operator/stencil grammar was designed using earlier source-assisted research; it has not been invented completely blind by the policy.
- The current deployable agent/my_agent.py and GitHub repo remain untouched; no competition submission or official score claimed.
- Next: general operator-hypothesis generation and falsification from public interventions; held-out cross-game and budget tests before repo promotion.