# Eight-source selective swallow: A/B workstation, October 19, 2026

**Rule:** inspect the actual referent, compare with implemented A/B source,
retain only a missing relationship that can be tested, keep every original
source/right untouched. A source being large is not evidence of novelty. This
is a finite inspection of named source files, **not** a proof that all the
upstreams or all of A/B were exhaustively understood.

All upstream files remain upstream; no upstream code, prompt or benchmark
was copied. The new A/B Python implementation keeps the project's own rights.

| Upstream source tree | Source relationship inspected | Existing A/B referent | Result |
| --- | --- | --- | --- |
| [FoundationAgents/AFlow](https://github.com/FoundationAgents/AFlow/tree/3f457218fc716093fe53f6df8a5d5e6379d66346) (`scripts/optimizer.py`, `optimizer_utils/experience_utils.py`, MIT) | Mutate/evaluate workflow alternatives and retain successes/failures under bounded iterations | `workstation_construction.py` already proposes and links candidates; `workstation_harness.py` bounds continuation; native feedback exists | **Reuse the question, not its LLM optimizer:** compare evidenced alternatives on fixed tasks. No MCTS or automatic graph evolution imported. |
| [gepa-ai/gepa](https://github.com/gepa-ai/gepa/tree/f1cfdee2856e9dc4b5b4dc5cc2e391d0aa20d819) (`src/gepa/core/state.py`, MIT) | Candidate frontiers can be indexed by instances/objectives and keep distinct specialists | `promotion.py` had edition preference but no demonstrated native Pareto report across multiple held-out tasks | **New:** `witnessed_frontier.py` only when both native job and independent score are verified; maintain all nondominated specialist editions. |
| [getzep/graphiti](https://github.com/getzep/graphiti/tree/6e3e3cb98edfac4ca5be6129002d76cdf714ad09) (`graphiti_core/utils/maintenance/temporal_edge_utils.py`, Apache-2.0) | Temporal validity/invalidity boundaries must be distinguished from future promises/deadlines | `nih_phase1_world_two_clock.py`, `language/words/temporal_observation.py` already separate observation and valid time for their declared scopes | **No new global graph:** extend only if a live non-NIH task reveals a missing temporal transition. |
| [microsoft/Trace](https://github.com/microsoft/Trace/tree/8190d032e43ffe18943a8cad9ea9ee99e43d6773) (`opto/trace/propagators/graph_propagator.py`, MIT) | Feedback can traverse structured parent/provenance nodes | `RuntimeJournal`, `workstation_construction.py`, `workstation_continuation.py` already retain parent and connection provenance | **Do not add learned backward credit:** it would infer an unverified cause from observed ancestry. |
| [UKGovernmentBEIS/inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai/tree/4aa17c03d738a31b16cf08a63d9a953279c2f6a8) (`design/checkpoint-snapshot-strategy.md`, MIT) | Explicit checkpoint storage and independent evaluation/resume contracts, with noted unimplemented retention features | W13 native journals, source hashes, replay/restore verification and existing worker-specific native verifiers | **No new checkpoint storage format.** Measured scores in `witnessed_frontier.py` require independent native AND evaluation receipts; no score invented from a run status. |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph/tree/1400d25b7b88cfa055c55b8a82bd95b7c25caef1) (`libs/checkpoint-conformance/langgraph/checkpoint/conformance/spec/test_copy_thread.py`, MIT) | Branch/copy a checkpoint history without changing its source, preserve ordering and metadata | Source-owned edition branches, lane parents, append-only handoffs and replay | **No graph executor:** a missing checkpoint-copy conformance result would be a future test, not permission to replace current journals. |
| [letta-ai/letta-code](https://github.com/letta-ai/letta-code/tree/e272bb9469181f482304092194c2da5063bd30c3) (`src/agent/memory-conflict-repair.ts`, Apache-2.0) | Concurrent memory repair uses process/token identity to prevent a late attempt from overwriting a newer one | A/B research uses native journal and exact jobs, not Letta's Git-backed agent-memory checkout | **Do not import agent personality or memory repair.** Revisit only if an actual A/B multiwriter race is observed. |
| [microsoft/agent-lightning](https://github.com/microsoft/agent-lightning/tree/69f5a40b36d9bff646b8e7a5532e8b78bd41eaf9) (`agentlightning/server/store.py`, MIT) | Preserve rollout/event references for later learning | Native worker results, journals and independent replay already exist | **No trainer/proxy:** no supported reward, training objective, or result justifies substituting learned optimization. |

## Exact addition

`systems/workspace/witnessed_frontier.py` works only on *existing*
source-owned job/evaluation receipts, with a caller-supplied independent
verification callback for each. The declared task set, scoring direction,
metric and test setup must match between editions. Each candidate uses one
stable worker/edition/source fingerprint for its receipts. It has a finite
32-candidate, 32-task bound and never schedules work, fabricates an unobserved
trial, or chooses/pins a winner.

An incomplete or unverifiable candidate is reported **UNKNOWN**, never as an
implicit low score; the resulting frontier is explicitly **PROVISIONAL**.
A dominated edition is retained in the report for provenance, not deleted.

This is a comparison primitive, **not** an automatic integration into
`controls.promote_edition`. That native gate remains the exclusive path to
pin an edition after an explicit approval and real source-specific replay.
Test fixtures deliberately do not assert a real research improvement.

## New non-AI source lane

The next source inspected is [Box2D](https://github.com/erincatto/box2d/tree/178495ba35695aefe9c321e569d2277f06db3b90)
(MIT), specifically `docs/collision.md` and `src/distance.c`.
Its one-sided **chain ghost-vertex** suppression requires neighboring
segments joined at endpoints. A/B WORLD Trial 05/06/07/08 uses **two
independently generated finite segments that intersect through their
interiors**, so importing chain ghost suppression would change the
observed geometry and might erase an actual simultaneous contact. Their
cases are not equivalent. Box2D's general time-of-impact/conservative
advancement for rotating convex shapes also should not replace the
already independently checked finite disc–segment solver without a
specific failing source-native experiment.

The physics follow-up belongs with the actual WORLD Trial 08 branch and
independent source tests, not under a renamed AI executor or a fake
universal physical-world claim.
