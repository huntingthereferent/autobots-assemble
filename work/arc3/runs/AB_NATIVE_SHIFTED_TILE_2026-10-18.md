# A/B shifted entry timing — prospective native test

The earlier long special-tile trial verified 132/132 full-frame equalities and 12/12 returns, but its absolute clock formula was already contradicted by training frames. Preserve that result and its red test. In the original source, the trace has 70 pixels at both steps 7 and 8 when entering the mixed tile, whereas other routes decrease by two at step 8.

This prospective test varies the time of entry using independently verified 12 return loops at the native root. Three distinct previous entry histories are tested with zero, two, four, or six additional native actions, and paired with a same-length non-entry final-action control.

H1: On entering the mixed-color tile, the entire native color-11 trace mask stays unchanged from the preceding frame and the glyph enters (row30,col19).

H2: With the identical preceding action sequence but a different final native action, the trace advances by two pixels and the glyph does not enter that tile.

The frozen 24 native action words are recorded in source before observation. All raw 64x64 frames are recorded independently through the official ARC-AGI-3 LS20 SDK and checked by a separate raw-pixel verifier. Any hypothesis failure or interruption remains an observable result.

All findings are about this native visible environment. No hidden-state equality, generic Markov dynamics, REA implementation, F3 identification, or solved game is claimed.