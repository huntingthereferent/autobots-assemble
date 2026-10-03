# Scope

This repository tracks bounded work as stable job records.

## Preferred referent

Each job records a `preferred_referent` marked with `📍`. It identifies the problem or specification that remains primary for that job. Implementation details and older experiments are supporting evidence unless the current job record explicitly moves the scope.

## Ordering

1. Current preferred referent
2. Immediate next movement
3. Supporting evidence
4. Frozen or older evidence

## Categories

- `external_bounded_problem` — externally supplied work with a finite specification and acceptance condition.
- `general_problem_solving` — bounded problems without a specialized domain category.
- `sports_betting` — sports-data output experiments.
- `ab_research` — work specifically about A/B mathematics, provenance, implementation, or tests.

The canonical operational state is stored in `jobs/JOB-###_*/job.json`.
