# Sports Betting Relation Contract

These are domain relations carried by the generic network. They do not create a sports-specific object type.

## Candidate identity

A candidate/selection should be anchored to a recoverable market identity before a live decision is admitted.

Recommended relations:

```text
candidate --event_id--> ...
candidate --market_id--> ...
candidate --selection--> ...
candidate --sportsbook--> ...
candidate --price_observed_at--> ...
candidate --market_status--> open
```

## Price evidence

```text
candidate --decimal_odds--> O
```

Required for decision:

- `O > 1`
- source/provenance known
- price freshness adequate for the current action
- market still actionable

## Probability evidence

```text
candidate --estimated_probability--> p
candidate --uncertainty--> u
candidate --probability_source--> ...
candidate --probability_version--> ...
candidate --probability_observed_at--> ...
```

Decision calculation uses:

```text
p_low = clamp(p - u, 0, 1)
```

Absence of `u` is not equivalent to `u = 0`.

## Bankroll state

```text
bankroll --current--> ...
bankroll --protected_floor--> ...
bankroll --day_start--> ...
bankroll --realized_day_pnl--> ...
```

A decision that enforces a daily-loss boundary requires the corresponding daily state to be known.

## Risk policy

Risk constraints should be explicit relations or a named policy profile:

```text
policy --per_bet_cap_fraction--> ...
policy --group_cap_fraction--> ...
policy --daily_loss_cap_fraction--> ...
policy --kelly_fraction--> ...
```

Do not silently infer missing policy values.

## Exposure

```text
candidate --exposure_group--> ...
candidate --stake--> ...
candidate --bet_status--> open
```

The group is a domain-level approximation of shared exposure. It is not proof of statistical independence between different groups.

## Derived evidence

Derived values may be recorded with provenance:

```text
candidate --pessimistic_probability--> ...
candidate --safe_ev--> ...
candidate --kelly_fraction--> ...
candidate --admissible_stake--> ...
```

Derived relations must remain traceable to the price, probability, bankroll, policy, and exposure evidence used.

## Decision movement

```text
candidate --decision--> BET | PASS
candidate --decision_reason--> ...
candidate --stake--> ...
candidate --bet_status--> open
```

A rendered recommendation does not create these relations. Only an explicit accepted/recorded movement does.
