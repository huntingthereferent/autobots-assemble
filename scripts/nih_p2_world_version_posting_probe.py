"""WORLD P2: test whether an original selected version exposes its OWN posted date.

Inspect ONLY two official ClinicalTrials.gov public Record History views in
fresh Chromium. Explicitly distinguish the current study header's Last Update
Posted and version history's Date submitted from dates *inside selected version
Study Details*. No historical posting instant is admitted without a version-
bound, owner-defined posted-date field and independent temporal verification.
"""
from __future__ import annotations
from datetime import date,datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import urlsplit,parse_qs
from scripts.nih_p2_world_history_field_probe import NCT,VERSIONS,exact_url,candidate

SCHEMA="world-nih-p2-original-version-posting-field-access/v1"
LABELS=("First Submitted","First Submitted that Met QC Criteria","First Posted",
        "Last Update Submitted","Last Update Posted","Study Record Dates",
        "Date submitted","Date posted","Posted","Record History")
DAY=re.compile(r"\d{4}-\d{2}-\d{2}")
SUBMITTED={94:"2019-08-01",105:"2019-11-22"}

def selected_version_dates(*,version,url,status,title,body,observed):
    field=candidate(url=url,status=status,body=body,version=version,
                    page_title=title,observed=observed)
    # Explicit original selected-view provenance required before dates inspected.
    if not field["version_page_independently_visible"]:
        return {"version":version,"url":exact_url(version),"result":"VERSION_UNAVAILABLE",
                "original_version_visible":False,"posted_at_authenticated":False,
                "submission_date_is_posted_at":False}
    if not title.startswith(f"Record History | ver. {version}: {SUBMITTED[version]} | {NCT} |"):
        raise ValueError("owner page title does not bind the submitted day to selected version")
    match=re.search(rf"(?<!\w)Viewing\s+V{version}\s*\(\s*{SUBMITTED[version]}\s*\)",body)
    if match is None:raise ValueError("selected viewer banner does not bind original submitted date")
    before,selected=body[:match.start()],body[match.end():]
    if not re.search(r"(?m)^\s*Study Details\s*$",selected):
        raise ValueError("version-specific details section absent")
    rows=[]
    for scope,text in (("current_header_or_history_index",before),
                       ("selected_historical_version_detail",selected)):
        lines=[v.strip() for v in text.splitlines()]
        for i,line in enumerate(lines):
            if line in LABELS:
                # No surrounding subject/patient descriptions. Values are dates only.
                nearby=lines[i+1:i+4]
                dates=[]
                for s in nearby:
                    for value in DAY.findall(s):
                        try: date.fromisoformat(value)
                        except ValueError:continue
                        dates.append(value)
                rows.append({"scope":scope,"label":line,"following_iso_dates":dates[:2]})
    # The current header must NEVER be relabelled as the date of selected V94/V105.
    current=[r for r in rows if r["scope"]=="current_header_or_history_index"
             and r["label"]=="Last Update Posted"]
    specific=[r for r in rows if r["scope"]=="selected_historical_version_detail"
              and r["label"] in ("Last Update Posted","Date posted")]
    # Even a selected-version date requires independent original publication
    # evidence before the research may assert its first-public-access instant.
    return {
        "version":version,"url":exact_url(version),
        "result":"VERSION_EXACT_DETAIL_TIMING_INSPECTED",
        "original_version_visible":True,
        "submission_date_owner_recorded":SUBMITTED[version],
        "observed_at_utc":observed,
        "owner_browser_visible_body_sha256":sha256(body.encode()).hexdigest(),
        "source_page_title_sha256":sha256(title.encode()).hexdigest(),
        "current_or_history_header_last_update_posted_label_count":len(current),
        "selected_version_detail_posting_field_label_count":len(specific),
        "selected_version_detail_posting_field_dates":[
            {"label":v["label"],"following_iso_dates":v["following_iso_dates"]} for v in specific],
        "selected_detail_date_labels":[
            v["label"] for v in rows if v["scope"]=="selected_historical_version_detail"],
        "current_header_last_update_posted_cannot_establish_version_posting":True,
        "version_submitted_at_is_not_version_posted_at":True,
        "posted_at_authenticated":False,
        "exact_first_publication_instant_authenticated":False,
        "clinical_verdict":"NOT_EVALUATED",
    }

