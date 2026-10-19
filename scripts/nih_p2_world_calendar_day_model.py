"""Day-granularity temporal access experiment, restricted to two real original
ClinicalTrials.gov version *source claims* independently witnessed in WORLD.

Date-only publication metadata CANNOT authenticate a UTC time or first-public
transaction. The temporal states are conditional model outcomes for the
source-owner-reported *Last Update Posted* calendar day, not observed 2019
traffic and not a modified original native temporal_query.py.
"""
from __future__ import annotations
from datetime import date, timedelta
import json
from pathlib import Path

SCHEMA="world-nih-p2-owner-reported-calendar-day-temporal/v1"
CUTOFFS=("2019-08-01","2019-08-02","2019-08-03",
         "2019-11-24","2019-11-25","2019-11-26")
NOT_YET="BEFORE_OWNER_REPORTED_DAY"
MAYBE="SAME_DAY_TIME_UNRESOLVED"
AFTER="AFTER_OWNER_REPORTED_DAY"
VERSIONS=(94,105)

def validate_source(source):
    if (type(source) is not dict or
        source.get("schema")!="world-nih-p2-two-original-version-posted-day-cross-witness/v1" or
        source.get("study")!="NCT00001756" or
        source.get("version_count")!=2 or
        source.get("historical_version_status_source_witness") is not True or
        source.get("original_version_last_update_posted_days_source_witnessed") is not True or
        source.get("status_and_date_independent_browser_views_exact_text_sha256_joined") is not True or
        source.get("exact_first_publication_UTC_instants_authenticated") is not False or
        source.get("independently_witnessed_original_public_posting_transactions") is not False or
        source.get("no_intervening_changes_proven") is not False or
        source.get("executable_source_owned_known_at_instant") is not None or
        source.get("source_event_2026_fictional_game_chronology_is_separate") is not True or
        source.get("original_twelve_job_native_journals_modified") is not False):
        raise ValueError("real original source/day and unresolved-time boundary not witnessed")
    items=source.get("source_owner_posted_day_claims")
    if type(items) is not list or len(items)!=2 or [x.get("version") for x in items]!=list(VERSIONS):
        raise ValueError("missing original source versions")
    from scripts.nih_p2_world_posted_day_cross_witness import (
        EXPECTED_OWNER_FIELD,KNOWN_BODY_HASHES,EXPECTED_SUBMITTED)
    for v,entry,day,h,sub in zip(VERSIONS,items,EXPECTED_OWNER_FIELD,
                                  KNOWN_BODY_HASHES,EXPECTED_SUBMITTED):
        if (entry.get("source_owner")!="ClinicalTrials.gov / NLM"
            or entry.get("source_url")!=f"https://clinicaltrials.gov/study/NCT00001756?a={v}&tab=history"
            or entry.get("historical_status")!="RECRUITING"
            or entry.get("original_page_text_sha256")!=h
            or entry.get("source_named_submission_day")!=sub
            or entry.get("source_named_last_update_posted_day")!=day
            or entry.get("source_named_posted_day_witnessed_twice") is not True
            or entry.get("source_named_posted_day_is_exact_first_public_transaction") is not False
            or entry.get("actual_first_public_instant_and_timezone_authenticated") is not False):
            raise ValueError("original-version source evidence drifted")
    return tuple((x["version"],date.fromisoformat(x["source_named_last_update_posted_day"]))
                 for x in items)

