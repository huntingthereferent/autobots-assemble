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
