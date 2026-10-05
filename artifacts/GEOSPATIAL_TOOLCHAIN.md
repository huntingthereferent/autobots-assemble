# Geospatial Production Toolchain

## Purpose

Define how world-referenced spatial artifacts are produced during Complete Stack traversal.

## Default toolchain

- **GeoPandas** — vector feature tables / transformations;
- **Shapely** — geometry and topology operations;
- **PyProj** — CRS transformations;
- **Rasterio** — georeferenced raster handling;
- **GeoJSON / GeoPackage** — preferred machine-readable vector outputs;
- **SVG/PDF/PNG** — generated human-readable maps when useful.

## Canonical production path

```text
real-world spatial referent
→ admitted source geometry / measurements
→ explicit CRS + provenance
→ canonical geospatial source
→ topology / distance / area / intersection checks
→ generated map views
→ derived quantities
→ downstream artifacts
```

## Checks

When supported:

- CRS present and valid;
- geometry validity;
- extent;
- topology;
- intersection/containment;
- distance;
- area/length;
- feature identity;
- layer/version provenance;
- stale-source detection.

## CAD relation

Geospatial and CAD-like artifacts can meet at an interface.

Example:

```text
geospatial site / road / parcel context
→ local project datum
→ CAD-like object geometry
→ constructed asset
→ surveyed/field position
→ geospatial update
```

Do not silently treat GIS accuracy as fabrication/survey accuracy.
