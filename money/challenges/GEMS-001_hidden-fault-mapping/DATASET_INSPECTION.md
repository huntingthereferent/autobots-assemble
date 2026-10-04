# Downloaded Dataset Inspection

These facts come from directly inspecting the three GeoTIFFs supplied in-session.

## Shared grid

All three files use the same raster dimensions and georeferencing:

```text
width:      3292
height:     3730
CRS:        EPSG:32611
resolution: 100 m × 100 m
origin:     (243350, 4508550)
bounds:     243350, 4135550, 572550, 4508550
```

## example_submission.tif

Observed contract:

- one band;
- float32;
- NaN nodata;
- LZW-compressed GeoTIFF;
- 5,167,373 finite pixels;
- 7,111,787 NaN pixels;
- finite values in this supplied example are only 0 and 1;
- 60,988 finite pixels are 1.

### Critical relation

The example submission is **exactly equal to `existing_faults.tif` on every finite submission pixel**.

```text
example_submission
=
existing_faults converted to float32
on the valid submission footprint
```

So do not treat its values as a blank starter prediction, hidden target, or novel-fault baseline. Its useful role is the **output-template witness**: grid, footprint, dtype, nodata behavior, and encoding.

## existing_faults.tif

- one band;
- int8;
- nodata = -1;
- same grid;
- 5,167,373 valid pixels;
- 60,988 positive fault pixels.

Its valid/nodata mask exactly matches the finite/NaN mask of the example submission.

## gems-geodawn-numerical-features.tif

- 19 bands;
- float32;
- nodata ≈ -3.4028235e38;
- same grid;
- LZW compressed.

Band names:

1. `mag_anom`
2. `rtp`
3. `tmi_hg`
4. `geod_2ndinv`
5. `iso_grav_anom_slope`
6. `tc`
7. `geod_shearrate`
8. `geod_dilaterate`
9. `tmi_vg`
10. `deq_n100a15`
11. `iso_grav_anom_vg`
12. `det_elev`
13. `iso_grav_anom`
14. `tmi`
15. `depth_to_base_surf`
16. `ieq_n100a15`
17. `cond_surf`
18. `iso_grav_anom_hg`
19. `det_elev_slope`

Eighteen bands have 5,165,852 finite/non-nodata pixels. Band 6 (`tc`) has 5,165,840.

All 19 bands are simultaneously valid at 5,165,840 pixels.

## Footprint mismatch that preprocessing must preserve

The submission mask and feature validity are not identical:

- **3,073** pixels are inside the submission footprint but lack at least one feature value;
- **1,540** pixels have all 19 features valid but are outside the submission footprint.

Therefore:

```text
model feature-valid mask
≠
submission-valid mask
```

The final output must follow the **example submission footprint**, not derive its output footprint by simply requiring all feature bands to be finite.

Missing input features inside the valid output footprint need an explicit preprocessing/imputation/masking policy.

## Binary storage

The raw GeoTIFFs are intentionally not committed to GitHub. The repository stores hashes and contracts so a future local session can verify it has the exact same files without redistributing competition data.
