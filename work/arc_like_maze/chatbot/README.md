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


## Mixed typed obligations (2026-10-12)

[Standalone finite checker](finite_mixed_contract.py) · [five finite tests](test_finite_mixed_contract.py) · [scope and evidence](MIXED_TASK_OBLIGATIONS_2026-10-12.md). The integrated local chatbot now checks required edges, exact rooted path histories, and destination identities as separate proof obligations, all on a single replay-audited pairing. The 129-file snapshot-backed chatbot and per-trial evidence are preserved as a separate local package; existing Continuity project pointers are unchanged.


## Explicit local-owner provenance (2026-10-12)

[Finite source-scope checker](finite_provenance_scope.py) · [four pure tests](test_finite_provenance_scope.py) · [evidence record and boundaries](PROVENANCE_CONTRACT_2026-10-12.md). The integrated local chatbot requires live verified owner bindings for explicit per-source proof demands, and downgrades previously witnessed labels if an owner binding is withdrawn. The full 137-file HTTP-pinned integration is a separate local archive; this GitHub sidecar is NOT remote-source authentication or the complete chatbot.


## Exact owner pins and deliberate re-pinning (2026-10-13)

[Standalone finite owner/snapshot identity model](finite_owner_pin_identity.py) · [five pure tests](test_finite_owner_pin_identity.py) · [scoped evidence and limits](EXACT_OWNER_PIN_2026-10-13.md). Explicit locally issued owner pins prevent a task from inheriting a previous owner's result after object/snapshot/revision substitution. An explicit re-pin creates a new task referent; source labels and digests do not authenticate remote providers. Full 145-file HTTP-pinned integration is packaged separately, not committed wholesale.


## Cross-pin historical revision comparison (2026-10-13)

[Independently runnable finite word comparison](finite_cross_pin_relation.py) · [five finite tests](test_finite_cross_pin_relation.py) · [bounded evidence and limitations](CROSS_PIN_COMPARISON_2026-10-13.md). The full local 153-file chatbot now compares explicitly requested rooted word relations across two independently pinned owner snapshots, with fresh new-version observation and complete cached replay. GitHub carries only the standalone finite counterpart and research record, not the entire HTTP-pinned chatbot.


## Joint cross-pin rooted histories (2026-10-13)

[Standalone finite join checker](finite_cross_pin_join.py) · [five independent finite tests](test_finite_cross_pin_join.py) · [bounded evidence and scope](JOINT_CROSS_PIN_2026-10-13.md). Two independently pinned revisions may support a **partial joint correspondence of actually witnessed paths**; incompatible source or target assignments return exact replayable collision words. The integrated 161-file HTTP-pinned chatbot is a separate artifact, not silently committed to GitHub.


## Explicit tasks from a previously joined witness (2026-10-13)

[Standalone finite consumer](finite_joint_task_consumer.py) · [six independent finite tests](test_finite_joint_task_consumer.py) · [scoped evidence record](JOINT_EVIDENCE_TASK_2026-10-13.md). A new task may check declared goals, edges, paths and destination identities **only** against the prior admitted partial join, without inventing source transitions. The full integrated HTTP-pinned 169-file chatbot is preserved separately; the GitHub sidecar is not its source-owner authentication mechanism.


## Fingerprint-bound joint evidence tasks (2026-10-13)

[Independent finite witness checker](finite_join_fingerprint.py) · [six finite tests](test_finite_join_fingerprint.py) · [scope and reproduction](JOIN_WITNESS_FINGERPRINT_2026-10-13.md). The full local 177-file integrated chatbot binds a task to the exact audited joint mapping and compares multiple candidate joins without importing missing edges or combining separate successes. The standalone checker does not authenticate HTTP owner origins.


## Explicit witnessed donor-edge transfer (2026-10-13)

[Standalone finite transfer oracle](finite_explicit_join_transfer.py) · [five finite tests](test_finite_explicit_join_transfer.py) · [research and evidence scope](EXPLICIT_JOIN_TRANSFER_2026-10-13.md). Under the SAME pinned source referents, one already-observed rooted donor edge may be selected to create a new derived partial correspondence without altering either original join. A conflicting subsequent edge is rejected with a word-equality witness. Full 185-file HTTP-pinned integration is a separately packaged local artifact.


## Selected edge transport across distinct owner scopes (2026-10-13)

[Independent finite four-law checker](finite_cross_scope_transport.py) · [six tests](test_finite_cross_scope_transport.py) · [scope, source and results](CROSS_SCOPE_TRANSPORT_2026-10-13.md). Distinct pinned local owners can yield one newly witnessed labeled commuting square only after explicit OLD and NEW endpoint maps and separate recipient-side transition observation. One square is not full source equivalence. Full 193-file owner-bound chatbot remains in a separate local archive.


## Two-hop transport of one selected finite edge (2026-10-13)

[Standalone six-law finite checker](finite_two_hop_transport.py) · [six independent tests](test_finite_two_hop_transport.py) · [evidence and limits](TWO_HOP_TRANSPORT_2026-10-13.md). Two separately observed recipient-side commuting squares across three distinct pinned source pairs yield one new six-state/five-edge derived witness; base joins remain unchanged. The complete 201-file owner-bound chatbot is available in the separate local archive, not committed wholesale to GitHub.


## Continuation after two-hop — route evidence and change propagation (2026-10-13)

The next six recorded steps, **21–26**, are indexed in [chatbot continuation provenance](PROVENANCE.md). They retain separate original witnesses rather than silently rewriting the two-hop result:

- **21: Two-route comparison.** Two separately witnessed chains can disagree on the image of the same donor endpoint; the mapping conflict is recorded without invalidating either route.
- **22: Source-change propagation.** On invocation, changed source pins/observations withdraw affected route evidence; unchanged pinned historical revisions may survive a newer owner head.
- **23: Source-replacement recovery.** A newly pinned replacement earns its own observations and may either agree with or conflict with the surviving route.
- **24: Selective propagation across comparisons.** Only comparisons depending on changed scopes are selected for re-audit; untouched results remain cached, not proof-for-use.
- **25: Selective refresh inside a comparison.** Only the affected route is replayed for an update; a usable combined comparison still requires a full two-route audit.
- **26: Route-specific task consumption.** An explicitly bound task checks only its selected, currently replayed route and never borrows obligations from another route.

These six stages are **locally executed integrated extensions, not six newly committed standalone mathematical source suites**. Their complete archives, filenames, SHA-256 hashes, reproducible commands, and recorded test counts are listed in [PROVENANCE.md](PROVENANCE.md). The latest locally preserved package has **249 files**. This GitHub README and index do not imply that the complete integrated code or its local test execution is already in the repository.


## Multi-task source dependency propagation (2026-10-13)

[Stage 27 evidence](MULTI_TASK_DEPENDENCY_2026-10-13.md) · [independent finite dependency model](finite_multi_task_dependency.py) · [eight finite tests](test_finite_multi_task_dependency.py) · [full stage index](PROVENANCE.md). Multiple exact route-bound tasks form a shared source-dependency graph. Changed middle-source evidence re-audits only dependent tasks; changed shared donor/final evidence reaches all of them. Cached tasks are never presented as freshly verified proof. The complete 257-file owner-bound integrated chatbot is packaged separately; this GitHub finite sidecar does not authenticate its source owners.
