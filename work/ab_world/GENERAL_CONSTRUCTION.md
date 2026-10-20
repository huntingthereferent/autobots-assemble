# General A/B world construction — executable boundary

The subject is **whatever is introduced**, not a preselected game, motor, geometry, or NIH-specific structure. Start with a bounded set of objects, declare only the relationships needed for the current investigation, record how they move or are revised, then compare recorded expectations with separately attributed observations. Continued movements can revise or withdraw a relation without changing earlier receipts.

The working implementation is construction.py. The separate verify_construction.py reconstructs the recorded changes through a distinct code path. This verifies ledger transitions, identities and provenance labels, **not** whether a claimed source emitted the data or whether mechanics are physically correct.

## Record contract

A plan declares one referent, an explicit record-capacity limit for objects, relations and steps, and a finite sequence of operations. These are **storage limits**, not the size, coordinate system, dimensions, or laws of the investigated world.

| Operation | Recorded effect |
| --- | --- |
| introduce | Introduce an object with arbitrary JSON state |
| connect | Relate two existing objects with a labeled, inspectable relationship |
| revise | Replace an object's state or revise a relationship's state |
| disconnect | Withdraw a relationship while preserving its earlier history |
| retire | Retire an object if no live relationship still points at it |
| observe | Store a separately attributed report about an existing object or relationship; do **not** overwrite its declared state |
| compare | Compare a cited observation with an expectation and retain MATCH or DIFFERENT |

Each operation carries a basis with a kind and source:

- **declared**: constructed input or proposed movement.
- **source-execution**: a reported result from an executable source; the source is named but is **not automatically reproduced** by this carrier.
- **external-report**: reported observation, such as an instrument export or historical source. Its existence and contents still require independent checks.

Source strings are **references, not authentication**. A claimed physical measurement is not elevated to a witnessed physical fact by selecting a label. This layer never asserts a physical object exists, a source is genuine, or a constraint actually governed the recorded movement. Domain-native solvers, hardware, clocks and external sources remain the authority for their own movements.

The receipt includes every complete operation, its effect, before/after state hashes, chained ancestry, terminal object/relation/observation/comparison state and an explicit evidence-depth boundary. A mismatch stays visible as a mismatch; it never silently updates the proposed object. Comparisons use exact JSON equality. Units remain as supplied, **not converted**; typed quantities, tolerances, uncertainty, geometry and physical laws belong to adapters that can justify them.

## Run the native example

From the repository root:

    python -m work.ab_world.construction --plan network/tests/fixtures/ab_world_construction_example.json > /tmp/ab-world-receipt.json
    python -m work.ab_world.construction --verify /tmp/ab-world-receipt.json
    python -m unittest -v network.tests.test_ab_world_construction

The fixture introduces two parts, declares a candidate relationship, revises a declared angle to 30 degrees, receives an **unverified** 29.8-degree report and retains the difference. A second native test constructs NIH-like temporal relationships using only timestamps and observations—without coordinates, mechanical bodies, a required 48-law set, or a renderer.

## Next movement toward the physical layer

Attach one **source-owned** movement or recorded observation from an existing investigation through this envelope. Then have the relevant original native source or physical instrument independently attest the emitted content, including input, source fingerprint, units, measurement uncertainty and timing. A visualization can consume the receipt read-only; it must not become the authority for physical movement.

The separate WORLD contact studies, W13, ARC, NIH Phase 1/2, World48 and their source histories are not altered by this construction. No GitHub job is implicitly admitted or dispatched. The A/B All Rights Reserved repository notice remains unchanged.

## First actual source handoff — W13

The W13-specific adapter in w13_source_handoff.py runs the existing native W13 game-construction source, first checks its intact action trace, then records its moves as source-attributed object revisions and observation events in the neutral A/B carrier. A separate W12 contract implementation computes independent expectations. A disagreement remains a DIFFERENT comparison; the source trace is not rewritten. The adapter is separate from the general construction code, so it does not make W13 rules, geometry, action vocabulary or turn counts universal.

    python -m work.ab_world.w13_source_handoff
    python -m unittest -v network.tests.test_ab_world_w13_source_handoff

This is **real local native source execution**, not browser attribution and not a physical measurement. Recorded source SHA-256 binds the code bytes used for the adapter's run; neither a string source reference nor an unsigned hash authenticates a physical instrument or external party.

The next physical ingress should use the exact same neutral carrier with a separately checkable original source receipt, rather than deriving physical rules from the W13 adapter.
