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

## External movement and observed return

[GitHub fork/return witness](fork_return.py) is a separate measurable experiment derived from **public GitHub repository provenance**, not speculation about human movement.

**Observable departure:** another account creates a public fork of `huntingthereferent/autobots-assemble` or `huntingthereferent/huntingthereferent`. This is *a copy*, not evidence that someone is using, following or understanding A/B.

**Observable return:** an exact pull request with a GitHub-verified head repository ID matching that same fork is **merged back into the original repository**. Only then does the harness record a return and measure seconds from the fork's recorded creation to its earliest qualifying upstream merge.

**Unreturned:** `OPEN` with null elapsed time. Never zero, infinite, or proof of no future return. A self-authored branch/PR is not external. Deleted forks, private copies, independent reimplementations, and external citations might be invisible. API reads are bounded at 300 forks and 300 PRs per repository; the output explicitly reports when a sample might be incomplete.

The [latest receipt](return-latest.json) and [human-readable report](RETURN_LATEST.md) come from the actual GitHub API, refreshed daily and on manual dispatch. No synthetic test fixture is written to the published data; insufficient or failed API evidence aborts a refresh rather than manufacturing a connection.

Local checks: `python -m unittest -v views.traces.test_fork_return`. Actual collection: `python -m views.traces.fork_return --refresh` (may use `GITHUB_TOKEN` in the environment). This is **only one measurable GitHub boundary** for the broader A/B tracing experiment, not a measure of James personally or of universal convergence.
