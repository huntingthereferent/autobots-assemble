"""WORLD/BUILD: the Phase-2 implementation blueprint carried by Phase-1 design.

Controls a bounded 2-D visual graph and the original W13 two-room movement
without treating display coordinates as knowledge-graph dimensions. Authentic
2019 registry release *instants* are unknown; owner-posted days are only
conditional metadata, not proof of a clinical temporal answer.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re

VERSION="world-phase1-phase2-nih-temporal-blueprint/v1"
PROVENANCES=("synthetic","owner-version-day-attested")
FIELDS={"id","subject","predicate","object","source_ref","provenance_state",
        "valid_from","valid_to","known_day","event_day","submitted_day",
        "posted_day","observed_day"}
REAL_DIGESTS={"ctgov-v94":"4370ff462cd731f2f42cc866aadb438e4d037c7a05de2cd64fb5acb53500c3ba",
              "ctgov-v105":"4daab6b95ea574a0aeaea3fba36a94fd9db8df8f0dafd41eee5b87bd9a6bd9db"}
REAL_DAYS={"ctgov-v94":("2019-08-01","2019-08-02"),
           "ctgov-v105":("2019-11-22","2019-11-25")}
ROOMS=[{"id":"first-room","spec":{"width":4,"height":3,"start":[0,1],"target":[2,1]}},
       {"id":"second-room","spec":{"width":3,"height":3,"start":[0,0],"target":[1,1]}}]
TOKEN=re.compile(r"[a-z][a-z0-9-]{1,63}\Z")
DAY=re.compile(r"\d{4}-\d{2}-\d{2}\Z")
KEYS=("source","assertion","valid interval","availability","query","witness")

def good_day(value,*,optional=False):
    if value is None and optional:return None
    if type(value) is not str or not DAY.fullmatch(value):
        raise ValueError("blueprint date must be canonical YYYY-MM-DD, or explicit null")
    try:parsed=date.fromisoformat(value)
    except ValueError as exc:raise ValueError("not a calendar day") from exc
    if parsed.isoformat()!=value:raise ValueError("noncanonical calendar date")
    return value

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)

def digest(value):
    return sha256(canonical(value).encode()).hexdigest()

def validate(bp):
    if type(bp) is not dict or set(bp)!={
        "schema","research_context","base_world","world_roles","clocks",
        "graph_schema","sample_sets","queries","source_policy","graph_layout"}:
        raise ValueError("blueprint structure changed")
    if bp["schema"]!=VERSION:raise ValueError("wrong world blueprint version")
    w=bp["base_world"]
    if (type(w) is not dict or w.get("version")!="game-w13-multiworld-v1" or
        w.get("rooms")!=ROOMS or w.get("advance")!="explicit-only-after-first-collection"):
        raise ValueError("original W13 room/movement specification must be preserved")
    ctx=bp["research_context"]
    if (ctx.get("phase1")!="concept-and-feasibility-DRAFT-NOT-SUBMITTED" or
        ctx.get("phase2")!="planned-implementation-blueprint-in-phase1" or
        "clinical result" not in ctx.get("claim","")):
        raise ValueError("actual Phase 1 / Phase 2 research boundary changed")
    if bp["world_roles"].get("first-room")!="source assertion construction and provenance" or bp["world_roles"].get("second-room")!="as-known-at reasoning, static comparison, independent witness":
        raise ValueError("WORLD room roles contradicted")
    if bp["clocks"]!=["valid_time","event_time","submission_time","public_posting_time","observation_time"]:
        raise ValueError("must preserve all five clocks separately")
    if bp["graph_schema"].get("validity")!="half-open [valid_from, valid_to)" or bp["graph_schema"].get("verification")!="independent source and answer oracle":
        raise ValueError("original temporal assertion or verifier contract changed")
    layout=bp["graph_layout"]
    if (type(layout) is not dict or set(layout)!={"columns","lanes"} or
        type(layout["columns"]) is not int or not 3<=layout["columns"]<=12 or
        layout["lanes"]!=list(KEYS)):
        raise ValueError("graph layout is 2-D presentation, not substitute for KG semantics")
    rows=bp["sample_sets"]
    if type(rows) is not dict or set(rows)!={"synthetic","registry"}:raise ValueError("original source partitions missing")
    if (type(rows["synthetic"]) is not list or type(rows["registry"]) is not list or
        not 2<=len(rows["synthetic"])<=32 or len(rows["registry"])!=2 or
        [x.get("id") for x in rows["synthetic"][:2]]!=["prior-note","delayed-result"] or
        [x.get("id") for x in rows["registry"]]!=["ctgov-v94","ctgov-v105"]):
        raise ValueError("source-qualified assertion versions drifted")
    for sample,claims in rows.items():
        ids=[x.get("id") for x in claims]
        if len(ids)!=len(set(ids)):
            raise ValueError("duplicate graph assertion identity")
        for entry in claims:
            real=sample=="registry"
            expected=FIELDS|({"source_text_sha256"} if real else set())
            if type(entry) is not dict or set(entry)!=expected:raise ValueError("source-qualified assertion schema changed")
            for k in ("id","subject","predicate","object"):
                if type(entry[k]) is not str or not TOKEN.fullmatch(entry[k]):raise ValueError("invalid bounded graph token")
            if type(entry["source_ref"]) is not str or not 2<=len(entry["source_ref"])<=256:
                raise ValueError("provenance source reference absent")
            if entry["provenance_state"]!=("owner-version-day-attested" if real else "synthetic"):
                raise ValueError("source class can't be converted by a layout edit")
            for k in ("valid_from","valid_to","known_day","event_day","submitted_day","posted_day","observed_day"):
                good_day(entry[k],optional=True)
            if real:
                ident=entry["id"]
                v=94 if ident=="ctgov-v94" else 105
                if (entry["source_ref"]!=f"https://clinicaltrials.gov/study/NCT00001756?a={v}&tab=history" or
                    entry["source_text_sha256"]!=REAL_DIGESTS[ident] or
                    (entry["submitted_day"],entry["posted_day"])!=REAL_DAYS[ident] or
                    entry["observed_day"]!="2026-10-19" or
                    any(entry[k] is not None for k in ("valid_from","valid_to","known_day","event_day")) or
                    (entry["subject"],entry["predicate"],entry["object"])!=("nct00001756","recruitment-status","recruiting")):
                    raise ValueError("real owner source claims cannot be edited/used as valid-time assertions")
            else:
                if (entry["valid_from"] is None or entry["valid_to"] is None or
                    entry["known_day"] is None or
                    entry["valid_from"]>=entry["valid_to"] or
                    any(entry[k] is not None for k in ("submitted_day","posted_day","observed_day","event_day")) or
                    not entry["source_ref"].startswith("synthetic-")):
                    raise ValueError("synthetic valid interval and modeled availability required")
    if (any(r["subject"]!="fictional-study" for r in rows["synthetic"]) or
        any(r["predicate"]!="has-status" for r in rows["synthetic"])):
        raise ValueError("do not silently change synthetic source domain")
    q=bp["queries"]
    if type(q) is not dict or set(q)!={"synthetic","registry"}:raise ValueError("query partition missing")
    for mode in ("synthetic","registry"):
        if set(q[mode])!={"knowledge_cutoff","valid_target"}:raise ValueError("query fields drifted")
        good_day(q[mode]["knowledge_cutoff"])
    good_day(q["synthetic"]["valid_target"])
    if q["registry"]["valid_target"] is not None:
        raise ValueError("actual registry source doesn't establish valid-time interval")
    policy=bp["source_policy"]
    if (policy.get("strict_original_publication_instant")!="UNAVAILABLE" or
        policy.get("owner_posted_day")!="conditional day-level availability only"):
        raise ValueError("unknown real first-public release must remain unknown")
    return bp

def evaluate(bp,mode):
    validate(bp)
    if mode not in ("synthetic","registry"):raise ValueError("unknown research source partition")
    query=bp["queries"][mode]
    k=query["knowledge_cutoff"];v=query["valid_target"]
    out={"eligible":[],"withheld_future":[],"outside_validity":[],
         "unresolved_validity":[],"owner_day_states":{},"static_union_valid":[]}
    for item in bp["sample_sets"][mode]:
        ident=item["id"]
        if item["provenance_state"]=="synthetic":
            if not item["valid_from"]<=v<item["valid_to"]:
                out["outside_validity"].append(ident)
            else:
                out["static_union_valid"].append(ident)
                out["eligible" if item["known_day"]<=k else "withheld_future"].append(ident)
        else:
            out["unresolved_validity"].append(ident)
            posted=item["posted_day"]
            out["owner_day_states"][ident]=(
                "BEFORE_OWNER_REPORTED_DAY" if k<posted else
                "SAME_DAY_TIME_UNRESOLVED" if k==posted else
                "AFTER_OWNER_REPORTED_DAY")
    return {**out,"schema":"world-phase1-phase2-temporal-query-receipt/v1",
        "source_partition":mode,"query":deepcopy(query),
        "static_future_leakage":sorted(set(out["static_union_valid"])-set(out["eligible"]))
              if mode=="synthetic" else [],
        "clinical_verdict":"NOT_EVALUATED",
        "publication_instant_authenticated":False if mode=="registry" else None,
        "source_reading":"fictional exact modeled known day" if mode=="synthetic" else
             "original owner-reported calendar days only; validity unknown",
        "blueprint_sha256":digest(bp)}

def graph(bp,mode):
    """Return independently reconstructable graph topology, not pixels."""
    validate(bp)
    if mode not in bp["sample_sets"]:raise ValueError("wrong graph mode")
    nodes=[];edges=[]
    for i,entry in enumerate(bp["sample_sets"][mode]):
        attrs=[
            ("source",entry["source_ref"]),
            ("assertion",entry["id"]+" → "+entry["object"]),
            ("valid interval",("[ "+entry["valid_from"]+", "+entry["valid_to"]+" )")
                if entry["valid_from"] is not None else "UNKNOWN validity"),
            ("availability",entry["known_day"] or
             ((entry["posted_day"] or "UNKNOWN")+" (owner day only)")),
            ("query","K="+bp["queries"][mode]["knowledge_cutoff"]+
             " / V="+("null" if bp["queries"][mode]["valid_target"] is None else bp["queries"][mode]["valid_target"])),
            ("witness",entry["provenance_state"])]
        for j,(lane,text) in enumerate(attrs):
            nid=f"{entry['id']}:{j}"
            nodes.append({"id":nid,"lane":lane,"column":j,"row":i,"label":text})
            if j:edges.append({"from":f"{entry['id']}:{j-1}","to":nid})
    return {"nodes":nodes,"edges":edges,"columns":bp["graph_layout"]["columns"],
            "logical_clocks":list(bp["clocks"])}
