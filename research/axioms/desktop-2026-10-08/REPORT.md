# Axioms: first bounded two-step witness

Date: 2026-09-30. Status: STOPPED FOR REVIEW.

## Result and scope

One execution of two_step.py exited 0 and recorded SUPPORTED_TWO_STEP_NATIVE_MOVEMENT. This is an all-axis integer finite-difference candidate, not an identification or definition of general A/B.

The identical ab entry point received X0 and then the complete returned X1 directly. No adapter, extra argument, new WATCH, orientation, or caller-selected pair was inserted between calls.

| Input/output | Retained numerical evidence |
| --- | --- |
| X0 | Binary square: 00=0, 01=1, 10=1, 11=0 |
| X1 | Route a: b=0 gives +1, b=1 gives -1; route b: a=0 gives +1, a=1 gives -1 |
| X2 | Route a,b gives -2; route b,a gives -2 |

X1 was directly admissible. Both outputs were SUPPORTED_MOVEMENT under the declared native rule. No missing relation was encountered within these two calls.

## What still comes from outside A/B?

Initially supplied: the fixture and its source labels, binary-axis representation, axis identities, orientation 0->1, exact integer subtraction, and the policy of processing every remaining axis. Nothing additional was supplied between the two calls.

The next contrasts are available because the initial binary square already contains both axes. This run does not show discovery of an unrepresented contrast. The function accepts the whole witness but computes on its active tables; retained provenance and history support those computations rather than becoming independent comparison targets. Whole-object admissibility alone is therefore not evidence of unrestricted whole-witness distinction discovery.

## Contract and support

X is one dictionary containing rule, nodes, tables, history, outcome, and reasons. Source nodes remain unchanged. Every derived node retains signed positive/negative parent references, its axis, orientation, and remaining coordinate. Both route orders are retained independently. X1 retains 8 nodes; X2 retains 10. The run checks arithmetic against parent values, source retention, direct admissibility, both route results, and absence of input mutation.

UNKNOWN, PARTIAL, EARNED_ZERO, and contract-limit paths exist in the candidate but were not exercised. No third call, extra fixture, general discovery test, or repair run was performed.

## Execution and files

Command executed once:

    & 'C:\Users\teepa\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -S -B 'E:\axioms\two_step.py' | Set-Content -LiteralPath 'E:\axioms\evidence\first.json' -Encoding utf8

Witness process exit: 0. Exact evidence: E:\axioms\evidence\first.json.
Implementation: E:\axioms\two_step.py.
Updated handoff: E:\axioms\AXIOMS_HANDOFF.md.

The initial PowerShell display of the saved JSON failed because the zero-axis scalar coordinate uses an empty property name. Reading the unchanged JSON with ConvertFrom-Json -AsHashtable succeeded. The witness was not rerun.

The local workspace E:\axioms was populated from the three documents in huntingthereferent/axioms main, tree d507f134dde08e94b89e60c28bec545371c99766. It is a local file workspace, not a Git clone. No commit, push, or remote modification was made. Eggy was left untouched.

Stop condition reached: one bounded witness recorded; review required before further implementation.
