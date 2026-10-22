# ARC4 lane B — source-pinned intervention

**State:** implementation and tests can run independently; real native intervention is **gated**, not yet executed.

## Relationship to [lane A — PR #407](https://github.com/huntingthereferent/autobots-assemble/pull/407)
Consume the exact emitted native JSON source record from lane A (not an imagined fluid simulator). Select a specific **first source-color-6 arrival outside cup windows** at row5 or row8, including both witnesses' identical frame/x record **and a matched negative control with a different native first arrival**. Merely finding the same pixel event in positive and negative cases is insufficient. Identify an already-authenticated native selectable-object click in the actual action receipts. The proposal must name both `case` and `contrast_case`; the positive must have a four-cup observation while the matched control does not. Candidate hypothesis must be written separately and admitted with `python -m work.arc3.arc4_intervention_gate --audit AUDIT.json --proposal PROPOSAL.json --out PLAN.json`.

## Intervention
The gate verifies the most recent original `ACTION6` click and its SDK receipts, then appends **one** legal movement `ACTION1..4` to the already-selected native object immediately before the existing genuine `ACTION5`. It deliberately does **not** add another click, which would confound movement with selection history. This is a **prospective experiment**, not a predicted causal solution. Run `python -m work.arc3.native_sp80_stage4_gated_intervention --plan PLAN.json --out OUT.json` only after the source audit has established the input and the exact source-derived plan has been inspected. The pinned paired experiment freezes a reviewed plan in `work/arc3/lanes/approved-*.json` and regenerates it from the original Lane A artifact before running; any mismatch fails closed.

The new separate manual GitHub Actions workflow refuses absent/noncanonical plans; the PR workflow itself only tests and compiles the gate. Both original native entry witnesses and full 64x64 returned frames are mandatory. Only official SDK level >=5 / WIN is game progress.

## Hold conditions
Unknown source contact, mismatching A/B witnesses, missing prior click receipt, or illegal action => stop at **UNKNOWN**. Do not widen to an uncontrolled search. Keep mathematical ARC-like models, WORLD, NIH, and other workers unchanged. Do not merge without native evidence and all required protocol gates.
