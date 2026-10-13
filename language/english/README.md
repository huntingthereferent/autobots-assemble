# English Shape Bank

English is currently the first active surface language.

The bank deliberately includes multiple registers because real English does not arrive only as dictionary/standard prose.

Current registers:

- **standard** — conventional complete English
- **plain** — direct low-jargon English
- **casual** — everyday conversation
- **slang** — colloquial forms
- **internet** — text/online shorthand
- **caveman** — the user-facing name for deliberately telegraphic English; internally this is treated as `telegraphic`
- **technical** — explicit protocol/machine-adjacent wording

The same expression can map differently in context. Example: **“send it”** can mean `MOVE.CONTINUE` or `WORK.SUBMIT`. The bank therefore supplies candidates, not a context-free dictionary.

See:

- `shape_bank.json` — canonical bank
- `registers.json` — register definitions
- `decoder.md` — surface → movement
- `renderer.md` — movement → surface
- `handoff.md` — English handoff vocabulary

## James is the same speaker in every register

The [language referent](../../LANGUAGE_REFERENT.md) is the same referent historically called A/B. The [regrounding record](../REGROUNDING.md) explains why a name helps recover a relation when a conversation branches farther than intended.

The register bank is a **candidate surface index**, not a personality generator. It cannot tell whether someone was being gentle, angry, playful, or precise merely by labeling them "casual" or "technical." Nor does a different register imply a different James. Preserve the original words when attribution matters, including swearing and humor; any normalized expression is a labeled rendering rather than a purported quote.

An observed *swallowing* of several people's perspectives is not automatically the repository's `LAYER.ABSORB` operator. "Surfing" may be James's metaphor for regrounding, not a standalone instruction. Context and evidence select the meaning.
