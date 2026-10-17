# ARC / A-B — when the current observation is enough

*Finite mathematical theorem and synthetic counterexample · October 17, 2026*

**Question:** Can the next observation after an action always be predicted using only the current visible observation, with no memory of earlier interactions?

This is a mathematically exact question about deterministic state-action systems. **It is not an ARC-AGI-3 win, a general solver, or a proof of the entire Language Referent inquiry.** It requires no game SDK, model API or paid autonomous agent.

## Exact theorem — observation quotient criterion

Let S be a declared finite set and let A, B: S → S be deterministic total transitions closed on S. Let p: S → O specify *exactly* the available observation: pixels, terminal feedback and/or score, as appropriate to the claim.

There exist deterministic observation-level transitions Ā, B̄: p(S) → p(S) satisfying

~~~text
p(A(s)) = Ā(p(s))
p(B(s)) = B̄(p(s))
~~~

for **every** s in S **if and only if** the following holds for **each** T in {A, B}:

~~~text
p(s) = p(t)  implies  p(T(s)) = p(T(t))
~~~

for all s,t in S.

### Proof

**Necessity.** Suppose an observation-level T̄ exists. When p(s)=p(t), applying T̄ to this same observation yields the same value. Therefore p(T(s))=p(T(t)).

**Sufficiency.** Suppose the implication holds for action T. For each observed value o in p(S), choose any representative state s with p(s)=o and define T̄(o)=p(T(s)). The implication guarantees the result does not depend on the representative chosen; hence T̄ is well-defined. Do this separately for A and B. Both equations now hold. **QED.**

**Corollary for compositions.** If both equations hold, induction on the length of a word w in A and B proves p(w(s))=w̄(p(s)) for every finite composition. Conversely, one exact violation under either generator obstructs that observation-only action representation. This is a representation obstruction, **not an impossibility proof for all history-aware agents or all possible solutions**.

## Exact synthetic counterexample — missing history

Use six reachable states of the form:

~~~text
(position, interacted, win)

position    ∈ {0,1}
interacted  ∈ {0,1}
win         ∈ {0,1}, with win=1 only after interaction occurred

A = move: flip position and preserve interaction history
B = interact: first B records the interaction; second B makes win=1
p(s) = (position, win)       # interaction history is omitted
~~~

Let s=(0,0,0) and t=B(s)=(0,1,0). Then:

~~~text
p(s)    = (0,0) = p(t)
p(B(s)) = (0,0)
p(B(t)) = (0,1)
~~~

Thus the same observable current state and same action B require *different* observed successors. A deterministic transition B̄ based solely on p(s) would have to output both (0,0) and (0,1). No such function exists. **This is a complete, constructive counterexample for the declared synthetic system.**

If the model retains interaction history, the ambiguity disappears. The companion checker enumerates every reachable declared state and verifies closure and compatibility under both operations.

## Evidence boundaries

| Status | What it establishes |
| --- | --- |
| **Proved** | The iff condition above for deterministic total actions on the declared state space |
| **Checked offline** | Six synthetic unit tests, including a contradictory observation pair, sufficient refinements, closure and invalid-input refusal |
| **Possible native ARC question** | Does a specific public game contain two real legal histories with identical permitted observations, followed by the same action yielding distinct permitted outcomes? |
| **Not demonstrated** | Any such pair from actual native ARC traces, independent first-contact game solving, general ARC transfer or universal A/B claims |

The existing [SP80 research note](../dives/ARC3-TRACE-001/oracles/SP80.md) describes accumulated ACTION5 interactions and is a **candidate**, not already the paired-history witness. The [SK48 record](../dives/ARC3-TRACE-001/oracles/SK48.md) describes the different problem of needing simultaneous spatial and symbolic constraints. They should not be collapsed into one issue.

The [native ARC observer](../../runtime/arc_native_observer.py) supplies a possible measurement surface for a future permitted pair-of-histories test. It does not already prove that such a pair exists. Previous [unsuccessful autonomous trials](AUTONOMOUS_TRIALS.md) and [saved route replays](README.md) remain distinct.

## Zero-cost reproduction

From the research repository root:

~~~bash
python -m unittest -v network.tests.test_arc_observation_sufficiency
~~~

Source: [finite checker](observation_sufficiency.py) · [six negative and positive tests](../../network/tests/test_arc_observation_sufficiency.py).

Six tests passed in the author's local scratch checkout on October 17, 2026; **the pushed branch has not been independently tested by GitHub CI at the time of writing**. Unit checks corroborate the constructed example; the written proof establishes the iff result.

## What would make this an actual ARC witness?

A future experiment would record exact SDK version, public game ID, reset/start conditions, permitted observation function, action payloads, distinct histories, and *matched native frame/feedback hashes*. It would present two real reachable histories with the same full allowed current observation, followed by the same legal action, and distinct permitted consequences. If no pair is found, record **NOT FOUND WITHIN BUDGET**; absence of a found pair is not proof of sufficient representation unless the complete declared reachable space has been checked.

No agent loop, API key, paid runtime or persistent workstation is required to maintain this mathematical proof.
