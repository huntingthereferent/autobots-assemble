# Program Artifact

## Definition

A program artifact is an **executable/computational representation produced by traversal**.

It sits at the same artifact layer as CAD-like geometry, system landscapes, math models, schematics, and measurement packages.

The frozen [Program Foundation](../foundation/PROGRAM_FOUNDATION.md) is the first broad evidence that this artifact family can be realized through shared structure rather than one fixed application shape.

## Typical contents

Depending on the referent:

- source code;
- manifests/configuration;
- input/output contracts;
- state model;
- interfaces/APIs;
- tests;
- deployment/package definition;
- execution evidence;
- runtime measurements;
- failure/recovery evidence;
- provenance.

## Evidence boundary

```text
source code ≠ tested behavior
tested behavior ≠ deployed operation
deployed operation ≠ correct behavior under every environment
```

Preserve the deepest witness actually reached.

## Cross-artifact use

Program artifacts may consume or produce other artifact outputs.

Examples:

```text
CAD parameter table
→ program artifact
→ mass / clearance calculation
→ math artifact
→ CAD revision
```

```text
system landscape
→ control interface contract
→ embedded program artifact
→ timing measurement
→ landscape / control-model update
```
