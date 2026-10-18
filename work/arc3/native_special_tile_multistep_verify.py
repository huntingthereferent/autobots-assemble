"""Independent raw native verifier for full-frame congruence at every suffix depth.

Preserves the original 3/5 terrain falsification. Does not infer hidden
state, does not change frozen source predictions after native observation.
"""
from __future__ import annotations
import argparse
from itertools import combinations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .native_special_tile_multistep import PROTOCOL,PREFIXES,SUFFIXES,RETURN_SUFFIXES
from .native_special_tile_successor import BASELINE_FRAME,BASELINE_GLYPH
from .native_observation_bridge import frame_summary
from .native_geometry_unknown_edge_verify import position

def predicted_trace_mask(depth:int)->np.ndarray:
    if type(depth) is not int or not 9<=depth<=14:
        raise ValueError("trace forecast only declared at native step depths 9..14")
    m=np.zeros((64,64),dtype=bool)
    m[61:63,13+depth:55]=True
    return m

def evaluate(frozen:dict,native:dict,raw)->dict:
    trials=frozen.get("registered_trials")
    sources=native.get("native_paths")
    if (frozen.get("kind")!="AB_SOURCE_FROZEN_SPECIAL_TILE_MULTI_SUFFIX_V1" or
        frozen.get("protocol")!=PROTOCOL or
        native.get("kind")!="AB_REAL_NATIVE_SPECIAL_TILE_MULTISTEP_RAW_V1" or
        native.get("protocol")!=PROTOCOL or native.get("game")!="ls20" or
        frozen.get("frozen_suffixes")!=list(SUFFIXES) or
        frozen.get("histories")!=list(PREFIXES) or
        frozen.get("return_hypothesis_suffixes")!=list(RETURN_SUFFIXES) or
        not isinstance(trials,list) or len(trials)!=36 or
        not isinstance(sources,list) or len(sources)!=36 or
        set(raw.files)!={f"trial_{i:02d}" for i in range(36)}):
        raise ValueError("missing preregistered or actual native source data")
    roots=set()
    observations={}
    reports=[]
    failures=[]
    interrupted=[]
    traces=trace_matches=0
    returns=return_matches=0
    for i,(trial,source) in enumerate(zip(trials,sources)):
        key=f"trial_{i:02d}"
        prefix=PREFIXES[i%3]
        suffix=SUFFIXES[i//3]
        word=prefix+suffix
        path=source.get("native_path")
        if (trial.get("word")!=word or trial.get("history")!=prefix or
            trial.get("suffix")!=suffix or
            source.get("key")!=key or source.get("trial_id")!=trial.get("id") or
            not isinstance(path,dict) or path.get("word")!=word):
            raise ValueError("native source path identity does not match frozen protocol")
        images=raw[key]
        states=path.get("states")
        if (not isinstance(states,list) or images.ndim!=3 or
            images.dtype!=np.uint8 or images.shape[1:]!=(64,64) or
            len(images)!=len(states)):
            raise ValueError("actual original native frame source incomplete")
        for depth,(meta,image) in enumerate(zip(states,images)):
            if (meta.get("index")!=depth or
                meta.get("action")!=(None if depth==0 else int(word[depth-1])) or
                meta.get("observation")!=frame_summary(image)):
                raise ValueError("independently verified native raw frame or action differs")
        if not len(states):
            raise ValueError("source lacked native root")
        roots.add(states[0]["observation"]["whole"])
        if (path.get("completed") is not True or
            path.get("interruption") is not None or
            path.get("steps")!=len(word) or
            len(states)!=len(word)+1):
            interrupted.append({"word":word,"reason":path.get("interruption"),
                                "completed_steps":path.get("steps")})
            continue
        frame8=images[8]
        if (frame_summary(frame8)["whole"]!=BASELINE_FRAME or
            position(frame8)!=BASELINE_GLYPH or
            states[8]["levels_completed"]!=0 or
            states[8]["state"]!="GameState.NOT_FINISHED"):
            raise ValueError("genuine common native frame did not replay on a new trial")
        after=images[9:].copy()
        observations[(suffix,prefix)]=after
        report={"word":word,"prefix":prefix,"suffix":suffix,
                "baseline_frame":BASELINE_FRAME,
                "native_glyph_positions_after":[list(position(frame)) for frame in after],
                "raw_sha16_per_step":[frame_summary(frame)["whole"] for frame in after],
                "native_states_after":[s["state"] for s in states[9:]],
                "native_levels_after":[s["levels_completed"] for s in states[9:]]}
        for offset,frame in enumerate(after,1):
            t=8+offset
            correct=bool(np.array_equal(frame==11,predicted_trace_mask(t)))
            traces+=1
            trace_matches+=int(correct)
            if not correct:
                failures.append({"kind":"TRACE_CLOCK_COUNTEREXAMPLE","word":word,
                                 "step":t,"expected":int(np.count_nonzero(predicted_trace_mask(t))),
                                 "actual":int(np.count_nonzero(frame==11))})
        if suffix in RETURN_SUFFIXES:
            returns+=1
            returned=position(after[-1])==BASELINE_GLYPH
            advanced=not np.array_equal(after[-1],frame8)
            if returned and advanced:return_matches+=1
            else:failures.append({"kind":"EXIT_RETURN_COUNTEREXAMPLE","word":word,
                                  "returned_to_original_glyph":returned,
                                  "whole_frame_changed_with_time":advanced})
            report["returned_to_original_glyph"]=returned
            report["whole_frame_changed_with_time"]=advanced
        reports.append(report)
    if (len(roots)!=1 or sorted(roots)!=native.get("native_visible_initial_root_hashes") or
        next(iter(roots))!=frozen.get("prior_replayed",{}).get("native_root_sha16") or
        native.get("native_actions")!=sum(s["native_path"]["steps"] for s in sources)):
        raise ValueError("different native origin or inconsistent action counts")
    pairs=equal_pairs=0
    for suffix in SUFFIXES:
        for p1,p2 in combinations(PREFIXES,2):
            key1,key2=(suffix,p1),(suffix,p2)
            if key1 not in observations or key2 not in observations:
                failures.append({"kind":"MISSING_HISTORY_PAIR","suffix":suffix,
                                 "histories":[p1,p2]})
                continue
            arr1,arr2=observations[key1],observations[key2]
            for step,(a,b) in enumerate(zip(arr1,arr2),1):
                pairs+=1
                same=bool(np.array_equal(a,b))
                equal_pairs+=int(same)
                if not same:
                    failures.append({"kind":"VISIBLE_SUCCESSOR_COUNTEREXAMPLE",
                                     "suffix":suffix,
                                     "histories":[p1,p2],
                                     "native_depth":8+step,
                                     "first_sha16":frame_summary(a)["whole"],
                                     "second_sha16":frame_summary(b)["whole"]})
    checks={"full_frame_equal":equal_pairs==frozen["predicted_full_frame_unordered_pairs"],
            "trace_clock":trace_matches==frozen["predicted_trace_pixel_masks"],
            "exit_return":return_matches==frozen["predicted_return_to_original_glyph"]}
    complete=not interrupted and all(checks.values()) and not failures
    return {"kind":"AB_LS20_SPECIAL_TILE_MULTISTEP_INDEPENDENT_VERDICT_V1",
        "all_hypotheses_passed":complete,
        "native_actions":native["native_actions"],
        "completed_native_trajectories":len(observations),
        "full_frame_equal_pairs":equal_pairs,"full_frame_pairs_checked":pairs,
        "trace_masks_exact":trace_matches,"trace_masks_checked":traces,
        "exit_return_with_advanced_visible_clock":return_matches,
        "exit_return_trials_checked":returns,
        "hypothesis_results":checks,
        "counterexamples":failures,"interruptions":interrupted,
        "per_trial":reports,
        "native_hidden_state_identity_not_proven":True,
        "original_terrain_passability_hypothesis_remains_falsified":True}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    with np.load(a.raw,allow_pickle=False) as source:
        result=evaluate(json.loads(a.frozen.read_text()),
                        json.loads(a.native.read_text()),source)
    result["source_sha256"]={
        "frozen_forecast":sha256(a.frozen.read_bytes()).hexdigest(),
        "original_native_manifest":sha256(a.native.read_bytes()).hexdigest(),
        "all_original_raw_frames":sha256(a.raw.read_bytes()).hexdigest()}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_NATIVE_SPECIAL_TILE_MULTISTEP_VERDICT "+json.dumps({
        "pass":result["all_hypotheses_passed"],
        "trajectories":result["completed_native_trajectories"],
        "actions":result["native_actions"],
        "full_frame_equal_pairs":result["full_frame_equal_pairs"],
        "full_frame_checked":result["full_frame_pairs_checked"],
        "exact_trace_masks":result["trace_masks_exact"],
        "trace_masks_checked":result["trace_masks_checked"],
        "return_and_clock":result["exit_return_with_advanced_visible_clock"],
        "counterexamples":len(result["counterexamples"]),
        "interruptions":len(result["interruptions"])
    },sort_keys=True))
    if not result["all_hypotheses_passed"]:
        raise SystemExit("Frozen native A/B multistep visible hypotheses falsified; raw evidence retained")
if __name__=="__main__":main()
