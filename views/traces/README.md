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