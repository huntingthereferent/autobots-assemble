# Cross-pin rooted-history union — 2026-10-13

This is an additive component of the existing 153-file A/B mathematical chatbot. It combines **only explicitly requested observed rooted word histories** from two independently pinned revision snapshots, without claiming source identity continuity or extending off the witnessed paths.

## Input

```python
{
 "required_owner_pins": {"old": "<local-registry-48-char-token>", "new": "<different-token>"},
 "join_words": ["A", "BAA"]
}
```

`join_words` must be a list of 2..8 distinct nonempty action words, using only `A` and `B`, at most 12 actions each. The two owner pins and snapshots must each pass the old `OwnerPinRegistry` and `CrossPinComparison` checks. This new layer does not issue or authenticate pins.

## Outcomes

- **JOINT_PARTIAL_CORRESPONDENCE_WITNESSED**: Each submitted word replays independently in both revisions. Their prefix state pairs form an injective partial mapping. Only the labeled edges actually traversed on the declared words are admitted; there is no greedy extension.
- **JOINT_RELATION_CONFLICT_WITNESSED**: A previously witnessed old state is assigned two incompatible new images, or two old states acquire the same new image. Returned witness names the two **prefix words** and their endpoint equality/inequality in both revisions. It does not erase earlier observed edges.
- **SEARCHING**, **UNKNOWN_BUDGET**, **UNKNOWN_VERSION**, **OWNER_PIN_UNPROVED**, or **WALL_OBSERVATION**: The old observation budget, source-version, exact-owner pin, and cached-edge replay rules remain active. No pairing is returned on an incomplete or invalid evidentiary state.

## Reproduced examples

Original revision phi=(0,0,0), new revision phi=(0,1,2), each rooted at (0,0,0):

- `A` and `BAA`: compatible union with **5 paired states and 4 admitted labeled edges**; 4 old and 4 new unique owner observations. Five paired states do not mean 10 observed edges.
- `A` and `BAB`: individually valid rooted paths, **incompatible joint mapping**. Original endpoints of `A` and `BAB` both (1,0,0); new endpoints differ (1,0,0) and (1,0,1). Both versions independently observed four edges. The obstruction is a `SOURCE_STATE_CONFLICT`.

Original phi=(0,0,1), new phi=(0,0,0): `B` and `ABBABA` give a `TARGET_STATE_CONFLICT`—old prefix endpoints differ while new prefix endpoints coincide. See `JOINT_CROSS_PIN_RESULTS.json` for complete data.

## Commands

```bash
python run_cross_pin_join_demo.py
python -m unittest -q test_ab_chatbot_cross_pin_join.JoinCrossPinTests
python -m unittest -q test_finite_cross_pin_join
python -m unittest -q test_ab_chatbot_cross_pin_comparison.CrossPinTests
```

The pure finite checker `finite_cross_pin_join.py` uses the fully specified finite `Law` and **does not** simulate local HTTP origin, owner revocation or snapshot audit; those belong to the integrated module. Five pure checker tests passed locally.

## Regression verification

New integrated join: 10 tests. Pure checker: 5. Existing cross-pin comparison: 10, owner-pin: 10, provenance: 14, rule-change: 14, mixed-obligation: 12, language-bridge: 35. **110 tests passed across separately completed module invocations**. The full historical suite was not run to completion; no GitHub CI status has been checked.

## Ground and next movement

A/B is language for observed relational movement; its finite A- and B-labeled operators are scoped model choices, not A/B itself. The new 8-file addition preserves all predecessor source exactly; neither full-system conjugacy nor physical continuity nor a complete task-solving agent is established.

Next: compare whether a *selected compatible union* of separately pinned histories can satisfy a new explicit task while preserving every original witness and never extending unobserved edges. Keep `state/current.json` owned by its separate Continuity referent.
