"""Public GitHub fork -> upstream PR return observations.

A fork is evidence of a *copy*, not attention, adoption, agreement, or a
person's movement. A later upstream merged PR from that exact fork is evidence
of a code return. Nothing else can silently become a return.

The independent GitHub API is the only source. This does not trace a person.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
REPOS=("huntingthereferent/autobots-assemble", "huntingthereferent/huntingthereferent")
VERSION="public-github-fork-return/v1"
NAME=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA=re.compile(r"^[0-9a-f]{40}$")
MAX_PAGES=3


def stamp(value):
    if type(value) is not str:
        raise ValueError("source timestamp missing")
    try:
        parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError as exc:
        raise ValueError("invalid GitHub UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timezone required")
    return parsed.astimezone(timezone.utc)


def checked_url(url):
    if type(url) is not str or not url.startswith("https://github.com/"):
        raise ValueError("non-GitHub evidence URL")
    return url


def fetch_page(repo, kind, page, token=""):
    if not NAME.fullmatch(repo) or kind not in ("forks","pulls") or not 1 <= page <= MAX_PAGES:
        raise ValueError("unapproved GitHub query")
    query=("sort=newest" if kind=="forks" else "state=all&sort=created&direction=desc")
    url=f"https://api.github.com/repos/{repo}/{kind}?{query}&per_page=100&page={page}"
    headers={"Accept":"application/vnd.github+json","User-Agent":"native-trace-return-witness",
             "X-GitHub-Api-Version":"2022-11-28"}
    if token:
        headers["Authorization"]="Bearer "+token
    request=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(request,timeout=30) as response:
        rows=json.load(response)
    if type(rows) is not list:
        raise ValueError("GitHub list response must be an array")
    return rows


def collect(repo, kind, token="", get=fetch_page):
    rows=[]
    covered=False
    for page in range(1, MAX_PAGES+1):
        batch=get(repo,kind,page,token)
        if type(batch) is not list or len(batch)>100:
            raise ValueError("invalid GitHub pagination response")
        rows.extend(batch)
        if len(batch)<100:
            covered=True
            break
    return rows,("PAGED_TO_END" if covered else "BOUNDED_FIRST_300")


def observe(repo, forks, pulls, *, fork_coverage, pr_coverage):
    """Return only records whose GitHub source identities prove fork membership."""
    if type(repo) is not str or not NAME.fullmatch(repo):
        raise ValueError("invalid root source")
    if type(forks) is not list or type(pulls) is not list:
        raise ValueError("unrecognized GitHub source arrays")
    if fork_coverage not in ("PAGED_TO_END","BOUNDED_FIRST_300") or pr_coverage not in (
            "PAGED_TO_END","BOUNDED_FIRST_300"):
        raise ValueError("unreported source coverage")
    fork_by_id={}
    for fork in forks:
        if type(fork) is not dict or type(fork.get("id")) is not int:
            raise ValueError("fork native id missing")
        ident=fork["id"]
        full=fork.get("full_name")
        if type(full) is not str or not NAME.fullmatch(full) or full==repo:
            raise ValueError("not a distinct public fork identity")
        when=stamp(fork.get("created_at"))
        url=checked_url(fork.get("html_url"))
        if ident in fork_by_id:
            raise ValueError("duplicate fork native identity")
        fork_by_id[ident]={"fork":full, "fork_id":ident,
                          "fork_created_at":when.isoformat().replace("+00:00","Z"),
                          "fork_url":url, "status":"OPEN",
                          "return_pr":None,"returned_at":None,
                          "elapsed_seconds":None,"merge_sha":None}
    # Recheck incoming PRs by exact fork ID and head/base repository names.
    # PR origin outside this bounded fork listing stays unknown, not connected.
    for pr in pulls:
        if type(pr) is not dict:
            raise ValueError("not a GitHub PR object")
        head=pr.get("head")
        base=pr.get("base")
        if not isinstance(head,dict) or not isinstance(base,dict):
            continue
        head_repo=head.get("repo")
        base_repo=base.get("repo")
        if not isinstance(head_repo,dict) or not isinstance(base_repo,dict):
            continue
        if base_repo.get("full_name")!=repo:
            continue
        ident=head_repo.get("id")
        record=fork_by_id.get(ident) if type(ident) is int else None
        if record is None or head_repo.get("full_name")!=record["fork"]:
            continue
        # A repository may be someone's fork, but an unmerged proposal does
        # not return the code to the original repository.
        merged=pr.get("merged_at")
        sha=pr.get("merge_commit_sha")
        if merged is None or type(sha) is not str or not SHA.fullmatch(sha):
            continue
        when=stamp(merged)
        began=stamp(record["fork_created_at"])
        if when<began:
            raise ValueError("merge predates purported fork")
        number=pr.get("number")
        if type(number) is not int or number<1:
            raise ValueError("missing original PR identity")
        checked_url(pr.get("html_url"))
        if record["returned_at"] is None or when<stamp(record["returned_at"]):
            record.update({
                "status":"RETURN_OBSERVED",
                "return_pr":{"number":number,"url":pr["html_url"]},
                "returned_at":when.isoformat().replace("+00:00","Z"),
                "elapsed_seconds":int((when-began).total_seconds()),
                "merge_sha":sha})
    observations=sorted(fork_by_id.values(),key=lambda x:(x["fork_created_at"],x["fork_id"]))
    returned=sum(x["status"]=="RETURN_OBSERVED" for x in observations)
    return {
        "repository":repo,
        "fork_coverage":fork_coverage,
        "pr_coverage":pr_coverage,
        "forks_observed":len(observations),
        "returns_observed":returned,
        "still_open":len(observations)-returned,
        "observations":observations,
        "meaning":"Fork = public repository copy; return = exact fork-head PR merged upstream.",
        "boundary":"No inference about a person's choices, usage, adoption or any return not proven by GitHub provenance."
    }


def build_snapshot(*, checked_at, inputs):
    stamp(checked_at)
    if type(inputs) is not dict or set(inputs)!=set(REPOS):
        raise ValueError("missing one of the two original repository sources")
    results=[]
    for repo in REPOS:
        data=inputs[repo]
        if type(data) is not dict or set(data)!={"forks","pulls","fork_coverage","pr_coverage"}:
            raise ValueError("source input incomplete")
        results.append(observe(repo,data["forks"],data["pulls"],
                               fork_coverage=data["fork_coverage"],pr_coverage=data["pr_coverage"]))
    return {
        "schema":VERSION,
        "checked_at":checked_at,
        "repositories":results,
        "interpretation":"Observable repository copies and exact upstream PR merges, not any human's physical or personal movement.",
        "latency_definition":"Seconds from GitHub fork.created_at to first witnessed upstream PR.merged_at; an open fork has null elapsed_seconds.",
        "coverage":"Bounded public API sampling. Zero observed does not prove zero existence or future returns."
    }


def markdown(snapshot):
    if snapshot.get("schema")!=VERSION:
        raise ValueError("unknown observation version")
    s=["# External movement and return — GitHub witness",
       "",f"Checked: **{snapshot['checked_at']}**",
       "",
       "A public fork is an observable **copy**, not a person leaving, using or endorsing the work.",
       "A *return* is only counted when GitHub verifies a pull request from **that same fork** was merged into its source repository.",
       "The timer measures the fork's creation until that merge, not when someone first saw the project.",
       "",
       "| Original source | Public forks sampled | Returned by native PR merge | Open | Coverage |",
       "| --- | ---: | ---: | ---: | --- |"]
    for row in snapshot["repositories"]:
        name=row["repository"]
        s.append(f"| [{name}](https://github.com/{name}) | {row['forks_observed']} | {row['returns_observed']} | {row['still_open']} | {row['fork_coverage']} / {row['pr_coverage']} |")
    s.extend(["","## Verified returns",""])
    returns=[(r,x) for r in snapshot["repositories"] for x in r["observations"] if x["status"]=="RETURN_OBSERVED"]
    if not returns:
        s.append("**None observed in the current bounded public GitHub sources.** This is an observation, not a prediction.")
    for repo,x in returns:
        minutes=x["elapsed_seconds"]/60
        s.append(f"- [{x['fork']}]({x['fork_url']}) forked **{repo['repository']}** at {x['fork_created_at']}; "
                 f"[PR #{x['return_pr']['number']}]({x['return_pr']['url']}) merged "
                 f"{x['returned_at']} (**{minutes:.1f} minutes** after fork creation).")
    s.extend(["","## Limits","",
              "Open forks have **no return interval**, not a return interval of zero. "
              "If the public API pages are bounded, the report is only a sample.",
              "Changes developed without GitHub forks, deleted forks, private repos, offline work, "
              "mentions without source-linked commits, and independent reuse may be invisible.",
              "Internal branches and PRs by the repository owner are **not** external departures.",
              "This test does not observe anything about James's personal decisions or health.",
              "",
              "[Original machine-readable observations](return-latest.json) · "
              "[Native collector and verifier](fork_return.py)",
              ""])
    return "\n".join(s)


def refresh(token=""):
    inputs={}
    for repo in REPOS:
        forks,fc=collect(repo,"forks",token)
        pulls,pc=collect(repo,"pulls",token)
        inputs[repo]={"forks":forks,"pulls":pulls,"fork_coverage":fc,"pr_coverage":pc}
    checked=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    return build_snapshot(checked_at=checked,inputs=inputs)


def main():
    parser=argparse.ArgumentParser(description="Native GitHub fork and merged-return tracer")
    parser.add_argument("--refresh",action="store_true",help="Read GitHub public API; never infer unseen events")
    args=parser.parse_args()
    if not args.refresh:
        raise SystemExit("Pass --refresh to obtain new observations; no fixtures published")
    result=refresh(os.environ.get("GITHUB_TOKEN",""))
    folder=ROOT/"views/traces"
    (folder/"return-latest.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (folder/"RETURN_LATEST.md").write_text(markdown(result),encoding="utf-8")
    print(json.dumps({"checked_at":result["checked_at"],"counts":[{
        k:v for k,v in x.items() if k in ("repository","forks_observed","returns_observed","still_open")}
        for x in result["repositories"]]}))


if __name__=="__main__":
    main()
