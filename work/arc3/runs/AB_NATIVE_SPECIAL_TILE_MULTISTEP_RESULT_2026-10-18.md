# A/B native special tile: multistep result and invalid clock preregistration

**Scientific verification status: MIXED / failed overall.** This is an audit of the original result, not a retroactive revision of its frozen predictions. Original experiment remains red.

[Native GitHub run 39123519894](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39123519894) tested 36 independently reset real ARC-AGI-3 LS20 trajectories, 12 frozen 2–6-action suffixes after each of three source-verified eight-action histories, **420 actual native actions**, all completed. [Frozen source JSON, native complete 64x64 raw pixels, and original independent verdict](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39123519894/artifacts/12134968679).

### H1 — PASS: complete native visible-frame congruence

For every one of the 12 suffix words, the three source-distinct histories reached identical complete native raw frames at EACH appended action, not just at the final glyph position. **132/132 pairwise exact raw-frame comparisons matched.** The original shared frame at depth 8 was independently reproduced before every suffix.

### H2 — INVALID FORECAST, not a new scientific counterexample

The frozen hypothesis incorrectly extrapolated an ordinary trace clock formula **84-2t** at native depths 9..14. This disagrees with independently available raw source observations **even before these new trials**. An original special-tile entry at step 8 had already caused a trace-mask plateau: depth 7 = 70 trace pixels; depth 8 = 70 again; depth 9 = 68. Other eight-action trajectories without the special-tile entry had depth 8 = 68. The source verification step audited pixel hashes but failed to check the proposed clock formula against all relevant original source frames. This was an experimental-design oversight.

The original frozen clock predictions were false **132/132**, but these mismatches **must not be called 132 newly discovered scientific counterexamples**. Their incorrect one-step phase was already discernible from the source.

Independent raw reanalysis shows the actual native special-tile histories:
- At native depths 7,8,9,10,11,12,13,14 the observed trace-pixel counts were respectively **70,70,68,66,64,62,60,58** whenever that depth was present.
- For depths 9–14 specifically, the trace occupies native rows 61–62 and columns **(12+t) through 54 inclusive**, giving **86-2t** cells. This is a *retrospectively observed* pattern in this batch, not a validated preregistered holdout claim.
- Previous observations that did not enter this special tile at depth 8 obeyed 84-2t through depth 8. Whether the one-step plateau depends on special-tile entry, action history or other events remains **open**.

### H3 — PASS: return to same glyph coordinate is not the same full visible state

**12/12** two-action leave-and-return paths (suffixes 12,21,34,43 independently applied after each of the three source histories) returned the native glyph to its original (row30,col19), while the complete raw frame had changed due to elapsed time. This independently distinguishes the same observed glyph position from the same full native visible state.

### Source files and independently computed SHA256s

- Frozen original hypothesis: 200d14e7dbe2ea0e10fb0838595f61d823a60a8c91fabea6d25917e17712b16f
- Actual native manifest: 712d539c6d18ac641b2a2e0f6ecbb31f35c5d1e4ad10125de919884e5355c699
- Original native frame NPZ: 88fd9bc9857cfa2fa8ba5febf1327d772f009ed7aac0c2beb4e161722b087f25
- Original independent verdict: c09c14d52e8d30926f67dfb8018c2b92508c7fae560506e7fb7d9bc95b0035b0

**Scope:** Real LS20 complete native pixels only; no hidden-state identity, general visible-state Markov proof, F3 mapping or ARC solve. The original earlier passability classifier remains separately falsified.

**Next valid test:** Preregister new equal-length source-verified routes that enter the same special mixed-color tile at different action depths (e.g. after 2, 4 or 6 independent source-backed root-return loops) plus paired routes that do NOT enter it. Test whether a trace pause follows the entry event instead of being tied to a fixed global step. No clock formula from this audit is allowed to masquerade as a preexisting hypothesis.
