"""Bounded source-owned synthetic temporal-vs-static benchmark.

Works only on copied inputs from already witnessed Phase 2 tests.
The separate host verifier must execute the ORIGINAL emitted Python program
and reconstruct answers against source observations before admitting evidence.
"""
import hashlib,json,os,sys
from datetime import date

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)

def compute(x):
    if type(x) is not dict or set(x)!={"kind","synthetic","queries","observations",
                                      "prototype_sha256","query_history_sha256"}:
        raise ValueError("exact synthetic benchmark source input required")
    if x["kind"]!="native-synthetic-temporal-static-benchmark/v1" or x["synthetic"] is not True:
        raise ValueError("benchmark cannot accept non-synthetic input")
    if type(x["observations"]) is not list or not 2<=len(x["observations"])<=100:
        raise ValueError("original observations missing")
    if type(x["queries"]) is not list or not 20<=len(x["queries"])<=96:
        raise ValueError("bounded benchmark grid required")
    if not all(type(x[k]) is str and len(x[k])==64 and
               all(c in "0123456789abcdef" for c in x[k])
               for k in ("prototype_sha256","query_history_sha256")):
        raise ValueError("pinned parent hashes missing")
    ids=[o["id"] for o in x["observations"]]
    if len(ids)!=len(set(ids)):
        raise ValueError("duplicate observation identities")
    if any(type(o) is not dict or
           any(type(o.get(k)) is not str for k in ("id","known_at","valid_from","valid_to"))
           for o in x["observations"]):
        raise ValueError("invalid source observations")
    seen=set()
    cases=[]
    for q in x["queries"]:
        if type(q) is not dict or set(q)!={"known_at","target_at"}:
            raise ValueError("invalid query")
        for k in ("known_at","target_at"):
            v=q[k]
            if type(v) is not str or len(v)!=10 or date.fromisoformat(v).isoformat()!=v:
                raise ValueError("noncanonical date")
        pair=(q["known_at"],q["target_at"])
        if pair in seen:
            raise ValueError("duplicate benchmark query")
        seen.add(pair)
        eligible=sorted(o["id"] for o in x["observations"]
                        if o["valid_from"]<=q["target_at"]<o["valid_to"])
        temporal=sorted(o["id"] for o in x["observations"]
                        if o["valid_from"]<=q["target_at"]<o["valid_to"]
                        and o["known_at"]<=q["known_at"])
        leakage=sorted(set(eligible)-set(temporal))
        cases.append({"request":q,"temporal_ids":temporal,
                      "static_snapshot_ids":eligible,"future_leakage_ids":leakage})
    leak_cases=sum(bool(c["future_leakage_ids"]) for c in cases)
    if leak_cases<1 or leak_cases==len(cases):
        raise ValueError("benchmark must show both leaking and non-leaking cases")
    return {"kind":"native-synthetic-temporal-static-benchmark-result/v1",
            "query_history_sha256":x["query_history_sha256"],
            "prototype_sha256":x["prototype_sha256"],
            "grid_sha256":hashlib.sha256(canonical(x["queries"]).encode()).hexdigest(),
            "query_count":len(cases),"static_future_leakage_cases":leak_cases,
            "static_future_leakage_ids_total":sum(len(c["future_leakage_ids"]) for c in cases),
            "temporal_leakage_ids_total":0,"cases":cases,
            "synthetic_only":True,"clinical_verdict":"NOT_EVALUATED",
            "official_nih_submission":False}

if __name__=="__main__":
    try:
        raw=sys.stdin.read(180001)
        if len(raw)>180000:raise ValueError("oversize source inputs")
        print(json.dumps({"pid":os.getpid(),"report":compute(json.loads(raw))},sort_keys=True))
    except (ValueError,TypeError,KeyError) as e:
        print(str(e),file=sys.stderr)
        raise SystemExit(2)
