# Sports Betting Domain

This directory is the reconstructed result of applying `ANALYZE.DISSECT` to the old v0.17 sports-betting layer.

The old code mixed several concerns under one familiar label:

```text
sports betting
├─ source acquisition
├─ evidence normalization
├─ probability / uncertainty
├─ price
├─ expected value
├─ bankroll state
├─ risk policy
├─ exposure aggregation
├─ bet/pass decision
├─ state mutation
└─ output presentation
```

Those are now separated and reconnected.

## Reconstructed routing

```text
external source / odds / model / bankroll
        ↓
research.source
        ↓
core.evidence + core.provenance
        ↓
sports-betting relation contract
        ↓
domain.sports-betting.decision
        ↓
MOVE / WALL / UNKNOWN / PARTIAL
        ↓
core.movement + core.provenance
        ↓
frozen snapshot
        ↓
output lens
```

The sports-betting domain therefore does **not** own source search, generic evidence rules, network movement, or rendering. It owns the domain-specific decision witnesses and calculations.

See [DISSECTION.md](DISSECTION.md), [RELATIONS.md](RELATIONS.md), and [MIGRATION.md](MIGRATION.md).
