"""Fetch a historical GitHub Actions job log with bounded signed redirects.

The authenticated GitHub REST endpoint redirects log downloads to a signed
storage host. Do not forward a GitHub API bearer token to another origin.
Logs are used *in memory only* for verification and are never printed or saved.
"""
from __future__ import annotations

from io import BytesIO
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from zipfile import ZipFile, is_zipfile

MAX_LOG_BYTES=4_000_000
MAX_TEXT_BYTES=4_000_000
SIGNED_HOST_SUFFIXES=("actions.githubusercontent.com","blob.core.windows.net")


class SignedGitHubLogsRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed=urlsplit(newurl)
        host=parsed.hostname or ""
        if (parsed.scheme!="https" or not any(
                host==suffix or host.endswith("."+suffix)
                for suffix in SIGNED_HOST_SUFFIXES)):
            raise ValueError("untrusted GitHub Actions signed log redirect")
        next_req=super().redirect_request(req,fp,code,msg,headers,newurl)
        if next_req is None:
            raise ValueError("GitHub log redirect was not accepted")
        for collection in (next_req.headers, next_req.unredirected_hdrs):
            for key in list(collection):
                if key.lower() in ("authorization","cookie","x-github-api-version"):
                    del collection[key]
        return next_req


def decode_job_log(data: bytes) -> str:
    if type(data) is not bytes or not data or len(data)>MAX_LOG_BYTES:
        raise ValueError("GitHub job log missing or oversized")
    raw=data
    if is_zipfile(BytesIO(data)):
        parts=[]
        total=0
        with ZipFile(BytesIO(data)) as archive:
            entries=[i for i in archive.infolist() if not i.is_dir()]
            if not entries or len(entries)>64:
                raise ValueError("unexpected GitHub job log archive shape")
            for entry in sorted(entries,key=lambda x:x.filename):
                if (not entry.filename.endswith(".txt") or
                        entry.file_size>MAX_TEXT_BYTES or
                        entry.flag_bits & 0x1):
                    raise ValueError("unexpected GitHub job log archive entry")
                total+=entry.file_size
                if total>MAX_TEXT_BYTES:
                    raise ValueError("unbounded job log archive decompression")
                part=archive.read(entry)
                if len(part)!=entry.file_size:
                    raise ValueError("truncated signed log archive entry")
                parts.append(part)
        raw=b"\n".join(parts)
    if len(raw)>MAX_TEXT_BYTES:
        raise ValueError("GitHub job log text exceeds bound")
    return raw.decode("utf-8","strict")


def fetch_signed_job_log(*,repository:str,job_id:int,token:str)->str:
    if repository!="huntingthereferent/autobots-assemble" or job_id!=117699812720:
        raise ValueError("log retrieval must select exact original owner job")
    if not isinstance(token,str) or not token:
        raise ValueError("GitHub authenticated source required")
    url=f"https://api.github.com/repos/{repository}/actions/jobs/{job_id}/logs"
    request=Request(url,headers={
        "Authorization":"Bearer "+token,
        "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28",
        "User-Agent":"w13-original-owner-child-source-observation"})
    with build_opener(SignedGitHubLogsRedirect()).open(request,timeout=30) as response:
        data=response.read(MAX_LOG_BYTES+1)
    return decode_job_log(data)
