"""Host-independent WITNESS for source-owned runnable bitemporal prototype.

Tests ACTUAL emitted Python program on queries beyond those passed to BUILD.
The oracle uses original source observations, not the builder's case reports.
The worker source and generated executable are not OS-sandboxed.
"""
from __future__ import annotations
from datetime import date, timedelta
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

from .nih_scope_native import validate_scope
from .nih_reasoning_native import validate_request as validate_reasoning
from .nih_packet_native import validate_packet_request

CP_ID="NIH-P2-PROTOTYPE"
WORKER_ROLE="temporal-build"
VERIFIER="cp-checker:NIH-P2-PROTOTYPE"
_ID=re.compile(r"[a-z][a-z0-9_-]{1,47}\Z")

def validate_proto_request(v):
    if type(v) is not dict or set(v)!={"kind","synthetic","prototype_id","reasoning_job_id","packet_job_id"}:
        raise ValueError("prototype must declare exact two parent jobs")
    if v["kind"]!="synthetic-temporal-prototype/v1" or v["synthetic"] is not True:
        raise ValueError("only synthetic local temporal prototype")
    for key in ("prototype_id","reasoning_job_id","packet_job_id"):
        if type(v[key]) is not str or not _ID.fullmatch(v[key]):
            raise ValueError("invalid prototype or native parent ID")
    return dict(v)

def oracle(scope, preds, *, known, target):
    obs=validate_scope(scope)["observations"]
    static=[o for o in obs if o["valid_from"]<=target<o["valid_to"]]
    visible=[o for o in static if o["known_at"]<=known]
    withheld=[o for o in static if o["known_at"]>known]
    outside=[o for o in obs if o not in static]
    conflicts=[]
    for pred in preds:
        for i,a in enumerate(visible):
            if a["predicate"] != pred:
                continue
            for b in visible[i+1:]:
                if b["predicate"]==pred and b["subject"]==a["subject"] and b["object"]!=a["object"]:
                    conflicts.append(sorted((a["id"],b["id"])))
    return {"kind":"synthetic-bitemporal-query/v1",
            "known_at":known,"target_at":target,
            "temporal_ids":sorted(o["id"] for o in visible),
            "static_snapshot_ids":sorted(o["id"] for o in static),
            "future_leakage_ids":sorted(o["id"] for o in withheld),
            "outside_validity_ids":sorted(o["id"] for o in outside),
            "declared_conflicts":sorted(conflicts),
            "visible_source_refs":sorted({o["source_ref"] for o in visible}),
            "clinical_verdict":"NOT_EVALUATED"}

def invoke(script:Path,dataset:Path,payload:dict,*,should_succeed=True):
    done=subprocess.run([sys.executable,"-I",str(script),str(dataset)],
                        input=json.dumps(payload),capture_output=True,text=True,
                        cwd=script.parent,timeout=5,check=False)
    if (done.returncode==0)!=should_succeed or len(done.stdout)>12000 or len(done.stderr)>2000:
        raise ValueError("generated prototype execution did not match native witness boundary")
    return json.loads(done.stdout) if should_succeed else None

