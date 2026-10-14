# Explicit task-to-witness contract — 2026-10-12

## Current referent

Can the finite A/B chatbot recognize a **preservation requirement actually supplied in the current task**, feed it to the previously verified required-edge prefilter, and avoid silently constructing such a requirement from ordinary goals or ambiguous language?

**Yes for a deliberately explicit grammar or structured task input.** No unrestricted natural-language understanding is claimed.

A/B remains the user's relational language for describing movement. The particular 27-state A- and B-labeled generators, source snapshots, and search algorithms are distinct finite mathematical representations.

## Task language

Two accepted shapes:

```text
goals: (0,1,1), (0,2,0)
goals: (0,1,1), (0,2,0); require: edge (0,0,0) B
```

and the structured shape:

```json
{"goals": [[0,1,1], [0,2,0]], "required_edge": {"state": [0,0,0], "action": "B"}}
```

`required_edge` is optional. Its absence means **no inferred edge requirement**. This implementation supports only **one** explicitly required finite labeled edge; multiple-edge or unknown schema keys remain unsupported, rather than being silently truncated. The textual grammar is intentionally narrow; loose wording (e.g. "keep the B thing") returns `UNKNOWN_TASK`, with no backend observations. Invalid states, duplicate goals, booleans and malformed schema are rejected before constructing an agent.

Accepted tasks retain the original expression, normalized distinct goals, optional edge, declaration channel (`EXPLICIT_GRAMMAR` or `EXPLICIT_SCHEMA`), and SHA-256 fingerprint of canonical mathematical constraints. This fingerprint identifies a contract, **not a source-authentication mechanism**. No finite mathematical conclusion is implied by parsing.

`TaskContractSession` dispatches to existing `PostExtensionPortfolio` when the edge is absent, and existing `RequiredEdgePortfolio` when it is present. It does not alter either class or existing default selection. The original snapshot source revisions, admitted-edge witnesses, cached owner replay, observation budgets, and remote provenance discipline remain controlled by those existing classes. An invalidated witness invalidates the current result, not the declared task.

## Reproduced result

Original law phi=(0,0,1); changed law phi=(0,0,0); root=(0,0,0); goals (0,1,1) and (0,2,0); both snapshots locally owned and separately pinned.

| Submitted task | Outcome | Goals carried | Evaluated candidates | Old + new observations |
|---|---|---:|---:|---:|
| Goals only | GOALS_CARRIED_WITNESSED | 2/2 | 11 | 28 + 18 = 46 |
| Goals + required root B edge | PARTIAL_GOALS_WITNESSED | 1/2 | 9 | 26 + 18 = 44 |
| Ambiguous text | UNKNOWN_TASK | no solver run | 0 | 0 |

**Do not interpret 2/2 versus 1/2 as a regression.** The constrained task is strictly harder. Its **unpruned eligible oracle** also carries 1/2, requires 11 extension trials and 46 observations, so prefiltering saves 2 trials and 2 owner edge observations in this declared example without changing its eligible best result. The requirements are not globally imposed on other tasks.

## Reproduce

From the package directory:

```bash
python run_explicit_task_demo.py
python -m unittest -q test_ab_chatbot_task_contract   # 11 new tests
python -m unittest -q test_finite_explicit_task       # 4 independent finite tests
python -m unittest -q test_ab_chatbot_evidence_prefilter
```

Additional relevant legacy modules were run separately and passed: `test_ab_chatbot_post_extension_portfolio` (25), `test_ab_chatbot_seed_first_extension` (12), `test_ab_chatbot_language_bridge` (35), `test_ab_chatbot_conflict_guided` (10), `test_ab_chatbot_path_union` (15), and `test_ab_chatbot_evidence_prefilter` (8). With the new modules, **120 tests passed in individually completed runs**. A combined regression command stalled between modules, and the entire historical suite is **not** being claimed. No GitHub CI execution is claimed.

The standalone `finite_explicit_task.py` and its four tests are independent of pinned HTTP owners; they verify the strict task grammar and oracle's seed-level contradictions under fully specified laws. They are not a second chatbot and not a provenance certificate.

## Evidence boundary and next movement

This layer does **not** infer requirements from everyday language, prove that inferred requests are accurate, support multiple preserved edges, or prove maximal finite correspondences. A requirement is an explicit **task constraint**, not evidence that an edge is satisfiable. Missing or contradictory observation evidence stays `UNDECIDED`, `UNKNOWN`, `WALL`, or `PARTIAL` according to the existing verifier.

The next narrow extension is to admit *multiple explicitly supplied required edges* without allowing pairwise witness contradictions to be flattened into an unsupported global exclusion. It should then be tested on held-out finite goal sets with equal observation budgets, including cases where the entire requirement set cannot be met.

The full local package remains separate from the GitHub finite sidecar and does not mutate the unrelated Continuity default `state/current.json` pointer.
