# Evidence boundaries

The native provenance sources are protocols/core/provenance-link.schema.json, protocols/core/trace.schema.json and runtime/journal.py. The package reads them: it neither renames nor replaces the original records.

Local state answers what is represented. Evidence answers what may support or contradict a claim. Provenance answers which recorded relations moved a referent to its present representation. Visual provenance is only a projection and cannot become an authoritative witness.

A source reference is a label until a source-specific verifier authenticates it. A SHA256 digest of input bytes identifies the input file but does NOT prove authorship, execution or truth. A handoff EVENT and an evidence depth string are recorded assertions, not promotion to native verified work.

Contested and invalidated relations are retained. A trace with no next referent and workstation parent references absent from the supplied journal are displayed unresolved, not completed. This tool does not run, authorize, or silently register a worker. Original source files and private workstation runtimes retain ownership of their state.

To extend this into an executable A/B investigator, integrate through the existing workstation admission and separate native witness callbacks, never through the graphical view.

The separate `ab swallow` command performs source-edition construction and actual REA native tests through existing ProcessWorkstation. This inspection module alone does not execute or independently verify any source claim; the test receipt and native test logs must be examined as separate evidence.
