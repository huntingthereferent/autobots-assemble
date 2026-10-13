# Joint rooted histories across separately pinned revisions — October 13, 2026

**Current referent:** Can the current finite mathematical A/B chatbot join several independently replayed action-word histories into a single partial state correspondence **without assuming unobserved edges**? Under the declared source laws, yes precisely when their recorded prefix-state pair assignments are mutually injective and agree on shared states.

The in-process integration is `ab_chatbot_cross_pin_join.py` in the separately attached full Python archive. It composes the preexisting pinned-owner `CrossPinComparison`: every explicit word is independently replayed in the old and new owner-held historical snapshots, with version checks, owner pins, retained-edge re-audits and bounded observation. It then checks the union of prefix-state pairs and admits **only actual traversed labeled transitions**. No greedy extension or unconstrained transport is performed.

## Local executed examples

1. **Compatible:** Old phi=(0,0,0), new phi=(0,1,2), words `A` and `BAA` produce `JOINT_PARTIAL_CORRESPONDENCE_WITNESSED`: **5 state pairs, 4 admitted edges**, with 4 unique old and 4 new observed owner transitions. Note that 5 state pairs does not imply 10 admitted edges.
2. **Source-state collision:** Same laws, individually legitimate histories `A` and `BAB`. Both old words reach **(1,0,0)**; the new words reach **(1,0,0)** and **(1,0,1)**. A forward partial mapping assigning one old state two new images cannot exist. Status `JOINT_RELATION_CONFLICT_WITNESSED`, carrying the exact separating word prefixes, old/new endpoints and equality flags.
3. **Target-state collision:** Old phi=(0,0,1), new phi=(0,0,0), histories `B` and `ABBABA`. Two distinct old prefix endpoints have identical new endpoints. Reverse injectivity fails with a distinct replayable certificate.
4. **Three-word compatible control:** Old phi=(0,0,1), new phi=(0,0,0), `ABAA`, `ABBABA` and `A` preserve **8 paired states** without claiming the additional greedy extension used in earlier experiments.

## Interface

    {
      "required_owner_pins": {"old": "<registry-issued-token>", "new": "<registry-issued-token>"},
      "join_words": ["A", "BAA"]
    }

2..8 distinct nonempty A/B words up to length 12. The two pins are separate; source labels or digests cannot create local evidence. No unrelated goal or source constraints are inferred.

Missing owner binding yields OWNER_PIN_UNPROVED, modified version yields UNKNOWN_VERSION, a retained-edge mismatch yields WALL_OBSERVATION, and insufficient budget yields SEARCHING or UNKNOWN_BUDGET. Every revisit separately replays cached historical witnesses; no successful pairing is returned on a wall, revision change, or withdrawal. The join operation cannot assert full-system conjugacy.

## Reproduction and file boundary

Full `ab_chatbot_cross_pin_join_2026-10-13.zip` (SHA-256 `2522daacfdc57c13a05a45f3ce9adc29ccbf029790597fe36f57671203322b53`) contains **161 files**, retaining all **153 files** from `ab_chatbot_cross_pin_comparison_2026-10-13.zip` byte-for-byte. Eight additions: integrated join source and 10 tests, independent finite-law checker and 5 tests, demo, result JSON, regression JSON, technical README.

**110 local tests passed** across separately completed module invocations: new join 10, new standalone finite 5, old cross-pin comparison 10, owner pin 10, provenance 14, rule change 14, mixed obligations 12, language bridge 35. Full historical suite was **not** run to completion, and GitHub CI is **not** claimed.

The GitHub sidecar `finite_cross_pin_join.py` is an independent **complete-law checker**, not a source-authentication or HTTP owner implementation. To replay:

    cd work/arc_like_maze/chatbot
    python finite_cross_pin_join.py
    python -m unittest -q test_finite_cross_pin_join.py

A/B remains James's language for relational movement; the two finite operators designated A and B in the toy model are only scoped formal generators.

**Next:** Determine whether an expressly requested task can consume one already verified joint correspondence without extending its admitted edge set and preserve its collision counterexamples as historical evidence. Maintain the unrelated active Continuity project pointer (`state/current.json`).
