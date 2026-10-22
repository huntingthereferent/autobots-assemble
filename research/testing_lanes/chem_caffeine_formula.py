"""CHEM-CAFFEINE-FORMULA-001: verify one public compound record against atom weights.

This is a record-level consistency check, not an experimental chemistry result.
It fetches only PubChem CID 2519, stores selected properties and a body hash,
and rejects unexpected record identity or formula/mass inconsistency.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

CID = 2519
SOURCE_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"
    "2519/property/MolecularFormula,MolecularWeight,CanonicalSMILES/JSON"
)
MAX_BYTES = 100_000
TIMEOUT = 15
ATOMIC_WEIGHTS = {"C": 12.011, "H": 1.008, "N": 14.007, "O": 15.999}
EXPECTED_FORMULA = "C8H10N4O2"
EXPECTED_CAS = "58-08-2"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def formula_mass(formula: str) -> float:
    tokens = re.findall(r"([A-Z][a-z]?)([0-9]*)", formula)
    if not tokens or "".join(element + count for element, count in tokens) != formula:
        raise ValueError("invalid molecular formula syntax")
    total = 0.0
    for element, count in tokens:
        if element not in ATOMIC_WEIGHTS:
            raise ValueError("unsupported element in bounded mass table")
        total += ATOMIC_WEIGHTS[element] * (int(count) if count else 1)
    return total


def validate_properties(properties: dict) -> dict:
    if properties.get("CID") != CID:
        raise ValueError("compound identity mismatch")
    formula = properties.get("MolecularFormula")
    if formula != EXPECTED_FORMULA:
        raise ValueError("molecular formula does not match pinned caffeine record")
    reported = float(properties["MolecularWeight"])
    calculated = formula_mass(formula)
    if abs(reported - calculated) > 0.05:
        raise ValueError("reported molecular weight disagrees with formula mass tolerance")
    smiles = properties.get("ConnectivitySMILES") or properties.get("CanonicalSMILES")
    if not isinstance(smiles, str) or not smiles:
        raise ValueError("missing structure identifier")
    return {
        "cid": CID,
        "molecular_formula": formula,
        "reported_molecular_weight_g_mol": reported,
        "formula_mass_from_fixed_atomic_weights_g_mol": round(calculated, 6),
        "absolute_mass_difference_g_mol": round(abs(reported - calculated), 6),
        "mass_tolerance_g_mol": 0.05,
        "structure_identifier_present": True,
        "outcome": "FORMULA_MASS_CONSISTENT",
    }


def run_live(opener=None):
    opener = opener or build_opener(NoRedirect)
    request = Request(SOURCE_URL, headers={"User-Agent": "Aeren-Research-CHEM-test/1.0"})
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            status = response.status
            raw = response.read(MAX_BYTES + 1)
    except HTTPError as exc:
        return {"status": "SOURCE_WALL", "http_status": exc.code,
                "redirect_denied": 300 <= exc.code < 400, "source_url": SOURCE_URL}
    except (URLError, TimeoutError, OSError) as exc:
        return {"status": "SOURCE_WALL", "error_type": type(exc).__name__,
                "source_url": SOURCE_URL}
    if len(raw) > MAX_BYTES:
        raise ValueError("source response exceeded byte cap")
    body_hash = hashlib.sha256(raw).hexdigest()
    payload = json.loads(raw.decode("utf-8"))
    props = payload["PropertyTable"]["Properties"]
    if len(props) != 1:
        raise ValueError("source returned unexpected record count")
    observed = validate_properties(props[0])
    return {
        "schema_version": 1,
        "experiment_id": "CHEM-CAFFEINE-FORMULA-001",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": observed["outcome"],
        "source": {"url": SOURCE_URL, "http_status": status, "bytes_read": len(raw),
                   "sha256": body_hash, "full_body_archived": False},
        "observed": observed,
        "limits": [
            "One PubChem compound record only; no independent experimental measurement.",
            "Atomic weights are fixed constants listed in this code and mass agreement is a consistency check.",
            "No conclusion about purity, physical state, biological activity or synthesis is tested.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.live:
        print("Offline mode: run tests; pass --live to query the single pinned record.")
        return
    receipt = run_live()
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if receipt.get("status") == "SOURCE_WALL":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
