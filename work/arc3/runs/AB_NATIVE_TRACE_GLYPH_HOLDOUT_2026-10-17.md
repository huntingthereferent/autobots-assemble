# A/B — independently falsifiable native glyph/clock relation

Original question: Are the moving native colored glyph and the progressing
two-cell trace independent visible factors of LS20 behavior, or did the
earlier action-word examples merely coincide?

## Preregistered source, before native execution

The original source artifacts are the official native ARC-AGI-3 public LS20
raw frames already independently checked by GitHub run 39091972954, artifact
12122494867. The new source rule was committed as e46f0d1289e4c72510d91a2bcc969802bd63967c,
then strict tests as 7237a63eed357fb37586bd4486048ac23795a9a7,
and holdout workflow as b502ad556aed502e8f058b82c03403401456196b. These commits precede
execution of the new native holdout.

Training evidence: 60 independently reset trajectories from historical and
independent native sources; 60 traces at each depth 0,1,2,3; 36 historical
and 24 newer traces at depth 4. The native trace pixels at time t=0..4 were
identical across every action sequence at a given t, and occupied rows 61
and 62 and columns 13+t..54. Counts: 84,82,80,78,76. In all prior source
comparisons with the same colored-glyph mask and same depth, the complete
native frame also agreed.

FROZEN PREDICTION #1: at NEW depths t=5 and t=6, color 11 will occupy EXACTLY
two native rows y=61,62 and columns x=13+t..54, giving 74 and 72 cells
respectively, regardless of the action word. One pixel discrepancy fails.

FROZEN PREDICTION #2: for two separately reset trajectories at the same
depth, equality of their native colored-glyph masks (colors 9 and 12)
implies equality of the WHOLE visible 64x64 frame. If no qualifying
cross-trajectory matching-glyph pair appears, report NOT TESTED.

The 16 preregistered new full native action words were:
- Depth five: 11111, 22222, 33333, 44444, 12341, 21432, 34123, 43214.
- Depth six: 111111, 222222, 333333, 444444, 123412, 214321, 341234, 432143.

The earlier training archive contains no five- or six-action trajectory.
Words were executed using the preexisting official native take_word helper.
The recorder saves independent resets and every intermediate actual raw
frame without itself scoring the proposed relation. A separate verifier
recomputes the reported action steps, full native frame hashes, predeclared
trace pixels and cross-word glyph/frame comparisons.

## Independent native holdout result

- [Native run 39092801419 — SUCCESS](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39092801419).
- [Frozen prediction, actual complete raw 64x64 frames, native metadata and independent verifier record](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39092801419/artifacts/12123113932). The artifact has the workflow's 14-day retention period.
- Native source count: 16 separately reset official LS20 trajectories, 88 actual actions, all completed from an identical visible root.
- Exact preregistered color-11 trace prediction PASS: 24/24 eligible held-out tests. At depth 5: 16/16 (74 cells in exact coordinates). At depth 6: 8/8 (72 cells in exact coordinates).
- Nonvacuous colored-glyph/time factor prediction PASS: 12/12 qualifying cross-trajectory comparisons of the whole frame, including 9 at depth 5 and 3 at depth 6.
- Training raw archive SHA-256: 033c574999a656ebf57ff628f03be47bcccf16e85705eabe4867f489a7e6bf7f
- Preregistered prediction JSON SHA-256: 35565cb908cd38cc487fdca5b6f26059c6052ea3d06010a90d187ddf1bb19e9d
- Native holdout manifest SHA-256: c346fea8ab5ac12daaefec8fa2305f3bf57497f561b6c8c0042c83dea37ee685
- Native holdout raw-frame ZIP-NPZ SHA-256: 988892e6b2a43ee51859649bbe2d7d83d8c93d72cc16900275f931255d173b47

## What the result says, and does not say

It demonstrates a **repeated and predictively supported visible regularity**
on the actual sampled native LS20 trajectories: the color-11 trace is a
depth-dependent visible clock through depth six, and the observed full frame
matches whenever depth and the combined two-color glyph mask match, on the
available qualifying pairs. The exact out-of-sample trace prediction held
across multiple previously unseen action words.

It does NOT prove action-independence for all possible LS20 histories, a
complete factorization of the hidden state, deterministic behavior of every
native control at every position, a F3 coordinate identification, or an ARC
level solution. Equal visible frames do not prove equal hidden native states,
and the original native-to-F3 counterexamples remain unrepaired.

Open next investigation: independently vary action order and length past six,
and test a *separately preregistered* glyph-transport transition model while
preserving the distinct visible trace clock and its possible boundary
conditions. Do not retrofit an observed failure or impose a modulo-three
mapping merely to match the original mathematics.
