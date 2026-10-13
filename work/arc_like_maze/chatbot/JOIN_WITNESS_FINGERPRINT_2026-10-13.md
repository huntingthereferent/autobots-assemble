# Exact joined-witness fingerprints and independent task comparisons — 2026-10-13

**Current referent.** Extend the current finite mathematical A/B chatbot to bind an explicit goal/edge/path/destination task to the exact **already audited** join it consumes, and compare a common task against independently witnessed alternative joins **without combining them**. A/B remains language for tracing relationships in movement; the finite operators A and B are only declared test generators.

## Executed integrated result

The new `ab_chatbot_joint_witness_binding.py` depends on **unchanged** `CrossPinJoin` and `JointEvidenceTask`. It accepts `witness_fingerprint` (64 lowercase hexadecimal characters) alongside the existing validated task schema.

A canonical SHA-256 hash includes the specific joined-task referent, pinned old/new owner descriptions, revisions, declared history words, full paired-state mapping and every admitted labeled edge. Display text and ambient owner-cache observation counts are excluded; acquiring unrelated independently verified edges cannot change the identity of an existing joined relation. This digest is a **relation-selection fingerprint, not a remote authentication credential**. The live owner pins and source transitions must still pass the already-established zero-read replay before and after task consumption.

The comparator accepts 2..8 independently bound joins, requiring *identical normalized task obligations*; it reports each candidate separately, with its digest and admitted-obligation counts. It **never joins two independent task successes**.

Finite old law phi=(0,0,0), changed law phi=(0,1,2). Two separately pinned joins:

- `A` + `BAA`: five state pairs, four observed edges.
- `B` + `ABB`: five state pairs, four observed edges.
- Task requiring labeled edge **(1,1,0) A**: first join satisfies 1/1, second 0/1; `TASK_COMPLETED_BY_INDEPENDENT_WITNESS`, winner is only the first join.
- Task requiring **(1,1,0) A AND (1,0,0) B**: each join supplies 1/2 obligations, and **neither** independently satisfies both. `TASK_UNPROVED_ACROSS_TESTED_WITNESSES`; never 2/2 by merging evidence.
- A mismatched digest returns `WITNESS_FINGERPRINT_MISMATCH`; revoked pin, version change, forged cached edge or historical collision withholds completion and preserves the relevant failure evidence.
- Task consumption and comparison perform **zero new owner-edge observations**. The demo's old/new owner caches each contain six observed transitions before and after both submitted tasks.

## Integration and artifacts

New separate local full package `ab_chatbot_joint_witness_binding_2026-10-13.zip`, SHA-256 `7cd016d1359aed33ce66a013a52b0815b6db6f6a453c42c838c065213c06f1e8`, **177 files**, preserving every one of the prior 169 files byte-for-byte. Eight additions: integrated source, 12 tests; independent complete-law finite checker, 6 tests; demo, README, result JSON and test record.

**Completed local testing:** 12 new integrated + 6 finite + 11 previous joint task + 10 previous cross-pin join + 10 previous cross-pin comparison + 10 previous exact owner pin + 14 provenance + 12 mixed obligations + 14 rule change = **99 passed across nine completed module runs**. The entire historical suite was not completed; GitHub CI is not asserted.

## Standalone GitHub finite reference

    cd work/arc_like_maze/chatbot
    python finite_join_fingerprint.py
    python -m unittest -q test_finite_join_fingerprint.py

The standalone reference hashes complete finite-law results, tests a deliberately changed declared source referent and rejects substitution. It is **not** a proof of HTTP ownership, and its source-referent identifiers are caller-supplied, not independently authenticated.

**Limits:** A joined history is partial. A valid mathematical law may define unobserved edges, but these cannot be imported into an earlier witnessed joint relation. A task is completed only if every obligation is admitted by **one** audited witness. No whole-system conjugacy, universal generalization or physical A/B claim follows.

**Next:** Test an explicit, separately verified transfer of evidence between independently pinned joins only under a declared transport witness. Until then, collisions, source revisions and missing edges remain distinct boundaries. Leave unrelated `state/current.json` untouched.
