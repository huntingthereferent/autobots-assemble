# Movement 8 — evidence-based A/B observation refinement

The real original REA matcher (`src/domain/javascript/javascriptApplicationVersionKeys.ts`) is retained as a pinned `ProcessWorkstation` control. An experimental source edition adds `refineJavaScriptApplicationPairByObservations`. The original upstream `matchJavaScriptApplicationVersions`, prior research editions and `main` are unchanged.

**Question.** Does adding an *observed input/output relationship* split a class of programs that REA's rename-resistant structural fingerprint treats as one? Is the separation monotonic while uncertainty remains explicit?

An independent, bounded VM harness executes only the exact 16 source strings authored in the test fixture. The REA library **does not execute untrusted source**. Each observation records an input digest, context ID and returned/thrown/unknown outcome. Only the same context and same input digest may establish a difference. Missing/ambiguous/unresolved contexts cannot. On 256 ordered pair comparisons, a first context using arguments (11,11) cannot distinguish any pair; a second context using (11,29) should distinguish the 240 pairs of different reference patterns, leaving 16 self-pairs **undetermined**, not declared equivalent. Adding evidence never turns an observed distinction back into a declaration of sameness.

This is bounded **observation refinement**, not a universal semantics engine, a proof of equivalence, or a promise that the runtime covers all environmental effects. The experiment intentionally does not inject live execution into REA's static reverse-engineering pipeline. The source version, patch, native tests and typecheck are auditable in CI.
