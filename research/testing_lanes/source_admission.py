"""Research source admission: 18 independent metadata-only source contracts.

Default actions are offline. Exactly one named public source may be probed per
explicit --probe invocation. Receipts contain hashes and structural evidence,
never raw datasets or claims of scientific replication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parent
CARDS = ROOT / "sources"
REGISTRY = ROOT / "registry.json"

ALLOWED_HOSTS = {
    "openalex": "api.openalex.org",
    "crossref": "api.crossref.org",
    "osf": "api.osf.io",
    "zenodo": "zenodo.org",
    "openml": "www.openml.org",
    "hf": "huggingface.co",
    "pubmed": "eutils.ncbi.nlm.nih.gov",
    "ctgov": "clinicaltrials.gov",
    "pubchem": "pubchem.ncbi.nlm.nih.gov",
    "earthdata": "cmr.earthdata.nasa.gov",
    "gwosc": "gwosc.org",
    "worldbank": "api.worldbank.org",
    "nvd": "services.nvd.nist.gov",
}
MANUAL = {"physionet", "openneuro", "nist", "noaa", "oecd"}
ALL_IDS = set(ALLOWED_HOSTS) | MANUAL
HEX = re.compile(r"^[a-z0-9-]+$")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def catalog(root: Path = ROOT) -> dict[str, dict]:
    reg = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    if reg.get("schema_version") != 1:
        raise ValueError("unsupported research registry version")
    registered = {x["id"] for x in reg["sources"]}
    if registered != ALL_IDS or len(reg["sources"]) != len(registered):
        raise ValueError("source list and expected registry do not agree")
    folder = root / "sources"
    files = sorted(folder.glob("*.json"))
    if len(files) != len(ALL_IDS):
        raise ValueError("missing or unexpected source card count")
    cards = {}
    for path in files:
        source = json.loads(path.read_text(encoding="utf-8"))
        sid = source.get("source_id")
        if not isinstance(sid, str) or not HEX.fullmatch(sid):
            raise ValueError("invalid source ID")
        if sid != path.stem or sid in cards or sid not in registered:
            raise ValueError("source ID/file does not match registry")
        if source.get("schema_version") != 1:
            raise ValueError("source schema invalid")
        if source.get("admission_stage") != "DOCUMENTED_NOT_OBSERVED" or source.get("observation_status") != "NOT_RUN":
            raise ValueError("unwitnessed catalog source may not claim observed status")
        if source.get("scientific_outcome") != "NOT_TESTED":
            raise ValueError("source catalog may not claim scientific outcomes")
        if source.get("rights_review") != "REQUIRED_PER_RECORD":
            raise ValueError("rights gate absent")
        if source.get("documentation_checked_on") != "2026-10-22":
            raise ValueError("catalog requires explicit documentation date")
        documentation = urlsplit(source.get("documentation_url", ""))
        if documentation.scheme != "https" or not documentation.netloc:
            raise ValueError("source documentation must be HTTPS")
        probe = source.get("probe")
        if not isinstance(probe, dict) or probe.get("redirects") != "deny":
            raise ValueError("missing probe safety boundary")
        if sid in MANUAL:
            if probe.get("url") is not None or probe.get("mode") != "manual_review_required":
                raise ValueError("manual-only sources cannot have active probes")
        else:
            url = urlsplit(probe.get("url") or "")
            if (url.scheme != "https" or url.hostname != ALLOWED_HOSTS[sid]
                    or url.username or url.password or probe.get("method") != "GET"
                    or probe.get("mode") != "explicit_opt_in"
                    or probe.get("expected_format") not in ("json", "html")
                    or not isinstance(probe.get("max_bytes"), int)
                    or not 0 < probe["max_bytes"] <= 300000
                    or probe.get("timeout_seconds") != 15):
                raise ValueError("unsafe live source probe")
        cards[sid] = source
    if set(cards) != ALL_IDS:
        raise ValueError("incomplete source cards")
    for lane in reg["lanes"]:
        if not set(lane["source_ids"]) <= set(cards):
            raise ValueError("lane depends on unregistered source")
    return cards


def inspect_shape(source_id: str, raw: bytes, expected_format: str) -> dict:
    """Limited structural receipts, not full source validation."""
    if expected_format == "html":
        return {"record_shape": "public_html_entry_page", "semantic_record_verified": False}
    data = json.loads(raw.decode("utf-8-sig"))
    if source_id == "crossref":
        matched = isinstance(data, dict) and (data.get("message") or {}).get("DOI", "").lower() == "10.1126/science.aac4716"
    elif source_id == "openalex":
        matched = isinstance(data, dict) and str(data.get("doi", "")).lower().endswith("10.1126/science.aac4716")
    elif source_id == "pubmed":
        matched = "26315443" in (data.get("esearchresult", {}).get("idlist", []) if isinstance(data, dict) else [])
    elif source_id == "pubchem":
        props = data.get("PropertyTable", {}).get("Properties", []) if isinstance(data, dict) else []
        matched = bool(props and props[0].get("CID") == 962)
    elif source_id == "worldbank":
        matched = isinstance(data, list) and len(data) >= 2 and isinstance(data[1], list)
    elif source_id == "ctgov":
        matched = isinstance(data, dict) and isinstance(data.get("studies"), list)
    elif source_id == "zenodo":
        matched = isinstance(data, dict) and isinstance(data.get("hits"), dict)
    elif source_id == "openml":
        matched = isinstance(data, dict) and "data_set_description" in data
    elif source_id == "hf":
        matched = isinstance(data, list)
    elif source_id == "osf":
        matched = isinstance(data, dict) and isinstance(data.get("data"), list)
    elif source_id == "earthdata":
        matched = isinstance(data, dict) and isinstance(data.get("feed"), dict)
    elif source_id == "nvd":
        matched = isinstance(data, dict) and isinstance(data.get("vulnerabilities"), list)
    else:
        raise ValueError("unsupported source structural predicate")
    return {"record_shape": "expected_structure" if matched else "schema_mismatch",
            "semantic_record_verified": bool(matched)}


def probe_one(source_id: str, cards: dict[str, dict], opener=None) -> dict:
    if source_id not in cards:
        raise ValueError("source not registered")
    card = cards[source_id]
    if source_id in MANUAL:
        return {
            "source_id": source_id,
            "state": "ACCESS_WALL",
            "reason": card["boundary"],
            "scientific_claim_verified": False,
        }
    probe = card["probe"]
    url = probe["url"]
    if urlsplit(url).hostname != ALLOWED_HOSTS[source_id]:
        raise ValueError("provider host mismatch")
    receipt = {"source_id": source_id, "source_url": url,
               "state": "UNKNOWN", "scientific_claim_verified": False,
               "source_data_archived": False}
    try:
        req = Request(url, headers={"Accept": "application/json,text/html;q=0.8",
            "User-Agent": "Research-source-admission/1.0 (huntingthereferent/autobots-assemble)"})
        client = opener if opener is not None else build_opener(NoRedirect)
        with client.open(req, timeout=probe["timeout_seconds"]) as response:
            if response.status != 200:
                raise ValueError("non-200 source status")
            raw = response.read(probe["max_bytes"] + 1)
            timestamp = datetime.now(timezone.utc).isoformat()
        if len(raw) > probe["max_bytes"]:
            raise ValueError("source exceeded response byte ceiling")
        shape = inspect_shape(source_id, raw, probe["expected_format"])
        receipt.update({
            "observed_at_utc": timestamp, "response_status": 200,
            "body_sha256": hashlib.sha256(raw).hexdigest(),
            "response_bytes": len(raw), "inspection": shape,
            "state": ("DOCUMENTATION_OBSERVED" if probe["expected_format"] == "html" else
                      "METADATA_OBSERVED" if shape["semantic_record_verified"] else "STRUCTURE_WALL"),
        })
    except (HTTPError, URLError, ValueError, TimeoutError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        receipt.update({"state": "SOURCE_WALL", "error_class": type(exc).__name__})
    return receipt


def main() -> int:
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("command", choices=("check", "list", "probe"))
    arg.add_argument("source_id", nargs="?")
    arg.add_argument("--output", type=Path)
    args = arg.parse_args()
    cards = catalog()
    if args.command == "check":
        output = {"schema_version": 1, "catalog_sources": len(cards),
                  "eligible_probes": len(ALLOWED_HOSTS), "manual_gates": len(MANUAL),
                  "state": "CONTRACT_VALID", "live_sources_verified": 0}
    elif args.command == "list":
        output = [{"id": k, "mode": cards[k]["probe"]["mode"], "state": cards[k]["observation_status"]}
                  for k in sorted(cards)]
    else:
        if not args.source_id:
            arg.error("probe requires one individual registered source ID")
        output = probe_one(args.source_id, cards)
    display = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(display, encoding="utf-8")
    print(display)
    return 0 if args.command != "probe" or output["state"] in ("METADATA_OBSERVED", "DOCUMENTATION_OBSERVED") else 2


if __name__ == "__main__":
    sys.exit(main())
