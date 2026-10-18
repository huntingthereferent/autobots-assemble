# A/B Quickstart — real source and release candidate

First supported source: original morluto/rea, pinned at
f0b9ef34c404c1c65f8167502db972b0bd708403.

Prerequisites: Python 3.11, Node.js 24, Git, and a disposable clone with
the correct submodule. This command operates on actual REA source and requires
explicit permission to modify a clean working checkout.

From the A/B repository root:

~~~sh
git submodule update --init experiments/rea-swallow/upstream
python -m pip install ./tools/ab-provenance
npm --prefix experiments/rea-swallow/upstream ci

ab source

# Freeze the original tests BEFORE changing the source.
python tools/ab-provenance/comparison/paired_reference.py baseline \
  --rea experiments/rea-swallow/upstream \
  --out runtime/data/ab-source-tool/original

ab swallow repo --allow-source-edit --repo-root . \
  --out runtime/data/ab-source-tool/first-pass

# Rerun the unchanged original cases against the corrected source.
python tools/ab-provenance/comparison/paired_reference.py compare \
  --rea experiments/rea-swallow/upstream \
  --ab-tool tools/ab-provenance \
  --baseline runtime/data/ab-source-tool/original \
  --out runtime/data/ab-source-tool/first-pass/comparison

# Retain the original witness alongside the paired result for the ship gate.
cp runtime/data/ab-source-tool/original/baseline.json \
  runtime/data/ab-source-tool/first-pass/comparison/
cp runtime/data/ab-source-tool/original/original-vitest.json \
  runtime/data/ab-source-tool/first-pass/comparison/
cp runtime/data/ab-source-tool/original/original-vitest.log \
  runtime/data/ab-source-tool/first-pass/comparison/

ab inspect runtime/data/ab-source-tool/first-pass/source-provenance.json
ab ancestors runtime/data/ab-source-tool/first-pass/source-provenance.json \
  --target "A/B source stage 5: checkpoint"
ab render runtime/data/ab-source-tool/first-pass/source-provenance.json \
  -o runtime/data/ab-source-tool/first-pass/source-provenance.html

python -m pip install build
python -m build tools/ab-provenance \
  --outdir runtime/data/ab-source-tool/first-pass/dist

ab ship --repo-root . \
  --evidence runtime/data/ab-source-tool/first-pass \
  --dist runtime/data/ab-source-tool/first-pass/dist \
  --out runtime/data/ab-source-tool/shipped-0.1.0
~~~

Use fresh output directories for each experiment; preserve the baseline and
start from a clean disposable source checkout. The installed wheel provides
the CLI; source transformation also requires this repository and its
ProcessWorkstation scripts. The wheel alone is not a standalone source runner.

The release directory contains an original A/B bundle and manifest.
Check the manifest before using any reported source evidence. This tool
does not silently rewrite an existing source checkout, overwrite a release,
upload private evidence or publish to GitHub.

The A/B product license is All Rights Reserved. Upstream REA keeps its own
MIT terms on upstream REA material; it is NOT included in the A/B bundle.
The limited JavaScript adapter must not be described as support for every
possible repository.