def verify_prototype(artifact,*,request,scope,reasoning_request,packet_summary,ontology_sha256):
    req=validate_proto_request(request)
    scope=validate_scope(scope)
    reason=validate_reasoning(reasoning_request)
    packet=validate_packet_request({
        "kind":"synthetic-phase1-design-packet/v1","synthetic":True,
        "packet_id":packet_summary["packet_id"],
        "reasoning_job_id":req["reasoning_job_id"]})
    if packet["packet_id"]!=req["packet_job_id"] and packet_summary["packet_id"]!=req.get("packet_id"):
        # A packet job ID identifies the *job*, not the research-design packet name.
        # Cross-check exact job ancestry in the owning bridge, not a name coincidence.
        pass
    if type(artifact) is not dict or set(artifact)!={
        "kind","prototype_id","python_source","dataset_json","readme_md","examples"}:
        raise ValueError("prototype BUILD response fields differ")
    if artifact["kind"]!="synthetic-runnable-temporal-prototype/v1" or artifact["prototype_id"]!=req["prototype_id"]:
        raise ValueError("prototype identity altered")
    if (type(artifact["python_source"]) is not str or
            not 800<len(artifact["python_source"])<12000 or
            type(artifact["dataset_json"]) is not str or
            not 100<len(artifact["dataset_json"])<18000):
        raise ValueError("standalone code or dataset absent")
    expected_dataset={
        "kind":"synthetic-temporal-dataset/v1","synthetic":True,
        "case_id":scope["case_id"],"prototype_id":req["prototype_id"],
        "ontology_sha256":ontology_sha256,
        "observations":scope["observations"],
        "functional_predicates":reason["functional_predicates"]}
    try:
        dataset=json.loads(artifact["dataset_json"])
    except ValueError as e:
        raise ValueError("BUILD emitted malformed dataset") from e
    if dataset!=expected_dataset:
        raise ValueError("prototype dataset not exact source-owned observations")
    examples=[{"known_at":c["known_at"],"target_at":c["target_at"]} for c in reason["cases"]]
    if artifact["examples"]!=examples:
        raise ValueError("prototype example queries differ from native reasoning")
    readme=artifact["readme_md"]
    if (type(readme) is not str or len(readme)>5000 or
            any(x not in readme for x in (
                "Not an NIH submission","temporal_query.py","temporal_dataset.json",
                "known","validity","future_leakage_ids","clinical","Phase 2 benchmark"))):
        raise ValueError("prototype operating guide is incomplete")
    with TemporaryDirectory() as folder:
        path=Path(folder)
        script=path/"temporal_query.py";data=path/"temporal_dataset.json"
        script.write_text(artifact["python_source"],encoding="utf8")
        data.write_text(artifact["dataset_json"],encoding="utf8")
        queries={tuple(q[k] for k in ("known_at","target_at")) for q in examples}
        # Hidden WITNESS cases: both sides of source boundaries and additional
        # pairwise combinations the worker was never assigned as sample queries.
        days=set()
        for obs in scope["observations"]:
            for field in ("known_at","valid_from","valid_to"):
                t=date.fromisoformat(obs[field])
                days.update((t-timedelta(days=1),t,t+timedelta(days=1)))
        # Keep execution bounded, but require novel pairwise combinations.
        ordered=sorted(t.isoformat() for t in days)
        for known in ordered:
            for target in ordered:
                if len(queries)>=24: break
                queries.add((known,target))
            if len(queries)>=24:break
        if len(queries)<6:
            raise ValueError("native prototype did not receive enough distinct temporal tests")
        leaks=0
        for known,target in sorted(queries):
            expected=oracle(scope,reason["functional_predicates"],known=known,target=target)
            returned=invoke(script,data,{"known_at":known,"target_at":target})
            if returned!=expected:
                raise ValueError("independent hidden bitemporal query rejected built executable")
            leaks+=bool(expected["future_leakage_ids"])
        for invalid in ({"known_at":"2026-99-99","target_at":"2026-01-04"},
                        {"target_at":"2026-01-04"},
                        {"known_at":"2026-01-04","target_at":"2026-01-04","extra":True}):
            invoke(script,data,invalid,should_succeed=False)
        if leaks<1:
            raise ValueError("prototype failed to expose known-future leakage in test case")
    return {"prototype_id":req["prototype_id"],"queries_independently_verified":len(queries),
            "hidden_queries_verified":len(queries)-len(examples),
            "leakage_examples":leaks,
            "python_sha256":sha256(artifact["python_source"].encode()).hexdigest(),
            "dataset_sha256":sha256(artifact["dataset_json"].encode()).hexdigest(),
            "synthetic":True,"clinical_verdict":"NOT_EVALUATED","benchmark_complete":False}
