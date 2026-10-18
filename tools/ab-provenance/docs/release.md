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
