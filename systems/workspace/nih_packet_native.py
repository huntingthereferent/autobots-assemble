"""Host-owned, source-INDEPENDENT verification of local NIH Phase-1 packet BUILD."""
from __future__ import annotations
from hashlib import sha256
import re

from .nih_scope_native import validate_scope
from .nih_reasoning_native import expected_reasoning_report

CP_ID = "NIH-P1-PACKET"
WORKER_ROLE = "artifact-builder"
VERIFIER = "cp-checker:NIH-P1-PACKET"
_ID = re.compile(r"[a-z][a-z0-9_-]{1,47}\Z")

def validate_packet_request(req: object) -> dict:
    if type(req) is not dict or set(req) != {"kind","synthetic","packet_id","reasoning_job_id"}:
        raise ValueError("exact NIH local packet request required")
    if req["kind"] != "synthetic-phase1-design-packet/v1" or req["synthetic"] is not True:
        raise ValueError("only local synthetic packet supported")
    if any(type(req[k]) is not str or not _ID.fullmatch(req[k])
           for k in ("packet_id","reasoning_job_id")):
        raise ValueError("invalid packet/parent identifier")
    return dict(req)


def packet_summary(req: dict, scope: dict, reasoning_request: dict,
                   ontology_sha256: str, ontology_triples: int) -> dict:
    """Recompute independently from the native parent's original scope inputs."""
    valid = validate_packet_request(req)
    valid_scope = validate_scope(scope)
    expected = expected_reasoning_report(reasoning_request, valid_scope)
    if type(ontology_sha256) is not str or not re.fullmatch(r"[a-f0-9]{64}", ontology_sha256):
        raise ValueError("invalid RDF provenance fingerprint")
    if type(ontology_triples) is not int or ontology_triples <= 0:
        raise ValueError("invalid RDF provenance size")
    evidence = []
    for case in expected["cases"]:
        evidence.append({
            "id":case["id"],"known_at":case["known_at"],"target_at":case["target_at"],
            "available":case["admissible"],
            "withheld_future":case["withheld_future"],
            "outside_validity":case["not_applicable"],
            "declared_conflicts":case["declared_conflicts"],
        })
    return {
        "packet_id":valid["packet_id"],
        "scope_case_id":valid_scope["case_id"],
        "research_question":valid_scope["question"],
        "ontology_sha256":ontology_sha256,
        "ontology_triples":ontology_triples,
        "synthetic_observations":len(valid_scope["observations"]),
        "temporal_cases":evidence,
        "declared_functional_predicates":expected["functional_predicates"],
        "scientific_scope":"synthetic point-in-time knowledge availability only",
    }


def verify_packet(packet: object, *, request: dict, scope: dict,
                  reasoning_request: dict, ontology_sha256: str,
                  ontology_triples: int):
    if type(packet) is not dict or set(packet) != {"kind","summary","markdown"}:
        raise ValueError("BUILD did not return exact packet artifact")
    if packet["kind"] != "local-synthetic-phase1-packet/v1":
        raise ValueError("not a local synthetic packet")
    expected = packet_summary(request, scope, reasoning_request,
                              ontology_sha256, ontology_triples)
    if packet["summary"] != expected:
        raise ValueError("packet claims are not independently reproducible")
    doc = packet["markdown"]
    if type(doc) is not str or not 1300 < len(doc) < 16000:
        raise ValueError("packet draft absent or unsafe length")
    headings = [
        "# Phase 1 research design — temporal evidence availability",
        "## Research question","## Hypothesis","## Method","## Evidence provenance",
        "## Temporal benchmark cases","## Acceptance tests",
        "## Next work","## Limits and external boundaries",
    ]
    if any(doc.count(h) != 1 for h in headings):
        raise ValueError("packet research design sections are missing or duplicated")
    if (expected["research_question"] not in doc or expected["scope_case_id"] not in doc
            or expected["ontology_sha256"] not in doc
            or str(expected["ontology_triples"]) not in doc):
        raise ValueError("packet has lost native research and RDF provenance")
    for case in expected["temporal_cases"]:
        row = ["| "+case["id"]+" | "+case["known_at"]+" | "+case["target_at"]+" |"]
        if doc.count(row[0]) != 1:
            raise ValueError("packet did not render exactly one row for each native temporal case")
        # All source-bounded facts must be present on that same row.
        line = next(line for line in doc.splitlines() if line.startswith(row[0]))
        for k in ("available","withheld_future","outside_validity"):
            values = case[k]
            if (", ".join(values) if values else "none") not in line:
                raise ValueError("packet withheld, available or validity evidence changed")
        conflicts = "; ".join("/".join(pair) for pair in case["declared_conflicts"]) or "none"
        if conflicts not in line:
            raise ValueError("packet conflict evidence differs from reasoning")
    if doc.count("\n| ") != len(expected["temporal_cases"]) + 2:
        raise ValueError("packet benchmark table has unexpected rows")
    for required in ("known_at","valid_from","PROV-O","OWL-Time","Biolink",
                     "clinical validation","NIH submission","Phase 2 prototype"):
        if required not in doc:
            raise ValueError("packet lacks explicit scientific or external boundary")
    return {
        "packet_id":expected["packet_id"],
        "case_count":len(expected["temporal_cases"]),
        "markdown_sha256":sha256(doc.encode("utf8")).hexdigest(),
        "synthetic":True,
        "clinical_verdict":"NOT_EVALUATED",
        "official_submission":False,
    }
