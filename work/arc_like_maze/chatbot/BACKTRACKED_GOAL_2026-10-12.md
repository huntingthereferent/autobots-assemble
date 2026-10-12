# Backtracked goal extension — finite research witness

**Date:** 2026-10-12
**Question:** When both AB-first and BA-first greedy rooted extensions miss a declared source goal, can bounded exploration of alternative compatible path prefixes find a usable relation, then enlarge it by checking remaining edges?

## Witness

Finite original law phi=(0,0,1); changed law phi=(1,0,1), root (0,0,0), source goal (1,1,2).

- Both old greedy priorities omit (1,1,2).
- Independent bounded path-prefix exploration (depth 6) discovers action word ABBBBB, giving changed-system image (1,1,1). No target route was supplied.
- Compatible discovered paths are joined on agreeing paired states; any rejected prefix has a separating endpoint-equality witness.
- Greedy edge extension of that **chosen** pairing gives 27 paired states, **42 admitted edges**, **12 excluded edges**. This is NOT closed under all A/B edges; being 27 paired states does not establish full conjugacy.
- An independent brute-force word enumerator checks the goal witness. Test code separately checks each admitted edge in both finite laws. 5 focused tests in this GitHub standalone witness.

Run from this directory:

    python bounded_backtracked_goal.py
    python -m unittest -q test_finite_goal_priority.py test_bounded_backtracked_goal.py

**Integrated chatbot:** The separate full local 61-file package includes \`ab_chatbot_backtracked_extension.py\`, integrating the existing pinned BranchDiscoverer, PathUnionAgent, and UnionEdgeExtender rather than replacing them. Its new module passed 9/9 focused tests; its larger historical regression status is recorded separately. That complete package is a conversation artifact, not silently claimed to have been uploaded to GitHub.

**Scope/limits:** The standalone witness is deterministic over specified complete 27-state laws. It has no remote observer, authenticated origin, or language understanding. Its 250-prefix and six-step defaults are finite limits; failure under those limits is not a global no-solution theorem. The selected correspondence is not proved maximal. A/B remains relational language; these are only scoped named generators.

**Next:** Compare two *different* completed path-seeded extensions on goal coverage and witness quality. Preserve alternate target images, source revision, and explicit search/resource walls. Do not change \`state/current.json\`: it belongs to the separately active Continuity referent.
