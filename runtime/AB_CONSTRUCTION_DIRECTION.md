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

## The next layer: executed simulation and A/B correction

The construction entry does not itself create native game worlds. For an
explicitly requested **simulation**, `EcosystemService.simulate_ab_constructions`
accepts the returned `PROPOSED` frames, checks that their proposal identities
and source addresses have not changed, then runs a caller-supplied
`SimulationWorld` (initial state, step function, and observer).

```python
from runtime.ab_world_experiment import SimulationWorld

# A tiny synthetic chamber model, not an observed real-world mechanic.
def begin(s):
    return (s["room"], s["gate0"], s["gate1"])

def advance(s, action):
    room, gate0, gate1 = s
    if action != "advance":
        raise KeyError(action)
    open_here = gate0 if room == 0 else gate1 if room == 1 else 0
    return (min(room + 1, 2) if open_here else room, gate0, gate1)

world = SimulationWorld(
    source="simulation://nested-chambers/v1",
    initial=begin,
    step=advance,
    observe=lambda s: s[0],
    relations=lambda structure: {
        "gate0": structure["gate0"],
        "gate1": structure["gate1"],
    },
)

# Frames must come from propose_ab_constructions with matching proposal IDs.
# They are not native evidence. Each candidate is replayed twice.
experiment = service.simulate_ab_constructions(
    frames=frames,
    world=world,
    action_path=("advance", "advance"),
    predict=lambda proposal, actions: (
        proposal.category, proposal.category
    ),
)

# Actual *simulated* continuations, not the user's prediction,
# determine the new information-minimal A/B partition.
if experiment.information is not None:
    new_fibers = inverse_fibers(
        experiment.observed_occurrences,
        experiment.information,
        source_locators=experiment.observed_locators,
        witness_contract="SIMULATION ONLY: 2-step chamber experiment",
        horizon=2,
    )
```

This diagram now has an executable **synthetic** middle layer:

```
prior witnessed quotient C₁
  -> inverse source fiber
  -> PROPOSED structures
  -> simulated action sequence (two independent replays)
  -> compared return traces (MATCH / COUNTEREXAMPLE / UNKNOWN)
  -> ordinary A/B categories C₂
  -> corrected inverse fiber for the next *proposal* layer
```

For four example configurations with two room gates:

- Action horizon 1: two continuation classes. Only the first gate
  matters for that one-step prediction.
- Action horizon 2: three continuation classes. The gate in the next
  room becomes consequential; the predicted second action is wrong in
  one branch. The counterexample is retained and a new relation is
  synthesized from the actual simulated returns.

If a trial has no executable rule, cannot be deterministically replayed,
or gives an unavailable observation, it is `UNKNOWN`, and no quotient is
returned from the incomplete trial set. If all traces return but the
available relation vocabulary is insufficient, the `unresolved_boundary`
records the missing relation rather than inventing an answer.

**Do not confuse** `SIMULATED_MATCH` with `MOVE`. The `simulation://`
locators are deterministic trial addresses but are never native witness
locators. `NativeABEvaluator` still rejects simulation for live movement.
The service wrapper registers no agents and writes no new tasks.

Run the fully online tests with:

```sh
python -m unittest discover -s network/tests -p 'test_ab_world_experiment.py' -v
```

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
7. Source locators are not independently validated by this pure module;\n   simulated traces have separate simulation-only locators.
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
