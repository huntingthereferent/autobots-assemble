"""Independent native raw-pixel verifier; preserve actual counterexamples."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .native_multi_edge_composition import PROTOCOL
from .native_observation_bridge import frame_summary
from .native_geometry_unknown_edge_verify import position

def verify(frozen:dict,native:dict,raw)->dict:
    claims=frozen.get("native_holdout_trials")
    received=native.get("native_trajectories")
    if (frozen.get("kind")!="AB_NATIVE_MULTI_UNKNOWN_EDGE_FROZEN_V1" or
        frozen.get("protocol")!=PROTOCOL or
        native.get("kind")!="AB_REAL_NATIVE_MULTI_NEW_EDGE_SOURCE_V1" or
        native.get("protocol")!=PROTOCOL or native.get("game")!="ls20" or
        not isinstance(claims,list) or len(claims)!=64 or
        not isinstance(received,list) or len(received)!=64 or
        set(raw.files)!={f"trial_{i:03d}" for i in range(64)}):
        raise ValueError("native source or originally frozen prediction incomplete")
    roots=set()
    outcomes=[]
    failures=[]
    interruptions=[]
    class_results=Counter()
    novel_edges_tested=0
    for index,(prediction,observation) in enumerate(zip(claims,received)):
        key=f"trial_{index:03d}"
        path=observation.get("native_path")
        if (observation.get("trial_key")!=key or
            observation.get("word")!=prediction["word"] or
            observation.get("kind")!=prediction["kind"] or
            not isinstance(path,dict) or path.get("word")!=prediction["word"]):
            raise ValueError("native trajectory/prediction identity mismatch")
        frames=raw[key]
        states=path.get("states")
        if (not isinstance(states,list) or frames.ndim!=3 or
            frames.dtype!=np.uint8 or frames.shape[1:]!=(64,64) or
            len(frames)!=len(states)):
            raise ValueError("missing original raw 64x64 native frames")
        actual=[]
        for depth,(metadata,image) in enumerate(zip(states,frames)):
            if (metadata.get("index")!=depth or
                metadata.get("action")!=(
                    None if depth==0 else int(prediction["word"][depth-1])
                ) or metadata.get("observation")!=frame_summary(image)):
                raise ValueError("actual native frame hash or action provenance mismatch")
            actual.append(list(position(image)))
        if not actual:
            raise ValueError("missing native initial observation")
        roots.add(states[0]["observation"]["whole"])
        if (path.get("completed") is not True or
            path.get("interruption") is not None or
            path.get("steps")!=len(prediction["word"]) or
            len(actual)!=len(prediction["word"])+1):
            interruptions.append({"trial":key,"reason":path.get("interruption"),
                                  "observed_steps":path.get("steps")})
            outcomes.append({"trial":key,"status":"INTERRUPTED","positions":actual})
            continue
        prefix=prediction["known_prefix_positions"]
        tail=prediction["predicted_new_positions"]
        if (len(actual)!=len(prefix)+len(tail) or
            len(tail) not in (2,3)):
            raise ValueError("expected source-known and newly predicted positions incomplete")
        known_ok=actual[:len(prefix)]==prefix
        new_actual=actual[len(prefix):]
        matches=[pred==value for pred,value in zip(tail,new_actual)]
        success=known_ok and all(matches)
        novel_edges_tested+=len(matches)
        if not success:
            failures.append({"trial":key,"word":prediction["word"],
                             "known_prefix_reproduced":known_ok,
                             "predicted_new_positions":tail,
                             "actual_new_positions":new_actual,
                             "per_edge_correct":matches})
        class_results[prediction["kind"]+("_pass" if success else "_fail")]+=1
        outcomes.append({"trial":key,"kind":prediction["kind"],
                         "word":prediction["word"],
                         "status":"MATCH" if success else "COUNTEREXAMPLE",
                         "known_prefix_reproduced":known_ok,
                         "predicted_new_positions":tail,
                         "actual_new_positions":new_actual,
                         "per_new_edge_match":matches,
                         "last_native_frame_sha16":states[-1]["observation"]["whole"]})
    if (len(roots)!=1 or next(iter(roots))!=frozen.get("common_native_root_sha16") or
        sorted(roots)!=native.get("all_roots") or
        native.get("native_actions")!=sum(
            record["native_path"]["steps"] for record in received
        )):
        raise ValueError("native root or action count changed")
    success=len(failures)==0 and len(interruptions)==0 and (
        class_results.get("two-new-edges_pass",0)==52 and
        class_results.get("three-new-edges_pass",0)==12
    )
    return {"kind":"AB_NATIVE_MULTI_NEW_EDGE_COMPOSITION_VERDICT_V1",
            "source_root_sha16":next(iter(roots)),
            "total_trials":len(claims),"trials_with_complete_native_outcome":len(claims)-len(interruptions),
            "observed_native_actions":native["native_actions"],
            "attempted_novel_action_edges":novel_edges_tested,
            "per_class":dict(class_results),
            "all_frozen_predictions_passed":success,
            "counterexamples":failures,"interrupted_trials":interruptions,
            "per_trial":outcomes,
            "not_F3_or_hidden_state_evidence":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    with np.load(a.raw,allow_pickle=False) as arrays:
        result=verify(json.loads(a.frozen.read_text()),
                      json.loads(a.native.read_text()),arrays)
    result["source_sha256"]={
        "prediction":sha256(a.frozen.read_bytes()).hexdigest(),
        "real_native_manifest":sha256(a.native.read_bytes()).hexdigest(),
        "actual_raw_frames":sha256(a.raw.read_bytes()).hexdigest()
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_NATIVE_MULTI_EDGE_VERDICT "+json.dumps({
        "passed":result["all_frozen_predictions_passed"],
        "trials":result["total_trials"],
        "actions":result["observed_native_actions"],
        "novel_edge_checks":result["attempted_novel_action_edges"],
        "classes":result["per_class"],
        "counterexamples":len(result["counterexamples"]),
        "interrupted":len(result["interrupted_trials"])},sort_keys=True))
    if not result["all_frozen_predictions_passed"]:
        raise SystemExit("Native A/B source-geometry composition falsified or interrupted; raw evidence retained")

if __name__=="__main__":
    main()
