# NIH Phase 2 — synthetic source-variation experiment

Status: separately executed experiment; not an additional native checkpoint.

## Question

Does the executable's valid-time / knowledge-time selection remain consistent
with an independent observation-level oracle when the **source observations**
change, rather than only varying the query dates?

## Source and procedure

The original twelve-job ProcessWorkstation supplies its verified
`NIH-P2-BENCHMARK` ancestor, original emitted `temporal_query.py`, source
observation set, and browser history digest. The experiment retains that
ancestor, makes recorded *counterfactual synthetic datasets*, and queries
each one at the same 81 known-time / valid-time combinations.

For every case, it executes the emitted Python program (not an in-memory
replacement), independently computes the observation-level oracle, and compares
the source-owned benchmark worker's exact temporal and static ID lists against
those independently replayed results. It keeps the original native journal
unchanged and saves each modified dataset, case, source hashes, and result.

Variations: unchanged source; later known-at; earlier known-at; later validity
start; earlier validity end; later validity end; extra delayed record; extra
conflicting record; source-reference replacement. The baseline has two
observations; two variations have three.

The static comparator selects observations valid at target time without
checking when they became known. This is a *particular* synthetic static
snapshot baseline, not every static knowledge graph system.

## Observed results

Independent GitHub CI execution:
[workflow 39087621807](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39087621807)
([evidence artifact 12120989688](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39087621807/artifacts/12120989688)).

| Source condition | Queries | Static future-leakage cases | Static future-evidence occurrences |
| --- | ---: | ---: | ---: |
| Original | 81 | 31 | 46 |
| Later knowledge | 81 | 41 | 56 |
| Earlier knowledge | 81 | 27 | 32 |
| Later valid start | 81 | 29 | 41 |
| Shorter valid end | 81 | 25 | 31 |
| Longer valid end | 81 | 31 | 46 |
| Additional delayed record | 81 | 36 | 76 |
| Additional conflict | 81 | 31 | 67 |
| Source reference change | 81 | 31 | 46 |

**729** actual emitted-Python executions (9 × 81) agreed with the
independent oracle and the source benchmark worker. Four focused tests
passed, including negative controls for changed original parent data,
replaced executable source, and replaced worker source.

The leakage counts describe the static comparator only. The temporal
implementation's observation selection agreed with the independently
computed as-known-at oracle in all 729 runs. The original 72-query
benchmark's 22 leakage cases and this experiment's 31 baseline leakage
cases use **different grids**; they are not contradictory estimates on
the same denominator.

## Limits

The variants deliberately share a small original synthetic source. This
does not measure performance, scale, clinical correctness, general
biomedical transfer, or independent datasets from unrelated systems.
It is not an NIH submission, NIH award, official NIH scientific
benchmark, or evidence involving real patients. No new research
checkpoint is marked witnessed, and no thirteenth native job is added.

## Reproduce

Run this from the repository root after installing the original
workstation dependencies and Playwright Chromium:

```bash
python -m unittest -v network.tests.test_nih_dataset_sensitivity
python -m systems.workspace.nih_dataset_sensitivity \
  --data-dir /tmp/nih-original-workstation \
  --output-dir /tmp/nih-source-variations
```

The dedicated GitHub workflow stores the original twelve-job journal,
case-level query results, variation datasets, and source digests. A later
run's exact results must be taken from its own artifact rather than
being silently substituted for the execution linked above.
