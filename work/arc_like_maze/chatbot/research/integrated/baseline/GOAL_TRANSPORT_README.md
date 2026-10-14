# A/B chatbot — witnessed goal transport under a change of coordinates

**Date:** October 12, 2026. **State:** Local, tested continuation; **not committed to GitHub**.

## Question

Can an already completed finite mathematical goal be carried to another presentation of the same *rooted* transformation system, without supplying the coordinate correspondence or silently upgrading the mathematical scope?

A/B remains the investigator's language-level reference for movement. The named A/B operations below are specifically declared finite mathematical transformations, not A/B's definition or a universal in-between theory.

## What was added

`ab_chatbot_goal_transport.py` **reuses** (does not reimplement) the existing `GoalAgent` goal witness, `FiniteSystem` source model, `discover(..., full=False)` rooted correspondence procedure, and two existing `LanguageBridge` pinned observers.

1. The first `GoalAgent` produces a completed path from cached **observed** transitions.
2. `RootedGoalTransport` replays every source path edge against the source's pinned observations and the declared source law. It never accepts a fabricated path merely because it has status `COMPLETE`.
3. Existing `discover` observes the second system's generator transitions, obtains the rooted correspondence without being given the relabeling, and independently checks all recorded A/B intertwining squares on the recovered rooted carrier.
4. The completed source action word is moved through that correspondence. Every target edge in the carried path must already have been observed, and target labels can differ from source labels.
5. The relation is cached for transporting additional completed goals on **the same pinned versions**, with zero fresh target HTTP edge reads. Re-pinning either observer invalidates reuse.

### Reproduce

Run these commands beside the other Python modules from the previous chatbot package:

```sh
python ab_chatbot_goal_transport.py
python -m unittest -q test_ab_chatbot_goal_transport
```

**Demonstrated example (two separately source-owned loopback systems):**

```text
Original:  COMPLETE_WITNESSED
  action word: AB
  states: (0,0,0) -> (1,0,0) -> (1,2,0)

Transport: PRESERVED_ROOTED_WITNESSED
  action word: AB
  states: (0,0,0) -> (1,0,0) -> (1,2,2)

Rooted relation: 9 mapped states; 18 target transition observations.
```

The example uses two independently owned presentations of one declared finite source law. The test constructor uses a nonlinear coordinate shear to construct the second owner's data, **but does not pass that shear to the correspondence-discovery routine**. The program discovers the mapping from target observations.

## Evidence status

- **11 new tests passed** covering independent mapping discovery, reuse for all reachable goals without additional target reads, resumption after a query cap, refusal to override an observer's total edge budget, incompatible models, tampered and unobserved source paths, repinned versions, unbound provenance, different laws and shears, corrupt/partial records, and a negative control where rooted agreement coexists with a different off-root law.
- **225 of 225 existing-plus-new tests passed across 14 independently run modules**. Each module was executed independently with the local Python standard-library test runner; this is not a claim of a successful monolithic combined run, GitHub Actions CI, external-world verification, or external chatbot benchmarking.
- A rooted certificate covers the source-root-reachable component and **both generators** on that component. It is not evidence of conjugacy of the full 27-state systems unless the component is the whole state space and a suitable full certificate is explicitly checked. Neither does success for a declared source model prove an unrelated black-box source follows the model at unobserved states.
- Trust is limited to the in-process explicitly bound local owner. Matching externally reported source labels, revisions, and digests do not prove external provenance. Unbound observers remain `PRESERVED_ROOTED_REMOTE_REPORTED`, not locally source-verified.
- The source goal's **specific path** is replayed from witnessed source edges; the full source transition law is a declared model and is *not* claimed independently measured over every source state by this layer.
- A small rooted certificate requires a bounded set of transition observations (18 in the example). This can cost **more** than solving a single target path directly. Its benefit is retaining a proven *relational mapping* for many paths; neither universal cost reduction nor general learning has been established.
- When a query/edge budget fails, the result is `UNKNOWN_RELATION_BUDGET`, never a fake correspondence. Rooted inconsistencies produce `ROOTED_OBSTRUCTED`. No status implies a solution to the broader mathematics of motion.

## Next warranted mathematical step

Investigate a change in the *model's relationship itself*, not merely a known family of coordinate re-labelings: choose a bounded rule change, ask whether any restricted relation survives, and preserve a counterexample when no corresponding map can be established. Keep model description, observed source identity, and the user's language-level referent separate.

**No repository write was made.**
