# Domain Layer

Domains are optional specialized adapters used only when a problem layer has a genuinely distinct witness/evidence contract.

A domain may define specialized evidence, witnesses, calculations, or presentation, but it must not redefine A/B or mutate the core relation contract.

Current domain dissections:

- [sports betting](sports_betting/README.md) — price/probability/risk/decision logic separated from source research, generic evidence, movement, and read-only output views.

Historical v0.17 domain logic remains evidence. A domain is promoted into an active protocol only when it has a genuinely distinct witness/evidence contract.
