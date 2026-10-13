# Consume a previously joined finite witness for explicit task completion — 2026-10-13

**Referent.** Test whether a new bounded task may legitimately use a previously established partial cross-pin correspondence **without** requesting or asserting new A/B-labeled source transitions. A/B here remains a language-level research referent; the finite symbols A and B are scoped, explicitly specified generators.

## Witness and observations

Old finite law phi=(0,0,0), new law phi=(0,1,2), two separately pinned local snapshot owners. Joined declared words A and BAA have **5 paired states and 4 witnessed labeled edges**. Only those four edges may be used for the new task.

The integrated adapter `ab_chatbot_joint_evidence_task.py` takes a live pre-existing `CrossPinJoin` and a strict structured task. It does **not** create another observer, alter the join, add edges, or infer a hidden preservation requirement. Each call performs `joint.advance(max_new_edges=0)`, which repeats pinned-owner, revision and retained-edge audit before exposing an answer.

Example task types in a single strict dict:

- `goals`: source states with witnessed paired images;
- `required_edges`: exact source state and action label in the already admitted joint edge map;
- `required_paths`: action word plus **both** explicitly required endpoints, every labeled step admitted in the same map;
- `required_destinations`: declared source/image state pairs in that same rooted correspondence.

The demo's declared 2 goals, 2 edges, 1 path (BAA), and 1 destination identity are **6/6 admitted**; result `TASK_COMPLETED_ON_JOINT_WITNESS`. Owner observations in either source before vs after evaluating these tasks are exactly equal: **zero new edge observations**.

Missing source edge (1,0,0) B and missing word-history AB yield `TASK_REQUIREMENTS_UNPROVED`, even though the complete finite law can calculate both transitions. A partial goal mapping cannot replace a path witness; no global impossibility is concluded. Existing `A` and `BAB` histories have a source-state collision; that joint report and its exact counterexample survive, without task success. Invalid/contradictory task inputs consume no new observations. Version mutation -> UNKNOWN_VERSION, pin revocation -> OWNER_PIN_UNPROVED, forged retained edge -> WALL_OBSERVATION, with prior success withdrawn.

## Local integrated package

`ab_chatbot_joint_evidence_task_2026-10-13.zip`, SHA-256 `cfd4a1b81a9e5376547e994b23d6a4173e1bd71c4320b17d476e75a41d5a94c8`, **169 files**; all **161 predecessor files** are preserved byte-for-byte. Adds integrated task adapter, 11 integration tests, standalone finite checker with 6 tests, demo, README, detailed JSON evidence and regression record.

**122 distinct targeted tests passed** in completed calls: 11 new integrated, 6 finite, 10 prior cross-pin join, 10 prior cross-pin comparison, 10 owner pin, 14 provenance, 12 mixed obligations, 35 language bridge, 14 rule change. A broader sequential runner was interrupted; do not claim the entire historical suite or GitHub CI.

## GitHub standalone finite checker

    cd work/arc_like_maze/chatbot
    python finite_joint_task_consumer.py
    python -m unittest -q test_finite_joint_task_consumer.py

The checker replays a supplied joint witness using the complete declared finite owner laws and refuses forged edge additions. It does **not** authenticate HTTP source origins, contain the integrated task adapter, or infer any off-path mapping. The complete observation-backed source is only in the separate local ZIP.

**Next warranted movement:** Bind each new task to the immutable fingerprint of the *particular* audited joined witness it claims to consume. Compare explicit task outcomes across different independently joined records, retaining every observation and conflict separately; no silent evidence promotion or unobserved edge transport.

The unrelated Continuity state/current.json remains unchanged.
