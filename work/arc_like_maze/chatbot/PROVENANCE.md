# Finite Correspondence Research — checkpoint provenance (October 13, 2026)

This is a trace of the finite correspondence investigation's **stages 20–30**, following the [research index](research/README.md). Historical code and archive identifiers remain unchanged for provenance and compatibility; they do not define the subject of this research. The declared A/B-labeled finite generators are experiment-specific operators; they do not define the language referent. These records preserve what was observed and how to revisit it. The source systems and their environment do not need to initiate autonomous goals for relations to be checked on the next invocation.

## Witness sequence

| Stage | What changed and what survived | Locally recorded result | Integrated archive |
| --- | --- | --- | --- |
| **20 · Two-hop selected-edge transport** | Two independently witnessed selected squares connect three owner-pinned pairs. Original joins remain untouched. | 6 paired states; 5 admitted edges; 2/2 required task edges; 76 completed targeted test executions. [GitHub finite source](finite_two_hop_transport.py), [tests](test_finite_two_hop_transport.py), [scoped record](TWO_HOP_TRANSPORT_2026-10-13.md). | `ab_chatbot_two_hop_transport_2026-10-13.zip` · 201 files |
| **21 · Two-route comparison** | Two valid two-hop routes share donor/final owner scopes but use different pinned middle scopes. Four old/new endpoint assignments disagree; neither route certificate is erased. | `ROUTE_COMPOSED_MAP_CONFLICT`; agreement control also tested; **113** completed tests. | `ab_chatbot_two_route_comparison_2026-10-13.zip` · 209 files |
| **22 · Source-change propagation** | On-demand owner-pin and evidence re-audit distinguishes withdrawn routes from preserved historical witnesses. A new owner head does not erase an unchanged pinned old snapshot. | One right-middle change withdraws the right route, not the left; **101** completed tests. | `ab_chatbot_source_change_propagation_2026-10-13.zip` · 217 files |
| **23 · Source-replacement recovery** | A new independent owner/snapshot/pin establishes replacement evidence; the old comparison stays historical. A replacement may agree or conflict. | `RECOVERY_AGREEMENT_WITNESSED` and `RECOVERY_CONFLICT_WITNESSED` demonstrated; **92** completed tests. | `ab_chatbot_source_replacement_recovery_2026-10-13.zip` · 225 files |
| **24 · Selective propagation across comparisons** | Changes select dependent comparison records; unrelated records are explicitly cached, never silently promoted as freshly verified. | One affected record replayed, one unrelated record skipped; **99** completed test executions. | `ab_chatbot_selective_propagation_2026-10-13.zip` · 233 files |
| **25 · Selective refresh inside a comparison** | Replays only the affected route for a local update. A task needing the combined route-independent comparison still replays both. | One of two routes selectively refreshed; zero new transition observations; **106** completed tests. | `ab_chatbot_route_selective_refresh_2026-10-13.zip` · 241 files |
| **26 · Exact route-bound task** | A declared task is tied to one exact route fingerprint and current owner-backed evidence, without borrowing the other route's edges. | 2/2 required edges completed on an unaffected route after the neighboring pin was revoked; **100** completed tests. | `ab_chatbot_route_bound_task_2026-10-13.zip` · 249 files |

These test figures are **per-stage completed targeted runs**, generally including overlapping regression suites. Do not add them into one unique cumulative test count. The full historical suite was not completed for these six additions; no GitHub CI outcome is asserted for the integrated archives.

## Archive identity (SHA-256)

Each archive below was verified as readable. Each successive archive adds **eight files**, preserves all preceding entries byte-for-byte, and does not overwrite the prior mathematical witnesses.

| Stage | SHA-256 |
| --- | --- |
| 20 | `e14793cf3c3831489af42a4bd2c9662431edb029d26014ee2066427abfb94f5b` |
| 21 | `191ed3da68ab40f6ee41575de81200bd325597c1c8c071c9e007322b7b4745f6` |
| 22 | `5c390e9a17fae2d6541b52d2321987561ea4f080589271beb5a6772f6ae1e661` |
| 23 | `f6b9f1a58f37f4876859ca030515ecfb98ab05757459b9cbeff892df7f5c9c54` |
| 24 | `cfb7e0b2c85384796d92fba6de1ce5eeb62ed8c2c9c803d245a41572e3809305` |
| 25 | `2ef7351439cde7413a6ebc49d9122e322f72fbdd82d40625396d9a84621e7da9` |
| 26 | `cbcab83b747e644aa3759ce8a6feb9a8cbdb195ea16f2c016725dbbdb5e856fd` |

**Current source locations:** [Checkpoint index](research/checkpoints/README.md) is the calm entry point. Stages **21–26** now have their eight individually recovered code/evidence files in matching GitHub folders, with `README.md` for navigation and `record.md` for the dated report. The original Stage 20 integrated 201-file baseline and Stage 27 integrated archive are still separate local ZIPs; the smaller original GitHub finite references remain available.

