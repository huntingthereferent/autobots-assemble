# Native source-edit feedback — bounded workstation worker

This is **real ProcessWorkstation source editing**, not another mock dashboard. The registered native subprocess reads an independently detected defect in the [factory simulation worker](factory_machine_worker.py), proposes one precise repair, and returns it to the host. The workstation creates a candidate edition, **changes its source code**, runs an independent behavioral test and creates a distinct successor edition only after PASS.

The specific defect: a string containing only spaces is currently accepted as a factory product name. The proposal changes the validation condition from checking only empty strings to also rejecting whitespace-only product names in the private edition. Neither the canonical repo source nor previously recorded worker editions are rewritten.

## Reproduce

From the repository root using Python 3.12 or later:

```sh
python -m unittest -v network.tests.test_process_workstation network.tests.test_workstation_edit_cycle

# Authorized opt-in, private working directory OUTSIDE the repository
python -m systems.workspace.workstation_edit_cycle \
  --data-dir /tmp/verified-workstation \
  --run-id factory-validation-001 \
  --execute \
  --output /tmp/verified-workstation/receipt.json
```

The native proposer and independent verifier run as different Python child processes. The source bytes are copied through the existing `ProcessWorkstation` copy/branch contract. Failures cannot create an accepted descendant, and repeated IDs do not quietly rerun the same action. The independent checks exercise valid product output, invalid quantity/material, and the newly observed invalid blank product.

This is a **source-native bounded edit**, not a freeform code-writing model, automatic bug-finding across a repository, a background scheduler, a secure sandbox, or a verified release. Any untrusted proposer would need stronger isolation and independently pinned source/verifier contracts. `-I` limits Python's interpreter environment but is not an OS sandbox.

The generated private `receipt.json` records the original observation, proposer PID, source hashes, candidate hash, and independent verifier outcome. The CI workflow saves that bounded receipt as a GitHub Actions artifact; a passing CI is evidence of the specific test only.

## Relation to the visual layer

The [native workstation monitor](monitor.py) can now observe the worker edition family, original parent, edited candidate and accepted successor. [PR #62](https://github.com/huntingthereferent/autobots-assemble/pull/62) is a separate draft for projecting that same existing monitor into a public-safe visual. It must not call an accepted edition a running worker or mistake this one scoped repair for general autonomous code editing.
