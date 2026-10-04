# Compatibility Alias — OSINT

`work.osint` is no longer a registered standalone protocol.

It has been **swallowed by** [`research.source`](../research/source.md) because the earlier OSINT rules did not require a distinct witness/evidence contract.

The term **OSINT** is still valid language for public/open-source investigation. Historical records using it remain valid provenance.

Operational routing:

```text
work.osint
    ↓ compatibility
research.source
    +
core.evidence
    +
core.provenance
```

This is absorption, not deletion: unique future OSINT-specific constraints may be added as a domain adapter if they actually require a different contract.
