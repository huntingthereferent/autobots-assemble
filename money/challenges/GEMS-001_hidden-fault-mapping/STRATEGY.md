# GEMS Strategy

## 1 — Reproduce plumbing

Confirm raster loading, CRS/bounds, model I/O, and GeoTIFF output.

## 2 — Exact metric

Use the published 300 m distance-weighted Tversky locally.

## 3 — Spatially honest validation

Use geographic blocks/folds with no overlapping training patches crossing validation boundaries.

## 4 — Unknown-aware learning

Avoid the false assumption that every unlabeled pixel is negative.

Test positive-unlabeled and tri-state sampling ideas:

```text
known fault = positive
supported non-fault = negative
everything else = unknown
```

## 5 — Structure-first features

Faults are elongated structures. Investigate multiscale:

- ridges/edges;
- orientation coherence;
- line continuity;
- magnetic/gravity gradient alignment;
- topographic scarps/lineaments;
- conductivity/depth discontinuities;
- strain and seismic context;
- extensions, splays, intersections and terminations.

## 6 — Competing model families

Do not bet everything on one U-Net:

- segmentation CNN/transformer;
- classical lineament/gradient model;
- positive-unlabeled learner;
- anomaly/disagreement model;
- ensemble.

## 7 — 1 m DEM

If rules/licenses permit, derive slope, curvature, local relief, multi-azimuth hillshade, and lineament/scarp evidence, then aggregate reproducibly to the 100 m submission grid.

### DEM ingestion policy

Do **not** manually upload every 1 m DEM tile into the chat.

Use one or a few tiles to validate the derivation pipeline first. If the derived terrain features improve spatially honest validation, batch-process **all tiles that overlap the GEMS submission footprint** locally from the TNM item manifest.

Per-tile processing:

```text
1 m DEM tile
→ verify hash / CRS / nodata
→ reproject only as needed
→ derive terrain structure at native/multiscale resolution
→ aggregate features to the 100 m GEMS grid
→ write compact derived layers + provenance
```

Candidate derived layers include slope, curvature, local relief, multi-azimuth hillshade, ridge/valley measures, lineament/scarp evidence, and orientation/coherence measures.

The first inspected tile, `USGS_1M_10_x75y441_CA_SierraNevada_B22.tif`, is ~10 × 10 km, EPSG:26910, and overlaps only a narrow western slice of the GEMS study grid after reprojection. It is therefore useful as a pipeline test tile, not as representative coverage of the entire challenge area.

## 8 — Expert-discovery list

Maintain a ranked internal list of likely unmapped faults with supporting modalities and model agreement. This matters because expert-confirmed discoveries can enter the final-round ground truth.
