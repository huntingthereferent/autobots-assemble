"""Read-only GitHub view over the existing public-data-monitor source adapters."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import html
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "work" / "projects" / "public-data-monitor"))
from app.adapters import LiveJsonAdapter
from app.github_source import fetch_repository
from app.identity import link_github_repo_to_package
from app.platform import SourceObservation, classify_change
from app.pypi_source import fetch_project
from app.usgs import USGS_ALL_HOUR

DIR = Path(__file__).resolve().parent
SCHEMA = "public-world-continuity/v1"


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def compose(quakes: list[SourceObservation], github: SourceObservation,
            pypi: SourceObservation, checked_at: datetime,
            previous: dict | None = None) -> dict:
    """Retain each source's native identity and verify no cross-domain join is fabricated."""
    if github.source != "github_api" or github.entity_type != "repository":
        raise ValueError("expected native GitHub repository observation")
    if pypi.source != "pypi_api" or pypi.entity_type != "package":
        raise ValueError("expected native PyPI package observation")
    if any(q.source != "live_json_api" for q in quakes):
        raise ValueError("expected native USGS observations")
    if checked_at.tzinfo is None:
        raise ValueError("observation time requires a timezone")
    if previous is not None and previous.get("schema") != SCHEMA:
        raise ValueError("refuse to overwrite unknown previous schema")
    relation = link_github_repo_to_package(github, pypi)
    before = (previous or {}).get("observations", {})
    changes = {}
    for key, value in (("github", github), ("pypi", pypi)):
        old = SourceObservation.model_validate(before[key]) if key in before else None
        result = classify_change(old, value)
        changes[key] = {"kind": result.kind.value, "changed_fields": result.changed_fields}
    observations = {
        "usgs": [q.model_dump(mode="json") for q in sorted(quakes, key=lambda q: q.source_id)],
        "github": github.model_dump(mode="json"),
        "pypi": pypi.model_dump(mode="json"),
    }
    magnitudes = sorted(
        [float(q.payload["magnitude"]) for q in quakes if q.payload.get("magnitude") is not None],
        reverse=True,
    )
    stable_values = {
        "usgs": [{"id": q.source_id, "payload": q.payload, "updated": str(q.source_updated_at)} for q in sorted(quakes, key=lambda q: q.source_id)],
        "github": github.payload, "pypi": pypi.payload,
        "match": [(e.kind, e.value, e.weight) for e in relation.evidence],
    }
    return {
        "schema": SCHEMA,
        "checked_at": checked_at.astimezone(timezone.utc).isoformat(),
        "content_sha256": digest(stable_values),
        "sources": {
            "usgs": {"url": USGS_ALL_HOUR, "count": len(quakes),
                     "max_magnitude": magnitudes[0] if magnitudes else None,
                     "window": "rolling past hour"},
            "github": {"url": github.source_url, "canonical_key": github.canonical_key},
            "pypi": {"url": pypi.source_url, "canonical_key": pypi.canonical_key},
        },
        "observations": observations,
        "changes": changes,
        "relationship": {
            "left_key": relation.left_key, "right_key": relation.right_key,
            "matched_by_declared_url_rule": relation.matched,
            "score": relation.score, "threshold": 100,
            "evidence": [vars(e) for e in relation.evidence],
            "scope": "explicit metadata correspondence, not independently authenticated ownership",
        },
        "unjoined": ["USGS earthquake events", "GitHub and PyPI software metadata"],
    }


def render_svg(s: dict) -> str:
    esc = lambda value: html.escape(str(value), quote=True)
    usgs = s["sources"]["usgs"]
    github = s["observations"]["github"]["payload"]
    pypi = s["observations"]["pypi"]["payload"]
    joined = s["relationship"]["matched_by_declared_url_rule"]
    matched = "URL-supported metadata match" if joined else "No supported metadata match"
    color = "#75d8c1" if joined else "#edc382"
    largest = usgs["max_magnitude"]
    largest_text = "No magnitude in window" if largest is None else f"Largest magnitude: {largest:.1f}"
    stamp = esc(s["checked_at"][:19].replace("T", " ") + " UTC")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="495" viewBox="0 0 1000 495">