Archive hashes below are integrity identifiers, **not** download links. A clean GitHub checkout does not yet contain the full Stage 20 integrated baseline needed to run every later owner-backed adapter. The locally preserved Stage 26 ZIP contains the complete 249-file flat package. To reproduce its latest task after extracting it:

```sh
python -m unittest -q test_ab_chatbot_route_bound_task.RouteBoundTaskTests
python -m unittest -q test_finite_single_route_task.FiniteSingleRouteTests
python run_route_bound_task_demo.py
```

The [finite checkpoint workflow](https://github.com/huntingthereferent/autobots-assemble/actions/workflows/chatbot-finite-checkpoints.yml) separately executes the six GitHub finite reference tests; those runs must not be conflated with full integrated test verification.

The independently executable finite reference models know their declared complete finite laws; they do not authenticate the integrated HTTP-backed owner's identity. The owner-pinned integrated adapters replay their own witnessed observations. When a route changes or its proof is revoked, a previous success is preserved **as history**, not current proof. Skipping an unchanged dependency is a cache decision, not an independently reverified theorem.

**Next possible test:** A shared dependency graph for several route-specific tasks responding to the same external changes. Not implemented by these records. This page records completed movement; it does not predeclare the next result.


## Stage 27 · Multi-task source dependency propagation (October 13, 2026)

[Bounded evidence and reproduction](MULTI_TASK_DEPENDENCY_2026-10-13.md) · [standalone pure finite dependency checker](finite_multi_task_dependency.py) · [eight finite tests](test_finite_multi_task_dependency.py).

The full owner-bound integrated chatbot adds a task-to-source incidence ledger: two tasks can depend on the left route while one depends on the right; a middle-source change selects only tasks using that middle; a shared source change selects all dependent tasks. Tasks that were not replayed remain historical/cached, and a task must freshly replay its own route before its obligations count as current evidence. A changed declaration or moving source blocks freshness rather than inheriting an earlier success.

**Local integrated handoff:** `ab_chatbot_multi_task_dependency_2026-10-13.zip` · 257 files · SHA-256 `03e3a0b89fb477b14c6b09e769e0d3515a004ebe9bf116f677cda86ea65c7a94`. All 249 predecessor entries unchanged. **127 completed targeted tests**: 27 new (19 live owner-bound + 8 independent finite) and 100 regressions. The full historical suite was not completed and no new GitHub CI result is asserted. The integrated owner-backed code and demo are in the local archive; the GitHub code here is the separately runnable finite reference.

## Stage 28 · Shared fresh route certificate across tasks (October 13, 2026)

[Bounded experiment, runnable integrated adapter, demonstrations, tests and regression record](research/checkpoints/28-shared-route-certificate/README.md).

In the locally reconstructed 257-file CP-27 owner-backed package, CP-28 groups independently declared tasks by identical selected route object and exact route fingerprint. Each selected route is checked twice, once per batch, and its current certificate is consumed by separate task obligations. Two left tasks jointly require 2 underlying route replay calls instead of 4, with separate task fingerprints. A missing left-route edge remains unproved even if the right route admits it. Unselected tasks remain historical rather than freshly verified. Zero new owner observations.

The CP-28 complete local ZIP has 265 files; all 257 CP-27 entry contents are unchanged. **35/35 completed targeted tests**: 13 new owner-backed, 14 new complete-law finite reference, and 8 prior finite regressions. Broad combined historical tests and a separate CP-27 integration suite timed out and are excluded. The ZIP remains conversation-local; the GitHub checkpoint folder includes the eight new source/evidence files but lacks the original Stage-20 runtime baseline needed for the full owner-backed execution from a clean checkout. See the checkpoint ledger below for the archive hash. The standalone GitHub reference does not authenticate owners or prove general equivalence.

## Stage 29 · Cross-invocation certificate handoff (October 13, 2026)

[Scoped record, runnable code, tests and outcomes](research/checkpoints/29-certificate-handoff/README.md).

An explicitly issued portable receipt records the already-audited selected route identity and source/witness digests, without any task obligations. A later invocation never trusts the receipt alone: it replays the identical selected owner-backed route twice and checks its complete current certificate before separately evaluating each receiving task. Two left-route tasks complete; a right-only obligation remains unproved. Revoked pins, stale evidence, mutated tasks and altered receipts fail closed. A subsequent receipt use demands a new audit. No new edge observations, independent remote authentication, or autonomous polling are claimed.

**Complete integrated handoff:** `ab_chatbot_cross_invocation_handoff_2026-10-13.zip` · 273 files · SHA-256 `c5342039a5f9f93b2f7ec01eb4130893a7f3b52d6e10e9057b597fd475ca8fb1`. All 265 CP-28 archive entries remain byte-for-byte unchanged. **67/67 completed targeted tests:** 16 new owner-bound, 16 independent finite, 13 CP-28 owner-bound, 14 CP-28 finite, and 8 CP-27 finite. The historical full suite is not claimed. The integrated owner runtime still requires the conversation-local baseline; GitHub finite reference checks do not authenticate independent processes.

## Stage 30 · Independent-process source attestations (October 13, 2026)

[Scoped record, executable signer/verifier, integrated adapter, tests, and exact observations](research/checkpoints/30-independent-process-identity/README.md).

This stage adds three separately pinned synthetic Ed25519 source-scope keys. A signer subprocess produces receiver-challenge-bound attestations for the donor, middle and final source digests, chosen route fingerprint and witnessed route digest. A separate verifier subprocess uses a receiver-provided public-key trust map, never keys embedded in the bundle. Only after all three signatures pass does the CP-29 receiver perform its own fresh two-pass route audit and independently evaluate each task's obligations. Two left-route tasks complete, a right-only required edge remains unproved, and no new source observations are made. Altered keys/signatures, stale source evidence or changed challenge cannot authorize new tasks.

**Complete integrated archive:** `ab_chatbot_independent_process_identity_2026-10-13.zip` · 281 files · SHA-256 `ec6ffe68eb7b1ae955745b04206c4ee6f7e77e2cdf9062b011447ad3522bc7c4`. All 273 CP-29 archive entries are preserved byte-for-byte. **100/100 completed targeted tests**: 16 new owner-backed, 17 new finite signer/verifier, 16 CP-29 owner-backed, 16 CP-29 finite, 13 CP-28 owner-backed, 14 CP-28 finite, and 8 CP-27 finite, counted from completed suites. One combined historical run stalled and is excluded. The finite GitHub tests require the Python `cryptography` package. External trust-anchor enrollment, true owner identity, key management, durable nonce replay protection, and full historical suite are not claimed.

<!-- CHATBOT-CP-LEDGER:BEGIN -->
## Checkpoint output ledger (harness-maintained)

Each row is derived from an explicit CP manifest. The record links are repository evidence indexes; archive filenames below are identifiers, not download links. A CP manifest is not, by itself, independent verification of its claims.

| CP | Observed movement | Survives | Verification | Archive |
| --- | --- | --- | --- | --- |
| [CP-0027](checkpoints/CP-0027.json) · 2026-10-13 | **Multi-task source dependency propagation** — Separate route-bound tasks share a dependency network while preserving independent task evidence. | Each task keeps its own obligations and exact pinned source identity. Unaffected tasks stay cached until explicit proof-for-use. | 127/127 (targeted); [MULTI_TASK_DEPENDENCY_2026-10-13.md](MULTI_TASK_DEPENDENCY_2026-10-13.md) | `ab_chatbot_multi_task_dependency_2026-10-13.zip` · 257 files · conversation-local |
| [CP-0028](checkpoints/CP-0028.json) · 2026-10-13 | **Shared fresh route certificate across tasks** — One fresh route certificate can serve multiple independently declared tasks in a bounded on-demand owner-backed audit. | Exact owner/source pin audits, separate task obligations, no cross-route edge borrowing, cached tasks not fresh, and zero new source observations. | 35/35 (targeted); [research/checkpoints/28-shared-route-certificate/record.md](research/checkpoints/28-shared-route-certificate/record.md) | `ab_chatbot_shared_route_certificate_2026-10-13.zip` · 265 files · conversation-local |
| [CP-0029](checkpoints/CP-0029.json) · 2026-10-13 | **Cross-invocation certificate handoff** — A portable historical route receipt can be freshly revalidated for independently declared tasks in a later invocation. | Exact source pins and route fingerprints, separate task obligations, no borrowing from another route, zero new owner-edge observations, and prior checkpoint evidence. | 67/67 (targeted); [research/checkpoints/29-certificate-handoff/record.md](research/checkpoints/29-certificate-handoff/record.md) | `ab_chatbot_cross_invocation_handoff_2026-10-13.zip` · 273 files · conversation-local |
| [CP-0030](checkpoints/CP-0030.json) · 2026-10-13 | **Independent-process source attestations** — Challenge-bound Ed25519 source attestations can be checked in a separate process, followed by mandatory fresh owner-backed route proof for independently declared tasks. | Previous 273 archive entries unchanged; each task keeps its own route obligations, prior receipts are historical only, missing edges remain unproved, and no new source observations were created. | 100/100 (targeted); [research/checkpoints/30-independent-process-identity/record.md](research/checkpoints/30-independent-process-identity/record.md) | `ab_chatbot_independent_process_identity_2026-10-13.zip` · 281 files · conversation-local |

### Latest checkpoint reproduction

- `python -m unittest -q test_finite_process_attestation.ProcessAttestationTests`
- `python -m unittest -q test_finite_certificate_handoff.FiniteHandoffTests`

Latest archive SHA-256: `ec6ffe68eb7b1ae955745b04206c4ee6f7e77e2cdf9062b011447ad3522bc7c4`

<!-- CHATBOT-CP-LEDGER:END -->
