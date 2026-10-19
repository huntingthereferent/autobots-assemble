# WORLD — playable temporal evidence blueprint for NIH Phase 1 concept / planned Phase 2

**Research date:** 2026-10-19. **Source branch:** `world/w13-two-world-advance-contract-20261016`.

## Correct referent and design authority

The **Phase 2 implementation blueprint belongs inside the Phase 1 concept and feasibility design**. It is not a separate official Phase 2 submission, an NIH award, or a clinical result. The source is the original owner-authored `NIH_Phase1_Concept_DRAFT.pdf` (October 18, 2026), particularly sections 2, 2.1, 2.2, 3, 4 and 5.

The WORLD design was constructed over the **exact original existing W13 two-world game**, not an invented replacement or an extra temporal research task. The original [WORLD_W13_MOVEMENT_01.md](WORLD_W13_MOVEMENT_01.md) contract and source fixture remain byte-preserved:

- `first-room`: 4 × 3, start (0,1), target (2,1); native `right, interact`.
- Explicit `advance` only **after first-world collection**, retaining every original W12 before/action/after record.
- `second-room`: 3 × 3, start (0,0), target (1,1); native `right, interact`.
- Original room reset and strict W13 session receipt preserved, independently replayed by the pinned source's W12/W13 native witness. **No new native twelve-job journal** is admitted by this build.

## The working world

**Open locally:** `docs/world_phase1_phase2_blueprint.html`. This is a single self-contained playable HTML page (no external scripts or API keys).

The unchanged existing W13 two-room controls remain available. A source-qualified temporal graph panel sits within the same playable page:

1. **Source world (Room 1):** choose a fictional assertion; change its literal value, `valid_from`, exclusive `valid_to` and modeled `known_day`. Add/remove fictional source assertions (bounded 2–32). The displayed graph is rebuilt from the actual values. **Original registered source records are immutable**: source owner IDs, version URLs, page digests and owner-posted days cannot be edited into a different historical claim.
2. **Advance:** collects Room 1's target and crosses the **existing** explicit W13 boundary. No 'advance' is emitted to the W12 local transition; local source history stays intact.
3. **Query / witness world (Room 2):** select a knowledge cutoff K and valid-time target V. Compare the temporal eligible/withheld/outside-validity observations with a naive static valid-fact union. Inspect future-evidence leakage. For real owner records, show **unresolved validity** and **conditional date-only owner posting state**, rather than inventing historical `known_at` instants.
4. **Graph projection:** six visible relational lanes—source, assertion, valid interval, availability, query, witness. Five logical clocks—valid/effective, event, submission, public posting and observation—are independently displayed for the selected assertion. Source identity is never inferred from a pixel or grid coordinate. The map's visual scale can change from 3 to 12 without changing ontology semantics or the source W13 room sizes.
5. **Export:** `Export blueprint/session receipt` saves the complete browser-reported W13 room evidence together with source records, changed assertions, query result, chronological query history, graph nodes and the admission disclaimer.

**Canonical data:** `network/tests/fixtures/world_nih_phase1_phase2_blueprint_v1.json`. **Native bounded model:** `systems/workspace/world_temporal_blueprint.py`. **Actual interactive browser:** `docs/world_phase1_phase2_blueprint.html`. **Independent browser/native verifier:** `scripts/verify_world_phase1_phase2_blueprint_browser.py`. **Negative tests:** `network/tests/test_world_nih_blueprint.py`.

## What is controlled versus not asserted

The exact synthetic source example from the Phase 1 draft demonstrates `Q(K,V)` and a future leak:

| Synthetic assertion | Valid interval | Modeled known day | Result at K=2026-01-04, V=2026-01-04 |
|---|---|---|---|
| `prior-note` | [2026-01-01, 2026-01-10) | 2026-01-01 | Eligible |
| `delayed-result` | [2026-01-03, 2026-01-10) | 2026-01-05 | Withheld as future information |

Static union would include both. Editing the second observation's `known_day` to 2026-01-03 changes the **actual executable query answer** to include both, without changing any W13 room coordinates. A stricter knowledge cutoff changes the result back. Additional fictional source assertions can grow the graph, again independently of the physical W13 4×3 and 3×3 maps.

The **real** registry sample uses separately witnessed original ClinicalTrials.gov `NCT00001756` V94 and V105: both source-status fields `RECRUITING`, owner-labelled `Last Update Posted` days 2019-08-02 / 2019-11-25, and pinned browser-text SHA-256. Their *historical valid-time bounds* and actual first-public UTC *instants* were not authenticated. Real-mode temporal public-knowledge eligibility therefore stays **unresolved**, not forced into a synthetic `known_day`.

The W13 grid world and 2-D graph layout are interface constructions, **not** the dimensionality of the biomedical KG. The initial native query is deliberately bounded to 2–32 fictional assertions, rather than claiming NIH-scale graph density or complete ontology coverage. The current semantic model is a deterministic source-qualified graph/query implementation with independent Python replay; its visual graph **is not yet an RDF/OWL materializer integrated into the Phase 1 original ontology worker**. That interoperability step requires separate source-owned native build and OWL-level witness. No general embeddings, clinical causal inference, full historical-version capture, authenticated browser origin, official competition review or NIH Phase 2 eligibility is claimed.

## Verification and continuation

[WORLD blueprint BUILD workflow](../../.github/workflows/world-nih-blueprint-build.yml) checks the original two-room contract against the blueprint, installs actual Chromium, executes the negative model tests and **plays the revised HTML in a browser**. It independently replays the exported original W13 receipt with the separately pinned reference source (commit `cbeea0e5994ac72674bc4e4e304405b5fff66dc2`), checks that the original JavaScript movement logic is unchanged, compares browser query results and graph nodes with the host-native Python model, tests edit/restore and frozen real metadata, and retains screenshot and evidence artifact.

Pass is evidence for this **bounded WORLD/BUILD blueprint** only; it does not automatically certify `GAME-W13-WORLDS` under its separate coordinator admission policy or change any original W12/W13 checkpoint. Preserve all earlier NIH Phase 2 and real-source evidence runs.

**Natural next engineering boundary:** materialize the controlled graph into independently validated RDF/OWL-Time/PROV/Biolink assertions, then evaluate topology/provenance/triple counts against Phase 1 criteria. Do not silently attribute graph observations to original clinical public-posting events.
