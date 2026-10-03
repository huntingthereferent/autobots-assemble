# State Layer

\`current.json\` is a **routing pointer**, not the historical ledger.

It should contain only enough state to let a new AI/session recover the present referent and the next admissible movement.

Historical evidence belongs in relations, commits, work records, or the evidence layer.

## Update rule

When the user explicitly changes the referent, update the current pointer. Preserve the previous state through Git history or an append-only movement record; do not overwrite historical evidence to make the present look cleaner.
