# LS20: native relationships before an F3 correspondence

**Status:** Native effects measured, F3 state correspondence **NOT ESTABLISHED**. Research date: 2026-10-17 (America/Chicago). The GitHub runner logged the tests after 00:00 UTC on October 18.

## Evidence and repeatability

- [Original F3 direct-mapping counterexamples](LS20_F3_NATIVE_2026-10-17.md).
- [Native raw-frame feature scan](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39087804926): independently reset LS20, three executions per allowed simple action.
- [Native mixed action-word tests](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39087965216): independently reset the **actual native** ARC-AGI-3 LS20 environment for each two-step word.
- [Mixed-word raw frames, per-action deltas and JSON](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39087965216/artifacts/12121845835). Artifact has a 14-day GitHub retention window.
- Repeatable code: [native relation scan](../native_relation_scan.py), [mixed-word probe](../native_mixed_relation_probe.py), [comparison to original F3 law](../f3_native_word_comparison.py).
- No puzzle solution was loaded, no replacement game engine was constructed, and no ARC win was recorded.

## Native color transport witnessed

Using **the original native colors**, not colors mapped modulo three, the same two exact pixel sets were transported together. An exact transport requires that every changed old pixel of a color maps onto every changed new pixel by one translation.

| Native action | Three consecutive observed rigid translations | Exact native-color transport | Other change |
| --- | --- | --- | --- |
| ACTION1 | (0,−5) each step | 15 color-9 + 10 color-12 cells | 2 color-11 cells became color 3 |
| ACTION2 | No rigid transport from the initial position | None at root | 2 color-11 cells became color 3 |
| ACTION3 | (−5,0) each step | 15 color-9 + 10 color-12 cells | 2 color-11 cells became color 3 |
| ACTION4 | (+5,0) each step | 15 color-9 + 10 color-12 cells | 2 color-11 cells became color 3 |

The two-cell changed region on successive native steps occurred at x=13,14,15 and y=61..62, respectively, under *each* constant-action three-step trace. This supports a distinct time-/history-related visible process; it is not itself a proof of the internal engine's causal variables.

The 50 pixels exchanged for colors 9 and 12, plus 2 cells changed from 11 to 3, account for the 52 changed cells under ACTION1/3/4. ACTION2 alone changed two cells from the root without transporting the color group.

## Exact native word experiments

Word digits represent actual ARC action IDs, in left-to-right temporal order. The native runtime was reset separately for each word.

| Two native words | Same exact complete final frame | Same transported glyph-color mask | Both end at original glyph mask? |
| --- | --- | --- | --- |
| 34 vs 43 | **Yes** | Yes | Yes |
| 23 vs 32 | **Yes** | Yes | No |
| 12 vs 21 | **No** | No | Only 12 |

All six complete final frames differ from the corresponding untouched root frame. In particular:

- ACTION3 followed by ACTION4 returns the glyph to the initial visible position, but the other two-cell changes persist; therefore *return of the glyph is not return of the complete observed state*.
- ACTION2 is ineffective on the transported glyph when applied first from this root, but after ACTION1 moves it up, ACTION2 transports the same color groups by (0,+5) and returns the glyph. Consequently the native pair 12/21 is order-sensitive at the observed root.
- ACTION2's two-cell change occurs even when it doesn't visibly transport the colored glyph.

These are observed relations on particular rooted action words. They do not establish global commutation, inverse operations on every state, or a hidden-state map.

## What F3 can and cannot say

[The original nine finite-field worlds](../../arc_like_maze/math.py) all satisfy rooted **AB != BA** and **A³ = identity** as equalities/inequalities of their full *mathematical* states. The previously observed native ACTION1..4 each violate A³ on the complete visible LS20 frame when interpreted literally as F3 A.

- Native 12 != 21 is **consistent with** original F3 rooted AB != BA as a *qualitative distinction*; not proof that ACTION1/2 are mathematical A/B, especially because the necessary A³ relation fails.
- Native 34 = 43 and 23 = 32 produce the same **visible final frame** for both action words, while all the original F3 mathematical candidates have distinct AB/BA endpoints. Equal visible frames may conceal different native histories, so this cannot independently rule out an unseen-state mapping.
- The independently witnessed glyph vs two-cell-trace distinction is a **candidate observational factorization**. The transport coordinate appears to change by 5 native grid cells per active move, not as an observed three-cycle. Reducing the position modulo three solely to force A³ to hold would be an *invented correspondence*, so do not do it.

**Next admissible question:** Can a state map extracted from native spatial geometry/history support consistent action-word predictions across *mixed* sequences and later states, while also reproducing a genuine F3 three-step relation? Until there is a witnessed, nontrivial return (not an imposed modulo), F3 remains a mathematical hypothesis family and the original nine candidates must **not** be reinstated as if the counterexample disappeared.

No change to `MyAgent` is warranted by these results alone. We still have 0 new ARC levels solved; mathematical relation discovery and game completion remain separate claims.
