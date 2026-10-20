# A/B native glyph transport — verified longer-sequence prediction

Real independent official ARC-AGI-3 LS20 environment. NOT REA, not F3 hidden-state identification, not a fabricated agent.

## Training was fixed before testing

Three already-verified original raw source sets:
- Historical: 36 independent trajectories, 120 native actions; raw SHA256 e7036323f8febfeca5ccd453c83e9a9e44c21824f975ee3c9b6b2d8874966fa1.
- Suffix holdout: 24 trajectories, 96 native actions; raw SHA256 033c574999a656ebf57ff628f03be47bcccf16e85705eabe4867f489a7e6bf7f.
- Depth-5/6 holdout: 16 trajectories, 88 native actions; raw SHA256 988892e6b2a43ee51859649bbe2d7d83d8c93d72cc16900275f931255d173b47.

The source-frozen training verifier checks original manifest and raw SHA256, every actual 64x64 pixel frame, action word, root, and precise two-row by five-column native color-12 glyph. Its 304 observed actions yield 27 distinct (top-left glyph position, native action) -> next glyph position relationships, with zero observed conflicts. Missing state/action relations stay UNKNOWN.

## Preregistered new words

17 new 8-step words were committed before native execution:

12341234, 21432143, 34123412, 43214321, 33333333, 44444444, 22222222, 12121212, 34343434, 43434343, 21212121, 24312431, 31423142, 12431243, 14321432, 23142314, 32143214.

Every word is a previously unobserved full sequence built exclusively out of previously independently recorded position/action edges. Predicted glyph positions at all depths 0-8 were frozen as a separate JSON artifact BEFORE the real native run.

## Independent result: PASS

- [Official native execution and verification](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39093565973) — SUCCESS; 12/12 regression tests.
- [Actual frozen model, native raw pixels, independent verifier receipt](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39093565973/artifacts/12124210279), retention 14 days.
- 17/17 independently reset native trajectories completed with the same visible root; 136 novel native actions.
- 153/153 **exact glyph positions** confirmed (including the 17 identical initial roots, so **136/136 actual next positions**).
- Frozen prediction SHA256: 4d66bfdbb7d213cd2c1ca065b9b0f8484a57110146fbf7b53fb57e21a3c6be0c.
- Independent native manifest SHA256: 7e3e4accd90c39199c0d23fa40dc52b1af12802439635d322d9016c55780c466.
- Actual new native NPZ SHA256: 09683abcb4cc534bac76d53ef0aabda31342b5d53029077cece14284844e91be.
- Separate verification verdict SHA256: 190a8a09510219af7ba362decb381ddd51a8ee37ea44c68d224a262879bd5727.

Illustrative witnessed blocked moves from prior evidence: from (y=45,x=29), ACTION1 or ACTION2 leaves the glyph unchanged. At (y=40,x=34), ACTION3 leaves it unchanged, while ACTION1 from (45,34) moves to (40,34). This is a source-observed position-dependent action relationship, not an unconditional global directional formula.

## Research limits / next genuine question

The completed native predictions verify recombination of previously witnessed glyph movements across longer, previously unobserved sequences. They do NOT prove a complete native law, unknown position/action transitions, hidden-state Markov property, F3 correspondence, 48-law native theory, or an ARC game solve. The previously established visible trace clock remains a separate observation contract, not silently merged with glyph dynamics.

Next boundary: propose a source-grounded transition for a **previously unseen position/action pair**, and test it against separately observed native pixels, explicitly preserving failures or unresolved cases rather than extrapolating without evidence.
