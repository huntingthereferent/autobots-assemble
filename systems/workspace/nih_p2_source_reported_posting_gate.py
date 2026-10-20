"""Bounded source-reported publication-clock probe; never silently admit known_at.

Inputs: byte-pinned minimal real Chromium source receipt (V259,V260),
plus a freshly inspected official NLM definition of 'Last Update Posted'.
No claim of a version-specific first-public timestamp from a second archive,
clinical validity, general temporal KG proof or NIH benchmark completion.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

SCHEMA = "nih-p2-source-reported-posting-comparison/v1"
EVIDENCE = Path(__file__).parent / "fixtures/nih_p2_original_adjacent_source_receipt_39421372666.json"
PINNED_RECEIPT_SHA256 = "9adf3d0419b89a8c098b97b61bbfec874d5833b69bdf0fced213628188ad5540"
ORIGINAL_ZIP_SHA256 = "45c245cf94200d26b7263d0d03eb86549da8661598627434fadca83e4755e414"
ORIGINAL_RUN = 39421372666
ORIGINAL_ARTIFACT = 12264180158
NLM_URL = "https://www.nlm.nih.gov/pubs/techbull/so17/so17_clinicaltrials.html"
CAP = 240_000
CUTOFFS = (
    "2022-10-26", "2022-10-27", "2022-11-06",
    "2022-11-07", "2022-11-08",
)
DATES = {259: ("2022-10-26", "2022-10-27"),
         260: ("2022-11-04", "2022-11-07")}
STATUS = {259: "Recruiting", 260: "Completed"}
SHA = re.compile(r"[0-9a-f]{64}\Z")


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def day(text: object) -> str:
    if type(text) is not str or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise ValueError("source day must be canonical")
    if date.fromisoformat(text).isoformat() != text:
        raise ValueError("source day is not a real calendar day")
    return text


def authenticate_receipt(raw: bytes) -> list[dict]:
    """Fail closed on byte changes; fixture is copied from an exact artifact."""
    if sha(raw) != PINNED_RECEIPT_SHA256:
        raise ValueError("original source receipt bytes differ from retained artifact")
    record = json.loads(raw)
    if (record.get("schema") != "nih-p2-official-adjacent-original-status/v1"
        or record.get("study") != "NCT00001756"
        or record.get("adjacent_version_pair_checked") is not True
        or record.get("two_original_version_fields_witnessed") is not True
        or record.get("observed_status_changed") is not True
        or record.get("first_public_version_timestamp") != "UNAVAILABLE"
        or record.get("known_at_admitted_to_W13") is not False
        or record.get("historical_temporal_benchmark_completed") is not False
        or record.get("original_twelve_job_W13_modified") is not False):
        raise ValueError("previous real source witness changed its bounded claim")
    pair = record.get("records")
    if type(pair) is not list or [r.get("version") for r in pair] != [259, 260]:
        raise ValueError("exact adjacent original versions missing")
    for r in pair:
        v = r["version"]
        submission, posting = DATES[v]
        if (set(r) != {
            "clinical_result_inferred", "first_public_version_timestamp_independently_authenticated",
            "observed_overall_status", "observed_version_local_last_update_posted",
            "observed_version_local_qc_submitted", "original_version_fields_witnessed",
            "original_visible_text_sha256", "posted_date_qualifier", "retrieved_utc",
            "source_url", "submitted_in_original_selected_version", "version",
            "version_local_status_section_sha256",
        } or r["observed_overall_status"] != STATUS[v]
            or r["submitted_in_original_selected_version"] != submission
            or r["observed_version_local_qc_submitted"] != submission
            or r["observed_version_local_last_update_posted"] != posting
            or r["posted_date_qualifier"] != "Actual"
            or r["first_public_version_timestamp_independently_authenticated"] is not False
            or r["original_version_fields_witnessed"] is not True
            or r["clinical_result_inferred"] is not False
            or r["source_url"] !=
              f"https://clinicaltrials.gov/study/NCT00001756?a={v}&tab=history"):
            raise ValueError("not exact original version-local fields")
        if not all(SHA.fullmatch(r[f]) for f in (
            "original_visible_text_sha256", "version_local_status_section_sha256")):
            raise ValueError("source fingerprints missing")
        stamp = datetime.fromisoformat(r["retrieved_utc"])
        if stamp.tzinfo is None or stamp.utcoffset() is None or stamp.date() < date.fromisoformat(posting):
            raise ValueError("original source retrieval time invalid")
    if not (day(DATES[259][0]) < day(DATES[259][1])
            < day(DATES[260][0]) < day(DATES[260][1])):
        raise ValueError("historical source date ordering is unsupported")
    return pair


def inspect_nlm_html(raw: bytes, *, observed_utc: str) -> dict:
    """The official field definition proves semantics, NOT specific version timing."""
    if not raw or len(raw) > CAP:
        raise ValueError("NLM definition response empty or too large")
    parser = _Text()
    parser.feed(raw.decode("utf8"))
    plain = " ".join(" ".join(parser.parts).split()).casefold()
    anchors = (
        "last update posted",
        "date on which changes to a study record were posted",
        "when updated study information is publicly available",
        "delays sometimes occur",
    )
    if not all(p in plain for p in anchors):
        raise ValueError("official NLM field semantics could not be independently observed")
    stamp = datetime.fromisoformat(observed_utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("NLM retrieval timestamp lacks timezone")
    return {
        "source_url": NLM_URL,
        "source": "U.S. National Library of Medicine Technical Bulletin, September 25, 2017",
        "retrieved_utc": observed_utc,
        "response_sha256": sha(raw),
        "source_defines_last_update_posted_as_public_availability": True,
        "original_version_first_public_observed_from_this_source": False,
    }


def live_nlm() -> dict:
    """Only one exact public NLM URL, no external credentials or bypass."""
    req = Request(NLM_URL, headers={"User-Agent": "A-B-NIH-Bounded-Source-Research/1.0"})
    with urlopen(req, timeout=25) as resp:
        final = urlsplit(resp.geturl())
        if (resp.status != 200 or final.scheme != "https"
                or final.hostname != "www.nlm.nih.gov"
                or final.path != "/pubs/techbull/so17/so17_clinicaltrials.html"):
            raise ValueError("official NLM document changed origin/path or HTTP status")
        length = resp.headers.get("Content-Length")
        if length and int(length) > CAP:
            raise ValueError("NLM source exceeded evidence bound")
        raw = resp.read(CAP + 1)
    return inspect_nlm_html(raw, observed_utc=datetime.now(timezone.utc).isoformat())


def movement(pair: list[dict], semantics: dict) -> dict:
    if (semantics.get("source_url") != NLM_URL
            or semantics.get("source_defines_last_update_posted_as_public_availability") is not True
            or semantics.get("original_version_first_public_observed_from_this_source") is not False
            or not SHA.fullmatch(semantics.get("response_sha256", ""))):
        raise ValueError("external NLM semantics not admitted")
    if [r["version"] for r in pair] != [259, 260]:
        raise ValueError("source ancestry lost")
    # No imposed clinical validity date: these are source-reported posting
    # candidates, shown for a conditional as-of exercise only.
    events = [{
        "source_version": r["version"],
        "status": r["observed_overall_status"],
        "source_reported_last_update_posted": r["observed_version_local_last_update_posted"],
        "source_url": r["source_url"],
        "historical_record_valid_at": "UNAVAILABLE",
        "independent_version_first_public_timestamp": "UNAVAILABLE",
    } for r in pair]
    comparisons = []
    for cutoff in CUTOFFS:
        eligible = [e for e in events
                    if e["source_reported_last_update_posted"] <= cutoff]
        last = eligible[-1] if eligible else None
        # Never call an absent earlier version false; it is unobserved.
        comparisons.append({
            "cutoff": cutoff,
            "selected_version_if_source_reported_posting_is_used":
                last["source_version"] if last else None,
            "selected_status_if_source_reported_posting_is_used":
                last["status"] if last else "UNAVAILABLE",
            "future_version_ids_withheld_under_this_assumption":
                [e["source_version"] for e in events if e not in eligible],
            "static_all_source_version_ids": [259, 260],
            "unknown_clinical_valid_at": True,
        })
    return {
        "schema": SCHEMA,
        "real_original_source_artifact": {
            "run_id": ORIGINAL_RUN, "artifact_id": ORIGINAL_ARTIFACT,
            "zip_sha256": ORIGINAL_ZIP_SHA256,
            "receipt_sha256": PINNED_RECEIPT_SHA256,
        },
        "external_semantics": semantics,
        "source_version_events": events,
        "conditional_comparisons": comparisons,
        "interpretation": "source-reported-posting-date-conditional-only",
        "original_version_first_public_independently_authenticated": False,
        "known_at_admitted_to_original_W13": False,
        "clinical_fact_valid_at_authenticated": False,
        "NIH_phase2_real_temporal_benchmark_completed": False,
        "original_W13_journal_modified": False,
        "source_original_bodies_copied": False,
    }


def run(*, live: bool) -> dict:
    pair = authenticate_receipt(EVIDENCE.read_bytes())
    if live:
        semantics = live_nlm()
    else:
        raise ValueError("a live independent official semantic witness is required")
    return movement(pair, semantics)


def main() -> None:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--output", required=True, type=Path)
    ns = args.parse_args()
    answer = run(live=True)
    ns.output.parent.mkdir(parents=True, exist_ok=True)
    ns.output.write_text(json.dumps(answer, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({
        "comparisons": [(r["cutoff"], r["selected_status_if_source_reported_posting_is_used"])
                        for r in answer["conditional_comparisons"]],
        "known_at_admitted": answer["known_at_admitted_to_original_W13"],
        "full_benchmark_completed": answer["NIH_phase2_real_temporal_benchmark_completed"],
    }))


if __name__ == "__main__":
    main()
