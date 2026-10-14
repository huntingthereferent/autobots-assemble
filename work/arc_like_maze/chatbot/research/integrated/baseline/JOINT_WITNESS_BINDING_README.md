# A/B chatbot: exact joint-witness binding and independent task comparison

**Date:** 2026-10-13. **Referent:** Continue the existing finite mathematical chatbot, not a replacement engine. The A/B labels in the runnable finite experiments refer only to specified mathematical transformations. They do not define the language-level A/B relation.

## What was added

`ab_chatbot_joint_witness_binding.py` layers over the unchanged `CrossPinJoin` and `JointEvidenceTask`.

1. An **audited witness fingerprint** hashes the joined contract fingerprint, owner pin descriptions, separately pinned revisions, explicit words, every admitted partial state pairing, and every witnessed labeled edge. Observation counters and descriptive output text do not affect identity. This is a content/referent fingerprint, **not remote-source authentication**. `current_digest(joint)` first invokes `joint.advance(max_new_edges=0)` to recheck both owner pins and independently cached transitions. Unsettled, withdrawn, conflicted, or otherwise unwitnessed joins have no consumable fingerprint.
2. `BoundJointTask` accepts an **explicit** `witness_fingerprint` plus the existing strict task schema. It accepts completion only when two independent zero-new-edge audits bracket the task check and produce the *same* fingerprint. A different join—even when its full finite laws agree—cannot borrow an old result. Forged cache values, changed revisions and revoked owner pins withdraw completion.
3. `JointWitnessTaskComparison` compares two to eight separately witnessed joins against the exact same normalized task, preserving independent verdicts, evidence fingerprints, admitted obligation counts and collision witnesses. **It never unions obligations across different candidates.** One individually complete result may identify its own completion; if no individual join carries all requirements, the task is unproved across the tested joins.

## Observed positive and negative comparison

Original finite law phi=(0,0,0), new finite law phi=(0,1,2), independently pinned historical snapshots. Join 1 consists of `A` and `BAA`, and join 2 consists of `B` and `ABB`. Both are independently valid rooted partial correspondences of **5 paired states and 4 admitted observed edges**. Their content fingerprints are different. Under the exact same task requiring old-state `(1,1,0)` labeled `A`, only the first completes. Under a task also requiring old-state `(1,0,0)` labeled `B`, each join admits just one of the two edges: **TASK_UNPROVED_ACROSS_TESTED_WITNESSES**. It would be incorrect to combine those separate successes into one task completion.

No additional owner edge observations were made when consuming or comparing the audited witnesses; the demo measured 6 old and 6 new owner observations before and after these two tasks. An unobserved required edge remains unproved despite being computable from the complete laws.

## How to run

From the folder containing the extracted 177-file archive:

```
python run_joint_witness_binding_demo.py
python -m unittest -q test_ab_chatbot_joint_witness_binding.ExactJointWitnessTests
python -m unittest -q test_finite_join_fingerprint.FiniteFingerprintTests
```

See `JOINT_WITNESS_BINDING_RESULTS.json` for the complete per-join outcomes, including the two separate content hashes. `JOINT_WITNESS_BINDING_REGRESSION.json` lists every separately completed local regression module and its count.

## Verification boundary

12 new integrated tests and 6 independently implemented finite-law tests passed. Earlier modules completed separately: joint evidence task (11), cross-pin join (10), cross-pin comparison (10), exact owner pin (10), provenance (14), mixed obligations (12), rule change (14). **99 tests total in completed runs.** A larger grouped legacy test attempt stalled, so the complete historical suite, and any GitHub CI claim, remain unverified.

The finite standalone checker does **not** authenticate HTTP owners or possess the integrated snapshot registry. The full integrated archive has live in-process owner binding, revision checks and cached transition audits, but does not certify remote origin, generalized autonomous language reasoning, global maximality or whole-system conjugacy.

**Next boundary:** Explicit evidence-subset or revision transport needs its own witnessed rule; neither matching digests nor identical state images alone justify importing evidence from another pinned owner or snapshot. Keep the unrelated `state/current.json` project referent unchanged.
