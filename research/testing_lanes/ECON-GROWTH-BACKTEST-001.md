# ECON-GROWTH-BACKTEST-001 — annual growth baseline comparison

**Question:** On a pinned historical window, which of two simple one-step annual baselines has lower absolute error for one public country indicator?

- Country: USA
- Indicator: World Bank `NY.GDP.MKTP.KD.ZG` (annual GDP growth)
- Source window: 1990–2023, one API response snapshot
- Frozen split: train through 2014; held-out one-step predictions from 2015 onward
- Baselines: previous year's observed value (persistence) and the fixed training-period mean
- Metric: mean absolute error, in percentage points
- Integrity controls: response hash, bounded response size, duplicate-year rejection, null/gap rejection, chronological split checks

## Evidence boundary

This is a narrow descriptive backtest. The World Bank may revise historical values, and this experiment does not reconstruct the data vintage available at each forecast date. One country, one indicator, and two simple baselines cannot establish general forecasting skill, explain economic causes, or support policy conclusions. Results must be read from the receipt; the workflow does not assume which baseline wins.

## Reproduction

```sh
python -m unittest discover -s research/testing_lanes -p 'test_econ_growth_backtest.py' -v
python research/testing_lanes/econ_growth_backtest.py --output ECON-GROWTH-BACKTEST-001.json
```

A source wall, malformed series, or missing years remains a recorded limitation rather than being silently bridged.
