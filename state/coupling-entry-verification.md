# Coupling-family entry verification

- Current referent: repository entry -> two-coupling origin-rooted class rotation.
- Goal: make the scoped 36-turn certificate reachable and executable without promoting it to universal closure, full-state equivalence or native ARC execution.
- Evidence: README.md, ENTRY.md, work/arc_like_maze/README.md, math.py, alignment.py, coupling_family.py, network/tests/test_arc_like_coupling_family.py, network/tests/test_arc_like_coupling_entry.py.
- Source claim: 8a3a06d40336628ee37d067c61ba1f31c6daf209.
- Implementation snapshot inspected: a362cbfa0632842213e3ee0fac8e7f38301d2ede.
- Verification committed: 299dfedb1cd4083df2cf2ca6f916245ab537c2a8.

## Witness conditions and observed result

12 local focused checks passed (nine existing family checks, three entry checks).
The README links ENTRY.md and the project README; the project README links
coupling_family.py. The root README exposes the focused family test command.
ENTRY.md admits a new explicit referent and preserves its output-record fields.

The new check verifies all 81 successor edges using origin-preserving,
action-label-preserving reachable-state alignment. The permutation is bijective;
its cycles are four of length 2, sixteen of length 4 and one of length 9.
Direct iteration rejects every simultaneous return from turn 1 through 35
and accepts turn 36. This does not claim each world has 36 distinct successors.

Existing tests preserve the phi=0 dormant-coordinate counterexample: rooted
alignment can hold while full-state B-fixed-point counts differ. Depth below
four remains UNKNOWN because the independent h coupling is invisible there.
No native ARC client or live environment was invoked.

## Movement and artifacts

Added only network/tests/test_arc_like_coupling_entry.py in the verification
commit. The test reads repository documentation and constructs in-memory
mathematical witnesses. It does not mutate source worlds, routing state or ARC.
The existing network test-discovery command includes the new file.

## Wall / unknown state

As observed on 2026-10-09, GitHub Actions run
[37930374060](https://github.com/huntingthereferent/language-network/actions/runs/37930374060)
reports completed/failure for the verification commit. A second check run
[37930450858](https://github.com/huntingthereferent/language-network/actions/runs/37930450858)
also reports failure for the same commit.

The first job's log retrieval returns 404 BlobNotFound. Both jobs return
empty step summaries. The check outputs contain no explanatory summary or
text. Therefore the failure cause and whether tests started are UNKNOWN;
neither test failure nor runner/billing failure is established by these reads.
Do not promote the local pass to a GitHub CI pass.

Documentation checks cannot enforce assistant compliance. The mathematical
certificate does not supply native ARC execution, universal inverse closure
or full-space equivalence for dormant-coordinate cases.

## Next referent

Recover the CI failure annotation or usable job log, then repair the evidenced
failure and rerun the focused checks. Keep the existing rooted contract intact;
a full-state or native ARC claim requires its own witness and execution bridge.
