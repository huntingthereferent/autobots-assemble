# CAD-Like Production Toolchain

## Purpose

Define how CAD-like artifacts are actually produced.

A CAD-like artifact is not satisfied by a technical-looking image. The canonical artifact begins from editable geometric source and produces inspectable engineering outputs.

## Default toolchain

### Parametric 3D geometry

**Primary:** CadQuery

Use when the referent requires:
- parametric solid geometry;
- assemblies;
- named dimensions;
- reusable interfaces;
- generated STEP/STL outputs;
- programmatic geometry checks.

### Simple declarative geometry

**Secondary:** OpenSCAD

Use when the referent is well represented by constructive solid geometry and transparent declarative operations, such as:
- brackets;
- spacers;
- fixtures;
- housings;
- simple enclosures;
- adapters.

### Engineering drawings / exchange

**DXF:** ezdxf

Use for:
- 2D manufacturing geometry;
- dimension/interface drawings;
- profiles;
- cut patterns;
- drawing exchange.

**SVG:** generated vector drawing

Use for:
- inspectable orthographic views;
- dimensioned diagrams;
- interface drawings;
- section views;
- human-readable repo evidence.

### Mesh / geometry inspection

**Trimesh / Shapely** where appropriate.

Use for:
- bounding boxes;
- intersections/collisions;
- clearances;
- area/volume;
- spatial tests;
- derived geometric checks.

## Canonical production path

```text
physical referent
→ parameter set
→ editable parametric source
→ generated geometry
   ├─ STEP
   ├─ STL when mesh output is useful
   ├─ DXF where 2D exchange is useful
   └─ SVG engineering views
→ programmatic geometry checks
→ derived quantities
→ provenance / assumptions / witness state
→ downstream artifacts
```

The editable source is canonical.

Generated exports must be reproducible from that source plus the preserved parameter/evidence inputs.

## Preferred package shape

```text
ART-####_name/
├─ artifact.json
├─ model/
│  ├─ model.py              # CadQuery or other canonical source
│  ├─ model.step
│  └─ model.stl             # when useful
├─ drawings/
│  ├─ general_arrangement.svg
│  ├─ general_arrangement.dxf
│  ├─ dimensioned_view.svg
│  ├─ interface_view.dxf
│  └─ section_*.svg         # when required
├─ parameters/
│  └─ parameters.json
├─ checks/
│  └─ geometry_checks.json
├─ derived/
│  └─ geometry_values.json
└─ evidence/
   └─ provenance.json
```

The referent may omit branches it does not require.

## Geometric checks

When the current relation supports them, generate machine-checkable evidence such as:

- bounding envelope;
- named dimensions;
- hole spacing;
- wall/plate thickness;
- intersection/collision;
- clearance;
- alignment;
- volume;
- estimated mass from declared density;
- center/centroid;
- interface compatibility.

Example:

```text
plate thickness = 8.000 mm        PASS
motor holes = 60 x 40 mm         PASS
shaft clearance >= 4.0 mm        PASS
motor/frame interference         FAIL
```

A failed check opens the failed relation for another traversal.

## Math ↔ CAD recurrence

CAD inputs may come from math artifacts, and CAD outputs may feed math artifacts.

```text
load model
→ required dimensions
→ CAD parameters
→ geometry
→ volume / mass / lever arms / clearances
→ math model
→ revised requirement
→ CAD regeneration
```

Derived values must retain lineage to the geometry and parameters that produced them.

## Evidence boundary

```text
parametric source
≠ generated geometry verified to export
≠ simulated geometry
≠ fabricated part
≠ measured physical part
```

Do not cross those witness boundaries silently.

## Concept imagery

Image-generation output may accompany a physical artifact only as:

**concept / appearance / communication**

It is never the canonical geometric artifact and must not be cited as dimensional, interface, manufacturing, or physical evidence.
