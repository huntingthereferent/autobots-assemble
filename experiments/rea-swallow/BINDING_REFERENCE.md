# Movement 4 — reference-aware structural fingerprint experiment

Full source remains pinned as REA MIT git submodule at `f0b9ef34c404c1c65f8167502db972b0bd708403`. In a separate `ProcessWorkstation` `control` and `experimental` edition, `javascriptAstFingerprint.ts` gains the experimental `fingerprintJavaScriptAstParameterRelations` function.

The **shipped** `babel-ast-v3` is preserved. This is **not** a silent change to REA's public matching algorithm. The candidate name `babel-ast-parameter-relations-v1` declares a separate representation and returns `null` for unsupported nested lexical scope, destructuring, parameter shadowing or complex declarations.

The first exact experiment examines **16** possible four-position sequences of two formal parameters. All 16 have the same original REA v3 fingerprint but produce 16 distinct output arrays on `select(11,29)`. A binding-aware fingerprint should distinguish all 16 choices while keeping 16 consistent formal-parameter renames equivalent. Separate counterexamples cover subtraction operand choice and local initializer selection. Existing REA fingerprint/version-matching native tests plus a TS typecheck must still pass. This does not establish arbitrary JavaScript semantic equivalence, and no permanent integration is claimed.

See `.github/workflows/rea-swallow-binding.yml` and GitHub Actions artifacts for actual outcome.
