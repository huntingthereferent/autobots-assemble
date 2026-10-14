# Selected cross-scope intertwining transport — October 13, 2026

**Current referent.** A finite extension to the *same existing mathematical finite A/B correspondence process*, checking whether a selected edge independently observed under one owner-pinned source pair can be mapped to a **different owner-pinned source pair** by an explicitly declared *two-sided state correspondence*. This is a limited mathematical result for finite operators, not a definition of A/B as relational language.

## Four local pinned finite laws

| Scope | Historical old law phi | Changed law phi | Base joined histories |
|---|---|---|---|
| Recipient | (0,0,0) | (0,1,2) | A, BAA |
| Donor | (0,0,1) | (1,0,1) | AB, B |

Different local owners and separate pin registries. Donor witnesses old state (1,0,0) under action **B** moving to (1,2,0), and donor changed source (1,0,0) under B moving to (1,2,1).

The caller must declare BOTH mappings on the exact selected edge's source/target:

- donor OLD: (1,0,0) -> recipient old (1,0,0); (1,2,0) -> (1,2,0);
- donor NEW: (1,0,0) -> recipient new (1,0,0); **(1,2,1) -> (1,2,0)**.

This nonidentity second mapping is material. The integrated implementation **actually observes** the corresponding recipient old/new B edges under their own verified local owner bindings: **two new recipient observations**, none on donor. The two squares commute on the selected edge. It creates a **new 6-state, 5-edge partial witness**, leaving the original recipient 5-state/4-edge join and donor join unchanged. A task requiring recipient (1,1,0) A AND the derived (1,0,0) B then completes **2/2** using the newly derived fingerprint.

A wrong declared endpoint mapping or a changed recipient law yields TRANSPORT_INTERTWINING_CONFLICT with the expected and independently observed endpoints. Missing donor edge, absent mapped endpoints, extra speculative mappings, budget exhaustion, falsified retained edges, wrong fingerprints, source revision mutation, or withdrawn exact owner pins never count as successful transport. Every task use repeats zero-new-read audits of the base joins and selected recipient observations.

**Scope:** One selected edge, two explicit endpoint maps, four in-process locally verified owner snapshots. This neither identifies general owner equivalence nor transports unobserved edges, whole state spaces or physical systems. A caller-provided mapping is a **hypothesis** until its selected squares have been independently replayed. Source labels, digests and fingerprints are not authentication credentials.

## Local package

Full 193-file local archive: `ab_chatbot_cross_scope_transport_2026-10-13.zip`, SHA256 `969bbb3b0373d5702deab7d5152920bd64f9c45b9588ab91535485800326b7be`. **All 185 predecessor files preserved byte-for-byte**, eight added source/test/demo/evidence files. The integrated module is `ab_chatbot_cross_scope_transport.py`; it composes the existing CrossPinJoin and JointEvidenceTask without changing their code. The test module `test_ab_chatbot_cross_scope_transport.py` passed 22 executions (12 new, 10 imported fixtures). Independent finite checker `finite_cross_scope_transport.py` passed 6 tests.

Targeted regression modules completed separately: same-pin transfer 23; prior witness binding 22; cross-pin join 20; owner pins 10. **103 test executions passing** across separately completed runs, including inherited-fixture overlap. A larger grouped command timed out, so no full historical suite or GitHub CI result is claimed.

## GitHub finite reference

```
cd work/arc_like_maze/chatbot
python finite_cross_scope_transport.py
python -m unittest -q test_finite_cross_scope_transport.py
```

This checker knows all four complete formal finite laws. It cannot prove that their transitions were observed through HTTP or that any remote identity is authentic; those constraints are in the separate integrated source archive. No unrelated Continuity repo pointer was changed.

**Next:** Explore a bounded *chain* of such explicitly evidenced squares across multiple owner scopes, requiring independent fresh observations for every new source and tracking cost. Do not infer an unrestricted global law or source equivalence from a single commuting edge.
