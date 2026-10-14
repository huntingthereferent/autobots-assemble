# Finite Correspondence Research

The ongoing investigation of **finite witnessed correspondence**, recorded one checkpoint at a time. It examines exact transformations and evidence-dependent continuation, rather than assuming a conversational interface or autonomous chatbot. A/B labels here are scoped finite generators, not a replacement name for the language referent.

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

**Source boundary:** Stages 21–26 have their eight individual patch-recovered source/evidence files here. Stage 20's full 201-file local baseline is preserved in the original archive, but its entire integrated package is not yet committed to GitHub. Stages 27–30 have independently published finite references in the parent directory; CP-28 through CP-30 checkpoint folders also include their integrated adapters and tests. CP-30 cryptographic tests require the Python cryptography package. Consequently the integrated owner-backed stages still need that baseline to execute from a clean GitHub checkout.

[Full provenance and archive hashes](../PROVENANCE.md) · [Earlier research index](../research-history.md) · [Language referent](../../../../LANGUAGE_REFERENT.md)
