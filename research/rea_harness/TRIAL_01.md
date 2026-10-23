# REA harness trial 01 — JavaScript import relations

Status: SOURCE-INSPECTED / NATIVE-EXECUTION-NOT-YET-WITNESSED.

Source: https://github.com/morluto/rea (original REA, not A/B REA). Public README and docs/cli.md specify `analyze-javascript-application PATH --json`; its output includes modules, imports, Electron boundaries and evidence. Pin the exact source revision and npm version before execution.

## Finite subject

Operation: given an extracted JavaScript application directory, identify source modules and their import edges. Keep output facts separate from guesses. The goal is an independently running Tracework-native operation, not wrapping REA.

## First comparison fixture

Create a local directory containing:
- `main.js`: `import { answer } from "./lib.js"; console.log(answer);`
- `lib.js`: `export const answer = 42;`
- `unused.js`: `export const unused = true;`

Native REA witness: run the documented CLI against the absolute fixture directory and retain raw JSON, exit status, stdout/stderr, source revision, runtime versions, and file hashes. Do not infer output schema before running it.

Compare against a Tracework-side independently extracted relation set: observed modules, exact import edge from main.js to lib.js, absence of an import edge to unused.js, and any evidence locations. An unimported file's module inclusion is a separate observed question, not a predeclared invariant.

## Nesting and stopping

When a mismatch appears, retain its precise wall and open only the discriminating nested comparison needed (static import, dynamic import, resolution, parse failure, path boundary, or evidence location). A worker may be assigned only through existing admission and handoff mechanisms. Retain source identity, parent referent, observations and unknowns.

Stop source investigation **for this operation** when a successful REA witness, relevant negative/boundary witness, finite input/output relation, native dependencies, and a discriminating independent test are available. Then construct and test the native operation. Stop is a construction threshold, not proof of universal equivalence.

## Present wall

REA native execution has not been witnessed in this trial. No success, module count, or comparison result is claimed. Current execution environment reports Node 22.16.0, below the source README's listed supported Node versions; use a supported runtime before testing.

See [Universal Harness](../../UNIVERSAL_HARNESS.md) and [Tracework](../../TRACEWORK.md).
