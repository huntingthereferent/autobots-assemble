# Multiple explicit required edges — 2026-10-12

**Active finite correspondence process referent:** Support a bounded task that explicitly requires preservation of **several** A/B-labeled finite transitions, never inferring them from goals or vague language. Formal A and B denote specified 27-state generators. A/B as language for movement is not redefined by this toy model.

## Executed integrated result

Original finite law phi=(0,0,1), changed law phi=(0,0,0), both separately pinned and independently owner-replayed. Root (0,0,0), source goals (0,1,1) and (0,2,0). Finite depth=6, variants=4, candidate limit=7, trial limit=12.

- Required edges: root B AND (0,1,0) B. Seed candidates **11 -> 9** using two replayable exclusion certificates; all retained tested candidates actually admit both requirements. Selected extension carries **1/2 goals**, with 9 paired states and 15 admitted edges, observed 26 original + 18 changed owner edges.
- Required edges: root B AND (1,2,0) B. Seed candidates **11 -> 7**; four independently replayable exclusions, two from each of the two distinct requirements. Selected extension carries **1/2 goals**, with 9 paired states and 13 admitted edges, observed 26 + 18 owner edges.
- Required edges: root B AND (0,0,1) A. Candidate set **11 -> 9**; none of nine completed bounded candidates admits BOTH required edges. Status **REQUIREMENTS_UNPROVED**, no selected completion, and each candidate's missing requirements retained. This is not a theorem of global impossibility.
- Identical-law control reaches the full 27-state rooted component, 54 admitted A/B edges and both goals plus both compatible requirements.

## Input

Explicit supported text:

    goals: (0,1,1), (0,2,0); require: edges (0,0,0) B, (0,1,0) B

Or structured:

    {"goals":[[0,1,1],[0,2,0]],"required_edges":[{"state":[0,0,0],"action":"B"},{"state":[0,1,0],"action":"B"}]}

The integration supports 2..8 distinct explicitly declared finite edges. It preserves the existing singular-required-edge and goals-only handlers without modifying them. Unknown task language never silently gains constraints. Each preflight exclusion retains its associated specific required edge, observed targets, state-pair collision and pinned-owner evidence; it must replay on every later read. Incomplete evidence is UNDECIDED, not a pruning certificate.

## Reproduction scope

From this directory:

    python finite_multi_required.py
    python -m unittest -q test_finite_multi_required.py

The GitHub standalone checker has four locally executed finite-law tests and independently reproduces 11->9 and 11->7, including the two separate conflict sources. It does not replay HTTP origin, authenticate task input, or replace the full integrated correspondence process.

Full separate local package: **ab_chatbot_multi_required_edges_2026-10-12.zip**, SHA-256 **e27833a0419b0163a42d43d4824ec638a513934d8e8f185556e9513fe67bd961**. 122 files, with all 115 predecessor files verified byte-for-byte unchanged. New integrated module, 13 tests, demo, four independent finite tests, data and detailed README. Local executed verification: 13 new integrated + 4 finite + 11 previous task intake + 8 previous single-edge prefilter + 4 previous finite explicit task + 3 individual path-union/edge-extension/post-extension regression controls = **43 passing tests**. A larger grouped regression timed out; the full historical suite and GitHub CI were not run to completion.

**Boundary:** Rejections are specific to each candidate seed pairing AND the user's stated task. All requirements must be admitted by one finished replayed candidate. No bounded search can justify a claim of universal mathematical impossibility, whole-system equivalence or real-world generalized autonomy. Do not change the separate Continuity project pointer.

**Next:** Admit other explicitly typed obligations (e.g. a witnessed path identity or final-state equality) through their *own* native replay contracts, without silently converting one relation into another. Compare on held-out tasks and track owner observation cost.
