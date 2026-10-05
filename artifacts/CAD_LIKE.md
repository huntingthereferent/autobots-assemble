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

## Standard CAD-like output package

When useful, emit:

1. **geometry source** — editable/native/parametric representation;
2. **overview render** — visual orientation only;
3. **orthographic views** — front/top/side or appropriate sections;
4. **dimensioned drawing** — dimensions needed by current relations;
5. **interface drawing** — connection/mating locations and contracts;
6. **parameter table** — named dimensions/variables with units and provenance;
7. **assumption/placeholder table**;
8. **derived quantities** — volume, estimated mass, centers, clearances, etc. when supported;
9. **witness status** — represented/modelled/simulated/built/measured;
10. **downstream dependency list** — what consumes the geometry.

Not every problem requires all ten. The referent selects the necessary subset.

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
