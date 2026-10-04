# Core Protocol — Evidence

## Input

A claim, observation, artifact, tool result, file, test, source, prior movement, or user instruction relevant to the current referent.

## Witness contract

Evidence must have:

- an identifiable source;
- a relation to the current referent or a relation reached from it;
- a preserved distinction between observed fact and interpretation;
- uncertainty retained when the source cannot support a stronger claim.

## Source role

Source *role* is evidence metadata, not a truth ranking by itself.

Useful roles include:

- `primary` — direct/original record, specification, filing, dataset, statement, or artifact;
- `secondary` — analysis/reporting about a primary event/source;
- `community` — user/community report, discussion, review, or experience;
- `index` — search result, directory, aggregator, catalog, or pointer;
- `derived` — transformation, summary, model output, calculation, or synthesis from other evidence.

An index/snippet is normally a pointer to inspect the underlying source, not a substitute for that source.

## Result states

- `SUPPORTED` — evidence satisfies the required witness condition.
- `PARTIAL` — some required support exists but coverage/preservation is incomplete.
- `UNKNOWN` — the contract cannot decide from available evidence.
- `REJECTED` — evidence is inapplicable to the current witness condition.

## Conflict

Contradictory evidence stays separate until the relevant correspondence, source, time, scope, or authority difference is resolved. Do not average contradictions into a fake consensus.

## Absence

Failure to find evidence is not automatically evidence of absence. A bounded exhaustive search may support a narrower absence claim only when the search boundary itself is explicit and adequate.

## Rule

Missing evidence does not become a negative fact. Older evidence does not orient the present unless the current relation reaches it.