def verify_pair(items):
    if type(items) is not list or len(items)!=2 or [v.get("version") for v in items]!=list(VERSIONS):
        raise ValueError("exact two official versions required")
    if any(v.get("url")!=exact_url(v["version"]) for v in items):
        raise ValueError("version identity substituted")
    for v in items:
        if (v.get("posted_at_authenticated") is not False or
            v.get("original_version_visible") is not True or
            v.get("result")!="VERSION_EXACT_DETAIL_TIMING_INSPECTED" or
            v.get("current_header_last_update_posted_cannot_establish_version_posting") is not True or
            v.get("version_submitted_at_is_not_version_posted_at") is not True or
            v.get("submission_date_owner_recorded")!=SUBMITTED[v["version"]]):
            raise ValueError("unsupported original-version post timestamp promoted")
    return {"schema":SCHEMA,"study":NCT,"original_selected_version_count":2,
        "records":items,"original_per_version_first_posted_instants_authenticated":False,
        "publication_date_oracle_available":False,"admissible_temporal_known_at":None,
        "history_query_without_posted_at":"BLOCKED_PENDING_OWNER_POSTING_EVIDENCE",
        "new_native_jobs":0,"original_12_job_source_unchanged":True,
        "official_NIH_submission":False,"clinical_verdict":"NOT_EVALUATED"}

def run(out):
    from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    records=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1220,"height":900})
            for v in VERSIONS:
                url=exact_url(v)
                try:
                    response=page.goto(url,wait_until="domcontentloaded",timeout=25000)
                    if response is None or response.status!=200:
                        raise ValueError("official historical version page unavailable")
                    page.wait_for_function(
                        "(a)=>document.body?.innerText?.includes('Viewing V'+a.v+' ('+a.submitted+')')",
                        arg={"v":v,"submitted":SUBMITTED[v]},timeout=18000)
                    body=page.locator("body").inner_text(timeout=15000)
                    record=selected_version_dates(version=v,url=page.url,
                        status=response.status,title=page.title() or "",body=body,
                        observed=datetime.now(timezone.utc).isoformat())
                except (PlaywrightTimeout,ValueError) as error:
                    record={"version":v,"url":url,"result":"VERSION_UNAVAILABLE",
                      "error_type":type(error).__name__,
                      "original_version_visible":False,"posted_at_authenticated":False,
                      "submission_date_is_posted_at":False}
                records.append(record)
        finally:browser.close()
    result={"schema":SCHEMA,"study":NCT,"records":records,
            "source_checked_at_utc":datetime.now(timezone.utc).isoformat(),
            "original_per_version_first_posted_instants_authenticated":False,
            "official_NIH_submission":False}
    if all(r["result"]=="VERSION_EXACT_DETAIL_TIMING_INSPECTED" for r in records):
        result=verify_pair(records)
        result["source_checked_at_utc"]=datetime.now(timezone.utc).isoformat()
    else:
        result["history_query_without_posted_at"]="BLOCKED_SOURCE_UNAVAILABLE"
        result["original_selected_version_count"]=sum(
            r.get("original_version_visible") is True for r in records)
        result["publication_date_oracle_available"]=False
        result["admissible_temporal_known_at"]=None
        result["new_native_jobs"]=0
    (out/"world-nih-p2-official-version-posting-probe.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"schema":SCHEMA,"actual_version_views":result["original_selected_version_count"],
        "field_counts":[r.get("selected_version_detail_posting_field_label_count",0) for r in records],
        "selected_dates":[r.get("selected_version_detail_posting_field_dates",[]) for r in records],
        "headings":[r.get("selected_detail_date_labels",[]) for r in records],
        "per_version_posted_at_verified":False,"temporal_claim":result["history_query_without_posted_at"]},
        sort_keys=True))
    # Inaccessibility is recorded as a result, not an invented date or success.
    return result

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    args=parser.parse_args()
    run(args.output_dir)
