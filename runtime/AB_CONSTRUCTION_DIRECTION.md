# Inverse A/B construction direction (opt-in)

**Research stage:** executable adapter, not a newly autonomous agent.
**Parent evidence:** [October 8 ARC migration](../research/arc-agi3/README.md), especially
`AB_INVERTED_CONSTRUCTION_AGENT_TEST_REPORT_2026-10-08.md`.

## Why it exists

Forward A/B observes a referent under a witness contract and constructs
the coarsest available partition sufficient for its witnessed futures:

```
witnessed occurrences -> information_closure -> continuation categories
```

For tasks explicitly asking to **construct**, **synthesize**, **simulate**
or explore **alternatives**, the *same* agent may move in the other direction:

```
ABInformationState + exact witnessed occurrences + source locators
  -> inverse_fibers()
  -> generator(fiber)  # caller-specified, bounded proposals
  -> project_candidates()  # PROPOSED, never MOVE
  -> frame_for_candidate()  # existing ABFrame shape
  -> existing evaluator / native witness / A/B refinement
```

Nothing about an inverse-category fiber automatically constructs new
physical states, a game environment, or a fractal. It recovers source
alternatives relative to a particular tested continuation horizon.
A generator *proposes* novel structures and must not be passed off as
an inverse theorem or a native observation.

No new agent scheduler, separate mathematics, or automatic construction
after every ordinary A/B operation is introduced.

## Example (small nested-world thought experiment)

```python
from runtime.ab_information import ABOccurrence, information_closure
from runtime.ab_construction import (
    inverse_fibers, project_candidates, frame_for_candidate,
)

occurrences = (
    ABOccurrence.create(
        referent="maze-room", relations={"gate": 0}, continuation="blocked"
    ),
    ABOccurrence.create(
        referent="maze-room", relations={"gate": 1}, continuation="open"
    ),
)
state = information_closure(occurrences)

fibers = inverse_fibers(
    occurrences, state,
    source_locators=("experiment://room/blocked", "experiment://room/open"),
    witness_contract="one witnessed action at room gate",
    horizon=1,
)

proposals = project_candidates(
    fibers,
    lambda f: ({"kind": "nested-room", "from_class": f.category},),
    intent="construct",
    max_candidates=4,
)
frame = frame_for_candidate(proposals[0])  # ordinary ABFrame; still PROPOSED
```

The existing `EcosystemService` also exposes the same explicitly requested
operation without requiring direct imports of the mathematical adapter:

```python
# service is an existing EcosystemService instance.
frames = service.propose_ab_constructions(
    occurrences=occurrences,
    state=state,
    source_locators=("experiment://room/blocked", "experiment://room/open"),
    witness_contract="one witnessed action at room gate",
    horizon=1,
    generator=lambda fiber: ({"kind": "nested-room", "from_class": fiber.category},),
    intent="construct",
    max_candidates=4,
)
```

These returned `ABFrame` objects are for subsequent A/B evaluation. This
service entry is read-only: it creates no task, agent lineage, evidence record,
or native movement by itself. It is a Python runtime entry, not an HTTP endpoint.

The source locators are supplied by the caller, not verified by the
inverse operation. The strings in this example are illustrative; they
must not be claimed as real measurements.

## Mathematical composition gate

For an action-labelled child transition `s --a--> s'` and a proposed
parent model with projection `q` and action translator `alpha`:

```
q(s') ?= T_parent(q(s), alpha(a))
```

`check_composition()` returns:

- `MODEL_COMMUTES` if the structural equation holds.
- `MODEL_SPLIT` when the parent abstraction loses a distinction.
- `UNKNOWN` when the source locator or model relation is missing.

These are **model test outcomes**, not runtime A/B statuses.
A model match cannot be promoted to `MOVE` without the native
observation contract being satisfied by the existing evaluator.

Nested-world example: four states consisting of room 0 and two gate
bits have two one-step future classes but three two-step future classes.
If the world projection only exposes room number, the second-step gate
influence is lost. The correct response is to split the category or
add a justified parent relation, not to pretend the first horizon
was universally sufficient.

## Boundaries

1. `runtime.ab_information`, `runtime.ab_loop` and `AgentLineage` are unchanged.
2. Every candidate retains the source category, source indices,
   declared source locators, witness contract, and tested horizon.
3. Generator output is always `PROPOSED`; it carries no `EvidenceRecord`.
4. Candidate enumeration is bounded by both size and iteration attempts.
5. An absent actual witness stays `UNKNOWN` or `READY` in the ordinary
   agent workflow; invalid predictions remain `PARTIAL`.
6. `check_composition` is *structural*; the caller is responsible for
   independent native before/after testimony and action identity.
7. Source locators are not independently validated by this pure module.
8. Distinct source histories need not produce distinct native states.
9. Finite ARC phase-equivalence data cannot prove an infinite fractal
   or a universal world generator.

## Verification

`python -m unittest discover -s network/tests -p "test_ab_construction.py" -v`

The default repository workflow also discovers this test module on
pull requests. This direction should remain opt-in until there is a
native observer capable of independently witnessing action-conditioned
continuation differences, including visually identical phase changes.

The user-facing application, website, game generator and live agent
activation routes have **not** been changed by this adapter. The opt-in
Python `EcosystemService` method is the reachable entry point.
