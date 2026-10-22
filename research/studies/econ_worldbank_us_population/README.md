# Economics lane — World Bank WDI annual-population backtest

**Existing source witness:** [World Bank Indicators API source record](../../testing_lanes/sources/worldbank.json), [source-admission workflow run 39771470448](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39771470448), response hash `b7d97d40e1d86955bac3ca5bbc4fe534f1872c505479392e029e37f99d8e605c`. This older witness proves the API returned a particular single-record sample, not the later study period. A new measurement must independently hash its own source bytes.

**Frozen source/study:** World Bank, World Development Indicators, `SP.POP.TOTL` (population, total), United States (ISO3 `USA`), yearly **1990–2023 inclusive**, unit **persons**. The exact public query is:

```text
https://api.worldbank.org/v2/country/US/indicator/SP.POP.TOTL?format=json&date=1990%3A2023&per_page=50
```

The indicator publisher's [API documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures) provides the date-range and pagination contract. [World Development Indicators](https://datacatalog.worldbank.org/search/dataset/0037712/world-development-indicators) is public, licensed CC BY 4.0, with World Bank's additional [dataset terms](https://www.worldbank.org/ext/en/legal/terms-conditions/datasets). The study downloads only one bounded JSON source, makes no remote writes, and retains only a derived small ledger and the exact response hash. Attribute World Bank WDI, record the retrieval clock, and do not conflate WDI's newest revisions with data available historically.

**Predeclared comparison:** 10 one-year-ahead target years **2014–2023**, using only years through `y-1` for each prediction. Compare **persistence** `population(y-1)` against a simple 5-year drift `population(y-1)+(population(y-1)-population(y-6))/5`. Measurement: mean absolute error in persons on those ten targets and each forecast's absolute error by year. A drift forecast can perform worse; preserve that outcome without choosing a favorable model. Null, negative, missing, duplicate or unrecognized source population/years, or an API error, remain `SOURCE_WALL`.

**Important inference boundary:** This is a **retrospective pseudo-out-of-sample backtest on one revised source-vintage**. It is not vintage-correct to historical publication dates, and therefore cannot establish live forecasting utility, causal demographic effects, or country-generalized prediction. Future information may influence past data revisions; this is explicitly outside the test.

**Offline first:** `python -m unittest discover -s research/studies/econ_worldbank_us_population -p "test_*.py" -v`. Default experiment state is `UNOBSERVED`. Bounded opt-in: `python research/studies/econ_worldbank_us_population/experiment.py --live --output wdi-derived.json`. The CI workflow preserves a derived-only receipt for the exact run, and a source wall remains a failed research run rather than a claim of success.

This is one independently scoped **ECON** lane. No other lane is promoted by this result.
