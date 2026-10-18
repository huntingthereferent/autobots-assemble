# A/B Provenance

Installable, read-only tool for research provenance built from the repository's own contracts.

[morluto/rea](https://github.com/morluto/rea) is a packaging reference (standalone tool, commands and documentation), **not** the A/B engine. No REA source, docs or MIT-licensed assets are bundled. This original tool follows the repository [All Rights Reserved](../../LICENSE) notice.

## Install and use

Requires Python 3.10 or later. Run from the cloned repository:

~~~sh
python -m pip install ./tools/ab-provenance
ab-prov inspect tools/ab-provenance/examples/illustrative-provenance.json
ab-prov inspect tools/ab-provenance/examples/illustrative-provenance.json --graph
ab-prov ancestors tools/ab-provenance/examples/illustrative-provenance.json --target sample/provisional-claim
ab-prov render tools/ab-provenance/examples/illustrative-provenance.json -o /tmp/ab-prov.html
~~~

Open the generated HTML in a browser; no network connection, CDN, remote server or API keys required. The example is explicitly fictional and does not demonstrate independently verified research.

To view a real existing local workstation journal, select its authentic path:

~~~sh
ab-prov inspect --journal runtime/data/workstation/runtime.jsonl
ab-prov render --journal runtime/data/workstation/runtime.jsonl -o /tmp/workstation-prov.html
~~~

That journal path is an example, not proof of a running worker or a file that exists on your machine. No original input is modified.

## Reusing our own provenance

- [Cross-layer links](../../protocols/core/provenance-link.schema.json): original from/relation/to, survived, invalidated, witness references, source times and boundaries.
- [Native traversal touches](../../protocols/core/trace.schema.json): touched source, referent before/after, changed relation and unknown continuation.
- [RuntimeJournal](../../runtime/journal.py): real handoff submissions, event lineage and cited evidence.
- [Visual provenance](../../design/visual-provenance/README.md): restrained research figure generated from source records, not a copied UI.

The output is inspectable typed JSON or a self-contained searchable SVG/HTML graph. Cited evidence remains cited, never silently promoted to independently verified. Contradictions and absent handoff parents remain visible.

## Documentation

- [Commands and input records](docs/cli.md)
- [Evidence / proof boundaries](docs/evidence.md)
- [Visual design provenance](docs/visual.md)
- [Illustrative provenance fixture](examples/illustrative-provenance.json)
- [Illustrative journal fixture](examples/illustrative-journal.jsonl)

Scope: a usable provenance viewer / CLI, **not** an autonomous worker, REA clone, F3 mapping, generalized A/B theory or fully operational Language Referent engine. Any future worker execution must preserve the repository's existing native workstation and owner/witness admission boundaries.
