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

## Actual pinned run — October 22, 2026

[GitHub Actions run 39827537491](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39827537491) passed the offline control and bounded-backtest jobs. Its full observed [derived receipt](observations/2026-10-22-ECON-GROWTH-BACKTEST-001-run-39827537491.json) is now preserved in the repository with the original response SHA-256, date, nine test-year predictions, and score totals. On this snapshot, **the frozen 1990–2014 training mean won**: MAE 1.1549775564 percentage points versus 2.2237911887 for previous-year persistence across 2015–2023. The negative-case tests and a separate archive recomputation enforce the result.

**Interpretation boundary:** the persistence predictor uses the previous year's *observed* value; this is retrospective one-step evaluation with revised public data, not a real-time forecast backtest by release vintage. These nine observations cannot establish general predictive superiority or explain GDP growth. The raw API response was not archived and its historical revisions are not resolved here.

**Data credit/terms:** World Bank, *GDP growth (annual %)*, indicator `NY.GDP.MKTP.KD.ZG`, United States; [World Bank Dataset Terms](https://www.worldbank.org/ext/en/legal/terms-conditions/datasets). World Bank datasets normally use CC BY 4.0 unless particular metadata imposes an exception. Provider-specific rights still require review before republishing raw series; the archive contains only calculated score inputs and a receipt.
