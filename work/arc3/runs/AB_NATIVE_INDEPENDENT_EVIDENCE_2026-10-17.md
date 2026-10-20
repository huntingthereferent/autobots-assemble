# Independent native observation — A/B evidence boundary (LS20)

Research begun October 17, 2026 CDT; independently collected/verified UTC October 18. This file contains **verified observations**, not a synthetic F3 demonstration or a claim about the hidden state.

## Reproducible sources

- [New independent A/B native evidence CI run 39091972954](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39091972954), **SUCCESS**.
- [Both raw original/new 64x64 frame archives, JSON and recomputed hashes](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39091972954/artifacts/12122494867), retention 14 days.
- Historical native source: [run 39088689691](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39088689691); source archive artifact 12121333239.
- Source computation: [native_suffix_probe.py](../native_suffix_probe.py), [native_suffix_extension.py](../native_suffix_extension.py), [native_observation_bridge.py](../native_observation_bridge.py).
- Actual native root whole-frame blake2b/16 hash: 88831de43456eb039e44d1fc7985c636 in BOTH independent datasets. Every stored raw native frame, not just final frames, was rehashed and compared to its original snapshot metadata.
- Historic JSON sha256: 51418edb3f403ce5696cd481cd25bbb593660bbd9f384212a468f5934dbac310
- Historic NPZ sha256: e7036323f8febfeca5ccd453c83e9a9e44c21824f975ee3c9b6b2d8874966fa1
- New JSON sha256: b3a1c793e3d3a41ff9660e4b1cd9e1ed2919767a8b8d47815c7704463fdbdcc6
- New NPZ sha256: 033c574999a656ebf57ff628f03be47bcccf16e85705eabe4867f489a7e6bf7f

## The actual native action-word observations

An action word is a sequence of native numeric ARC control IDs, not a field element or a claimed F3 generator. Each left/right word starts with a fresh independently reset official LS20 native environment.

| Prefix pair | Prefix whole frames | Historical suffixes 1,2,3,4,12,21 | New predeclared suffixes 11,22,31,42 |
| --- | --- | --- | --- |
| 34 / 43 | Equal | Equal, equal, equal, equal, equal, equal | Equal, equal, equal, equal |
| 23 / 32 | Equal | Equal, equal, equal, equal, equal, equal | Equal, equal, equal, equal |
| 12 / 21 | Distinct | Distinct, **equal**, distinct, distinct, distinct, **equal** | Distinct, **equal**, distinct, **equal** |

The new suffixes were selected and committed in source **before** their native execution. Under those suffixes, native 12 and 21 trajectories visibly converge after **22 and 42** but remain distinct after **11 and 31**.

- Historical run: 18 paired comparisons / 36 reset trajectories / 120 native actions, 12/12 equal-prefix suffix results still equal, 2/6 unequal-prefix suffix results converge.
- New run: 12 paired comparisons / 24 reset trajectories / 96 native actions, 8/8 equal-prefix suffix results still equal, 2/4 unequal-prefix suffix results converge.
- Total cross-source: 30 paired comparisons, 60 separately reset trajectories, **216 actual native actions**, with no reported interrupted action sequence or changed native root in the admitted set.
- New native verification workflow also passed **18 Python tests**, including the original nine-law inverse and rooted 48-law inverse guards. Every original raw frame and new frame was independently verified byte-for-byte against its recorded hash. The audit would fail on missing NPZ sources, interrupted paths, altered equality classifications, nonmatching root hashes or a mismatch between snapshots and pixels.

## Exact mathematical interpretation

The nine original F3 mathematical worlds all require AB != BA at their rooted full mathematical states, and bijectivity preserves that distinction after any common A/B suffix. Under the **provisional and unproven** assignment native ACTION1=A and ACTION2=B, the native visible convergences after suffix 2, 21 and now 22 conflict with an **injective direct identification of visible frames with full F3 states**. The suffix 42 contains unmapped ACTION4 and is not a valid F3-generator comparison; it remains a native observation only.

No mapping of native hidden states to F3 has been established. Equal native visible frames do not prove identical hidden native states, and their full 64x64 pixel arrays must not be injected into the existing F3 inverse investigator or 48-law root/fixed-count investigator. In particular, the native visible relation after suffix 22 is **one new direct-visibility obstruction under a provisional mapping**, not a disproof of abstract F3 mathematics or a native ARC solve.

The durable Markdown record retains observed distinctions and source hashes past the ephemeral artifact window, but the original raw source files remain in the downloadable GitHub artifact until retention expiration. Refreshing the native measurement requires executing the original native-source scripts again; no observation has been fabricated to fill missing data.

**Next admissible work:** propose and test an explicit native observable relation/predictive factor (e.g. transported glyph position and progressing two-cell trace), with out-of-sample action-word consequences and a source-recorded falsification test. Do not posit three-cycle reduction or replace an observed relationship with an invented hidden-state explanation.
