# PhysioNet / public MIT-BIH catalog identity

This sublane examines **only the public source catalog record**, not physiological recordings, beat annotations, personal information, or published conclusions. The [PhysioNet MIT-BIH Arrhythmia Database](https://physionet.org/content/mitdb/1.0.0/) identifies dataset slug `mitdb`, version `1.0.0`, version DOI `10.13026/C2F305`, access policy **Open Access**, and published file license **Open Data Commons Attribution License v1.0**.

The provider distinguishes **open**, **restricted**, and **credentialed** access policies. The public catalog contains human-origin ECG recordings, but this query intentionally requests neither an individual recording nor a file list API: it reads only the fixed publisher page and validates five catalog identity signals. This is not consent, an ethics ruling, or confirmation that use of individual recordings complies with licensing terms. A later scientific test would require explicit record selection, license attribution, clinical-data handling safeguards, a frozen protocol, negative controls, and careful avoidance of subject overlap between train and test splits.

The [source reader](catalog_identity.py) defaults to `UNOBSERVED`. A single `--live` execution performs one HTTPS GET against the fixed publisher landing page. Strict UTF-8, bounded response (600 kB), no redirects, fixed URL, 15-second timeout, full-response SHA-256, source UTC timestamp, verified field labels, and **derived-only artifact** apply. It discards the HTML after checking it. A license label appearing on the publisher page does not waive per-record use restrictions.

Run the synthetic suite:

    python -m unittest discover -s research/testing_lanes/physionet_public -p 'test_*.py' -v

The dedicated [Actions workflow](../../../.github/workflows/research-physionet-public-catalog-metadata.yml) runs offline controls first, then one public identity observation and saves only a source hash/receipt. A timeout, changed license, missing DOI, or HTML format change yields `SOURCE_WALL`; it is **never** silently converted to a pass.

This source-intake sublane remains separate from the parent `NEURO` and `CLIN` experimental lanes. They are not granted access to ECG files by this catalog observation, and no physiological experiment is claimed.
