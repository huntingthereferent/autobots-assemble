"""Bounded NIH Phase 1 *local draft* builder from the source-owned temporal results.

No network, no NIH submission, no clinical claims. This process is the BUILD
actor: it constructs a new research design packet from the witnessed inputs.
"""
import hashlib
import json
import os
import sys

def compact(value):
    return ", ".join(value) if value else "none"

def build(data):
    if type(data) is not dict or set(data) != {
        "request", "scope", "reasoning_report", "ontology_sha256", "ontology_triples"}:
        raise ValueError("packet BUILD requires exact native input envelope")
    req,scope,reason = data["request"],data["scope"],data["reasoning_report"]
    if req.get("kind") != "synthetic-phase1-design-packet/v1" or req.get("synthetic") is not True:
        raise ValueError("only local synthetic packet")
    if reason.get("conclusion") != "synthetic-temporal-logic-only":
        raise ValueError("reasoning must remain synthetic")
    evidence = []
    for case in reason["cases"]:
        evidence.append({
            "id":case["id"],
            "known_at":case["known_at"],
            "target_at":case["target_at"],
            "available":list(case["admissible"]),
            "withheld_future":list(case["withheld_future"]),
            "outside_validity":list(case["not_applicable"]),
            "declared_conflicts":list(case["declared_conflicts"]),
        })
    summary = {
        "packet_id":req["packet_id"],
        "scope_case_id":scope["case_id"],
        "research_question":scope["question"],
        "ontology_sha256":data["ontology_sha256"],
        "ontology_triples":data["ontology_triples"],
        "synthetic_observations":len(scope["observations"]),
        "temporal_cases":evidence,
        "declared_functional_predicates":list(reason["functional_predicates"]),
        "scientific_scope":"synthetic point-in-time knowledge availability only",
    }
    lines = [
        "# Phase 1 research design — temporal evidence availability",
        "",
        "**Status:** local synthetic design packet. Not an NIH submission or award.",
        "",
        "## Research question",
        scope["question"],
        "",
        "## Hypothesis",
        "A query that separates the time a fact describes from the time that fact becomes knowable can prevent future evidence from entering earlier decisions.",
        "",
        "## Method",
        "Compare an as-known-at temporal view with a static union of every synthetically valid fact. The latter may leak later-known observations into earlier knowledge cutoffs.",
        "For each query, require valid_from <= target_at < valid_to and known_at <= query known_at. Validity intervals are half-open.",
        "Represent intervals with OWL-Time, source provenance with PROV-O, and typed research entities with the chosen Biolink mapping. This is RDF structure, not general OWL entailment.",
        "",
        "## Evidence provenance",
        "- Scope case: " + scope["case_id"],
        "- Synthetic observation count: " + str(len(scope["observations"])),
        "- Independently mapped RDF triples: " + str(data["ontology_triples"]),
        "- RDF source SHA-256: " + data["ontology_sha256"],
        "- Functional constraints only for declared predicates: " + compact(reason["functional_predicates"]),
        "",
        "## Temporal benchmark cases",
        "| Case | Known at | Target at | Available | Future withheld | Outside validity | Conflicts |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in evidence:
        lines.append("| " + " | ".join([
            row["id"],row["known_at"],row["target_at"],
            compact(row["available"]),compact(row["withheld_future"]),
            compact(row["outside_validity"]),
            "; ".join("/".join(pair) for pair in row["declared_conflicts"]) or "none",
        ]) + " |")
    lines += [
        "",
        "## Acceptance tests",
        "1. Independently reproduce each available, future-withheld, and outside-validity observation set from the original synthetic scope.",
        "2. Re-run each query with different knowledge cutoffs; forbid future observations from appearing before their known_at date.",
        "3. Evaluate conflicting values only where the source explicitly declares the predicate functional.",
        "4. Compare temporal and static-union baselines; report any leakage and negative cases rather than assuming improvement.",
        "5. Preserve the original ontology, reasoning, and scope worker identities and native independent evidence.",
        "",
        "## Next work",
        "Develop a separate Phase 2 prototype and game-backed temporal test only after their source-owned contracts and independent witnesses exist.",
        "The currently playable game room is a build/test instrument, not evidence that the temporal prototype or official competition submission has been completed.",
        "",
        "## Limits and external boundaries",
        "Synthetic records only; no patient data, no disease predictions, no clinical validation, no official NIH submission or eligibility decision.",
        "The fixed examples do not establish general temporal KG correctness, OWL entailment, or superiority over an external benchmark.",
    ]
    return {"kind":"local-synthetic-phase1-packet/v1", "summary":summary,
            "markdown":"\n".join(lines)+"\n"}

if __name__ == "__main__":
    try:
        raw=sys.stdin.read(128001)
        if len(raw)>128000:
            raise ValueError("bounded input envelope too large")
        built=build(json.loads(raw))
        print(json.dumps({"packet":built,"pid":os.getpid()}, sort_keys=True))
    except (KeyError,TypeError,ValueError) as exc:
        print(str(exc),file=sys.stderr)
        raise SystemExit(2)