<rect width="1000" height="495" rx="20" fill="#0d1117"/>
<rect x="12" y="12" width="976" height="471" rx="15" fill="#13202b" stroke="#435466"/>
<g font-family="Arial,Helvetica,sans-serif">
<text x="36" y="52" fill="#8ae0d4" font-size="13" letter-spacing="2">EXTERNAL DATA · READ-ONLY OBSERVATIONAL PROJECTION</text>
<text x="36" y="92" fill="#eef4fa" font-size="33" font-weight="bold">World data through continuity</text>
<text x="36" y="116" fill="#b4c5d3" font-size="15">Observed {stamp}</text>
<rect x="34" y="147" width="297" height="191" rx="12" fill="#1a3036" stroke="#40787e"/>
<text x="53" y="178" fill="#7ed8d4" font-size="16">USGS · earthquakes</text>
<text x="53" y="235" fill="#f1f5f8" font-size="43" font-weight="bold">{int(usgs["count"])}</text>
<text x="53" y="258" fill="#c0d2dc" font-size="15">events in rolling past hour</text>
<text x="53" y="292" fill="#b7cdd4" font-size="15">{esc(largest_text)}</text>
<text x="53" y="317" fill="#a3b9c5" font-size="13">Independent source identity</text>
<rect x="348" y="147" width="297" height="191" rx="12" fill="#24273a" stroke="#7163a5"/>
<text x="367" y="178" fill="#d0b9ff" font-size="16">GitHub · repository</text>
<text x="367" y="221" fill="#f1f5f8" font-size="22" font-weight="bold">{esc(github["full_name"])}</text>
<text x="367" y="257" fill="#cbd4e4" font-size="16">Stars {int(github["stargazers_count"])}</text>
<text x="367" y="292" fill="#d0b9ff" font-size="15">Change: {esc(s["changes"]["github"]["kind"])}</text>
<text x="367" y="317" fill="#a3b9c5" font-size="13">Stable repository ID</text>
<rect x="662" y="147" width="304" height="191" rx="12" fill="#302a22" stroke="#a68a61"/>
<text x="681" y="178" fill="#eed09b" font-size="16">PyPI · package</text>
<text x="681" y="221" fill="#f1f5f8" font-size="25" font-weight="bold">{esc(pypi["name"])}</text>
<text x="681" y="257" fill="#d4d4d4" font-size="16">Version {esc(pypi["version"])}</text>
<text x="681" y="292" fill="#eed09b" font-size="15">Change: {esc(s["changes"]["pypi"]["kind"])}</text>
<text x="681" y="317" fill="#a3b9c5" font-size="13">Package metadata source</text>
<path d="M495 338 V356 H813 V338" fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="5 5"/>
<rect x="444" y="363" width="426" height="43" rx="10" fill="#193031" stroke="{color}"/>
<text x="657" y="390" fill="{color}" font-size="16" font-weight="bold" text-anchor="middle">{matched}</text>
<text x="37" y="382" fill="#99ced0" font-size="14">No inferred USGS/software link</text>
<line x1="35" y1="431" x2="965" y2="431" stroke="#45586a"/>
<text x="36" y="453" fill="#bccbd5" font-size="13">Every observation has a source, ID and timestamp. Follow source links in LATEST.md.</text>
<text x="36" y="472" fill="#e8cb9c" font-size="12">A source-metadata match is not an ownership proof or a universal A/B claim.</text>
</g></svg>
'''


def render_markdown(s: dict) -> str:
    r = s["relationship"]
    evidence = "\n".join(
        "- " + e["kind"] + ": " + e["value"] + " (rule weight " + str(e["weight"]) + ")"
        for e in r["evidence"]
    ) or "- No accepted matching evidence"
    status = "matched by local metadata rule" if r["matched_by_declared_url_rule"] else "not matched by local rule"
    return f"""# Latest world observation

![Public world observation view](latest.svg)

Collected: {s["checked_at"]} (UTC). This projection uses the original public-data-monitor adapters.

| Source | State | Direct source |
| --- | --- | --- |
| USGS / rolling past hour | {s["sources"]["usgs"]["count"]} events | [USGS]({USGS_ALL_HOUR}) |
| GitHub / psf/requests | {s["changes"]["github"]["kind"]} | [GitHub]({s["sources"]["github"]["url"]}) |
| PyPI / requests | {s["changes"]["pypi"]["kind"]} | [PyPI]({s["sources"]["pypi"]["url"]}) |

## Relationship: GitHub and PyPI

Result: **{status}**, not independently verified ownership.

{evidence}

USGS is **not connected** to the software observations merely because their timestamps overlap. Because its feed is a sliding window, absence from the next fetch is not evidence of disappearance.

## Verify the observation

- [Machine-readable observations and source IDs](latest.json)
- [Historical poll summaries](checks.jsonl)
- [Actual public-data-monitor adapters](../../work/projects/public-data-monitor/app/)
- [Original change and identity logic](../../work/projects/public-data-monitor/app/platform.py)
- [Original identity rule](../../work/projects/public-data-monitor/app/identity.py)
- [Existing Prometheus instrumentation](../../work/projects/public-data-monitor/app/metrics.py)

The SHA-256 digest in latest.json is an integrity fingerprint, **not** proof of source authenticity. The SVG is GitHub-rendered output, not a running Prometheus database or proof of continuous hosting.
"""


def execute(out: Path) -> None:
    latest = out / "latest.json"
    previous = json.loads(latest.read_text(encoding="utf-8")) if latest.exists() else None
    # Fail before writes if an external source cannot be reached.
    quakes = LiveJsonAdapter().fetch()
    github, pypi = fetch_repository(), fetch_project()
    if len(github) != 1 or len(pypi) != 1:
        raise ValueError("native GitHub/PyPI adapter should return exactly one observation")
    snapshot = compose(quakes, github[0], pypi[0], datetime.now(timezone.utc), previous)
    record = {
        "checked_at": snapshot["checked_at"], "digest": snapshot["content_sha256"],
        "usgs_count": snapshot["sources"]["usgs"]["count"],
        "github_change": snapshot["changes"]["github"]["kind"],
        "pypi_change": snapshot["changes"]["pypi"]["kind"],
        "url_matched": snapshot["relationship"]["matched_by_declared_url_rule"],
    }
    out.mkdir(parents=True, exist_ok=True)
    history = out / "checks.jsonl"
    old = history.read_text(encoding="utf-8") if history.exists() else ""
    latest.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "latest.svg").write_text(render_svg(snapshot), encoding="utf-8")
    (out / "LATEST.md").write_text(render_markdown(snapshot), encoding="utf-8")
    history.write_text(old + json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Permit public network calls and generated files")
    parser.add_argument("--out-dir", type=Path, default=DIR)
    args = parser.parse_args()
    if not args.execute:
        parser.error("explicit --execute required; viewing the README cannot start collection")
    execute(args.out_dir)


if __name__ == "__main__":
    main()
