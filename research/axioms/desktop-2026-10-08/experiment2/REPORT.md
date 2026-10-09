# Axioms — Experiment #2 handoff

Date: 2026-09-30. Status: COMPLETE; STOPPED FOR REVIEW.

## Outcome

One witness execution, exactly two ab calls, process exit 0.
Result: SUPPORTED_RELATION_CARRIED_RECURSION.
The complete returned X1 was directly admissible and passed to the same ab entry point.
X2 contains two values: -2 and -2. No unsupported relation blocked either computation.

## What changed

Experiment #1 used remaining-axis tables. Experiment #2 retains explicit directed source edges and signed parent links instead. It has no axes list, remaining coordinates, queue, future route, or next-comparison field.

The current list identifies the nodes produced by the preceding call (source nodes initially). It does not name or order future comparisons. Every ordered pair of current nodes is inspected by the same relation rule. History is an audit record and is not read to select comparisons.

A relation is admitted when it is an explicit source edge, or when both same-sign parent pairs carry relations of the same native kind. The source relations are retained unchanged. Derived support proofs are retained on each node. The second call earns its proofs from the retained parents/source relations.

## Exact witness

X0 nodes: 00=0, 01=1, 10=1, 11=0.
Explicit directed source edges, all oriented 0->1:

- b0: 00 -> 01
- b1: 10 -> 11
- a0: 00 -> 10
- a1: 01 -> 11

X1 nodes:

| ID | Signed parents | Value |
| --- | --- | --- |
| d4 | 01 - 00 | +1 |
| d5 | 10 - 00 | +1 |
| d6 | 11 - 01 | -1 |
| d7 | 11 - 10 | -1 |

X1 -> X2 admissions:

- d4 -> d7: positive parents 01 -> 11 have a1; negative parents 00 -> 10 have a0. Both are kind a. d8 = d7 - d4 = -2.
- d5 -> d6: positive parents 10 -> 11 have b1; negative parents 00 -> 01 have b0. Both are kind b. d9 = d6 - d5 = -2.

The other ordered pairs have no supported directed relation and are recorded as unadmitted candidates. They are not converted into loss, gain, or zero. All 12 ordered candidates are recorded at each call; 4 are admitted on the first and 2 on the second.

## Outside choices and limits

Nothing was supplied between calls. The next comparison arose from relations carried by X1 under the declared same-sign parent lifting rule.

Initial choices remain: the square and source labels, native directed edges and orientation, integer subtraction, same-sign relation lifting, and inspecting all ordered pairs of current nodes. These are declared candidate rules, not discoveries of general A/B.

This result concerns exactly the supplied complete square. Other fixtures, a third call, absent/partial evidence, earned zero, and malformed-input paths were not exercised. The implementation records UNKNOWN when no relation is admitted and EARNED_ZERO when admitted differences are all zero; it does not establish a general PARTIAL coverage policy. No repair or rerun occurred.

## Preservation and execution

SHA256 before/after comparisons confirmed these Experiment #1 files remained byte-for-byte unchanged:

- E:\axioms\two_step.py
- E:\axioms\evidence\first.json
- E:\axioms\REPORT.md

Exact witness command:

    & 'C:\Users\teepa\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -S -B 'E:\axioms\experiment2\two_step.py' | Set-Content -LiteralPath 'E:\axioms\experiment2\second.json' -Encoding utf8

Runtime checks covered retained arithmetic and relational proofs, source retention, and unchanged inputs. The result was computed from values; no expected -2 value was used in the operation or asserted to force the outcome.

## Files and handoff state

Created under E:\axioms\experiment2:

- two_step.py: isolated candidate and witness
- second.json: full X0/X1/X2 and admission audit
- REPORT.md: this report
- first-hashes-before.json and first-hashes-after.json: preservation evidence
- pre-experiment2-CODEX_HANDOFF.md and pre-experiment2-AXIOMS_HANDOFF.md: previous local handoffs

Updated E:\axioms\CODEX_HANDOFF.md and E:\axioms\AXIOMS_HANDOFF.md from the authorized repo handoffs, then appended completion status. Repo handoffs were read from main tree b210879815508c0de2e44f3fb6b5b0a916fedee8.

Session outputs also contain axioms-experiment2.py, axioms-second.json, axioms-experiment2-report.md, and axioms.md (the current portable handoff).

This remains a local USB file workspace, not a Git checkout. No commit or GitHub write was made. Eggy was untouched.

STOP. Experiment #2 is complete; the earlier run instruction is now historical. No third call, broader build, or additional witness is authorized by this handoff.
