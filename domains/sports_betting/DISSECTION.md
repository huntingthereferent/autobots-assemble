# Dissection — Sports Betting

## Source referent

Frozen v0.17 evidence contained `sports_loss_policy.py` plus a `sports_betting` output mode in `output_views.py`.

The old policy correctly sat one layer above the generic relation network: it read a frozen snapshot and derived a decision without changing the network until `record_decision(...)` was explicitly called.

## 1. Break apart

### A. Source acquisition

Needed inputs originate outside the domain policy:

- market odds / price;
- estimated probability;
- uncertainty around the estimate;
- bankroll state;
- realized P/L;
- open exposure;
- explicit risk policy.

This belongs to `research.source`, `core.evidence`, and `core.provenance`, not to sports-specific source-search code.

### B. Domain relation vocabulary

The old code expected generic relations such as:

- candidate → `decimal_odds` → number
- candidate → `estimated_probability` → number
- candidate → `uncertainty` → number
- candidate → `exposure_group` → group
- candidate → `stake` → number
- candidate → `bet_status` → open/settled/closed
- bankroll → `current` → number
- bankroll → `protected_floor` → number
- bankroll → `day_start` → number
- bankroll → `realized_day_pnl` → number
- policy → cap fractions

This remains a good pattern: domain meaning lives in relation vocabulary, not a sports-specific network object.

### C. Derived calculations

The old code computed:

```text
p_low = clamp(estimated_probability - uncertainty, 0, 1)

safe_EV = p_low * decimal_odds - 1

full_Kelly = ((decimal_odds - 1) * p_low - (1 - p_low))
             / (decimal_odds - 1)

quarter_Kelly = max(0, full_Kelly * 0.25)
```

Then candidate stake was bounded by:

- quarter-Kelly amount;
- per-bet cap;
- bankroll protected floor;
- exposure-group remaining capacity;
- daily-loss stop.

Those are genuine domain calculations and belong in the sports-betting decision protocol.

### D. Decision

The old result was:

- `BET`
- `PASS`

with stake, conservative EV, and a reason.

Under the current outer contract, the richer result space is:

- `MOVE` — evidence supports a concrete decision;
- `WALL` — a required state/evidence input is missing;
- `UNKNOWN` — available evidence cannot resolve the decision;
- `PARTIAL` — some calculation is supported but the full decision boundary is not.

The action inside a successful movement may still be `BET` or `PASS`.

### E. State mutation

`record_decision(...)` was not presentation. It created new relations:

- decision
- decision_reason
- safe_ev
- stake
- bet_status

That is generic `core.movement` + provenance.

### F. Output lens

The v0.17 `sports_betting` output mode was read-only, but it called the domain decision function while rendering.

That is acceptable only if the boundary is explicit:

```text
frozen snapshot
→ pure domain assessment
→ read-only render
```

The lens does not own the decision rules and never records the decision.

## 2. What the old implementation got right

- generic relation network stayed domain-neutral;
- domain policy read a frozen snapshot;
- decisions became movement only through an explicit recording function;
- exposure was grouped instead of treated as isolated bets;
- risk boundaries limited raw Kelly sizing;
- output rendering itself did not mutate the network.

## 3. What the old implementation collapsed or assumed

### Missing uncertainty defaulted to zero

This is the biggest evidence-contract problem.

```python
if u is None:
    u = 0.0
```

Missing uncertainty is **not** evidence of zero uncertainty. Under the current contract this should normally be `WALL` or `UNKNOWN`, unless an explicit policy supplies a documented fallback.

### Missing realized P/L defaulted to zero

That can erase an unknown daily-loss state. If the daily loss boundary matters, the state must be known or explicitly waived by policy.

### Missing risk policy silently created defaults

The code defaulted to:

- per-bet cap: 0.5% bankroll
- group cap: 1%
- daily loss cap: 1.5%

Conservative defaults can be useful, but they must be an explicit named policy profile with provenance, not invisible substitutions.

### Missing protected floor defaulted to zero

Again, this is a policy choice, not neutral absence.

### Market identity/freshness was under-specified

`decimal_odds` alone does not preserve:

- sportsbook/source;
- event/market identity;
- selection;
- observed timestamp freshness;
- market status;
- price availability at execution.

A stale price can make a mathematically valid EV calculation operationally invalid.

### Probability provenance/calibration was under-specified

`estimated_probability` did not say:

- model/source;
- model version;
- sample horizon;
- calibration evidence;
- applicable market;
- update time.

### Correlation was only coarse

`exposure_group` is useful, but correlation/conditional dependence was manually represented and not independently witnessed.

### Settlement/learning was missing

The layer did not yet separate:

- open;
- settled;
- void/push;
- realized P/L update;
- model calibration;
- closing-line comparison;
- post-result evidence.

Those are future domain movements, not part of the initial decision protocol.

## 4. Reconstruct

Sports betting should now be treated as a composed domain:

```text
research.source
  finds/refreshes external evidence
        +
core.evidence
  admits or rejects it
        +
domain.sports-betting.decision
  applies domain witnesses/calculations
        +
core.movement
  records an accepted action/result
        +
output.lens
  renders the frozen state
```

The domain-specific core is therefore much smaller than “sports betting” as a whole.

## 5. Current unresolved frontier

Not yet reconstructed:

- settlement protocol;
- odds/source freshness rule;
- probability-model provenance schema;
- correlation/exposure model beyond explicit groups;
- multi-book price selection;
- market/selection canonical identity;
- void/push/cancel handling;
- learning/calibration loop.

Those remain explicit future referents rather than being invented during this dissection.
