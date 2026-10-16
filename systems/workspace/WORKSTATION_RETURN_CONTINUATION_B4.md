# B4 — Native feedback opens the next witnessed relationship

**Referent:** a verified source-native worker return should become useful
input to the workstation's *next movement*, not merely a completed job card.
This is a narrow follow-up to B2 and B3 in the same `RuntimeJournal`.

## Actual movement

1. B2 preserves A and B plus their independent sources and child identities.
2. B3 admits a native finite worker via `branch_help`, executes through the
   existing `controls.run_job`, independently re-verifies its bounded output,
   and records one `WORKSTATION_NATIVE_RESULT_VERIFIED` event against the
   exact child lane.
3. B4 reopens the complete source-bound return: exact job, opening, metadata,
   current SHA-256 worker edition, native output and evidence. It calls the
   existing `verify_return` **and** `reverify_job` and checks the output,
   evidence and edition fingerprints against B3's saved event.
4. A domain-specific, registered `NextMovement` provider decides whether
   the *verified content* exposes a new branch worth investigating. A separate
   source-sensitive `verify_relation` callback checks the meaning of that
   proposed movement. There is **no generic NLP similarity rule**.
5. Only then does B4 record an `WORKSTATION_MOVEMENT_OBSERVED` event linked
   by digest to the native job, plus a
   `WORKSTATION_RETURN_RELATION_ADMITTED` provenance event.
6. `next_pass()` reruns native return verification and domain-relation
   admission before delegating to B2's `tick` with a verification override.
   B2 either creates a new **coordination** lane for a registered source
   capability or records `OPEN_UNSTAFFED`, preserving the opening.
7. New child lanes are now addressable by their actual durable identity, so
   they can produce later observations in the same journal. Restart and
   repeated invoked passes preserve identity without duplicating branches.

## First scoped provider

`finite_prefilter_next` is deliberately narrow:

- Recovered `CONTRADICTED` verdicts exclude their specific tested finite
  correspondence candidates.
- `NOT_CONTRADICTED` and `UNDECIDED` do **not** establish any newly
  witnessed source edge. The only justified next request is to obtain
  **owner-native evidence** of the unresolved candidate.
- The needed capability is
  `owner-native-correspondence-witness`. No such native execution adapter is
  registered yet. The workstation can open its need but cannot fabricate
  either the worker or the witness.
- This policy does **not** turn James's language referent into a scheduler,
  prove a universal A/B theorem, or use a finite toy-generator label as a
  language-level definition.

## Verified vs still open

`network/tests/test_workstation_return_continuation.py` uses B3's actual
source-pinned finite subprocess and native verifier in an isolated temporary
workstation, with a declared source-sensitive finite-domain follow-up policy.
Tests include successful derivation, duplicate-free restart, original-witness
withdrawal, source tampering, invalid cross-domain providers, missing relation
proof, and refusal to invent a two-lane join.

**Still open:** the initial A/B branch opportunity is a test fixture;
the owner-native observation capability is not staffed; true pairwise lane
collisions require independent join evidence; the W13 game worker and
independent browser/WITNESS contracts remain on a separate branch. No
always-on autonomous model-worker loop is demonstrated. Sequential journaling
has been tested; concurrent writer locking has not.

## Reproduction

```bash
python -m pip install 'cryptography>=45,<47'
python -m unittest -v \
  network.tests.test_workstation_harness \
  network.tests.test_workstation_native_feedback_integration \
  network.tests.test_workstation_return_continuation \
  network.tests.test_agent_lineage \
  network.tests.test_branch_help
```

Next: add a genuine owner-native observation adapter that can satisfy the
open capability, and preserve independent connection provenance when two
real branches warrant a connecting observer. Do not treat a matching label
as a collision proof.
