"""Independently join two public Chromium original-version observations.

Only source-owner *day-labelled* Last Update Posted metadata is admitted.
The actual first-public-availability transaction/timezone and any historical
patient/clinical outcome are NOT authenticated. Original W13 twelve-job
native history and WORLD multiroom contract remain untouched.
"""
from __future__ import annotations
from datetime import date
import json
from pathlib import Path

SCHEMA="world-nih-p2-two-original-version-posted-day-cross-witness/v1"
NCT="NCT00001756"
VERSIONS=(94,105)
EXPECTED_OWNER_FIELD=("2019-08-02","2019-11-25")
KNOWN_BODY_HASHES=(
 "4370ff462cd731f2f42cc866aadb438e4d037c7a05de2cd64fb5acb53500c3ba",
 "4daab6b95ea574a0aeaea3fba36a94fd9db8df8f0dafd41eee5b87bd9a6bd9db",
)
EXPECTED_SUBMITTED=("2019-08-01","2019-11-22")

def join(status,dates):
    if (type(status) is not dict or
        status.get("schema")!="world-nih-p2-original-version-field-probe/v1" or
        status.get("nct_id")!=NCT or
        type(dates) is not dict or
        dates.get("schema")!="world-nih-p2-original-version-posting-field-access/v1" or
        dates.get("study")!=NCT or
        dates.get("history_query_without_posted_at")!="BLOCKED_PENDING_OWNER_POSTING_EVIDENCE" or
        dates.get("original_per_version_first_posted_instants_authenticated") is not False or
        dates.get("admissible_temporal_known_at") is not None or
        status.get("independent_historical_version_status_count")!=2):
        raise ValueError("historical source owner context or time boundary missing")
    s=status.get("version_records")
    d=dates.get("records")
    if (type(s) is not list or len(s)!=2 or type(d) is not list or len(d)!=2 or
        [r.get("version") for r in s]!=list(VERSIONS) or
        [r.get("version") for r in d]!=list(VERSIONS)):
        raise ValueError("historical source versions missing or substituted")
    claims=[]
    for index,(r,p) in enumerate(zip(s,d)):
        v=VERSIONS[index]
        url=f"https://clinicaltrials.gov/study/{NCT}?a={v}&tab=history"
        h=KNOWN_BODY_HASHES[index]
        sub=EXPECTED_SUBMITTED[index]
        expected_day=EXPECTED_OWNER_FIELD[index]
        posted_fields=p.get("selected_version_detail_posting_field_dates")
        if (r.get("url")!=url or p.get("url")!=url or
            r.get("version_page_independently_visible") is not True or
            p.get("original_version_visible") is not True or
            r.get("version_detail_status_authenticated") is not True or
            r.get("version_detail_status")!="RECRUITING" or
            r.get("original_source_body_sha256")!=h or
            p.get("owner_browser_visible_body_sha256")!=h or
            p.get("submission_date_owner_recorded")!=sub or
            p.get("posted_at_authenticated") is not False or
            p.get("version_submitted_at_is_not_version_posted_at") is not True or
            p.get("current_header_last_update_posted_cannot_establish_version_posting") is not True or
            p.get("selected_version_detail_posting_field_label_count")!=1 or
            type(posted_fields) is not list or len(posted_fields)!=1 or
            posted_fields[0] != {"label":"Last Update Posted","following_iso_dates":[expected_day]}):
            raise ValueError("nonmatching original version field/page hash/owner date")
        if not (date.fromisoformat(sub)<date.fromisoformat(expected_day)):
            raise ValueError("owner named posting day cannot precede submission")
        claims.append({
            "version":v,"source_owner":"ClinicalTrials.gov / NLM",
            "source_url":url,
            "original_page_text_sha256":h,
            "historical_status":"RECRUITING",
            "historical_status_source_field":"Overall Status / Recruitment Status",
            "source_named_submission_day":sub,
            "source_named_last_update_posted_day":expected_day,
            "source_named_posted_day_witnessed_twice":True,
            "source_named_posted_day_is_exact_first_public_transaction":False,
            "actual_first_public_instant_and_timezone_authenticated":False})
    if not (claims[0]["source_named_last_update_posted_day"]
            <claims[1]["source_named_last_update_posted_day"]):
        raise ValueError("source posting-day order contradicted")
    return {"schema":SCHEMA,
        "source":"official original historical ClinicalTrials.gov viewer",
        "study":NCT,
        "version_count":2,
        "historical_version_status_source_witness":True,
        "original_version_last_update_posted_days_source_witnessed":True,
        "status_and_date_independent_browser_views_exact_text_sha256_joined":True,
        "source_owner_posted_day_claims":claims,
        "specific_page_version_source_claims_not_real_world_clinical_truth":True,
        "version_posted_day_metadata_attested_by_primary_owner":True,
        "independently_witnessed_original_public_posting_transactions":False,
        "exact_first_publication_UTC_instants_authenticated":False,
        "no_intervening_changes_proven":False,
        "executable_source_owned_known_at_instant":None,
        "source_event_2026_fictional_game_chronology_is_separate":True,
        "original_twelve_job_native_journals_modified":False,
        "official_NIH_submission":False}

def run(folder):
    p=Path(folder)
    s=json.loads((p/"world-nih-p2-original-history-field-probe.json").read_text())
    d=json.loads((p/"world-nih-p2-official-version-posting-probe.json").read_text())
    report=join(s,d)
    (p/"world-nih-p2-historical-posted-day-cross-witness.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "schema":SCHEMA,
        "versions":[r["version"] for r in report["source_owner_posted_day_claims"]],
        "source_owner_posted_days":[r["source_named_last_update_posted_day"]
                                   for r in report["source_owner_posted_day_claims"]],
        "matched_independently_witnessed_page_sha256":True,
        "original_posting_transactions_authentic":False,
        "exact_UTC_instants_supported":False,"native_jobs_added":0},sort_keys=True))
    return report

if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--evidence-dir",required=True)
    args=a.parse_args()
    run(args.evidence_dir)
