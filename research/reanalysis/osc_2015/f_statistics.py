"""Independent F-test p-value recomputation for the pinned RPP public export.

This is a *statistic-level* partial replication, not a repeat of any experiment.
The upstream CSV already contains test statistics and source recalculated p-values.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from scipy.stats import f as f_distribution

from aggregate import fetch_source, inspect_bytes

SIDES = {
    "original": ("O", "T.sign.O.131"),
    "replication": ("R", "T.sign.R.132"),
}
TOLERANCE = 1e-6
ALPHA = 0.05


def _positive_float(value: str, name: str, *, allow_zero=False) -> float:
    try:
        number = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid " + name) from exc
    if not math.isfinite(number) or (number < 0 if allow_zero else number <= 0):
        raise ValueError("invalid " + name)
    return number


def analyze(csv_text: str) -> dict:
    rows = csv.DictReader(io.StringIO(csv_text))
    columns = rows.fieldnames
    if not columns or len(set(columns)) != len(columns):
        raise ValueError("missing or duplicate source columns")
    expected = {"Local.ID"}
    for side, flag in SIDES.values():
        expected |= {
            "T.Test.Statistic." + side,
            "T.df1." + side, "T.df2." + side,
            "T.Test.value." + side,
            "T.pval.recalc." + side,
            flag,
        }
    if not expected.issubset(columns):
        raise ValueError("missing statistical test columns")
    results = {
        side: {
            "eligible_f_tests": 0,
            "reported_p_available": 0,
            "reported_p_agree": 0,
            "reported_p_disagree": 0,
            "reported_p_missing": 0,
            "flags_available": 0,
            "flags_agree": 0,
            "flags_disagree": 0,
            "flags_missing": 0,
            "largest_absolute_p_error": 0.0,
        }
        for side in SIDES
    }
    seen = set()
    n_rows = 0
    for row in rows:
        if None in row or not row.get("Local.ID") or row["Local.ID"] in seen:
            raise ValueError("malformed or repeated study row")
        seen.add(row["Local.ID"])
        n_rows += 1
        for kind, (side, flag) in SIDES.items():
            if row["T.Test.Statistic." + side] != "F":
                continue
            # A selected F record with missing statistic is NOT silently treated as a result.
            degrees1 = _positive_float(row["T.df1." + side], "F df1")
            degrees2 = _positive_float(row["T.df2." + side], "F df2")
            statistic = _positive_float(row["T.Test.value." + side], "F statistic", allow_zero=True)
            p = float(f_distribution.sf(statistic, degrees1, degrees2))
            if not math.isfinite(p) or not 0 <= p <= 1:
                raise ValueError("invalid calculated F survival probability")
            slot = results[kind]
            slot["eligible_f_tests"] += 1
            supplied = row["T.pval.recalc." + side]
            if supplied in ("", "NA"):
                slot["reported_p_missing"] += 1
            else:
                claimed = _positive_float(supplied, "supplied p", allow_zero=True)
                if claimed > 1:
                    raise ValueError("supplied p above 1")
                difference = abs(claimed - p)
                slot["largest_absolute_p_error"] = max(slot["largest_absolute_p_error"], difference)
                slot["reported_p_available"] += 1
                slot["reported_p_agree" if difference <= TOLERANCE else "reported_p_disagree"] += 1
            source_flag = row[flag]
            if source_flag in ("", "NA"):
                slot["flags_missing"] += 1
            elif source_flag in ("0", "1"):
                slot["flags_available"] += 1
                observed = 1 if p < ALPHA else 0
                slot["flags_agree" if observed == int(source_flag) else "flags_disagree"] += 1
            else:
                raise ValueError("unexpected source significance flag")
    if not n_rows:
        raise ValueError("empty source data")
    for slot in results.values():
        if (slot["reported_p_available"] + slot["reported_p_missing"] != slot["eligible_f_tests"]
                or slot["flags_available"] + slot["flags_missing"] != slot["eligible_f_tests"]):
            raise ValueError("incomplete F-test ledger")
    return {
        "total_source_rows": n_rows,
        "only_test_family": "F",
        "method": "SciPy F survival function: scipy.stats.f.sf(statistic, df1, df2)",
        "absolute_p_tolerance": TOLERANCE,
        "alpha_for_flag_check": ALPHA,
        "side_results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="One read from the same commit-pinned public source as aggregate.py")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({"status": "UNOBSERVED", "reason": "opt-in source retrieval required"}))
        return 0
    raw, seen = fetch_source()
    base = inspect_bytes(raw)
    # Lossless one-byte transport for ASCII stats in mixed-encoding CSV.
    result = analyze(raw.decode("latin-1"))
    out = {
        "schema_version": 1,
        "status": "MEASURED",
        "observed_at_utc": seen,
        "source_git_blob_sha1": base["source_git_blob_sha1"],
        "source_sha256": base["source_sha256"],
        "source_commit": base["source_commit"],
        "source_bytes": base["source_bytes"],
        "analysis": result,
        "limits": [
            "F-test rows only; other statistical families not classified",
            "Inputs are study-team summary statistics, not original participant data",
            "Source F-statistics may be rounded, so p-value disagreement can reflect source precision",
            "Matching p-values does not independently reproduce experiments or effect estimates",
            "No source CSV rows or personal researcher details archived",
        ],
    }
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
