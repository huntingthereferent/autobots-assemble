# Explicit finite task contract — 2026-10-12

**Question:** Can a task supply a finite A/B-labeled *must-admit edge* as an explicit requirement without the chatbot silently constructing one from its goals or vague wording?

**Scoped answer:** Yes, for exact admitted text grammar or an explicit structured schema. The full snapshot-backed local chatbot adds immutable task declarations and routes goals-only to the existing PostExtensionPortfolio; it routes an explicit single must-admit edge to the existing RequiredEdgePortfolio. Parsed text is a declaration, **not** a mathematical witness, source-authenticated provenance claim, or universal interpretation of language.

Supported text forms:

    goals: (0,1,1), (0,2,0)
    goals: (0,1,1), (0,2,0); require: edge (0,0,0) B

Supported structured form:

    {"goals":[[0,1,1],[0,2,0]],"required_edge":{"state":[0,0,0],"action":"B"}}

No required_edge key means **no preservation requirement**. The parser admits one explicit edge only; ambiguous prose is UNKNOWN_TASK, unknown schema keys and multiple-edge demands are unsupported, and malformed or duplicate finite states are rejected. Original accepted expression, declaration channel and normalized constraints survive; canonical SHA-256 distinguishes contracts without pretending to authenticate sources.

## Executed local integration

Two independently pinned locally verified laws: original phi=(0,0,1), changed phi=(0,0,0); goals (0,1,1), (0,2,0).

| Submission | Goals carried | Candidate extensions | Observed old + changed edges |
|---|---:|---:|---:|
| Goals only | 2/2 | 11 | 28 + 18 = 46 |
| Same goals with required root B | 1/2 | 9 | 26 + 18 = 44 |
| Ambiguous language | No solver executed | 0 | 0 |

The 2/2 and 1/2 are **different task contracts**, not a performance comparison. A separately verified unpruned eligible oracle for the required-edge contract also selects 1/2 goals, but uses 11 candidate extensions and 46 owner edge observations. The task parser neither infers the constraint nor weakens the mathematical witness obligations. A pinned revision change, forged edge, or remote observation still follows the original evidence/UNKNOWN/WALL boundary.

**Local verification:** 11 new integrated task tests and 4 separate standalone finite tests. Relevant unchanged module runs: existing required-edge prefilter 8, post-extension portfolio 25, seed-first extension 12, language bridge 35, conflict-guided portfolio 10, path union 15. **120 completed tests** in separate runs. A grouped run stalled; full historical regressions and GitHub CI are not asserted.

Full **115-file** local package: ab_chatbot_explicit_task_contract_2026-10-12.zip, SHA-256 **269d2c2f22dd99567d70a515fca5686ffee5b4a5c7e43674cab18f7537f061dd**. All 108 files from its predecessor were checked byte-for-byte unchanged. This archive has the integrated code, demo, both test modules and EXPLICIT_TASK_RESULTS.json; the entire chatbot is **not copied into GitHub**.

## GitHub standalone finite checker

    cd work/arc_like_maze/chatbot
    python finite_explicit_task.py
    python -m unittest -q test_finite_explicit_task.py

This checker depends only on committed finite_goal_priority.py and finite_required_edge_guard.py. It confirms three seed-level verdicts from the explicit grammar using defined complete finite laws, plus the goals-only no-pruning case. It **cannot** certify HTTP owners, integration behavior or missing observations.

**Next:** Support multiple *explicitly* declared required edges, checking consistency of each candidate across the requirement set and preserving unknown and competing evidence rather than treating a failed candidate as a global impossibility. Separately benchmark held-out finite goals and observation costs. Do not change the unrelated Continuity state/current.json project pointer.
