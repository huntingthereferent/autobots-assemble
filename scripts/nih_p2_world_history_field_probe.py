"""WORLD NIH-P2: inspect two original *historical version* Study Details fields.

Use only public official Record History pages in real Chromium, not undocumented
internal JSON. Fail closed if a version's field cannot be isolated from the
record history index and the current-status header. Do not borrow submitted
date as public posting time, or change source-owned twelve-job W13 evidence.
"""
from __future__ import annotations
from datetime import datetime,timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit,parse_qs

SCHEMA="world-nih-p2-original-version-field-probe/v1"
NCT="NCT00001756"
VERSIONS=(94,105)
HOST="clinicaltrials.gov"
MAX_TEXT=1_200_000
STATUS=re.compile(r"(?i)\b(?:overall status|recruitment status)\b\s*[:\n\t ]{1,40}\s*(RECRUITING|NOT YET RECRUITING|ACTIVE, NOT RECRUITING|COMPLETED|TERMINATED|WITHDRAWN|SUSPENDED|ENROLLING BY INVITATION|UNKNOWN STATUS)\b")

def exact_url(v):
    if type(v) is not int or v not in VERSIONS:raise ValueError("not one of two original recorded source versions")
    return f"https://{HOST}/study/{NCT}?a={v}&tab=history"

def candidate(*,url,status,body,version,page_title,observed):
    if type(body) is not str or len(body)>MAX_TEXT:raise ValueError("unbounded webpage response")
    p=urlsplit(url)
    route=(p.scheme=="https" and p.hostname==HOST and
           p.path==f"/study/{NCT}" and parse_qs(p.query)=={"a":[str(version)],"tab":["history"]}
           and not p.username and not p.password and p.fragment=="" and p.port is None)
    match=re.search(rf"(?<!\w)Viewing\s+V{version}(?!\w)",body)
    details=body[match.end():] if match is not None else ""
    index=details.find("Study Details")
    details=details[index+len("Study Details"):] if index>=0 else ""
    # Match ONLY within the version-specific details after the selected banner.
    # Do not silently fall back to the page's current record summary.
    found=list(STATUS.finditer(details))
    values=[m.group(1).upper() for m in found]
    unique=sorted(set(values))
    trustworthy=(route and status==200 and match is not None and
        NCT in body and "Study of Mast Cell Precursors" in body and
        "Study Record Versions" in body and index>=0 and
        not any(x in body.lower() for x in ("are you a robot","access denied","verify you are human")))
    return {"version":version,"url":exact_url(version),"http_status":status,
        "effective_url_exact":route,"page_title_sha256":sha256(page_title.encode()).hexdigest(),
        "observed_at_utc":observed,
        "version_banner_confirmed":match is not None,
        "study_details_after_version_banner":index>=0,
        "version_page_independently_visible":bool(trustworthy),
        "recruitment_field_candidates_in_details":len(found),
        "distinct_field_candidate_values":unique,
        "version_detail_status_authenticated":bool(trustworthy and len(found)==1 and len(unique)==1),
        "version_detail_status":unique[0] if trustworthy and len(found)==1 else None,
        "original_source_body_sha256":sha256(body.encode()).hexdigest(),
        "version_submission_date_is_public_posting_date":False,
        "per_version_original_posting_date_authenticated":False,
        "source_content_publication_time_instant_authenticated":False,
        "historical_clinical_outcome_evaluated":False}

def verify_receipt(rows):
    if type(rows) is not list or len(rows)!=2 or [r.get("version") for r in rows]!=list(VERSIONS):
        raise ValueError("need two bounded real original registry version probes")
    for v,r in zip(VERSIONS,rows):
        if r.get("url")!=exact_url(v) or r.get("per_version_original_posting_date_authenticated") is not False:
            raise ValueError("false historical time or version identity")
        if r.get("version_detail_status_authenticated") is True and (
            r.get("version_page_independently_visible") is not True or
            r.get("recruitment_field_candidates_in_details")!=1 or
            r.get("version_detail_status") not in
                {"RECRUITING","NOT YET RECRUITING","ACTIVE, NOT RECRUITING","COMPLETED",
                 "TERMINATED","WITHDRAWN","SUSPENDED","ENROLLING BY INVITATION","UNKNOWN STATUS"}
        ):
            raise ValueError("current-record or index status falsely certified historical")
    return {"schema":SCHEMA,"nct_id":NCT,"version_records":rows,
       "historical_versions_visible":sum(r.get("version_page_independently_visible") is True for r in rows),
       "independent_historical_version_status_count":sum(r.get("version_detail_status_authenticated") is True for r in rows),
       "verified_version_statuses":[{
           "version":r["version"],"field":"recruitment_status","value":r["version_detail_status"],
           "evidence_page_text_sha256":r["original_source_body_sha256"]}
           for r in rows if r.get("version_detail_status_authenticated") is True],
       "per_version_first_public_posting_instants_authenticated":False,
       "clinical_verdict":"NOT_EVALUATED","synthetic_W13_game_modified":False,
       "original_native_twelve_jobs_modified":False,"official_NIH_submission":False}

def run(output):
    from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout
    rows=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1250,"height":900})
            for v in VERSIONS:
                url=exact_url(v)
                rec=None
                try:
                    rsp=page.goto(url,wait_until="domcontentloaded",timeout=25000)
                    status=rsp.status if rsp else None
                    try:
                        page.wait_for_function(
                           "(v)=>document.body?.innerText?.includes('Viewing V'+v)",
                           arg=v,timeout=17000)
                    except PlaywrightTimeout:pass
                    body=page.locator("body").inner_text(timeout=15000)
                    title=page.title() or ""
                    if len(body)>MAX_TEXT:raise ValueError("page text exceeds bounded scope")
                    rec=candidate(url=page.url,status=status,body=body,version=v,
                       page_title=title,observed=datetime.now(timezone.utc).isoformat())
                    # Record a bounded layout diagnosis, not the full historical page.
                    idx=body.find(f"Viewing V{v}")
                    tail=body[idx:] if idx>=0 else ""
                    rec["post_banner_detail_preview"]=tail[:900]
                    rec["diagnostic_status_labels_below_banner"]=[
                        x for x in ("Recruitment Status","Overall Status","Study Details")
                        if x in tail]
                except (PlaywrightTimeout,ValueError) as e:
                    rec={"version":v,"url":url,"result":"UNAVAILABLE",
                        "exception_type":type(e).__name__,"observed_at_utc":datetime.now(timezone.utc).isoformat(),
                        "version_page_independently_visible":False,
                        "version_detail_status_authenticated":False,
                        "per_version_original_posting_date_authenticated":False}
                rows.append(rec)
        finally:browser.close()
    report=verify_receipt(rows)
    dest=Path(output);dest.mkdir(parents=True,exist_ok=True)
    (dest/"world-nih-p2-original-history-field-probe.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"schema":SCHEMA,
        "original_version_views":report["historical_versions_visible"],
        "historical_version_status_fields":report["independent_historical_version_status_count"],
        "status_values":report["verified_version_statuses"],
        "real_per_version_public_posting_time_verified":False},sort_keys=True))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output-dir",required=True)
    a=p.parse_args();run(a.output_dir)
