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
