from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import rasterio


def validate_submission(candidate_path, template_path):
    """Validate candidate GeoTIFF against the observed example-submission contract."""

    candidate_path = Path(candidate_path)
    template_path = Path(template_path)
    errors = []
    report = {}

    with rasterio.open(template_path) as t, rasterio.open(candidate_path) as c:
        checks = {
            "driver": (c.driver, t.driver),
            "width": (c.width, t.width),
            "height": (c.height, t.height),
            "count": (c.count, 1),
            "crs": (str(c.crs), str(t.crs)),
            "transform": (tuple(c.transform), tuple(t.transform)),
            "dtype": (c.dtypes[0], "float32"),
        }

        for key, (actual, expected) in checks.items():
            report[key] = actual
            if actual != expected:
                errors.append(f"{key}: expected {expected!r}, got {actual!r}")

        if not (c.nodata is not None and math.isnan(float(c.nodata))):
            errors.append(f"nodata: expected NaN, got {c.nodata!r}")

        if c.width == t.width and c.height == t.height and c.count == 1:
            ta = t.read(1)
            ca = c.read(1)
            expected_valid = np.isfinite(ta)
            actual_valid = np.isfinite(ca)

            mismatch = int(np.count_nonzero(expected_valid != actual_valid))
            report["footprint_mask_mismatch_pixels"] = mismatch
            if mismatch:
                errors.append(f"finite/NaN footprint differs at {mismatch} pixels")

            inside = ca[expected_valid & actual_valid]
            if inside.size:
                report["finite_min"] = float(inside.min())
                report["finite_max"] = float(inside.max())
                bad = int(np.count_nonzero((inside < 0.0) | (inside > 1.0)))
                report["out_of_range_pixels"] = bad
                if bad:
                    errors.append(f"{bad} finite pixels fall outside [0, 1]")

        report["compression"] = c.compression.value if c.compression else None
        report["tiled"] = bool(c.profile.get("tiled", False))
        report["block_shapes"] = [tuple(shape) for shape in c.block_shapes]

    return {"ok": not errors, "errors": errors, "report": report}
