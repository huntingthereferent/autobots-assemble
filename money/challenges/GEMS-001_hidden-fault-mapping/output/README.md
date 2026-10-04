# GEMS Submission Output Layer

This directory turns an already-produced probability raster into the exact external file shape witnessed by the downloaded `example_submission.tif`.

It is **not** a model and does not create geological evidence.

```text
model probability raster
        ↓
submission output adapter
        ↓
template footprint + exact grid
        ↓
float32 GeoTIFF
        ↓
validator
        ↓
submission candidate
```

## Why use the template directly

The example file is the strongest available witness for:

- raster dimensions;
- CRS;
- affine transform;
- valid/NaN footprint;
- float32 output;
- nodata = NaN;
- encoding/profile.

The writer copies the template profile and mask instead of reconstructing them from memory.

## Writer

`write_submission.py` accepts a full-grid probability array.

Rules:

- shape must be 3730 × 3292;
- every prediction inside the template footprint must be finite;
- values inside the footprint must be in [0, 1];
- outside the footprint is forced to NaN;
- template profile/tags are copied.

## Validator

`validate_submission.py` checks:

- driver;
- dimensions/band count;
- CRS;
- affine transform;
- float32 dtype;
- NaN nodata;
- exact finite/NaN footprint;
- probability range.

Compression/tile/block information is reported as template-fidelity metadata. The public challenge contract is geospatial/value semantics; encoding details are preserved by our writer because they are cheap to match.

## Local dependencies

```text
numpy
rasterio
```

## Important

The downloaded example submission's **values** are just the existing-fault raster represented as float32 on the submission footprint. Never use those example values as the model output unless deliberately testing file plumbing.
