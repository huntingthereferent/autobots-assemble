# CAD-Like Artifact

## Definition

"CAD-like" means a **structured geometric representation of a physical referent that is sufficiently explicit to inspect physical relations and feed downstream work**.

It does not require one specific CAD application or file format.

A CAD-like artifact may be:

- native CAD;
- parametric CAD script;
- STEP/STL/DXF/OBJ or similar geometry;
- dimensioned SVG/vector drawing;
- orthographic drawing set;
- coordinate/primitive-based geometry specification;
- assembly/interface model;
- another machine-readable geometric representation that preserves the required physical relations.

A decorative concept image is **not** CAD-like evidence by itself.

## Required structure when relevant

### Geometry

- coordinate system / datum;
- overall envelope;
- component geometry;
- relative positions;
- mating geometry;
- clearances;
- motion envelopes.

### Dimensions

- critical dimensions;
- units;
- parameter names;
- derived dimensions where applicable.

### Interfaces

- mounting points;
- fastener locations;
- electrical/mechanical pass-throughs;
- contact surfaces;
- shaft/bearing interfaces;
- fluid/air paths when relevant;
- keep-out zones.

### Physical assumptions

- material or material placeholder;
- density when mass is derived;
- manufacturing/process assumption;
- tolerance assumption;
- load/thermal assumptions when geometry depends on them.

### Assembly structure

- parts;
- subassemblies;
- parent/child relations;
- degrees of freedom or fixed relations;
- replaceable placeholder components.

## A/B-ordered CAD-like output package

The package is grouped by one local question at a time rather than one flat deliverable list.

### 1. Geometry source

What carries the editable spatial referent?

- native/parametric geometry;
- assembly structure;
- component geometry.

### 2. Geometric views

What spatial relation must be inspected?

- **orientation** → overview render;
- **projection/section** → orthographic or sectional views;
- **dimension** → dimensioned drawing;
- **mating/interface** → interface drawing.

### 3. Parameter and evidence records

What makes the geometry usable downstream?

- parameter table with units/provenance;
- assumption/placeholder table;
- derived quantities such as volume, estimated mass, centers, clearances;
- witness status;
- downstream dependency list.

Not every branch is required. The current relation selects the necessary branch, and any child can be decomposed again.

## Example

```text
motor mount CAD
├─ hole pattern: witnessed from motor datasheet
├─ frame rail spacing: measured
├─ plate thickness: calculated/assumed
├─ material: 6061-T6 design choice
├─ motor mass: sourced
├─ load case: modeled
├─ FEA: not yet performed
├─ fabricated: no
└─ downstream
   ├─ fastener calculation
   ├─ frame assembly
   ├─ motor alignment
   └─ fabrication drawing
```

That is useful physical evidence without claiming a fabricated mount exists.
