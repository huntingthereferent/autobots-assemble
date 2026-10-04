"""Auditable NumPy implementation of the public GEMS distance-weighted Tversky metric."""

from __future__ import annotations

import math
import numpy as np


def _shift(arr: np.ndarray, dy: int, dx: int) -> np.ndarray:
    out = np.zeros_like(arr, dtype=float)
    sr0, sr1 = max(0, dy), arr.shape[0] + min(0, dy)
    sc0, sc1 = max(0, dx), arr.shape[1] + min(0, dx)
    dr0, dr1 = max(0, -dy), arr.shape[0] - max(0, dy)
    dc0, dc1 = max(0, -dx), arr.shape[1] - max(0, dx)
    if sr1 > sr0 and sc1 > sc0:
        out[dr0:dr1, dc0:dc1] = arr[sr0:sr1, sc0:sc1]
    return out


def _max_weighted_neighborhood(arr: np.ndarray, radius_pixels: float) -> np.ndarray:
    if radius_pixels <= 0:
        raise ValueError("radius_pixels must be > 0")
    arr = np.asarray(arr, dtype=float)
    out = np.zeros_like(arr, dtype=float)
    r = int(math.ceil(radius_pixels))
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = math.hypot(dy, dx)
            if d > radius_pixels:
                continue
            w = max(1.0 - d / radius_pixels, 0.0)
            np.maximum(out, _shift(arr, dy, dx) * w, out=out)
    return out


def distance_weighted_tversky(
    prediction: np.ndarray,
    ground_truth: np.ndarray,
    *,
    alpha: float = 0.2,
    beta: float = 0.8,
    radius_pixels: float = 3.0,
    valid_mask: np.ndarray | None = None,
    eps: float = 1e-12,
) -> float:
    p = np.asarray(prediction, dtype=float)
    g = (np.asarray(ground_truth) > 0).astype(float)
    if p.shape != g.shape or p.ndim != 2:
        raise ValueError("prediction and ground_truth must be same-shape 2D arrays")
    if np.any(~np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise ValueError("prediction must be finite and in [0, 1]")

    valid = np.ones_like(g, dtype=bool) if valid_mask is None else np.asarray(valid_mask, dtype=bool)
    if valid.shape != g.shape:
        raise ValueError("valid_mask must match raster shape")

    p = np.where(valid, p, 0.0)
    g = np.where(valid, g, 0.0)

    p_support = _max_weighted_neighborhood(p, radius_pixels)
    g_support = _max_weighted_neighborhood(g, radius_pixels)

    tp = float(np.sum(g * p_support))
    fn = float(np.sum(g * (1.0 - p_support)))
    fp = float(np.sum(p * (1.0 - g_support)))

    return tp / (tp + alpha * fp + beta * fn + eps)
