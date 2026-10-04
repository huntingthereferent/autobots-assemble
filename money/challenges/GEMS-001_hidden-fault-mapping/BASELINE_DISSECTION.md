# Baseline Dissection

The public DrivenData reference solution uses a U-Net with a ResNet18 encoder over the 19-channel geospatial raster.

## Reference configuration

- 5 Monte Carlo train/test splits
- 128 × 128 patches
- 50% held out among selected patches
- training stride 32 after held-out regions are zeroed
- batch size 32
- 5 epochs
- learning rate 1e-4
- AdamW
- ordinary binary Tversky loss, alpha=.2 beta=.8
- random crop/flip/rotation augmentation
- all 19 channels

## 19 notebook-reported bands

1. magnetic anomaly
2. reduced-to-pole magnetics
3. magnetic horizontal gradient
4. geodetic second invariant
5. gravity anomaly slope
6. tilt angle / total curvature
7. geodetic shear rate
8. geodetic dilatation rate
9. magnetic vertical gradient
10. distance to earthquake
11. gravity vertical gradient
12. detrended elevation
13. isostatic gravity anomaly
14. total magnetic intensity
15. depth to basement
16. earthquake intensity/density
17. conductivity surface
18. gravity horizontal gradient
19. detrended elevation slope

## Openings in the reference baseline

### Positive-patch selection

Its patch builder only admits patches containing at least one known fault pixel. That means pure-negative regions are excluded, and prediction coverage is anchored to known-fault neighborhoods.

### Spatial validation

Random patches from one geophysical field are not a strong test of geographic generalization. Spatial autocorrelation can make validation optimistic.

### Loss != official metric

Training uses ordinary Tversky loss. Official scoring is **distance-weighted** Tversky with 300 m support.

### Incomplete labels

The competition explicitly says the known fault map is incomplete and may contain inaccuracies.

```text
not mapped
≠
negative
```

A serious solution needs unknown/unlabeled handling rather than hard-negative treatment everywhere.

### Full-region discovery

Our model should infer across the entire valid study region, not only patches already containing known faults.

## First strategic correction

Treat the reference notebook as a plumbing benchmark, not as the model architecture we are obligated to preserve.
