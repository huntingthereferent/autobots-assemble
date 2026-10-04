from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio


def write_submission(probabilities, template_path, output_path):
    """Write GEMS probabilities using example_submission.tif as the exact format witness."""

    template_path = Path(template_path)
    output_path = Path(output_path)
    p = np.asarray(probabilities, dtype=np.float32)

    with rasterio.open(template_path) as src:
        expected_shape = (src.height, src.width)
        if p.shape != expected_shape:
            raise ValueError(f"prediction shape {p.shape} != template {expected_shape}")

        template = src.read(1)
        valid = np.isfinite(template)
        inside = p[valid]

        if np.any(~np.isfinite(inside)):
            raise ValueError("predictions inside the submission footprint must be finite")
        if np.any((inside < 0.0) | (inside > 1.0)):
            raise ValueError("predictions inside the submission footprint must be in [0, 1]")

        out = np.full(expected_shape, np.nan, dtype=np.float32)
        out[valid] = p[valid]

        profile = src.profile.copy()
        tags = src.tags()

    profile.update(driver="GTiff", count=1, dtype="float32", nodata=np.nan)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(out, 1)
        if tags:
            dst.update_tags(**tags)

    return output_path
