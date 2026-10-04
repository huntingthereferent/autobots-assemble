# Output Lenses

Output lenses are restored as a first-class layer.

A lens is **read-only**: it projects one frozen network snapshot into a different representation.

```text
snapshot
├─ raw
├─ json
└─ english
```

The representation can change radically while the snapshot remains identical.

This is intentionally separate from language decoding. A language decoder asks “what movement does this surface expression carry?” A lens asks “how should this already-recorded state be shown?”
