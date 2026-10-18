"""Bounded source-owned GAME-WORKER-READY analysis, no new process runtime."""
import hashlib,json,os,sys

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)

def compute(data):
    if type(data) is not dict or set(data)!={"kind","parents","adapter","synthetic"}:
        raise ValueError("exact source-owned worker readiness required")
    if data["kind"]!="game-adapter-readiness/v1" or data["synthetic"] is not True:
        raise ValueError("not admitted readiness")
    parents=data["parents"]; adapter=data["adapter"]
    required={"game-w13-cp-joined-001":"GAME-W13-WORLDS",
              "game-native-verifier-joined-001":"GAME-NATIVE-VERIFIER",
              "live-game-temporal-001":"LIVE-GAME-TEMPORAL"}
    if type(parents) is not dict or set(parents)!=set(required):
        raise ValueError("parent native worker set differs")
    manifest={}
    for job,cp in required.items():
        parent=parents[job]
        if (type(parent) is not dict or set(parent)!={"worker_id","version_id","fingerprint",
                                                     "status","verifier","contract","evidence_digest"}
                or parent["status"]!="COMPLETE" or parent["contract"]!=cp
                or type(parent["fingerprint"]) is not str or len(parent["fingerprint"])!=64
                or type(parent["evidence_digest"]) is not str or len(parent["evidence_digest"])!=64):
            raise ValueError("parent not a source-owned, completed native handoff")
        manifest[job]={"worker_id":parent["worker_id"],
                       "version_id":parent["version_id"],
                       "fingerprint":parent["fingerprint"],
                       "evidence_digest":parent["evidence_digest"]}
    if (type(adapter) is not dict or set(adapter)!={"route","w13_worker","verifier_worker","exact_confirmation","wrong_confirmation_rejected"}
            or adapter["route"]!="controls.run_job"
            or adapter["w13_worker"]!="game-worlds-w13"
            or adapter["verifier_worker"]!="game-native-independent-verifier"
            or adapter["exact_confirmation"]!="game-w13-cp-joined-001"
            or adapter["wrong_confirmation_rejected"] is not True):
        raise ValueError("adapter route not source-verified")
    return {"kind":"game-adapter-ready-receipt/v1",
            "parent_manifest_digest":hashlib.sha256(canonical(manifest).encode()).hexdigest(),
            "worker_count":len(parents),
            "game_cp_contracts":["GAME-W13-WORLDS","GAME-NATIVE-VERIFIER"],
            "adapter_route":adapter["route"],
            "wrong_confirmation_rejected":True,
            "live_temporal_parent_present":True,
            "game_worker_edition":manifest["game-w13-cp-joined-001"]["fingerprint"],
            "witness_edition":manifest["game-native-verifier-joined-001"]["fingerprint"],
            "scope":"source-owned-synthetic-readiness-only"}

if __name__=="__main__":
    try:
        raw=sys.stdin.read(24001)
        if len(raw)>24000:raise ValueError("readiness envelope too large")
        print(json.dumps({"receipt":compute(json.loads(raw)),"pid":os.getpid()},sort_keys=True))
    except (KeyError,TypeError,ValueError) as e:
        print(str(e),file=sys.stderr)
        raise SystemExit(2)
