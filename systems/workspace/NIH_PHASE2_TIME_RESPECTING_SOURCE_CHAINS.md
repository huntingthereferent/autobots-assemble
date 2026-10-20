# NIH Phase 2 — first generic time-respecting A/B relationship movement

**Built to address the actual observed Phase 2 failures, not re-run Phase 1 source intake.**

The independently verified [PR #269](https://github.com/huntingthereferent/autobots-assemble/pull/269) executed the **unchanged original W13** emitted temporal Python against 13 predeclared fictional biomedical practice questions:

- **8/13** native correct; original static snapshot **6/13**.
- Longitudinal relationship inference **0/3**.
- RDF/OWL property-chain inference **0/1**.
- Retraction/supersession handling fails: a corrected publication's earlier claim remains visible.

The first missing operation is not a larger grid, another renderer, or more laws; it is a bounded **relationship across events**.

## The general finite operation

`ab_time_respecting_source_chain.observe(observations, stages, known_at, target_at, subject)` accepts:

- **Declared source observations**, retaining exact source identifiers and `source_ref`, `subject`, `predicate`, `object`, event start/end dates and knowledge-availability date.
- **An explicit ordered pattern**, each stage defined by the researcher as a predicate/object pair. The engine **does not generate, rename or assume** what those relationships mean.
- **Independent clocks**: `known_at` gates whether an original event source was available; `target_at` bounds the last allowable event **start**, not whether all earlier events remain currently valid. This matters: an earlier therapy can have ended while remaining part of a longitudinal path.
- **An exact subject join** across every path, with strictly increasing event starts. Different subjects, same-day ties, missing events, late-known evidence and backdated queries do **not** produce valid paths.
- **Exhaustive finite witness results**, including ordered original evidence IDs, event dates, source-known dates and source references. A negative means no path in the bounded declared source set, **not** no possible clinical path in reality.
- **An explicit capacity limit**: at most 64 source rows, 2–5 stages and 128 reported paths. Overflow fails closed instead of being scored as absence.

This **does not** claim that temporal succession causes a treatment switch or a clinical effect. It proves only the supplied source sequence fits the explicitly requested event relationship.

## Honest original benchmark comparison

The separate `nih_phase2_time_respecting_chain_trial` re-executes [PR #269's original direct trial](nih_phase2_direct_reproduction.py), invoking the unchanged emitted Python source on the same 13 inputs. The new operation answers **only** the three previously unsupported longitudinal questions, while preserving all original fact, retraction and RDF failures.

| Capability | Unchanged W13 | W13 plus source-chain operation |
| --- | ---: | ---: |
| Temporal source fact questions (nine) | 8/9 | 8/9 |
| Longitudinal path questions (three) | 0/3 | *evaluated live* |
| RDF entailment (one) | 0/1 | 0/1 |
| **Total (13 predeclared practice questions)** | **8/13** | *evaluated live* |

A later native PASS confirms the new **separately implemented A/B capability**, not an in-place update to the original W13 emitted Python or a new native journal checkpoint.

## Generalization and independent verification

The code also generates **160 deterministic but unseen** example cases with:

- Independently varying event start days, information-availability days, target days, and input order.
- Both synthetic biomedical-care and public-health-surveillance relationship patterns, including distinct subjects and deliberately misleading decoy paths.
- Independently implemented **Cartesian-product enumeration** as an oracle; it checks **every exact observed path**, not just expected positive/negative percentages.

The new suite separately covers equal-time ties, reversed events, cross-subject splicing, evidence arriving after query time, earlier event expiration, over-capacity witness enumeration, bad source dates and altered record provenance. Both positive and negative generated cases must occur.

This is meaningful *finite temporal source relationship construction* but remains a practice-world test, not original NIH shared clinical data, official Phase 2 completion, an OWL reasoner, or medically validated causal inference.

## Next actual Phase 2 movements

Continue from **measured failures**, without losing this source path:

1. Source-revision/supersession, keeping both old/new history and deciding which claim remains supported *as of known time* rather than deleting history.
2. An actual RDF temporal property-chain operator with independent entailment and OWL inconsistency measurements, not merely graph formatting.
3. More heterogeneous domains, larger observed source graphs and a strong static reasoning baseline; then real source event provenance and external biomedical benchmarks where available.

The original W13 twelve-job journal, emitted temporal Python, active world trials, World48 mathematical laws and A/B license remain unchanged.

## Reproduce

```sh
python -m pip install 'rdflib>=7,<8'
python -m unittest -v network.tests.test_nih_phase2_direct_reproduction \
    network.tests.test_nih_phase2_time_respecting_chain_trial
python -m systems.workspace.nih_phase2_time_respecting_chain_trial \
    --output-dir /tmp/nih-p2-chain-trial
```

The focused GitHub Action must finish before recording the output scores in this document. It retains original fact-case results, path witnesses and 160 independent unseen-case comparisons.
