"""Observe two ORIGINAL public ClinicalTrials.gov historical-version UI routes.

Unlike the blocked, undocumented history API in draft PR #107, this reads
only the official publicly intended Record History pages using Chromium.
It is a SOURCE ACCESS test, not proof of field-level historical contents
or individual publication dates. A current study badge, a search snippet,
an index's submit date, or a URL's a= parameter alone NEVER authenticates
the version's content.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit

SCHEMA="nih-p2-clinicaltrials-official-history-browser-access/v1"
HOST="clinicaltrials.gov"
NCT="NCT00001756"
TITLE="Study of Mast Cell Precursors"
VERSIONS=(94,105)
MAX_BODY=1_200_000
MARKERS=("Record History","Study Record Versions","Study Details","Viewing V")
INACCESSIBLE=("access denied","forbidden","are you a robot","verify you are human",
              "enable javascript to continue","just a moment")


def version_url(version):
    if type(version) is not int or version not in VERSIONS:
        raise ValueError("requested version outside exact frozen source inspection")
    return f"https://{HOST}/study/{NCT}?a={version}&tab=history"


def validate_observed_page(*, requested_version, requested_url, effective_url,
                           body_text, title, status, retrieved_utc):
    if version_url(requested_version)!=requested_url:
        raise ValueError("selected original version URL unexpectedly changed")
    original=urlsplit(effective_url)
    if original.scheme!="https" or original.hostname!=HOST:
        return {
            "requested_version":requested_version,
            "requested_url":requested_url,
            "status":status,
            "retrieved_utc":retrieved_utc,
            "result":"CROSS_ORIGIN_REDIRECT",
            "actual_original_version_rendered":False,
            "historic_status_field_authenticated":False,
            "public_version_post_date_authenticated":False,
        }
    if type(body_text) is not str or len(body_text)>MAX_BODY:
        raise ValueError("invalid or excessive site text; cannot identify exact historical content")
    if type(status) not in (int,type(None)):
        raise ValueError("unexpected source status type")
    text=" ".join(body_text.split())
    marker=f"Viewing V{requested_version}"
    # A substring such as "Viewing V940" must not count as V94.
    # The index lists versions, but only the exact selected route and banner
    # can establish that this original version was presented in Chromium.
    marker_found=re.search(rf"(?<![A-Za-z0-9])Viewing\s+V{requested_version}(?![A-Za-z0-9])",text) is not None
    qs=parse_qs(original.query,keep_blank_values=True)
    exact_route=(original.path==f"/study/{NCT}" and
                 qs=={"a":[str(requested_version)],"tab":["history"]} and
                 not original.fragment and not original.username and
                 not original.password and original.port is None)
    render=(marker_found and exact_route and NCT in text and TITLE in text and
            "Study Record Versions" in text and
            "Study Details" in text and
            status==200 and
            not any(k in text.casefold() for k in INACCESSIBLE))
    return {
        "requested_version":requested_version,
        "requested_url":requested_url,
        "observed_effective_host":original.hostname,
        "observed_query_selected_version":qs.get("a",[None])[0],
        "selected_exact_original_route":exact_route,
        "status":status,
        "retrieved_utc":retrieved_utc,
        "observed_page_title":title[:180],
        "visible_study_identifier":NCT in text,
        "record_history_list_visible":"Study Record Versions" in text,
        "study_detail_heading_visible":"Study Details" in text,
        "selected_version_view_banner_visible":marker_found,
        "explicit_rendered_version_banner":marker if render else None,
        "visible_source_text_sha256":hashlib.sha256(body_text.encode("utf-8")).hexdigest(),
        "result":"EXPLICIT_ORIGINAL_VERSION_VIEW" if render else "VERSION_VIEW_NOT_INDEPENDENTLY_RENDERED",
        "actual_original_version_rendered":render,
        "historic_status_field_authenticated":False,
        "public_version_post_date_authenticated":False,
        "submission_date_is_public_posting_date":False,
        "source_access_scope":"official_public_record_history_browser",
    }


def summarize(version_records):
    if type(version_records) is not list or len(version_records)!=len(VERSIONS):
        raise ValueError("incomplete original two-version UI experiment")
    if [r["requested_version"] for r in version_records]!=list(VERSIONS):
        raise ValueError("missing, duplicated or misordered original version trials")
    if any(r.get("historic_status_field_authenticated") is not False or
           r.get("public_version_post_date_authenticated") is not False for r in version_records):
        raise ValueError("source access cannot be promoted to version-content/publication proof")
    for r in version_records:
        if r.get("actual_original_version_rendered") is True and (
            r.get("result")!="EXPLICIT_ORIGINAL_VERSION_VIEW" or
            r.get("selected_exact_original_route") is not True or
            r.get("selected_version_view_banner_visible") is not True
        ):
            raise ValueError("contradictory original historical-version view witness")
    return {
        "schema":SCHEMA,
        "original_source_owner":"ClinicalTrials.gov / U.S. National Library of Medicine",
        "official_site_host":HOST,
        "target_public_study":NCT,
        "version_route_probe_records":version_records,
        "actual_version_view_count":sum(r["actual_original_version_rendered"] is True
                                        for r in version_records),
        "both_original_version_views_witnessed":all(r["actual_original_version_rendered"] is True
                                                   for r in version_records),
        "historical_source_fields_verified":False,
        "per_version_public_posting_date_verified":False,
        "blocked_undocumented_api_reused":False,
        "external_derived_noncommercial_dataset_accessed":False,
        "clinical_verdict":"NOT_EVALUATED",
        "original_twelve_native_jobs_modified":False,
        "official_NIH_submission":False,
    }


def run(*,output_dir):
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

    records=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1100,"height":900})
            for version in VERSIONS:
                url=version_url(version)
                status=None
                try:
                    response=page.goto(url,wait_until="domcontentloaded",timeout=25000)
                    status=response.status if response else None
                    if status==200:
                        try:
                            page.wait_for_function(
                                "(v)=>document.body?.innerText?.includes('Viewing V'+v)",
                                arg=version,timeout=16000)
                        except PlaywrightTimeout:
                            pass
                    body=page.locator("body").inner_text(timeout=12000)
                    if len(body)>MAX_BODY:
                        raise ValueError("official page response exceeds bounded text")
                    actual=validate_observed_page(
                        requested_version=version,requested_url=url,
                        effective_url=page.url,body_text=body,
                        title=page.title() or "",status=status,
                        retrieved_utc=datetime.now(timezone.utc).isoformat())
                except (PlaywrightTimeout, ValueError) as exc:
                    actual={
                        "requested_version":version,"requested_url":url,
                        "result":"PUBLIC_BROWSER_READ_UNAVAILABLE",
                        "exception_type":type(exc).__name__,
                        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
                        "actual_original_version_rendered":False,
                        "historic_status_field_authenticated":False,
                        "public_version_post_date_authenticated":False,
                    }
                records.append(actual)
        finally:
            browser.close()
    result=summarize(records)
    dest=Path(output_dir)
    dest.mkdir(parents=True,exist_ok=True)
    (dest/"nih-p2-original-study-history-browser-access.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    opts=parser.parse_args(argv)
    result=run(output_dir=opts.output_dir)
    print(json.dumps({
        "schema":result["schema"],
        "verified_original_version_banners":result["actual_version_view_count"],
        "individual_status_historical_field_authenticated":False,
        "per_version_public_posting_date_authenticated":False,
        "probe_results":[x["result"] for x in result["version_route_probe_records"]],
    },sort_keys=True))


if __name__=="__main__":
    main()
