# Axioms — Experiment #3 handoff

Date: 2026-09-30. Status: STOPPED FOR REVIEW.

## Task and result

The user authorized continuation after proposing removal of the special same-sign lifting rule. Remote handoffs still describe Experiment #2; this attempt follows the newer conversation instruction.

One isolated rule-removal witness ran once, with exactly two ab calls and the same square, arithmetic, orientation, source edges and all-pairs policy.

Observed:
- X1 is directly admissible and contains +1, +1, -1, -1.
- The complete X1 reaches the same ab entry point.
- All 12 ordered pairs on the second call are unadmitted.
- X2 retains the evidence but has an empty current list: no second difference was earned.
- Raw recorded outcome: UNKNOWN. Process exit: 0 (execution completed, not evidence of a successful recursion result).
- Interpretation: CONTRACT / IMPLEMENTATION LIMIT in relation admission, not mathematical UNKNOWN or earned zero.

## Exact change

experiment3/two_step.py is an isolated copy of experiment2/two_step.py with the derived-node lifting branch removed from relations(), its now-unused local variables removed, and descriptive report metadata updated. No substitute relation rule was introduced. Prior implementations were not edited.

Remaining admission code recognizes explicit native source edges only. Those edges connect source IDs; they do not directly connect derived IDs. Consequently this ablation cannot admit derived-node pairs. This result is a dependency observation of the existing implementation, not an independent test of whether another formulation of A/B could express lifting.

## Retained evidence and missing operation

X0 source values remain 00=0, 01=1, 10=1, 11=0.
Source relations remain b0:00->01, b1:10->11, a0:00->10, a1:01->11.

X1:
- d4 = 01 - 00 = +1
- d5 = 10 - 00 = +1
- d6 = 11 - 01 = -1
- d7 = 11 - 10 = -1

For d5 -> d6, the retained positive parents have b1:10->11 and negative parents have b0:00->01. For d4 -> d7, the retained positive parents have a1:01->11 and negative parents have a0:00->10.

Those facts remain present, but the remaining operator has no rule to consume their joint structure as a relation between the differences. Integer subtraction operates only after admission. Applying that arithmetic alone does not establish relational admission.

The first enumerated unadmitted pair is d4 -> d5; all decisions are in third.json. The two previously successful comparisons above also remain unadmitted. No numeric zero, loss, or gain was inferred from that absence.

## Answer to the active question

Relation lifting has NOT been shown to collapse into the same A/B operation. Removing it exposes an explicit dependency in this candidate. Nothing new was supplied between calls.

To proceed, a justified operation on retained relational structure would need to be specified or derived. Merely moving the deleted condition inside ab would retain the same supplied rule. This run neither provides that operation nor establishes that it is impossible.

Initial supplied structure still includes source edges, orientation, subtraction, and all-pairs enumeration. General relation discovery, other fixtures, malformed inputs, partial coverage, zero and a third call remain untested.

## Execution and preservation

Exact command, executed once:

    & 'C:\Users\teepa\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -S -B 'E:\axioms\experiment3\two_step.py' | Set-Content -LiteralPath 'E:\axioms\experiment3\third.json' -Encoding utf8

Files created:
- E:\axioms\experiment3\two_step.py
- E:\axioms\experiment3\third.json
- E:\axioms\experiment3\REPORT.md
- E:\axioms\experiment3\prior-hashes-before.json
- E:\axioms\experiment3\prior-hashes-after.json

SHA256 comparisons confirmed the source, evidence JSON and report from Experiments #1 and #2 remained byte-for-byte unchanged. The local AXIOMS_HANDOFF.md and CODEX_HANDOFF.md received completion notes. Portable outputs include this handoff as axioms.md, axioms-experiment3-report.md, axioms-experiment3.py and axioms-third.json.

No repair/rerun, third call, GitHub write or Eggy change occurred.

STOP. The removal attempt is complete. The broader question of expressing relation admission through A/B remains unresolved.
