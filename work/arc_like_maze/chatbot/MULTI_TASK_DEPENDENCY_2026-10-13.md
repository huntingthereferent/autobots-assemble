# Stage 27 — selective propagation across route-bound tasks (October 13, 2026)

**Referent:** Multiple separately declared tasks can share one or more pinned finite transport source pairs. When the surrounding source record changes, only tasks that depend on that exact pair are selected for renewed proof. The tasks still have distinct requirements and cannot share obligations merely because they share source objects.

## Executed finite and integrated results

In the full local owner-backed prototype, three tasks attach to two different route certificates that share donor and final scopes. Two tasks use the left middle scope; one task uses the independently pinned right middle scope.

- Idle: zero task replay; all results explicitly cached, not new proof.
- Right middle source pin revoked: only the right-route task re-audited and withdrawn; both left tasks remain historical/cached. Explicit proof-for-use of a left task independently succeeds.
- Left middle pin revoked: the two left tasks re-audited; the right task was skipped.
- Shared donor pin or final revision changed: all three tasks re-audited.
- A source moving during an audit invalidates fresh status of all tasks dependent on it, including an earlier pass in that batch.
- Substituting a task obligation or route object is not admitted as the original bound task. New owner head does not invalidate an unchanged historical pinned snapshot.

**Reported completed local targeted execution:** 127 passing tests (19 new integrated, 8 new independent finite, 100 targeted regression tests). The prior 249-file archive is preserved byte-for-byte inside a new **257-file** locally packaged ZIP, `ab_chatbot_multi_task_dependency_2026-10-13.zip`, SHA-256 `03e3a0b89fb477b14c6b09e769e0d3515a004ebe9bf116f677cda86ea65c7a94`.

## GitHub reproduction

```sh
python finite_multi_task_dependency.py
python -m unittest -q test_finite_multi_task_dependency.FiniteMultiTaskDependencyTests
```

The finite dependency checker and its tests in this directory are a pure reference for selecting which tasks need replay. **They do not audit remote owner identities, run the integrated chatbot, or certify any skipped task.** The 257-file complete owner-bound chatbot, its 19 integration tests, JSON replay and targeted regression records are separately retained in the local ZIP; their successful local runs are not new GitHub Actions evidence.

The language referent is not reduced to these finite A/B-labelled generators. The movement is supplied by externally changed source conditions and a caller invoking the finite checks; no autonomous polling is asserted.

**Next possible movement:** A single fresh verified route certificate reused to check multiple differently declared tasks, with independent task obligations and exact owner identity still enforced. That optimization is not implemented here.
