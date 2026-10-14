# Stage 29 — Cross-invocation route-certificate handoff (October 13, 2026)

**Referent.** Continue the owner-pinned finite correspondence process from CP-0028. Does an earlier selected-route certificate survive a move into a new caller invocation without borrowing the earlier task's obligations or treating historical proof as current? The A/B labels remain local operators in an experiment; the language referent is not reduced to them.

## Witnessed local result

Yes, **as an explicitly limited and revalidated reference**. CP-0029 introduces a small JSON `selected-route-handoff/v1` envelope containing only a route label, exact pinned route fingerprint, a digest of witnessed paired states/edges/links, a digest of source evidence, and an integrity checksum. The sender first executes the existing twice-replayed owner-bound route audit, then issues the receipt; the receipt carries **no individual task fingerprint, goal, or required edge**.

On the next caller invocation, `accept_handoff(receipt, named_tasks)` rejects malformed or mismatched receipts, checks that every bound task selects the identical in-process route object, and **reruns the full two-pass owner/pin audit**. Only when the witness and source evidence digests still match does it evaluate *each receiving task's own admitted obligations*. Two different left-route tasks complete, and a third task requesting a right-only edge is left `ROUTE_TASK_REQUIREMENTS_UNPROVED` rather than inheriting proof from elsewhere. One fresh receiver route audit makes two route replay calls, not two audit pairs. A *second* receive of the same receipt incurs another two replay calls. The prior success is never itself proof for a later call.

| Case | Result |
| --- | --- |
| Fresh receipt, same pinned left route, two independently declared tasks | `HANDOFF_FRESHLY_REVALIDATED`, 2/2 tasks individually complete |
| Add a left task requesting a right-only edge | That task remains `ROUTE_TASK_REQUIREMENTS_UNPROVED`; other tasks unaffected |
| Neighboring right route owner pin revoked | Left receipt can still revalidate |
| Selected owner pin revoked or source no longer auditable | `HANDOFF_REAUDIT_UNPROVED`, zero usable tasks |
| Receipt digest changed, even with recomputed checksum | `HANDOFF_EVIDENCE_CHANGED`, zero usable tasks |
| Task declaration mutated after admission | `TASK_DECLARATION_CHANGED`, no task authorized |
| Selected source moves during the new audit | `SOURCE_MOVED_DURING_HANDOFF`, no task authorized |
| Receipt reused on another call | New twice-replayed audit required; nothing silently cached |

This result transfers a **description of historical evidence**, not authority to skip a new audit. Receipt SHA-256 is only an accidental-integrity and comparison mechanism; it is **not an authenticated signature** and cannot establish trust in an unknown sender. The owner registry is an in-process synthetic owner-pinning fixture. No independent remote trust, cross-process owner credential validation, background polling, or new physical-system observation is claimed. No source edges or states were added.

## Completed tests

**67 of 67 targeted local tests passed** in one completed command: 16 new owner-backed integration cases, 16 new pure finite cases, 13 CP-28 owner-backed regressions, 14 CP-28 finite regressions, and 8 CP-27 finite regressions. These are real completed tests, not a full historical suite or a claim of GitHub CI.

From the extracted complete Stage-29 ZIP, use:

```sh
python run_certificate_handoff_demo.py
python -m unittest -q test_ab_chatbot_certificate_handoff.HandoffOwnerTests test_finite_certificate_handoff.FiniteHandoffTests test_ab_chatbot_shared_route_certificates.SharedRouteTaskTests test_finite_shared_route_certificate.SharedFiniteTests test_finite_multi_task_dependency.FiniteMultiTaskDependencyTests
```

`CERTIFICATE_HANDOFF_RESULTS.json` is the local demo's exact output; `CERTIFICATE_HANDOFF_REGRESSION.json` identifies the completed suites and accounting. `finite_certificate_handoff.py` independently checks declared complete finite laws and pins but does not authenticate live owners.

## Package and provenance

The complete Stage-29 ZIP contains 273 entries: **all 265 Stage-28 original contents remain byte-for-byte identical**, with exactly eight CP-29 files appended: integrated handoff, owner-backed tests, finite reference, finite tests, executable demo, recorded result, regression accounting and this record. The Stage-28 ZIP is not overwritten.

The compact GitHub CP-29 folder exposes the eight new source/evidence files. The integrated CP-29 code still depends on the original Stage-20 local owner-backed baseline that is not fully published on GitHub; a clean GitHub checkout alone does **not** reproduce the full integration test. The independent finite reference is additionally available in the parent correspondence process directory for GitHub CI.

**Next supported experiment:** A truly independent-process receiving boundary would require explicit independently verifiable owner credentials and source pin attestations. Test a minimal export/import identity contract and demonstrate failure against source substitution before claiming that broader transfer; do not treat a SHA-256 receipt as an authentication token.
