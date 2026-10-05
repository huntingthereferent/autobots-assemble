# Geospatial Artifact

## Definition

A geospatial artifact is a **structured spatial representation anchored to a real-world coordinate reference**.

It is a sibling of CAD-like geometry under the structural → spatial relation.

The distinction is the reference frame:

```text
spatial
├─ object / local frame
│  └─ CAD-like
└─ georeferenced / world frame
   └─ geospatial
```

A city, road network, utility extent, watershed, parcel layer, transit route, or land-use surface should not be forced into CAD merely because geometry is involved.

## Required structure when relevant

- coordinate reference system / datum;
- geographic extent;
- geometry type;
- source resolution/scale;
- features and identifiers;
- attributes;
- topology / adjacency where material;
- uncertainty / accuracy;
- source/provenance;
- time/version of the represented geography;
- downstream dependencies.

## Canonical forms

Depending on the relation:

- GeoJSON;
- GeoPackage;
- georeferenced vector source;
- GeoTIFF / other georeferenced raster;
- another machine-readable spatial format that preserves CRS and provenance.

Rendered SVG/PDF/PNG maps are views, not the canonical geospatial source.

## Evidence boundary

```text
public map
≠ surveyed geometry
GIS parcel line
≠ property boundary survey
mapped utility extent
≠ field-located utility
aerial image
≠ measured 3D geometry
```

Preserve the actual source accuracy and legal/engineering boundary.
