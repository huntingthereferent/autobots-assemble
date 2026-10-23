# Cross-object source lineage — bounded test

**Question:** when a structurally accepted public-source metadata receipt becomes a research-lane handoff, does the handoff retain enough provenance to identify the exact observation it accepted?

## Test boundary

This experiment covers the transition from one metadata receipt object to one lane source record. It preserves the provider URL, observation timestamp, HTTP status, source-response hash, and a deterministic SHA-256 fingerprint of the canonical receipt JSON. It also checks that a receipt from one source does not activate an unrelated lane and that an invalid receipt cannot emit accepted-lineage fields.

The fingerprint is computed over JSON serialized with sorted keys, compact separators, and UTF-8 encoding. It identifies the receipt representation; it is not a digital signature and does not independently authenticate who produced the receipt.

## Expected invariant

An accepted receipt can make a lane's **source feed** ready, but it must not change the scientific state from `NOT_TESTED` or increment the experiment count. Metadata identity and scientific evidence remain separate objects.

## Reproduction

```sh
python -m unittest research.testing_lanes.test_cross_object_source_lineage -v
python -m unittest discover -s research/testing_lanes -p 'test_*.py' -v
```

This is a software-integrity test over controlled receipts. It does not test the scientific claims represented by any source and does not establish a universal engineering mechanism.
