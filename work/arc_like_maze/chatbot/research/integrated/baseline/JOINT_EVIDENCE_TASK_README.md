# Joint evidence as a task witness — October 13, 2026

## Current question

Can the same finite A/B chatbot complete a separately declared task *using a previously witnessed cross-pin partial correspondence* without admitting any unobserved labeled transition?

**Yes for requirements wholly contained in the existing observed union.** No new mathematical law is inferred. All owner-provenance, source-revision, and observation-cache replay checks remain controlled by the existing `CrossPinJoin` instance.

## New additive code

`ab_chatbot_joint_evidence_task.py` introduces `JointEvidenceTask(joint, task_input)` where `joint` is an existing `CrossPinJoin`. It accepts one strict structured dict (1..8 obligations per category, and at least one total):

```python
{
  "goals": [[1,0,0],[2,1,0]],
  "required_edges": [
    {"state":[0,0,0], "action":"A"},
    {"state":[1,1,0], "action":"A"}
  ],
  "required_paths": [{"word":"BAA", "old_end":[2,1,0], "new_end":[2,1,0]}],
  "required_destinations": [{"source":[1,0,0], "image":[1,0,0]}]
}
```

No implicit path discovery, new source action, or path extension is allowed. The adapter invokes **`joint.advance(max_new_edges=0)`** on every task read; this audits the already retained evidence, rejects outdated pins and changed snapshots, and never requests an unknown transition. Required paths replay each labeled admitted edge through the existing joint pairing; source/destination matches alone cannot stand in for a full path.

## Independent finite demonstration

Original law `phi=(0,0,0)`, changed law `phi=(0,1,2)`. Two separately pinned owner snapshots, joined histories `A` + `BAA`:

- Original union: **5 paired states / 4 admitted edges** (only edges traversed by the two submitted words).
- The structured example above: `TASK_COMPLETED_ON_JOINT_WITNESS`, with 6/6 obligations witnessed (2 goals, 2 edges, 1 path, 1 destination).
- A task requiring source edge `(1,0,0) B` is `TASK_REQUIREMENTS_UNPROVED`, even though the original full finite law defines that transition. The edge was **not admitted in the observed union**.
- A task with an already paired goal but an unwitnessed required path `AB` is likewise `TASK_REQUIREMENTS_UNPROVED`.
- A join of `A` + `BAB` is itself `JOINT_RELATION_CONFLICT_WITNESSED` with the underlying source-state collision certificate; no task may report completion from it.
- All task reads preserve original/new edge observation counts exactly, **0 extra owner transition reads**; results for the successful join before and after task evaluation match the independently replayed finite law reference.

An invalid task is `INVALID_TASK`, a directly contradictory declared image is `INCONSISTENT_TASK`; neither is treated as an independent mathematical no-solution theorem. A missing joint witness returns `SEARCHING` (with zero new reads), stale revision `UNKNOWN_VERSION`, revoked owner `OWNER_PIN_UNPROVED`, and corrupted retained evidence `WALL_OBSERVATION`. Any previous task success is withheld when its joint witness is no longer valid.

## Reproduce

```bash
python -m unittest -q test_ab_chatbot_joint_evidence_task.JointEvidenceTaskTests
python -m unittest -q test_finite_joint_task_consumer.FiniteJointTaskConsumerTests
python run_joint_evidence_task_demo.py
```

New integrated tests **11/11 passed**. Independent finite task-consumer checks **6/6 passed**. Seven relevant older modules: cross-pin join 10, cross-pin comparison 10, owner-pin 10, provenance 14, mixed obligations 12, language bridge 35, rule change 14; altogether **122 distinct targeted tests passed** in completed module/class runs. Historical all-module suite and GitHub CI not claimed.

## Boundary and next movement

This task adapter **uses** existing evidence. It is not allowed to extend or optimize the pairing, to assert correspondence where no old/new rooted history was recorded, or to interpret the language-level A/B referent as the toy finite generators. Task declaration is not evidence of validity. The full integration remains in the ZIP; the GitHub standalone model uses complete declared finite laws and does not authenticate HTTP owner provenance.

**Next:** Allow a task to cite a particular immutable joint-witness *fingerprint* and compare task outcomes across two independently joined records, without transferring unseen edges or silently strengthening past evidence.
