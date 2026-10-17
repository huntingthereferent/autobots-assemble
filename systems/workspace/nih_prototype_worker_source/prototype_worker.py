"""Bounded BUILD: package a runnable synthetic temporal query prototype.

The ENGINE is copied into the returned artifact by this independent native
worker process. Its dataset, demonstration queries and README are constructed
from the exact source-owned Phase-1 reasoning and packet inputs.
"""
import json, os, sys

ENGINE = '''"""Local synthetic valid-time / known-time query prototype. No network."""
import json
import sys
from datetime import date

def day(v):
    if type(v) is not str or len(v) != 10 or date.fromisoformat(v).isoformat() != v:
        raise ValueError("query dates must be canonical YYYY-MM-DD")
    return v

def query(dataset, request):
    if type(request) is not dict or set(request) != {"known_at","target_at"}:
        raise ValueError("expected exact known_at and target_at query")
    known, target = day(request["known_at"]), day(request["target_at"])
    if (type(dataset) is not dict or dataset.get("synthetic") is not True
            or type(dataset.get("observations")) is not list
            or type(dataset.get("functional_predicates")) is not list):
        raise ValueError("not a synthetic temporal dataset")
    eligible = [o for o in dataset["observations"]
                if o["valid_from"] <= target < o["valid_to"]]
    temporal = [o for o in eligible if o["known_at"] <= known]
    withheld = [o for o in eligible if o["known_at"] > known]
    outside = [o for o in dataset["observations"] if o not in eligible]
    conflict = []
    for pred in dataset["functional_predicates"]:
        for i, a in enumerate(temporal):
            if a["predicate"] != pred:
                continue
            for b in temporal[i + 1:]:
                if b["subject"] == a["subject"] and b["predicate"] == pred and b["object"] != a["object"]:
                    conflict.append(sorted([a["id"], b["id"]]))
    return {"kind":"synthetic-bitemporal-query/v1",
            "known_at":known,"target_at":target,
            "temporal_ids":sorted(o["id"] for o in temporal),
            "static_snapshot_ids":sorted(o["id"] for o in eligible),
            "future_leakage_ids":sorted(o["id"] for o in withheld),
            "outside_validity_ids":sorted(o["id"] for o in outside),
            "declared_conflicts":sorted(conflict),
            "visible_source_refs":sorted(set(o["source_ref"] for o in temporal)),
            "clinical_verdict":"NOT_EVALUATED"}

def main():
    if len(sys.argv) != 2:
        raise ValueError("usage: python temporal_query.py temporal_dataset.json")
    with open(sys.argv[1], "r", encoding="utf8") as fh:
        data = json.load(fh)
    request = json.loads(sys.stdin.read(4097))
    print(json.dumps(query(data, request), sort_keys=True))
if __name__ == "__main__":
    try:
        main()
    except (KeyError, TypeError, ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
'''

def build(data):
    required={"request","scope","reasoning_request","reasoning_report",
              "packet_summary","ontology_sha256"}
    if type(data) is not dict or set(data) != required:
        raise ValueError("prototype requires complete exact source ancestry")
    req,scope,reason,packet=data["request"],data["scope"],data["reasoning_report"],data["packet_summary"]
    if (req.get("kind") != "synthetic-temporal-prototype/v1"
            or req.get("synthetic") is not True
            or not isinstance(packet.get("packet_id"), str)
            or reason.get("conclusion") != "synthetic-temporal-logic-only"):
        raise ValueError("prototype must derive from native synthetic packet and reasoning")
    dataset={"kind":"synthetic-temporal-dataset/v1","synthetic":True,
             "case_id":scope["case_id"],"prototype_id":req["prototype_id"],
             "ontology_sha256":data["ontology_sha256"],
             "observations":scope["observations"],
             "functional_predicates":data["reasoning_request"]["functional_predicates"]}
    samples=[{"known_at":case["known_at"],"target_at":case["target_at"]}
             for case in data["reasoning_request"]["cases"]]
    readme="\n".join([
        "# Temporal Evidence — runnable synthetic prototype",
        "",
        "Local demonstration for "+scope["case_id"]+". Not an NIH submission.",
        "",
        "Run python temporal_query.py temporal_dataset.json and send one JSON line on stdin.",
        "Example input: "+json.dumps(samples[0],sort_keys=True),
        "",
        "temporal_ids only includes valid-at-target evidence already known at query time.",
        "static_snapshot_ids ignores when information became known.",
        "future_leakage_ids is the difference: evidence a static view would expose too early.",
        "outside_validity_ids is not true at the target time; conflicts only use declared functional predicates.",
        "",
        "Dates are YYYY-MM-DD; validity intervals are half-open [start, end).",
        "Each visible fact retains its synthetic source_ref; no patient data or clinical predictions.",
        "",
        "The executable reads a new local query each time, not just the examples shipped with BUILD.",
        "This prototype does not implement OWL entailment, external clinical validation, a Phase 2 benchmark or official NIH submission.",
        "",
    ])
    return {"kind":"synthetic-runnable-temporal-prototype/v1",
            "prototype_id":req["prototype_id"],
            "python_source":ENGINE,
            "dataset_json":json.dumps(dataset,sort_keys=True,indent=2)+"\n",
            "readme_md":readme,
            "examples":samples}

if __name__=="__main__":
    try:
        incoming=sys.stdin.read(128001)
        if len(incoming)>128000: raise ValueError("bounded prototype source too large")
        built=build(json.loads(incoming))
        print(json.dumps({"pid":os.getpid(),"artifact":built},sort_keys=True))
    except (ValueError,TypeError,KeyError) as exc:
        print(str(exc),file=sys.stderr)
        raise SystemExit(2)
