"""SPORTS multi-source collection probe. Stdlib only; never fabricates observations."""
import datetime as dt
import json
import urllib.request
import urllib.error
from pathlib import Path

SOURCES = {
    "nflverse_release": "https://api.github.com/repos/nflverse/nflverse-data/releases",
    "espn_scoreboard": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=20261025",
    "nfl_schedule": "https://www.nfl.com/schedules/2026/reg8/",
}
OUT = Path("research/sports/observations")
OUT.mkdir(parents=True, exist_ok=True)

def probe(name, url):
    at = dt.datetime.now(dt.timezone.utc).isoformat()
    request = urllib.request.Request(url, headers={"User-Agent": "TraceworkSportsProbe/0.1", "Accept": "application/json, text/html"})
    record = {"provider": name, "source_url": url, "retrieved_at": at, "status": "error"}
    try:
        with urllib.request.urlopen(request, timeout=18) as response:
            body = response.read(4_000_000)
            record.update(status="retrieved", http_status=response.status, bytes=len(body), content_type=response.headers.get("Content-Type"), truncated=len(body)==4_000_000)
            (OUT / f"{name}.raw").write_bytes(body)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        record["error"] = str(exc)
    return record

if __name__ == "__main__":
    results = [probe(name, url) for name, url in SOURCES.items()]
    (OUT / "retrieval_receipt.json").write_text(json.dumps({"sources": results}, indent=2)+"\n")
    print(json.dumps(results, indent=2))
