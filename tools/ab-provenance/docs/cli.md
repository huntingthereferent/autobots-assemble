# CLI

The Python package installs a command named ab-prov.

~~~sh
ab-prov inspect path/to/provenance.json
ab-prov inspect path/to/provenance.json --graph
ab-prov ancestors path/to/provenance.json --target observed-referent
ab-prov render path/to/provenance.json --target observed-referent -o ancestry.html
ab-prov render path/to/provenance.json -o research.html
ab-prov inspect --journal path/to/real/runtime.jsonl
ab-prov render --journal path/to/real/runtime.jsonl -o workstation.html
~~~

It accepts schema_version=1 JSON with provenance_links (records conforming to existing protocols/core/provenance-link.schema.json), traces (existing protocols/core/trace.schema.json), or both. The optional journal uses existing RuntimeJournal JSONL SUBMISSION and EVENT records, not a fabricated alternate worker schema. Both inputs can be supplied simultaneously.

inspect prints a scoped summary (nodes, relationships, unresolved, contested, warnings) or the full typed graph with --graph. render emits self-contained offline HTML and never changes the input. The output can be opened directly.

Exit 0 means a structurally readable projection. Exit 2 means invalid or contradictory input. It does NOT mean a source's evidence was independently verified. The parser checks identifiers, core record fields, duplicates, parent gaps, source sizes and structural limits; it does not claim full JSON Schema validation or cryptographic source ownership.

Backward ancestry traverses only recorded upstream relationships, at a bounded depth (32 hops by default). The target can be an exact graph node ID from inspect --graph or an unambiguous node label. Missing evidence remains unresolved; a path is never independent proof. The focused render displays only the selected recorded ancestry.
