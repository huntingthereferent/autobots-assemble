# Finite Correspondence Research

<!-- integrated-cp20-cp30-source-recovered -->
**Current integrated-source location:** [Restored CP20–CP30 historical baseline and deltas](integrated/README.md), with hash-checked reconstruction of the original 201-file CP20 archive through the 281-file CP30 archive. The original separate ZIPs remain historical integrity evidence; their recovered source can now be rebuilt from this Git checkout. This source restoration does **not** assert that every owner-backed integrated regression test has passed.


The ongoing investigation of **finite witnessed correspondence**, recorded one checkpoint at a time. It examines exact transformations and evidence-dependent continuation, without presupposing a conversational interface or autonomous application. A/B labels here are scoped finite generators, not a replacement name for the language referent.

## Checkpoints

| CP | Question | Observed or reported result |
| --- | --- | --- |
| [20](checkpoints/20-two-hop-transport/README.md) | Two-hop transport | 6 paired states, 5 edges, 2/2 requirements |
| [21](checkpoints/21-two-route-comparison/README.md) | Two-route comparison | Independent routes can disagree without either witnessed chain being erased. |
| [22](checkpoints/22-source-change-propagation/README.md) | Source-change propagation | Changed source evidence withdraws only the dependent route. |
| [23](checkpoints/23-source-replacement-recovery/README.md) | Source replacement and recovery | A new pinned replacement can produce either agreement or conflict. |
| [24](checkpoints/24-selective-propagation/README.md) | Selective propagation | Unrelated comparison records stay cached until checked for use. |
| [25](checkpoints/25-route-selective-refresh/README.md) | Route-selective refresh | A changed route can be rechecked without replaying its unaffected neighbor. |
| [26](checkpoints/26-route-bound-task/README.md) | Route-specific task | A task checks only its selected route, even if the other route is withdrawn. |
| [27](checkpoints/27-multi-task-dependency/README.md) | Multi-task dependencies | Finite dependency selector |
| [28](checkpoints/28-shared-route-certificate/README.md) | Shared route certificate | One fresh route audit serves distinct task requirements; 35 targeted checks |
| [29](checkpoints/29-certificate-handoff/README.md) | Cross-invocation handoff | Historical receipt requires a new audit; 67 targeted checks |
| [30](checkpoints/30-independent-process-identity/README.md) | Independent-process source attestation | Three signed scopes, separate verifier, fresh two-pass route audit; 100 targeted checks |

Open a checkpoint to see its **record, code, tests, demonstration, and result files**. Reports retain their stated scope: historical targeted tests are not a full CI pass; hashes are identifiers, not authentication.

**Source boundary:** The full original CP20–CP30 integrated source is now available in [the recovered historical archive](integrated/README.md) on `main`: 201 baseline files and ten eight-file deltas, 281 original files total. CP-27–CP-30 also retain their standalone finite references and checkpoint evidence. The integrated recovery workflow verified original file identities, reconstructed CP30, and passed a selected test scope; the full historical owner-backed suite is not yet verified as a whole. CP30's cryptographic tests need the `cryptography` package.

[Full provenance and archive hashes](../PROVENANCE.md) · [Earlier research index](../research-history.md) · [Language referent](../../../../LANGUAGE_REFERENT.md)
