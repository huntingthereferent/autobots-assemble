# A/B source absorption — actual pinned REA code

REA is the original code being analyzed, changed and tested by A/B. It is NOT inspiration for an unrelated viewer. This tool unifies the previously tested REA source-edition pipeline and the A/B provenance viewer.

The first actual functional slice is the JavaScript application matcher and investigation continuation. The existing ProcessWorkstation versions real REA TypeScript and preserves control/experimental provenance.

## Reproduce in a disposable git checkout

Python 3.11 and Node.js 24 are recommended. Real upstream REA has its own MIT license. This tool does not remove upstream copyright or relicense upstream code as original A/B.

~~~sh
git submodule update --init experiments/rea-swallow/upstream
python -m pip install ./tools/ab-provenance
ab source
cd experiments/rea-swallow/upstream
npm ci
cd ../../
ab swallow --allow-source-edit --repo-root . --out runtime/data/ab-source-tool/first-pass
ab inspect runtime/data/ab-source-tool/first-pass/source-provenance.json
ab ancestors runtime/data/ab-source-tool/first-pass/source-provenance.json --target "A/B source stage 5: checkpoint"
ab render runtime/data/ab-source-tool/first-pass/source-provenance.json -o runtime/data/ab-source-tool/first-pass/visual-provenance.html
~~~

The swallow operation **edits the pinned local REA worktree** through five existing ProcessWorkstation-backed source stages: observed difference, next test choice, novel source-derived test input, investigation advance with two-sided independent capture, and disk checkpoint/resumption. It then runs actual upstream native REA JavaScript matching tests, the checkpoint investigation test, a TypeScript typecheck and a source diff check. Input worktree must be pristine; prior worker editions are not overwritten. This is not arbitrary source evaluation or a general JS equivalence proof.

The resulting receipt includes exact commands, return codes, source hashes and native test logs; the accompanying provenance graph is derived from those local real source-edition receipts, not a fictional example. A failed native result leaves red evidence and an error, not success.

## What is still incomplete

Only a finite REA JavaScript investigation slice is integrated. REA has many binary, native, Android, web, MCP and other providers that are not absorbed into A/B by this change. Production REA's default CLI and MCP commands are not rerouted through A/B. No general A/B mathematical identification or independent verification of arbitrary source code is claimed. Future sources and providers enter through documented source-owned native adapters and verified transitions.

The original REA is MIT and its licensing terms remain valid. Original A/B code/docs are governed separately by the root All Rights Reserved notice; the latter does not cancel REA's MIT grant.
