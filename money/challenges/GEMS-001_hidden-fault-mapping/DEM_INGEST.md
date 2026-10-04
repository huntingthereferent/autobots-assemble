# 1 m DEM Ingestion

## First inspected tile

`USGS_1M_10_x75y441_CA_SierraNevada_B22.tif`

Observed directly from the uploaded GeoTIFF:

- size: 238,657,987 bytes;
- SHA-256: `cd6823dafb960c8eb49b95eb2fe91dacecf52d7856599739879093ed86302a65`;
- 10,012 × 10,012 pixels;
- one float32 band;
- 1 m resolution;
- CRS: EPSG:26910 (NAD83 / UTM zone 10N);
- nodata: -999999;
- LZW compression;
- 88,172,690 valid elevation pixels;
- 12,067,454 nodata pixels;
- elevation range: 1437.4375–2393.7852 m;
- mean elevation: 1665.1833 m.

Its source bounds are:

```text
749994.0000, 4399994.0001
760006.0000, 4410006.0001
```

Reprojected to the GEMS CRS (EPSG:32611), its approximate bounds are:

```text
235655.93, 4399804.76
246316.11, 4410464.94
```

The GEMS grid begins at x = 243350 in EPSG:32611, so this tile overlaps only a narrow strip along the western edge.

## Do we need all DEM tiles?

Potentially **all overlapping tiles**, but not all should be uploaded or processed immediately.

First prove that 1 m terrain-derived features add useful signal under spatial validation. If they do, use the TNM manifest/index to batch-download and process every tile intersecting the GEMS submission footprint.

The raw 1 m tiles are working evidence. The durable repo artifact should be the reproducible derivation recipe, per-tile provenance/hashes, and compact 100 m derived layers—not a GitHub dump of hundreds of gigabytes of raw elevation data.
