"""ML lane: one verified OpenML Iris v1 held-out baseline comparison.

No background work, no unrestricted source fetch, no source data committed.
The source metadata, ARFF, checksum and split are verified at *run time*;
do not use the word 'reproduced' for an unrelated paper's conclusions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

META_URL = "https://www.openml.org/api/v1/json/data/61"
DATA_URL = "https://www.openml.org/data/v1/download/61/iris.arff"
ALLOWED_HOSTS = {"www.openml.org", "api.openml.org"}
SPLIT_SEED = "sourcefirst-iris-v1-split-20261022"
CLASS_SIZE = 50
HOLDOUT_PER_CLASS = 10
FEATURE_COUNT = 4
REQUIRED_N = 150
MAX_META = 300000
MAX_DATA = 120000
ARCHIVED_METADATA_SHA256 = "7e408fec68984cfcf25f360ca267e706bc5ef27284a17351f78429660c14acd0"
ARCHIVED_RUN_URL = "https://github.com/huntingthereferent/autobots-assemble/actions/runs/39771470448"


class RestrictedRedirect(HTTPRedirectHandler):
    """Only follow HTTPS redirects between exact OpenML data API hosts."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        u = urlsplit(newurl)
        if (u.scheme != "https" or u.hostname not in ALLOWED_HOSTS or
                u.username or u.password or u.port not in (None, 443) or
                not (u.path.startswith("/data/v1/download/") or
                     u.path.startswith("/api/v1/json/data/"))):
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get_exact(url: str, byte_limit: int, opener=None) -> tuple[bytes, str]:
    loc = urlsplit(url)
    if (url not in (META_URL, DATA_URL) or loc.scheme != "https" or
            loc.hostname not in ALLOWED_HOSTS):
        raise ValueError("not an approved exact research source")
    client = opener or build_opener(RestrictedRedirect)
    request = Request(url, headers={"Accept": "application/json,text/plain,*/*;q=0.5",
                                    "User-Agent": "HuntingReferentResearch/1.0 openml-61"})
    with client.open(request, timeout=20) as response:
        final_url = response.geturl()
        target = urlsplit(final_url)
        if target.scheme != "https" or target.hostname not in ALLOWED_HOSTS:
            raise ValueError("source redirected out of allowed domain")
        if response.status != 200:
            raise ValueError("source did not return HTTP 200")
        content = response.read(byte_limit + 1)
    if len(content) > byte_limit:
        raise ValueError("source exceeded strict byte budget")
    return content, final_url


