# A/B release assembly

The shipped artifact is an **A/B release candidate**, not a repackaging of
the original referent. REA remains real source under investigation. It
does not become the name, interface or license of A/B.

A release passes only after A/B verifies:

- Five actual source-edition preparation and application records, including
  exact command logs, return codes and SHA-256 identities.
- A passing source-level native REA Vitest suite, TypeScript typecheck,
  and original source diff check, with unchanged evidence files.
- A coherent original source-provenance chain from the real execution.
- A built A/B wheel and sdist containing the **same A/B LICENSE** as the root
  repository. They must not embed or relabel REA's source license.
- Original docs, changelog, manifest, offline HTML visual, source ledger,
  native test logs, and a machine-readable file-hash release manifest.

Build with the [quickstart](quickstart.md). The command is:

~~~sh
ab ship --repo-root . --evidence <real-run-dir> \
   --dist <ab-wheel-and-sdist-dir> --out <new-release-dir>
~~~

It refuses incomplete evidence, changed source logs, missing product
license, malformed Python distributions, and overwrite of an existing
release candidate. It does not publish anything to PyPI or GitHub.

The upstream repository remains MIT on its own original source; A/B
original code is All Rights Reserved. The product artifact contains
THIRD_PARTY_NOTICES.md so the distinction is inspectable, without
transferring the upstream license onto A/B.

## Does it make the same thing? Original-source comparison

A/B never decides this by comparing screenshots or license text. The paired
experiment first runs three existing pinned REA native JavaScript suites
**before** any source change, preserving the original test identities,
results and source hashes. After ProcessWorkstation source corrections,
the same original upstream cases run again with their test files unchanged.

The generated comparison distinguishes:
- Matched original test behavior (22 assertions in the first native run).
- Actual changed REA TypeScript source.
- Original REA CLI/MCP and other provider operations that A/B does NOT yet
  reproduce.
- Original A/B documentation (not upstream documentation copied).
- REA's independent MIT rights and the A/B product license.

The release gate requires the before/after reports and embeds both raw native
test result files, the frozen baseline, the comparison JSON and a readable
comparison report. It blocks shipping if they are missing, changed, or
falsely claim the full original REA was reconstructed.

A matching regression suite is evidence only for those tested cases.
It does not establish full behavioral equivalence, provider parity, or
a universal regrounding capability.
