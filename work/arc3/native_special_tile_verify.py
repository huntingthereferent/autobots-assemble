"""Raw-pixel verifier of visible-congruence and 5px envelope at a new tile.

Both hypotheses are independent from prior terrain-passability model, which
remains falsified and is never imported as an oracle.
"""
from __future__ import annotations
import argparse
from itertools import combinations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .native_special_tile_successor import PROTOCOL,PREFIXES,ACTIONS,BASELINE_FRAME,BASELINE_GLYPH
from .native_observation_bridge import frame_summary
from .native_geometry_unknown_edge_verify import position

DELTA={"1":(-5,0),"2":(5,0),"3":(0,-5),"4":(0,5)}

def examine(frozen:dict,native:dict,raw)->dict:
    if (frozen.get("kind")!="AB_SOURCE_FROZEN_SPECIAL_TILE_SUCCESSOR_V1" or
        frozen.get("protocol")!=PROTOCOL or
        frozen.get("prior_verified_same_full_visible_frame_sha16")!=BASELINE_FRAME or
        frozen.get("prior_verified_glyph_position")!=list(BASELINE_GLYPH) or
        native.get("kind")!="AB_OFFICIAL_NATIVE_SPECIAL_TILE_SUCCESSOR_CAPTURE_V1" or
        native.get("protocol")!=PROTOCOL or native.get("game")!="ls20" or
        len(frozen.get("frozen_trials",[]))!=12 or
        len(native.get("trials",[]))!=12 or
        set(raw.files)!={f"trial_{i:02d}" for i in range(12)}):
        raise ValueError("independent native source or preregistration missing")
    observed=[]
    roots=set()
    interruptions=[]
    for i,(registered,source) in enumerate(zip(frozen["frozen_trials"],native["trials"])):
        key=f"trial_{i:02d}"
        word=registered["word"]
        path=source.get("path")
        if (source.get("key")!=key or source.get("trial_id")!=registered["trial_id"] or
            word!=PREFIXES[i//4]+ACTIONS[i%4] or
            not isinstance(path,dict) or path.get("word")!=word):
            raise ValueError("source trial order/identity changed")
        frames=raw[key]
        states=path.get("states")
        if (not isinstance(states,list) or frames.ndim!=3 or frames.dtype!=np.uint8 or
            frames.shape[1:]!=(64,64) or len(states)!=len(frames)):
            raise ValueError("incomplete raw native frame source")
        for depth,(state,frame) in enumerate(zip(states,frames)):
            if (state.get("index")!=depth or
                state.get("action")!=(None if depth==0 else int(word[depth-1])) or
                state.get("observation")!=frame_summary(frame)):
                raise ValueError("source raw frame not witnessed by original metadata")
        roots.add(states[0]["observation"]["whole"])
        if (path.get("completed") is not True or
            path.get("interruption") is not None or path.get("steps")!=len(word) or
            len(states)!=len(word)+1):
            interruptions.append({"key":key,"word":word,
                                  "reason":path.get("interruption"),
                                  "steps":path.get("steps")})
            observed.append({"key":key,"word":word,"action":word[-1],
                             "status":"INTERRUPTED"})
            continue
        prefix_frame=frames[len(word)-1]
        if (frame_summary(prefix_frame)["whole"]!=BASELINE_FRAME or
            position(prefix_frame)!=BASELINE_GLYPH or
            path["states"][len(word)-1]["state"]!="GameState.NOT_FINISHED" or
            path["states"][len(word)-1]["levels_completed"]!=0):
            raise ValueError("the previously verified same source frame did not replay")
        successor=frames[-1]
        actual_position=position(successor)
        dy,dx=DELTA[word[-1]]
        admitted_moves=(BASELINE_GLYPH, (BASELINE_GLYPH[0]+dy,BASELINE_GLYPH[1]+dx))
        envelope=actual_position in admitted_moves
        observed.append({
            "key":key,"word":word,"action":word[-1],"status":"COMPLETE",
            "prefix_raw_sha16":BASELINE_FRAME,
            "after_raw_sha16":frame_summary(successor)["whole"],
            "raw_full_frame_hex_sha256":sha256(successor.tobytes()).hexdigest(),
            "native_state":states[-1]["state"],
            "native_level":states[-1]["levels_completed"],
            "glyph_after":list(actual_position),
            "five_pixel_cardinal_or_block":envelope,
            "color_11_trace_pixels_after":int(np.count_nonzero(successor==11)),
            "special_tile_remaining_colors":{str(x):int(np.count_nonzero(successor==x))
                                              for x in (0,1,3,5,9,12)}
        })
    if (len(roots)!=1 or sorted(roots)!=native.get("root_hashes") or
        next(iter(roots))!=frozen.get("prior_native_root_sha16") or
        native.get("native_action_count")!=sum(row["path"]["steps"] for row in native["trials"])):
        raise ValueError("fresh source reset or action totals inconsistent")
    comparisons=[]
    pairs_agree=0
    for action in ACTIONS:
        group=[r for r in observed if r["action"]==action]
        if len(group)!=3:
            raise AssertionError("incomplete action group")
        for left,right in combinations(group,2):
            equal=(left.get("status")=="COMPLETE" and right.get("status")=="COMPLETE"
                   and left["raw_full_frame_hex_sha256"]==right["raw_full_frame_hex_sha256"])
            if equal:pairs_agree+=1
            comparisons.append({
                "action":action,"prefixes":[left["word"][:-1],right["word"][:-1]],
                "exact_full_native_successor_equal":equal,
                "first_frame_sha16":left.get("after_raw_sha16"),
                "second_frame_sha16":right.get("after_raw_sha16"),
            })
    full=[x for x in observed if x["status"]=="COMPLETE"]
    envelope_pass=sum(x["five_pixel_cardinal_or_block"] for x in full)
    return {
        "kind":"AB_NATIVE_SPECIAL_TILE_SUCCESSOR_VERDICT_V1",
        "source_frame_sha16":BASELINE_FRAME,
        "original_native_histories":list(PREFIXES),
        "native_actions":native["native_action_count"],
        "complete_trials":len(full),"interrupted":interruptions,
        "visible_successor_equal_pairs":pairs_agree,
        "visible_successor_total_pairs":len(comparisons),
        "visible_successor_congruence_passed":pairs_agree==12 and not interruptions,
        "five_pixel_cardinal_or_block_correct":envelope_pass,
        "five_pixel_cardinal_or_block_tested":len(full),
        "movement_envelope_passed":envelope_pass==12 and not interruptions,
        "trials":observed,"pairwise_exact_full_frame_comparisons":comparisons,
        "source_hidden_state_identity_claimed":False,
        "native_F3_or_REA_mapping":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    with np.load(a.raw,allow_pickle=False) as frames:
        report=examine(json.loads(a.frozen.read_text()),
                       json.loads(a.native.read_text()),frames)
    report["source_sha256"]={
        "frozen_prediction":sha256(a.frozen.read_bytes()).hexdigest(),
        "native_manifest":sha256(a.native.read_bytes()).hexdigest(),
        "all_raw_native_frames":sha256(a.raw.read_bytes()).hexdigest()}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    print("AB_SPECIAL_TILE_VERDICT "+json.dumps({
        "whole_frame_equal_pairs":report["visible_successor_equal_pairs"],
        "pair_count":report["visible_successor_total_pairs"],
        "envelope_correct":report["five_pixel_cardinal_or_block_correct"],
        "trials":report["complete_trials"],
        "interruptions":len(report["interrupted"])},sort_keys=True))
    if not report["visible_successor_congruence_passed"] or not report["movement_envelope_passed"]:
        raise SystemExit("Predeclared native visible-congruence or displacement envelope falsified; original raw record retained")
if __name__=="__main__":main()
