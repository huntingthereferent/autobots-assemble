# Two independently witnessed transport routes — October 13, 2026

## Purpose and referent

Continue the **same finite A/B correspondence process**. Compare two already evidenced two-link routes from the *same exact pinned donor sources* to the *same exact pinned final sources*, via **different independently pinned middle source pairs**. The question is whether the explicitly composed OLD and NEW endpoint maps agree on **one named donor labeled transition**. No unobserved edges are admitted, and neither route's prior certificate is rewritten.

A/B at the language/research level is not defined by the two formal A/B-labeled operators in this scoped 27-state fixture.

## Executed counterexample

Each scope has its own independently pinned old/new owner snapshots:

| Scope | OLD phi | NEW phi | Witnessed base words |
|---|---|---|---|
| Shared donor | (0,0,1) | (1,0,1) | `AB`, `B` |
| Middle route 1 | (0,0,0) | (0,1,2) | `A`, `BAA` |
| Middle route 2 | (1,1,0) | (1,1,1) | `A`, `BAA` |
| Shared final | (2,0,0) | (2,2,1) | `A`, `BAA` |

The donor's selected `B` transition is witnessed as `(1,0,0) -> (1,2,0)` on the donor old side and `(1,0,0) -> (1,2,1)` on its changed side. The two paths each admit **two independently checked commuting squares**, with new owner observations at both their middle scope and shared final scope.

The resulting **compositions** assign different final images to the **same** donor endpoints:

| Donor endpoint | Route 1 final image | Route 2 final image |
|---|---|---|
| old source `(1,0,0)` | `(1,0,0)` | `(0,1,2)` |
| old destination `(1,2,0)` | `(1,2,2)` | `(0,2,2)` |
| new source `(1,0,0)` | `(1,0,0)` | `(0,1,2)` |
| new destination `(1,2,1)` | `(1,2,2)` | `(0,2,1)` |

Each route separately gives `TWO_HOP_CHAIN_WITNESSED` with **6 paired states, 5 admitted edges**. Their route-independent composition hypothesis returns `ROUTE_COMPOSED_MAP_CONFLICT` with all four exact assignments and both still-audited route fingerprints; this **does not refute either separately witnessed route**, and no merged relation is published. A second fixture with the same middle laws but **different owner objects and registries** yields `ROUTES_AGREE_ON_SELECTED_EDGE`, which is not a general equivalence claim.

### Observation accounting

Base joins: donor `3+3`, each middle `4+4`, final `4+4` local old/new transition observations. After both routes: donor `3+3`, middle 1 `5+5`, middle 2 `5+5`, final `6+6` — **eight new owner observations total** across constructing both route certificates, none needed to compare or revisit the finished routes. All base joins remain unchanged at their previously admitted edge counts.

If either path is revoked, its owner revision mutates, an observation is tampered, a route reference changes, or a claimed fingerprint is substituted, no route-independent result is admitted. The report identifies the particular failed route. The comparator re-audits **both** existing chains before and after assessing the composed maps; these are bounded zero-new-read replays. This is *responsive on invocation*, not autonomous background monitoring.

## Components and tests

New files are `ab_chatbot_two_route_comparison.py`, `test_ab_chatbot_two_route_comparison.py`, `finite_two_route_comparison.py`, `test_finite_two_route_comparison.py`, `run_two_route_comparison_demo.py`, this README, results JSON and regression JSON. The independent finite checker is an **all-laws-known oracle**, not a certification of HTTP local owner identities. Only the full integrated adapter can re-audit the preexisting pinned evidence.

To reproduce from the extracted archive directory:

```bash
python run_two_route_comparison_demo.py
python -m unittest -q test_ab_chatbot_two_route_comparison.TwoRouteTests
python -m unittest -q test_finite_two_route_comparison.FiniteRouteTests
```

**113 completed tests passed** across ten named suites, comprising **12 new integration**, **7 independent finite**, **14 prior two-hop**, **12 prior cross-scope**, **11 prior joint task**, **10 prior cross-pin join**, **13 prior same-pin transfer**, **10 prior cross-pin comparison**, **10 prior exact owner**, and **14 prior provenance**. All ten named suites completed in separate bounded test runs or explicitly selected completed groups. Early invocations specifying nonexistent test class names were not counted; those regressions were rerun successfully. Full historical suite and GitHub CI are not asserted.

## Provenance and boundaries

The ZIP adds eight files while preserving every one of the 201 preceding files byte-for-byte. This creates a *comparison of composed mappings* rather than a new transfer. Fingerprints are in-process relation handles, **not remote identity credentials**. The composed maps are only declared hypotheses until their respective selected transitions have been checked. The final scope can support two different independently witnessed edges without proving their external donor-state images must be equal. No global, physical, or open-ended A/B theorem is claimed.

**Next warranted movement:** Let the harness be invoked by an actual changed owner source/version and show how **which route comparisons survive** updates without automatically expanding any witness. This is a proposal for a later step, not implemented here.

The unrelated Continuity project pointer `state/current.json` is unchanged. No GitHub repository mutation is included in this release.
