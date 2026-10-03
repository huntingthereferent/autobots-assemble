# Domain Layer

Domains are adapters above the generic network/protocol contract.

A domain may define specialized evidence, witnesses, calculations, or presentation, but it must not redefine A/B or mutate the core relation contract.

Historical v0.17 sports-betting logic is evidence of this pattern: sports-specific policy read generic relations one layer above the network. Future domain protocols should follow the same separation.