def projection(source,day):
    pairs=validate_source(source)
    if type(day) is not str or day not in CUTOFFS:
        raise ValueError("query day outside bounded original historical study")
    cutoff=date.fromisoformat(day)
    states=[(v,NOT_YET if cutoff<posted else MAYBE if cutoff==posted else AFTER)
            for v,posted in pairs]
    admitted=[v for v,s in states if s==AFTER]
    possible=[v for v,s in states if s!=NOT_YET]
    # Historical-version queries return what might be the LATEST version
    # under the conditional model; preserve the possibility of none.
    possible_latest=[]
    for v in possible:
        if not any(other>v and st==AFTER for other,st in states):
            possible_latest.append(v)
    if not admitted:
        possible_latest=[None]+possible_latest
    latest=admitted[-1] if admitted else None
    return {"day":day,"statuses":{str(v):st for v,st in states},
        "static_latest_version":pairs[-1][0],
        "possible_latest_versions":possible_latest,
        "latest_guaranteed_version":latest if possible_latest==[latest] else None,
        "version_status_values_at_source":["RECRUITING","RECRUITING"],
        "boundary":"source-reported posted DAY, unknown first-public TIME",
        "real_world_availability_authenticated":False,
        "exact_known_at_utc":None}

def independent_oracle(source,day):
    """Independent event-sequence enumeration, not a copy of projection rules.

    Enumerate two counterfactual intraday posting orders (before/after an
    arbitrary within-day reader moment) for *each* original version. All
    alternatives remain source-claim-conditional rather than historical facts.
    """
    pairs=validate_source(source)
    target=date.fromisoformat(day)
    if day not in CUTOFFS:raise ValueError("outside declared grid")
    # Distinct implementation: enumerate morning/late release scenarios and
    # classify each version using agreement across complete event histories.
    from itertools import product
    histories=[]
    for choices in product((0,1),repeat=len(pairs)):
        present=[]
        for (v,posted),before_observation in zip(pairs,choices):
            # One day is mapped onto ordinal day bins with 0/1 intraday slots;
            # the cutoff observes the middle of the selected date.
            release_order=posted.toordinal()*2+before_observation
            observation_order=target.toordinal()*2
            if release_order<=observation_order:present.append(v)
        histories.append(tuple(sorted(present)))
    labels={}
    for version,_ in pairs:
        occurrences=sum(version in history for history in histories)
        labels[str(version)]=(AFTER if occurrences==len(histories)
                              else NOT_YET if occurrences==0 else MAYBE)
    latest=sorted(set(max(h) if h else None for h in histories),
                  key=lambda x: (-1 if x is None else x))
    return {"statuses":labels,"possible_latest_versions":latest}

def verify_grid(source):
    rows=[]
    for d in CUTOFFS:
        actual=projection(source,d)
        independent=independent_oracle(source,d)
        if (actual["statuses"]!=independent["statuses"] or
            actual["possible_latest_versions"]!=independent["possible_latest_versions"]):
            raise ValueError("source-day classifier diverged from independent scenario oracle")
        rows.append(actual)
    expected=[
        (NOT_YET,NOT_YET,[None]),
        (MAYBE,NOT_YET,[None,94]),
        (AFTER,NOT_YET,[94]),
        (AFTER,NOT_YET,[94]),
        (AFTER,MAYBE,[94,105]),
        (AFTER,AFTER,[105])]
    for r,(v94,v105,latest) in zip(rows,expected):
        if (r["statuses"]!={"94":v94,"105":v105}
            or r["possible_latest_versions"]!=latest
            or r["exact_known_at_utc"] is not None):
            raise ValueError("conditional temporal movement wrong")
    return rows

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--evidence-dir",required=True)
    a=p.parse_args()
    root=Path(a.evidence_dir)
    source=json.loads((root/"world-nih-p2-historical-posted-day-cross-witness.json").read_text())
    records=verify_grid(source)
    report={"schema":SCHEMA,"query_records":records,"query_days":list(CUTOFFS),
        "independent_complete_event_histories_compared":True,
        "underlying_posted_day_is_source_owner_report":True,
        "historic_posting_UTC_instants_authenticated":False,
        "first_public_transaction_authenticated":False,
        "model_is_conditional_on_owner_day_claim":True,
        "absence_of_intervening_versions_proven":False,
        "native_jobs_added":0,"official_NIH_submission":False}
    (root/"world-nih-p2-day-level-temporal-query.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"schema":SCHEMA,
        "days":list(CUTOFFS),
        "latest_version_candidates":[r["possible_latest_versions"] for r in records],
        "exact_instant_authenticated":False,"independent_oracle_passed":True}))
