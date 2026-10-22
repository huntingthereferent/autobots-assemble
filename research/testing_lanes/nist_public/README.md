# NIST Chemistry WebBook · public species identity

A **separate source-contract sublane** to validate only the identity of a named chemical in the original [NIST Chemistry WebBook SRD 69](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Units=SI). It is deliberately NOT an extraction of NIST thermodynamic measurements, spectra, constants, compiled data tables, or a chemistry experiment.

## Fixed referent

One publisher species page, with canonical identity:

- Name: Water
- CAS Registry Number: `7732-18-5`
- Molecular formula: `H2O`
- IUPAC Standard InChIKey: `XLYOFNOQVPJJNP-UHFFFAOYSA-N`
- NIST source family: Chemistry WebBook / Standard Reference Database 69

The [source-specific reader](species_identity.py) defaults to offline `UNOBSERVED`. The explicit live mode requests **one fixed HTTPS URL** with no redirects, no query composition, no scripts, a 400-kB cap, a 15-second timeout and an exact publisher/compound ID/structure identity check. It records the UTC observation time and SHA-256 of the webpage, then discards the webpage and emits *only* the identity flags. NIST reference-data compilation copyright and reuse conditions require a further per-record rights review before downloading or using measured source tables.

Run the offline negative tests:

    python -m unittest discover -s research/testing_lanes/nist_public -p 'test_*.py' -v

Opt-in direct source check:

    python research/testing_lanes/nist_public/species_identity.py --live --output nist-water-source-receipt.json

CI [research-nist-public-species-identity.yml](../../../.github/workflows/research-nist-public-species-identity.yml) first runs synthetic identity and missing-field controls and then attempts the one named public source. If blocked or changed, the outcome remains **SOURCE_WALL**. No scientific claim is inferred from a successful source response.

This work is separated from the main registry's **NIST manual data-rights gate**. The CHEM context already has a distinct PubChem metadata provider. Neither metadata source proves measurement agreement, thermochemical correctness, or an original scientific result. Measurement admission would require a new explicit question, source-field units and conditions, reuse terms, frozen response, independent reference and counterexample.
