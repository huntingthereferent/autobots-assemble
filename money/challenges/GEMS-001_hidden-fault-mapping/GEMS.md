# GEMS-001 — Geologic Enhanced Mapping System Prize

**Status:** active  
**Primary lane:** Money / Prize  
**Secondary relation:** Research / geoscience  
**Fields:** geophysics, geology, spatial ML, remote sensing, raster analysis  
**Deadline:** 2026-12-03 23:59 UTC  
**Prize pool:** $300,000

## Current referent

Predict previously unmapped geological faults in the GeoDAWN region using provided geospatial/geophysical evidence and permitted external data.

## Why this is active

The work has an unusually strong external witness:

- hidden expert labels;
- public/private scoring;
- final expert review that can add newly verified faults to the ground truth;
- fixed GeoTIFF acceptance format;
- scientific value plus prize money.

## Eligibility boundary

The official NLR rules publication and the DrivenData competition materials establish the following public eligibility boundary:

- individual competitors must be U.S. citizens or permanent residents;
- a team must have a captain who is a U.S. citizen or permanent resident;
- private entities must be incorporated in the United States and maintain a primary place of business in the United States;
- federal entities and federal employees are not eligible.

Nothing in the public eligibility summary adds a professional, academic, or licensing credential to the word **captain**. Here, captain is the qualifying team representative role; citizenship/permanent-resident status is the relevant public eligibility condition.

Registration also carries a federal certification: the competitor certifies eligibility and rule compliance, under penalty of perjury, and represents that submission information is truthful.

## Submission contract

One GeoTIFF:

- EPSG:32611;
- 100 m resolution;
- competition bounds;
- one float32 band;
- values in [0, 1];
- null/NaN outside study bounds.

## Evaluation

Distance-weighted Tversky:

- radius: 300 m / 3 pixels;
- alpha = 0.2 false-positive penalty;
- beta = 0.8 false-negative penalty.

Known USGS/INGENIOUS fault pixels are pixel-exact masked from scoring. The mask is not buffered. New-fault labels may occur within 300 m of known traces when they represent corrections/extensions.

## Data

Three downloaded competition files were supplied in-session and inspected directly:

- `example_submission.tif`
- `gems-geodawn-numerical-features.tif`
- `existing_faults.tif`

The repository intentionally stores their hashes, metadata, and contract rather than committing the raw GeoTIFF binaries.

See [DATASET_INSPECTION.md](DATASET_INSPECTION.md) and [data_manifest.json](data_manifest.json).

The observed numerical feature raster is 3730 × 3292 with 19 float32 bands at 100 m resolution in EPSG:32611.

## Rules / data-use boundary

The competition data page requires logged-in enrollment.

The public rule excerpts explicitly allow and encourage external data when the competitor/team has the necessary licenses to use it for the challenge.

The official rules PDF is now treated as **swallowed evidence** for this challenge rather than as a separate protocol. A direct full-text render of the 19-page PDF was not available through the current retrieval path, so the repository distinguishes:

- **SUPPORTED:** facts exposed by the official NLR publication record and DrivenData's official rule excerpts;
- **PARTIAL:** rule sections that require the PDF text itself before we assert their exact wording;
- **UNKNOWN:** any AI/data-sharing restriction not visible in the public excerpts.

Therefore, before gated competition data is transferred to a third-party AI/service, confirm the exact data-use language from the enrolled rules/data page. Public documentation and public reference code can be analyzed now.

## Output layer

The downloaded `example_submission.tif` is now the canonical submission-template witness.

Challenge-local output code lives under [`output/`](output/). It:

- writes one float32 GeoTIFF matching the template grid/CRS/transform;
- preserves the template finite/NaN footprint exactly;
- rejects finite output values outside [0, 1];
- validates structure against the supplied example before submission.

Important observation: on every finite template pixel, the downloaded `example_submission.tif` is **exactly equal** to `existing_faults.tif`. It is therefore a format/example scaffold, not a neutral blank prediction and not evidence of new faults.

## Next movement

1. Verify the exact GEMS-specific competition-data sharing/third-party-service language.
2. Run the reference baseline locally against the downloaded inputs.
3. Route baseline probabilities through the challenge-local output writer.
4. Validate the generated GeoTIFF against the exact downloaded template.
5. Replace random positive-patch validation with spatially honest validation.
6. Build full-region inference where “unmapped” is not silently treated as “negative.”

## Rules summary

See [OFFICIAL_RULES_SUMMARY.md](OFFICIAL_RULES_SUMMARY.md). The rules are evidence attached to GEMS-001; they do not create a new architectural layer.

## Public sources

- https://www.drivendata.org/competitions/306/competition-doe-gems/page/966/
- https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- https://www.drivendata.org/competitions/306/competition-doe-gems/rules/
- https://www.herox.com/GEMSPrize/resource/2274
- https://github.com/drivendataorg/gems-prize-reference-solution
- https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- https://community.drivendata.org/t/leaderboard-aggregation-pooled-over-public-test-pixels-or-mean-of-per-chunk-scores/11550
