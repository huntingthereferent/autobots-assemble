# OSC 2015 — significance-flag aggregate reanalysis

This is a separate, bounded scientific reanalysis lane. The named study is [Open Science Collaboration, *Estimating the reproducibility of psychological science* (2015)](https://doi.org/10.1126/science.aac4716).

## What was calculated

Using the [Center for Open Science RPP analysis export](https://github.com/CenterForOpenScience/rpp) pinned to commit a7c5b87f15f60178e6f5d25f983217d39f5ac654, path `data_allformats/RPPdataConverted.csv`, Git blob SHA-1 `6c8ce0b93b9a83ac42669745bd1054da7c22a687`, the independent count reads the `T.sign.O.131` and `T.sign.R.132` columns.

Only records where *both flags* are precisely 0 or 1 participate in the paired comparison. Every other row is excluded and counted. The original project analysis uses pairwise selection for its reported significance comparison ([masterscript.R](https://github.com/CenterForOpenScience/rpp/blob/a7c5b87f15f60178e6f5d25f983217d39f5ac654/masterscript.R)). The export contains **168 data rows**; **100** contain both selected binary flags.

| Observed count from pinned public export | Count |
|---|---:|
| Paired records | 100 |
| Significant original | 97 |
| Significant replication | 36 |
| Both significant | 35 |
| Original only | 62 |
| Replication only | 1 |
| Neither | 2 |
| Unpaired/excluded | 68 |

The published paper reports 97% significance for original effects and 36% for replication effects. The upstream masterscript also explicitly prints 35/97 for jointly significant results conditional on significant originals.

## Evidence and limits

- This is a reproducible *descriptive aggregation of precomputed binary significance flags*. It does **not** rerun participants or calculate their p-values from raw observations.
- We check the exact Git blob SHA-1 and byte length before any assertion. A newer OSF file, other Git commit or altered CSV is not silently admitted.
- Upstream documentation cautions that source data used in the original publication and files subsequently hosted on OSF may differ. Exact historical equivalence is **not established** by a matching aggregate count.
- The upstream repository does not expose a recognized license for unrestricted reuse in repository metadata. This work fetches a public export transiently, processes it in memory, and stores **only derived counts, evidence hashes, observation timestamps and limitations**; it does not redistribute its rows.
- GitHub Actions runs a fixed-source fetch using standard-library Python, with a byte cap. Unit tests use synthetic records only and must not be mistaken for reproducing any study.
- Follow-up work can reconstruct the statistical transformations upstream of these flags and compare alternate public data versions. Any difference should become a counterexample/branch, not a patched number.

## Run and inspect

Offline contract (no source fetch):

    python -m unittest discover -s research/reanalysis/osc_2015 -p 'test_*.py' -v
    python research/reanalysis/osc_2015/aggregate.py

Explicitly fetch the pinned public source and write derived-only witness:

    python research/reanalysis/osc_2015/aggregate.py --live --output osc-2015-derived-only.json

No source dataset, experimental subject record, or original full-text article is committed to this lane.

See [original source](https://github.com/CenterForOpenScience/rpp/tree/a7c5b87f15f60178e6f5d25f983217d39f5ac654), [the study publication](https://doi.org/10.1126/science.aac4716), and the dedicated GitHub Actions workflow for independent test evidence.
