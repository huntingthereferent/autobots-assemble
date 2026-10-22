"""Count paired significance flags in a frozen public research-data export.

Offline by default; fetches one fixed GitHub source only with --live.
No original experimental observation is repeated here.
"""
import argparse
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from urllib.request import urlopen

COMMIT = "a7c5b87f15f60178e6f5d25f983217d39f5ac654"
PATH = "data_allformats/RPPdataConverted.csv"
URL = f"https://raw.githubusercontent.com/CenterForOpenScience/rpp/{COMMIT}/{PATH}"
BLOB_SHA = "6c8ce0b93b9a83ac42669745bd1054da7c22a687"
BYTES = 288855
ORIG = "T.sign.O.131"
REPL = "T.sign.R.132"
PUBLISHED = {"paired": 100, "original": 97, "replication": 36, "both": 35}


def summarize(data):
    reader = csv.DictReader(io.StringIO(data))
    if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError("ambiguous column headers")
    if not {"Local.ID", ORIG, REPL}.issubset(reader.fieldnames):
        raise ValueError("missing required research columns")
    seen = set()
    result = {"total": 0, "paired": 0, "original": 0, "replication": 0,
              "both": 0, "original_only": 0, "replication_only": 0,
              "neither": 0, "excluded": 0}
    for record in reader:
        ident = record["Local.ID"]
        if not ident or ident in seen or None in record:
            raise ValueError("duplicate, missing or malformed record")
        seen.add(ident)
        result["total"] += 1
        a, b = record[ORIG], record[REPL]
        if a in ("", "NA") or b in ("", "NA"):
            result["excluded"] += 1
            continue
        if a not in ("0", "1") or b not in ("0", "1"):
            raise ValueError("unrecognized significance flag")
        x, y = int(a), int(b)
        result["paired"] += 1
        result["original"] += x
        result["replication"] += y
        if x and y:
            result["both"] += 1
        elif x:
            result["original_only"] += 1
        elif y:
            result["replication_only"] += 1
        else:
            result["neither"] += 1
    if not result["total"]:
        raise ValueError("empty source")
    return result


def inspect_bytes(raw, check_source=True):
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
    if check_source and (len(raw) != BYTES or sha != BLOB_SHA):
        raise ValueError("unrecognized source snapshot")
    # The upstream pinned CSV includes non-UTF-8 bytes in free-text columns.
    # ISO-8859-1 is a lossless byte-to-codepoint transport for CSV parsing;
    # only ASCII numeric flags and record identifiers participate in this test.
    counts = summarize(raw.decode("latin-1"))
    difference = {k: {"expected": v, "observed": counts[k]}
                  for k, v in PUBLISHED.items() if counts[k] != v}
    return {
        "status": "MATCH" if not difference else "MISMATCH",
        "source_git_blob_sha1": sha,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_bytes": len(raw),
        "source_verified": check_source,
        "source_commit": COMMIT,
        "data_path": PATH,
        "counts": counts,
        "published_reference": "https://doi.org/10.1126/science.aac4716",
        "differences": difference,
        "scope": "Published paired significance-flag aggregation only",
        "psychology_experiments_repeated": False,
        "source_flags_recomputed_from_raw_observations": False,
        "raw_data_archived": False,
        "source_rights": "Research source is public; redistribution license not confirmed",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--output")
    args = ap.parse_args()
    if not args.live:
        print(json.dumps({"status": "UNOBSERVED", "source": URL}))
        return 0
    with urlopen(URL, timeout=20) as stream:
        raw = stream.read(400001)
        observed = datetime.now(timezone.utc).isoformat()
    if len(raw) > 400000:
        raise ValueError("source size exceeds limit")
    receipt = inspect_bytes(raw)
    receipt["observed_at_utc"] = observed
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        from pathlib import Path
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    print(text)
    return 0 if receipt["status"] == "MATCH" else 2


if __name__ == "__main__":
    raise SystemExit(main())
