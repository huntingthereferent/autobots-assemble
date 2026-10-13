# Finite goal-priority experiment (2026-10-12)

**Referent.** The A/B chatbot research asks whether independently witnessed continuations can be compared before one is selected for a declared completion goal. In this folder, A and B mean only the finite generators of two explicitly given 27-state laws. This does not redefine A/B's language-level referent.

## Runnable GitHub witness

Run from this directory:

    python finite_goal_priority.py
    python -m unittest -q test_finite_goal_priority.py

On the original law phi=(0,0,1) and changed law phi=(1,0,1), an A-first greedy partial correspondence admits 20 paired states and 28 edges but misses source goal (0,0,2). A B-first extension admits 25 paired states and 37 edges and reaches that goal, mapped to (0,0,1), with action word BBBBBB. Both use the same pinned mathematical rules; each rejected extension is accompanied by a separating endpoint-equality witness.

The GitHub sidecar is standalone and verified by an independent finite oracle in 4 local tests. It is *not the complete chatbot* and provides no remote provenance or language bridge.

## Larger local chatbot continuation

The full local package **ab_chatbot_alternative_extension_2026-10-12.zip** (SHA-256: 199d6ff85c0a8073f665720deefd374923d10864405cf5fb40b9379a83646d1b) extends a previous 55-file local package to 59 files. The integration adds AlternativeExtensionChooser, tests, demo and action-order parameter while preserving the default AB path. It uses pinned source snapshots, replay, budget/version walls and remote-source status. Those 59 files are **not yet all in this GitHub repository**; the checksum is a handoff identifier, not a claim of GitHub upload.

Local executed verification for the expanded package: 9 new tests, plus 30 + 28 relevant legacy regression tests (67 total). The previous version's 312-test result is historical; the full historical suite was not rerun to completion this turn. GitHub Actions has not been claimed to have run.

**Evidence boundary:** Only two greedy priorities are compared. Neither exhaustive maximality, arbitrary-language learning, nor physical coupling has been established. Different candidate goal images remain separate; root-restricted agreement never silently becomes whole-system equivalence.

**Next movement:** Bounded backtracking beyond two preset priorities, using replayable edge-conflict witnesses and explicit observation budgets. Preserve this experiment's scope and results as evidence rather than overwriting the current Continuity project pointer.


## Next completed bounded experiment

See [Backtracked goal extension (2026-10-12)](BACKTRACKED_GOAL_2026-10-12.md), the [runnable standalone witness](bounded_backtracked_goal.py), and its [independent tests](test_bounded_backtracked_goal.py). This branch explores compatible path prefixes beyond the two greedy priorities, then checks whether the selected union can be extended. The complete chatbot implementation remains a separate local package.


## Completed-extension portfolio

See the [2026-10-12 experiment](COMPLETED_EXTENSION_PORTFOLIO_2026-10-12.md), [standalone compatible-subset evaluator](finite_extension_portfolio.py), and [finite verification tests](test_finite_extension_portfolio.py). Independent complete extensions may be incompatible: joint goals are not counted unless a single chosen partial pairing carries them. The full integrated chatbot remains a separate local package.


## Seed-first multi-goal coupling

[2026-10-12 scoped evidence](SEED_FIRST_GOAL_COUPLING_2026-10-12.md), [finite executable](finite_seed_first.py), and [finite checks](test_finite_seed_first.py) show a case where compatible paths can be joined before greedy extension despite incompatible independently completed extensions. The integrated chatbot remains a separate local package.


## Post-extension portfolio (2026-10-12)

[Scoped experiment and evidence](POST_EXTENSION_PORTFOLIO_2026-10-12.md) · [standalone finite comparator](finite_post_extension_portfolio.py) · [four independent finite checks](test_finite_post_extension_portfolio.py). The comparison preserves two goals while improving locally admitted edges from 40 to 42 under the stated changed-law pair. The complete pinned-observer chatbot remains a separate local package.


## Conflict-guided continuation (2026-10-12)

[Finite witness](finite_conflict_guidance.py) · [four standalone tests](test_finite_conflict_guidance.py) · [scoped research record](CONFLICT_GUIDANCE_2026-10-12.md). This checks a rejected A/B edge from one partial pairing that becomes admitted under another without claiming the two complete pairings can be fused. Equal-budget negative results and separate local chatbot evidence are recorded explicitly.


## Controlled search-policy benchmark (2026-10-12)

[Scoped evidence and decision](POLICY_BENCHMARK_2026-10-12.md) · [standalone record checker](finite_policy_benchmark_record.py) · [record checker tests](test_finite_policy_benchmark_record.py). Eighteen paired finite comparisons preserve fixed-order selection as the default: no observed guided goal wins, one fixed admitted-edge win, two fixed observation-cost wins. The full executed benchmark and its detailed JSON live in the separate complete chatbot archive.


## Required-edge evidence prefilter (2026-10-12)

[Finite checker](finite_required_edge_guard.py) · [four finite tests](test_finite_required_edge_guard.py) · [scoped research record](REQUIRED_EDGE_PREFILTER_2026-10-12.md). An explicit must-admit-edge task can disqualify two already-contradicted seed pairings before full extension, while preserving nine other alternatives. The opt-in integrated chatbot is in the separate 108-file local archive; default search policy is unchanged.


## Explicit task contracts (2026-10-12)

[Finite explicit task checker](finite_explicit_task.py) · [four finite tests](test_finite_explicit_task.py) · [scoped record](EXPLICIT_TASK_CONTRACT_2026-10-12.md). Only caller-declared task requirements are admitted; goals alone never imply must-admit edges. The integrated HTTP-pinned task session remains in the separate 115-file local archive, and the old default search policy is preserved.


## Multiple explicit required edges (2026-10-12)

[Standalone finite conjunction checker](finite_multi_required.py) · [four finite tests](test_finite_multi_required.py) · [bounded research handoff](MULTI_REQUIRED_EDGES_2026-10-12.md). Two explicit edge requirements can reject different seed pairings and must be proved **together** by a single extension. A bounded failure remains REQUIREMENTS_UNPROVED, never a global no-solution theorem. Full pinned-owner integration is in the separately preserved 122-file local package.