def validate_metadata(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8-sig"))
    record = data.get("data_set_description") if isinstance(data, dict) else None
    if not isinstance(record, dict):
        raise ValueError("missing OpenML description")
    if (str(record.get("id")) != "61" or
            str(record.get("version")) != "1" or
            str(record.get("name", "")).lower() != "iris" or
            str(record.get("default_target_attribute", "")).lower() != "class"):
        raise ValueError("OpenML dataset identity/version/target mismatch")
    expected_count = record.get("NumberOfInstances", record.get("number_of_instances"))
    if expected_count is not None and int(expected_count) != REQUIRED_N:
        raise ValueError("dataset metadata number of rows changed")
    declared_md5 = str(record.get("md5_checksum") or "").lower().strip()
    if declared_md5 and not re.fullmatch(r"[0-9a-f]{32}", declared_md5):
        raise ValueError("invalid publisher data MD5")
    return {"record_id": "openml:61", "version": 1, "target": "class",
            "source_md5": declared_md5 or None,
            "source_metadata_sha256": hashlib.sha256(raw).hexdigest()}


def parse_iris_arff(raw: bytes) -> list[tuple[tuple[float, ...], str]]:
    text = raw.decode("utf-8-sig")
    attributes = []
    in_data = False
    data = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("%"):
            continue
        if not in_data:
            if line.lower().startswith("@attribute"):
                attributes.append(line)
            elif line.lower() == "@data":
                in_data = True
            continue
        if line.startswith("{"):
            raise ValueError("sparse ARFF not admitted")
        fields = next(csv.reader([line]))
        if len(fields) != FEATURE_COUNT + 1 or "?" in fields:
            raise ValueError("missing/incorrect ARFF values")
        try:
            vec = tuple(float(f) for f in fields[:FEATURE_COUNT])
        except ValueError as e:
            raise ValueError("nonnumeric Iris feature") from e
        if any(not math.isfinite(x) for x in vec):
            raise ValueError("nonfinite Iris feature")
        label = fields[-1].strip().strip("'\"")
        if not label:
            raise ValueError("missing Iris class")
        data.append((vec, label))
    if not in_data or len(attributes) != FEATURE_COUNT + 1 or len(data) != REQUIRED_N:
        raise ValueError("unexpected ARFF schema or row count")
    labels = Counter(cls for _, cls in data)
    if len(labels) != 3 or sorted(labels.values()) != [CLASS_SIZE] * 3:
        raise ValueError("unexpected class balance")
    return data


def split_indices(rows: list[tuple[tuple[float, ...], str]]) -> tuple[list[int], list[int]]:
    # Group repeated feature vectors BEFORE splitting to prevent exact leakage
    # between training and held-out data. The Iris source has a repeated row.
    groups = {}
    for i, (vector, label) in enumerate(rows):
        item = groups.setdefault(vector, {"label": label, "indexes": []})
        if item["label"] != label:
            raise ValueError("identical features carry contradictory labels")
        item["indexes"].append(i)
    by_class = {}
    for vector, item in groups.items():
        by_class.setdefault(item["label"], []).append((vector, item["indexes"]))
    train, test = [], []
    for label, group_list in sorted(by_class.items()):
        def order(item):
            vector, _ = item
            key = (SPLIT_SEED + "|" + label + "|" +
                   ",".join(format(v, ".17g") for v in vector)).encode("utf-8")
            return hashlib.sha256(key).hexdigest()
        picked, chosen_groups = 0, set()
        for vector, indexes in sorted(group_list, key=order):
            if picked + len(indexes) <= HOLDOUT_PER_CLASS:
                chosen_groups.add(vector)
                picked += len(indexes)
            if picked == HOLDOUT_PER_CLASS:
                break
        if picked != HOLDOUT_PER_CLASS:
            raise ValueError("group-stratified holdout cannot reach exact target")
        for vector, indexes in group_list:
            (test if vector in chosen_groups else train).extend(indexes)
    if (len(train) != 120 or len(test) != 30 or set(train) & set(test) or
            {rows[i][0] for i in train} & {rows[i][0] for i in test}):
        raise ValueError("group-stratified split has leakage")
    return sorted(train), sorted(test)


def measure(rows: list[tuple[tuple[float, ...], str]]) -> dict:
    if len(rows) != REQUIRED_N:
        raise ValueError("incomplete dataset")
    train, held_out = split_indices(rows)
    label_counts = Counter(rows[i][1] for i in train)
    baseline_label = sorted(label_counts, key=lambda cls: (-label_counts[cls], cls))[0]
    means = [sum(rows[i][0][j] for i in train) / len(train) for j in range(FEATURE_COUNT)]
    scales = [math.sqrt(sum((rows[i][0][j] - means[j]) ** 2 for i in train)
                        / len(train)) for j in range(FEATURE_COUNT)]
    if any(s == 0 for s in scales):
        raise ValueError("train-only feature variance is zero")
    labels = sorted(label_counts)
    centroids = {}
    for label in labels:
        subs = [rows[i][0] for i in train if rows[i][1] == label]
        centroids[label] = tuple(
            sum((point[j] - means[j]) / scales[j] for point in subs) / len(subs)
            for j in range(FEATURE_COUNT)
        )
    def classifier(vector):
        scaled = [(vector[j] - means[j]) / scales[j] for j in range(FEATURE_COUNT)]
        return min(labels, key=lambda label: (
            sum((scaled[j] - centroids[label][j]) ** 2 for j in range(FEATURE_COUNT)), label
        ))
    model_correct = sum(classifier(rows[i][0]) == rows[i][1] for i in held_out)
    baseline_correct = sum(baseline_label == rows[i][1] for i in held_out)
    split_hash = hashlib.sha256(",".join(map(str, held_out)).encode()).hexdigest()
    return {
        "n_total": len(rows), "n_train": len(train), "n_held_out": len(held_out),
        "holdout_per_class": HOLDOUT_PER_CLASS, "n_features": FEATURE_COUNT,
        "split_seed": SPLIT_SEED, "holdout_index_sha256": split_hash,
        "split_is_stratified": True, "duplicate_feature_groups_kept_intact": True,
        "train_only_scaler": True,
        "majority_correct": baseline_correct, "majority_accuracy": baseline_correct / len(held_out),
        "centroid_correct": model_correct, "centroid_accuracy": model_correct / len(held_out),
        "delta_accuracy": (model_correct - baseline_correct) / len(held_out),
        "hypothesis": "Train-only standardised nearest-centroid exceeds train-majority accuracy on this exact held-out Iris split.",
        "boundary": "No other tasks, random seeds, datasets, inference claims, or generalization have been tested.",
    }


def live_run() -> dict:
    meta_bytes, observed_meta_url = get_exact(META_URL, MAX_META)
    identity = validate_metadata(meta_bytes)
    raw_data, observed_data_url = get_exact(DATA_URL, MAX_DATA)
    exact_md5 = hashlib.md5(raw_data).hexdigest()
    if identity["source_md5"] and exact_md5 != identity["source_md5"]:
        raise ValueError("dataset content does not match OpenML-declared checksum")
    rows = parse_iris_arff(raw_data)
    metrics = measure(rows)
    return {
        "schema_version": 1, "status": "MEASURED_ON_EXACT_SOURCE_BYTES",
        "lane_id": "ML", "source_id": "openml", "record_id": "61",
        "record_version": 1, "source_metadata_url": observed_meta_url,
        "source_data_url": observed_data_url,
        "source_metadata_sha256": identity["source_metadata_sha256"],
        "source_data_sha256": hashlib.sha256(raw_data).hexdigest(),
        "source_data_md5": exact_md5, "md5_matched_declared_source": bool(identity["source_md5"]),
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_receipt_reference": ARCHIVED_RUN_URL,
        "source_metadata_reference_sha256": ARCHIVED_METADATA_SHA256,
        "comparison": metrics,
        "data_redistributed": False,
        "limits": [
            "Only 150-row OpenML Iris dataset v1, not every Iris variant or another OpenML task.",
            "One predeclared stratified split and single algorithm/baseline; no confidence interval or multi-seed stability.",
            "Download does not establish clinical/botanical conclusions or external generalization.",
            "ARFF contents are not redistributed; public dataset catalog lists reuse as Public, review applicable terms before reuse.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Opt in to two bounded, checked OpenML requests")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {"schema_version": 1, "lane_id": "ML", "status": "UNOBSERVED",
              "scientific_experiments_run": 0, "reason": "explicit --live needed"}
    if args.live:
        try:
            result = live_run()
        except (HTTPError, URLError, ValueError, TimeoutError, OSError,
                UnicodeError, json.JSONDecodeError) as e:
            result = {"schema_version": 1, "lane_id": "ML", "status": "SOURCE_WALL",
                      "error_class": type(e).__name__,
                      "error": str(e)[:180], "scientific_experiments_run": 0,
                      "source_metadata_url": META_URL, "source_data_url": DATA_URL}
    text = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0 if result["status"] != "SOURCE_WALL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
