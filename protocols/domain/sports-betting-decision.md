# Domain Protocol — Sports Betting Decision

## Identity

- **Protocol ID:** `domain.sports-betting.decision`
- **Layer:** domain
- **Purpose:** derive a conservative BET/PASS decision from supported price, probability, bankroll, risk-policy, and exposure evidence.

This protocol does not search for data, place a wager, mutate the network, or render output.

## Current referent

One concrete candidate/selection under one current market/price context.

## Input contract

Required evidence classes:

1. candidate/market identity;
2. current actionable price;
3. probability estimate;
4. uncertainty around the estimate;
5. bankroll state;
6. explicit risk policy;
7. current relevant exposure.

## Witness contract

### Price witness

- decimal odds are numeric and > 1;
- price source is identifiable;
- observation time/version is known;
- market is still actionable.

### Probability witness

- estimated probability is in [0,1];
- uncertainty is in [0,1];
- probability provenance/model/source is identifiable;
- evidence is applicable to the candidate/market.

### Bankroll witness

- current bankroll known;
- protected floor known;
- day-start bankroll known when daily-loss control is active;
- realized day P/L known when daily-loss control is active.

### Policy witness

Risk parameters are explicit, not silently defaulted:

- Kelly fraction;
- per-bet cap;
- group/exposure cap;
- daily-loss cap if used.

### Exposure witness

Open relevant exposure is recoverable from the current frozen snapshot.

## Calculation

```text
p_low = clamp(p - uncertainty, 0, 1)

safe_EV = p_low * decimal_odds - 1

b = decimal_odds - 1
full_Kelly = (b * p_low - (1 - p_low)) / b
fractional_Kelly = max(0, full_Kelly * policy.kelly_fraction)
```

Then bound stake by:

- fractional-Kelly amount;
- per-bet cap;
- protected-floor headroom;
- remaining exposure-group capacity;
- active daily-loss boundary.

## Result states

### MOVE

All required witnesses are supported.

The embedded domain action is one of:

- `BET` with admissible stake and reason;
- `PASS` with reason.

A PASS can therefore be a supported movement; it is not a failure.

### WALL

A required operational input is missing, inaccessible, stale, or unusable.

Examples:

- bankroll missing;
- uncertainty missing;
- market no longer actionable;
- required daily P/L state missing;
- risk policy absent.

### UNKNOWN

Evidence exists but does not resolve a required distinction, such as conflicting probability inputs without a supported correspondence rule.

### PARTIAL

Some domain calculations are supported but a full actionable decision is not.

## Output contract

Return:

- candidate identity;
- result state;
- embedded action if resolved;
- conservative probability;
- safe EV if resolved;
- admissible stake if resolved;
- witnesses used;
- evidence/provenance refs;
- wall/unknown details;
- next referent.

## Movement boundary

This protocol's output is **assessment**, not network mutation.

Recording a decision is a separate `core.movement` step.

## Output-lens boundary

A sports-betting lens may render the pure assessment over a frozen snapshot. Rendering must not record or place the decision.

## Closure

The resulting assessment can be re-entered under the same contract after price, probability, bankroll, policy, or exposure changes. No hidden evidence standard is introduced on the next pass.
