# Cross-pin historical evidence comparison — 2026-10-13

## Current referent

Continue the existing A/B mathematical chatbot. Compare **explicitly selected** rooted action-word relationships across two **independently pinned and locally verified** finite-version snapshots. Do not infer equivalence of versions, owners, full transformation systems, mathematical generators or language-level A/B from a matching word pair.

## Contract

Two previously issued `OwnerPinRegistry` local handles are required, plus 1–8 explicitly declared, *distinct* pairs of rooted A/B words of length at most 12 (empty word permitted for the root). No interpretation of ambiguous prose. Example:

```python
request = {'required_owner_pins': {'old': old_pin.token, 'new': new_pin.token},
           'compare_words': [['', 'AAA'], ['BA', 'ABB']]}
comparison = CrossPinComparison(old_bridge, new_bridge, request, registry=registry)
result = comparison.advance(max_new_edges=2)
```

Each pin is bound to an **exact in-process owner and snapshot object**, source label, revision and digest by the existing registry. The version equality and validity of both pins are rechecked before and after every advance, even a zero-read revisit. If a pin is revoked or substituted, `OWNER_PIN_UNPROVED` returns no previously successful result. If snapshot or source version changed, `UNKNOWN_VERSION` returns no comparison. An incomplete observation cap is `SEARCHING`, a source-wide exhausted budget `UNKNOWN_BUDGET`, and a tampered retained transition `WALL_OBSERVATION`. The fingerprint binds both issued tokens and the exact word-pair set.

Old and new histories are never merged. Historical old edges may be reused *only under their old pinned owner and revision*, with local replay; the new pinned snapshot starts with no inherited transitions and independently observes all required words. Every cached edge in the comparison is audited again on every advance and matched against the appropriate historical owner-held law. Matching source-reported metadata never supplies the owner binding.

For each word pair the report records both full root-to-endpoint histories and a Boolean equality on **each** version. `DECLARED_EQUALITY_PRESERVED_WITNESSED` means at least one required equality was witnessed both times and none changed; `DECLARED_NONIDENTITY_PRESERVED_WITNESSED` means all required inequalities persisted; `RELATION_CHANGED_WITNESSED` means at least one equality status differs. Those are statements only about the *declared finite rooted word pairs*, not a universal conjugacy claim. Under a local-owner-only scope, these are research claims about the explicitly constructed 27-state finite systems.

## Reproduced result

The same locally owned source holds revision 0 from law phi=(0,0,0), then revision 1 from phi=(0,1,2), both with identity state correspondence. The earlier owner-held revision remains immutable and addressable after replacement.

| Pair | Revision 0 endpoints | Revision 1 endpoints | Witness |
|---|---|---|---|
| `'' / AAA` | `(0,0,0) / (0,0,0)` | `(0,0,0) / (0,0,0)` | Equal in both |
| `BA / ABB` | `(1,1,0) / (1,1,0)` | `(1,1,0) / (1,1,2)` | Equality broken |

Independent edge observations: **7 in rev 0 and 7 in rev 1**; no new snapshot inherited the old cache. Zero observation allowance reports `SEARCHING`, not success. Subsequent zero-read replay confirms status if pins remain live and observations intact.

## Test evidence

Completed separately using Python unittest:

- `test_ab_chatbot_cross_pin_comparison`: 10 passed.
- `test_finite_cross_pin_relation`: 5 passed.
- `test_ab_chatbot_owner_pin_contract`: 10 passed.
- `test_ab_chatbot_provenance_contract`: 14 passed.
- `test_ab_chatbot_rule_change`: 14 passed.
- `test_ab_chatbot_mixed_obligations`: 12 passed.
- `test_ab_chatbot_language_bridge`: 35 passed.

**100/100 completed tests**, not a full historical regression sweep. GitHub CI was not verified. Standalone finite reference uses fully declared finite law tables and **does not authenticate remote sources**. This is scoped work, no new engine or implicit re-pin.

## Run

From this directory:

```bash
python -m unittest -q test_ab_chatbot_cross_pin_comparison.py test_finite_cross_pin_relation.py
python run_cross_pin_demo.py
```

## Next mathematical question

Can more than one separately witnessed cross-pin relation be joined into a compatible map **without** assuming that shared word endpoints identify all unseen states? Keep witnessed word histories and source versions distinct, and demand fresh bounded transition evidence for each additional comparison.
