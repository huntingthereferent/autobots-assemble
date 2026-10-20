# Public trace sources and world Internet map

[Source registry](registry.json) · [Map renderer](internet_map.py) · [Internet world map](internet-map.svg) · [Original world observations](../world-continuity/README.md)

The catalog contains **60 candidate trace systems in ten categories**: solar activity, objects in space, earthquakes, fires, weather, oceans, transport, infrastructure, Internet activity and digital updates. Each entry names the original provider, its access requirements, observable type, identity and whether an adapter actually exists. **A catalog entry does not mean that feed is running.**

## The world map

The map combines source-owned, distinctly labeled measurements:

**Geography** comes from the public-domain Natural Earth 110m countries, pinned to [ca96624](https://github.com/nvkelso/natural-earth-vector/tree/ca96624a56bd078437bca8184e78163e5039ad19).

**Measurement locations** come from the public RIPE Atlas API. A bounded *first page* of up to 300 public connected probes is plotted as violet points. This is not a representative global sample, a network traffic measurement, or a claim of actual traffic between points.

**HTTP request traffic by country** comes from Cloudflare Radar, but only when its documented free read-only API token is installed. The country fill then shows measured percentages of HTTP requests in Cloudflare's observed traffic, with its actual measurement time range. Missing countries are **no data**, not zero. This never purports to show all packets worldwide.

### Run

From the repository root:

```sh
python -m unittest -v views.traces.test_internet_map
python -m views.traces.internet_map --refresh
```

The renderer contacts the allowlisted RIPE and Natural Earth sources. The optional Cloudflare layer can be activated by adding an Actions repository secret named **CLOUDFLARE_RADAR_TOKEN**, using a free Radar Read token following [Cloudflare's instructions](https://developers.cloudflare.com/radar/get-started/first-request/). Tokens must not appear in generated source files.

The GitHub workflow refreshes the source snapshot and SVG about every six hours on main, and supports manual runs. An unconfigured traffic credential produces an explicitly empty traffic layer (not a fake gradient). Failure of mandatory geography or probe reads fails rather than fabricating a previous time stamp.

All future trace adapters need native source identities, units, observed vs model/forecast status, source time, collection time, geography accuracy, licensing, missing-data semantics and independently supported link rules. The view does not execute workers or claim universal A/B relationships.

## Trace to the observed focus (A/B precision)

[Native convergent-focus projection](convergence_focus.py) accepts **only directed relationships admitted by each domain's own verifier**. It traces all observed paths to their terminal referents. If every participant reaches one terminal, it reports `ONE_OBSERVED`. It reports `TWO_WITNESSED` **only if two terminals cover the observations and a separate source-owner verifier accepts an explicit reason for the split**. No source evidence, a third terminal, cycles without exits, or a partial dataset remain `OPEN`.

This is neither a similarity-ranking model nor a rule that any real-world domain must have a leader. Stocks, gambling, solar observations and networks must each supply a meaningful native definition of their directed relation before applying it. The [finite A/B confluence renderer](../motion/convergence.py) demonstrates a narrower, independently checked mathematical path meeting; that is not yet a global one-followed-by-everything result.

Reproduce focus tests: `python -m unittest -v views.traces.test_convergence_focus`.

## GitHub execution revisions on the Work page

The [Work page](../../docs/live/work.html) reads a selected GitHub Actions run's exact
`head_sha` and the changed-file list of that Git commit. It compares exact filenames
against currently published structured research paths and movement-heading locators.
A match establishes only **source-path overlap at an observed revision**. The panel
links to the immutable commit and the file at that SHA. The GitHub changed-file list
may be paginated; the interface labels its first-page limit.

The existing GitHub run details separately report workflow jobs and steps.
Neither a matching path nor a successful workflow is a verified native workstation
movement, and there is no inferred cause/effect relation between a source heading
and the workflow. Native `RuntimeJournal` / `HandoffRuntime` receipts are not
automatically public. A future native receipt link requires an explicitly admitted,
redacted publication source with exact handoff/event identity and an independent
native verifier; never backfill the link from names, nearby timestamps or folder
similarity. No private journal is read or uploaded by this page.

Reproduce the exact-match and negative-link checks:

```sh
python -m unittest -v network.tests.test_work_activity_ui
```

## Full GitHub Actions execution history

The public [Workstation](../../docs/live/work.html) no longer relies on visitors
clicking through batches of 100 GitHub runs. The authenticated, read-only source
adapter in [workflow_history.py](workflow_history.py) retrieves **all currently
accessible repository Actions run pages**, independently preserving their GitHub
identities, commit SHA, status, and original URL. The
[scheduled publication workflow](../../.github/workflows/workstation-run-index.yml)
runs every three hours, and also after the index program or Work page changes. It
publishes [workflow-runs-index.json](workflow-runs-index.json) to `main` only
when the API source reported count agrees with the individually recorded IDs.
A partial fetch fails publication rather than labeling an incomplete sample
complete.

The browser then loads the published complete index in one download while
showing only the first 20 rows initially for responsiveness. Its existing
two-minute **GitHub API check of the latest 100** updates recent statuses and
takes precedence over older snapshot statuses. Search operates over the
retrieved archive, not just the displayed rows. An unavailable/stale index
is explicitly labeled; the fallback older-page control stays available.
Archival freshness is the `collected_at` time, not a claim that every historical
job is currently running. A deleted, inaccessible, or missing workflow run
cannot be recreated from this index. No worker journals or secrets are exposed.

Reproduce the archive safeguards:

```sh
python -m unittest -v network.tests.test_workflow_history network.tests.test_work_activity_ui
```

