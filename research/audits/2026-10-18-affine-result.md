# Finite affine result audit — October 18, 2026

## Question and verdict

Does the documented finite affine construction result agree with its definitions,
implementation, negative controls and executable checks? **Supported within the
declared nine-world, three-dimensional F3 family.** No defect was found in this
bounded audit. This does not audit the complete repository, external observations,
the entry protocol's behavioral effectiveness, or the universal language referent.

James supplied an external GitHub review and authorized continuation. This record is AI-authored audit work, not James's
verbatim research account or validation by an independent human researcher.

## Source and execution

Audited source: `4b25841f68450c81a215acb28ff82de6bd75f11b`.
Read the entry/session and evidence contracts, the finite research README,
`math.py`, `alignment.py`, `operators.py`, and `affine_scan.py` in
`work/arc_like_maze/`.

Executed from the repository root:

```bash
python -m unittest network.tests.test_arc_like_inverse_ab network.tests.test_arc_like_alignment network.tests.test_arc_like_operators network.tests.test_arc_like_affine_scan -v
```

Observed: **39 tests passed**, locally. This is not a GitHub CI result.

A separate inline Python reconstruction implemented the three-coordinate
transitions, checked all 81 ordered pairs of parameter worlds by forced rooted
transition correspondence, and enumerated all 729 affine parameter maps.
It imported the production scanner only after reconstructing the counts, for
comparison. Observed class sizes: 1,2,2,2,2; counts: 729 affine maps, 432
bijections, 89 compatible maps, 48 compatible bijections, and 24 induced
quotient actions. All 2,304 ordered compositions of the accepted permutations
remained accepted. The inline reconstruction was a session check; the committed
suite above is the durable reproduction route.

## Mathematical check and failure boundary

For parameters v in F3^2 the recovered equivalence is v ~ -v, with zero
alone. The rooted state correspondence between phi and 2phi scales the third
state coordinate by 2, preserving both labeled transitions.

For an invertible linear map M, equivalent inputs have equivalent outputs.
For an invertible affine map Mv+t with t nonzero, choose v=M^-1 t.
The equivalent inputs v and -v map to 2t and zero. They are inequivalent,
so no translated bijection is admitted. There are (9-1)(9-3)=48 invertible
linear maps, and nine translations per matrix give 432 affine bijections.
The exhaustive enumeration agrees with this derivation.

Concrete negative control: translation by (1,0) takes (1,0) ~ (2,0)
to (2,0) and (0,0), which are inequivalent. Existing tests also preserve
UNKNOWN on exploration-budget exhaustion and reject whole-world equivalence
across different reachable-state counts.

## Changes and next movement

No implementation, license, personal profile or mathematical claim was changed.
This audit record preserves the evidence and limitations. Next warranted audit:
trace one external source observation from retrieval through stored provenance,
verification and display, using the then-current source and repository state.
