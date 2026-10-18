"""Bounded source-owner inspection of CTTI AACT's 2022 snapshot catalog.

This checks the ORIGINAL CTTI public download catalog, not a constructed
Zenodo source, and MUST NOT infer archive URLs from a date or try to bypass
the site's session/access requirements. Neither an archive nor study row is
fetched. An inaccessible or dynamic catalog is a valid negative inspection
receipt, NEVER proof that a dated source snapshot was downloaded.

No W13 twelve-job journal/workstation or licensed source is modified.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

SCHEMA = "nih-p2-ctti-primary-2022-catalog-access/v1"
OWNER = "Clinical Trials Transformation Initiative (CTTI)"
OWNER_HOST = "aact.ctti-clinicaltrials.org"
CATALOG_URLS = (
    "https://aact.ctti-clinicaltrials.org/downloads/snapshots?type=flatfiles&year=2022",
    "https://aact.ctti-clinicaltrials.org/snapshots",
)
MAX_RESPONSE_BYTES = 2_000_000
MAX_ARCHIVE_BYTES_FOR_FUTURE_SOURCE_TEST = 4_000_000_000
NAME = re.compile(r"^2022[01][0-9][0-3][0-9]_(?:export|clinical_trials)[\w-]*\.zip$",re.I)
SENSITIVE = re.compile(r"(?i)(?:access_token|auth|sig|signature|credential|key|session)=")


class CatalogLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs=[]
        self.text=[]
        self.title=""
        self._in_title=False

    def handle_starttag(self,tag,attrs):
        if tag=="a":
            href=dict(attrs).get("href")
            if href is not None:
                self.hrefs.append(href)
        if tag=="title":
            self._in_title=True

    def handle_endtag(self,tag):
        if tag=="title":
            self._in_title=False

    def handle_data(self,data):
        self.text.append(data)
        if self._in_title:
            self.title+=data


def catalog_candidates(html, *,base_url):
    """Only accept genuine server-returned links on the CTTI owner host."""
    if type(html) is not str or len(html.encode("utf8")) > MAX_RESPONSE_BYTES:
        raise ValueError("catalog page absent or exceeds inspection bound")
    parser=CatalogLinks()
    parser.feed(html)
    discovered=[]
    for href in parser.hrefs:
        if not isinstance(href,str) or SENSITIVE.search(href):
            continue
        url=urljoin(base_url,href)
        p=urlsplit(url)
        name=Path(p.path).name
        if (p.scheme!="https" or p.hostname!=OWNER_HOST or p.username or p.password or
                not NAME.fullmatch(name) or p.fragment or p.query):
            continue
        discovered.append({"owner_catalog_link":url,"archive_filename":name})
    links={row["owner_catalog_link"]:row for row in discovered}
    page_text=" ".join(" ".join(parser.text).casefold().split())
    return {
        "source_page_title":parser.title.strip()[:180],
        "login_or_access_banner_seen":any(
            text in page_text for text in ("sign in","log in","create account","access the aact cloud database")),
        "candidate_archive_links":sorted(links.values(),key=lambda x:x["archive_filename"]),
        "page_mentions_2022":bool(re.search(r"\b2022\b",page_text)),
    }


def _open_bounded(url, *, opener=urlopen,method="GET"):
    p=urlsplit(url)
    if p.scheme!="https" or p.hostname!=OWNER_HOST:
        raise ValueError("cross-origin CTTI source not permitted")
    if method not in ("GET","HEAD"):
        raise ValueError("unsupported inspection method")
    req=Request(url,headers={
        "User-Agent":"A-B-original-CTTI-source-inspection/1.0",
        "Accept":"text/html,application/xhtml+xml" if method=="GET" else "*/*",
    },method=method)
    try:
        with opener(req,timeout=20) as response:
            status=response.status
            effective=response.geturl()
            headers=response.headers
            data=b""
            if method=="GET":
                data=response.read(MAX_RESPONSE_BYTES+1)
            if len(data)>MAX_RESPONSE_BYTES:
                raise ValueError("owner catalog response larger than bounded inspection")
            # We preserve the host, not query strings or redirect credentials.
            effective_host=urlsplit(effective).hostname
            if effective_host!=OWNER_HOST and method=="GET":
                # A redirect to a login provider does not establish a public snapshot.
                return {"status":status,"effective_host":effective_host,
                        "redirected_cross_origin":True,"body":""}
            return {"status":status,"effective_host":effective_host,
                    "redirected_cross_origin":effective_host!=OWNER_HOST,
                    "content_type":headers.get("Content-Type",""),
                    "content_length_header":headers.get("Content-Length"),
                    "last_modified_header":headers.get("Last-Modified"),
                    "etag_present":bool(headers.get("ETag")),
                    "body":data.decode("utf-8","replace") if method=="GET" else ""}
    except HTTPError as error:
        return {"status":error.code,"effective_host":OWNER_HOST,"error":"HTTP_ACCESS_OR_MISSING"}
    except (URLError,TimeoutError) as error:
        return {"status":None,"effective_host":OWNER_HOST,
                "error":"NETWORK_OR_ACCESS_UNAVAILABLE",
                "exception_type":type(error).__name__}


def inspect(*,opener=urlopen, checked_at=None):
    rows=[]
    all_candidates={}
    for url in CATALOG_URLS:
        received=_open_bounded(url,opener=opener)
        status=received.get("status")
        entry={"source_catalog_url":url,"http_status":status,
               "effective_host":received.get("effective_host"),
               "error":received.get("error"),
               "redirected_cross_origin":received.get("redirected_cross_origin",False),
               "matched_2022_archive_links":[]}
        if (status==200 and
                not received.get("redirected_cross_origin") and
                "html" in received.get("content_type","").lower()):
            parsed=catalog_candidates(received["body"],base_url=url)
            entry.update({k:v for k,v in parsed.items() if k!="candidate_archive_links"})
            entry["matched_2022_archive_links"]=parsed["candidate_archive_links"]
            for candidate in parsed["candidate_archive_links"]:
                all_candidates[candidate["owner_catalog_link"]]=candidate
        rows.append(entry)
    # No blind GET/HEAD against fabricated date-formatted filenames. Even HEAD
    # is reserved for an archive URL actually returned by the owner catalog.
    return {
        "schema":SCHEMA,"source_owner":OWNER,"source_owner_host":OWNER_HOST,
        "checked_at_utc":checked_at or datetime.now(timezone.utc).isoformat(),
        "unauthenticated_public_catalog_checks":rows,
        "candidate_archive_links_from_actual_owner_html":
            sorted(all_candidates.values(),key=lambda x:x["archive_filename"]),
        "public_2022_archive_url_discovered":bool(all_candidates),
        "archive_bytes_downloaded":0,
        "archive_whole_file_sha256_verified":False,
        "source_2022_record_contents_witnessed":False,
        "historical_primary_record_version_content_witnessed":False,
        "original_registry_per_version_public_posting_time_witnessed":False,
        "catalog_access_or_linkage_unresolved":not bool(all_candidates),
        "not_attempted_to_bypass_authentication":True,
        "third_party_bulk_data_copied_to_A_B":False,
        "original_twelve_job_workstation_modified":False,
        "NIH_submission":False,
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    a=parser.parse_args(argv)
    result=inspect()
    a.output_dir.mkdir(parents=True,exist_ok=True)
    (a.output_dir/"nih-p2-ctti-owner-catalog-2022.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({
        "schema":SCHEMA,"catalog_url_found":result["public_2022_archive_url_discovered"],
        "matching_2022_owner_links":len(result["candidate_archive_links_from_actual_owner_html"]),
        "catalog_checks":[{"status":x["http_status"],"error":x["error"]}
                          for x in result["unauthenticated_public_catalog_checks"]],
        "original_archive_downloaded":False,
        "historical_version_timestamp_witnessed":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
