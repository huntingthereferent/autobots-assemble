"""Independent raw-pixel test for geometry predictions on previously unobserved edges."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .native_geometry_unknown_edge import PROTOCOL,WORDS
from .native_observation_bridge import frame_summary

def position(frame:np.ndarray)->tuple[int,int]:
    if frame.shape!=(64,64) or frame.dtype!=np.uint8:
        raise ValueError("native frame dimensions invalid")
    c=np.argwhere(frame==12)
    if c.shape!=(10,2):raise ValueError("native glyph missing or malformed")
    y,x=int(c[:,0].min()),int(c[:,1].min())
    if not np.all(frame[y:y+2,x:x+5]==12) or not np.array_equal(
        frame==12,np.pad(np.ones((2,5),dtype=bool),
                         ((y,64-y-2),(x,64-x-5)))):
        raise ValueError("native glyph not the expected full 2x5 raw block")
    return y,x

def check(frozen:dict,native:dict,raw)->dict:
    if (frozen.get("protocol")!=PROTOCOL or
        frozen.get("kind")!="NATIVE_AB_GEOMETRY_SOURCE_FROZEN" or
        frozen.get("frozen_holdout_words")!=list(WORDS) or
        native.get("kind")!="AB_LS20_UNKNOWN_GEOMETRY_RAW_FRAMES_V1" or
        native.get("protocol")!=PROTOCOL or native.get("game")!="ls20" or
        native.get("words")!=list(WORDS) or
        len(frozen.get("unseen_holdout_edge_predictions",[]))!=len(WORDS) or
        len(native.get("trajectories",[]))!=len(WORDS) or
        set(raw.files)!=set(WORDS)):
        raise ValueError("native trial/prediction missing or different source")
    roots=set()
    rows=[]
    correct=0
    prefix_correct=0
    moved_correct=0
    blocked_correct=0
    for word,forecast,trajectory in zip(
        WORDS,frozen["unseen_holdout_edge_predictions"],native["trajectories"]
    ):
        if (forecast["word"]!=word or trajectory.get("word")!=word or
            trajectory.get("steps")!=len(word) or
            trajectory.get("completed") is not True or
            trajectory.get("interruption") is not None or
            len(trajectory.get("states",[]))!=len(word)+1):
            raise ValueError("unverified original native trajectory")
        frames=raw[word]
        if frames.shape!=(len(word)+1,64,64) or frames.dtype!=np.uint8:
            raise ValueError("original native pixel frames missing")
        observed=[]
        for i,frame in enumerate(frames):
            original=trajectory["states"][i]
            if (original["index"]!=i or
                original["action"]!=(None if i==0 else int(word[i-1])) or
                original["observation"]!=frame_summary(frame)):
                raise ValueError("original native step disagrees with full raw pixels")
            observed.append(list(position(frame)))
        roots.add(trajectory["states"][0]["observation"]["whole"])
        predicted_known=forecast["known_prefix_positions"]
        if len(predicted_known)!=len(word) or observed[:-1]!=predicted_known:
            raise ValueError("previously verified prefix path unexpectedly changed")
        prefix_correct+=len(predicted_known)
        matched=observed[-1]==forecast["predicted_next_position"]
        correct+=matched
        if matched and forecast["predicted_moved"]:moved_correct+=1
        if matched and not forecast["predicted_moved"]:blocked_correct+=1
        rows.append({"word":word,
            "unobserved_edge":[forecast["unobserved_source_position"],word[-1]],
            "predicted_destination":forecast["predicted_next_position"],
            "actual_destination":observed[-1],
            "predicted_moved":forecast["predicted_moved"],
            "exact_prediction":matched,
            "actual_full_frame_sha16":trajectory["states"][-1]["observation"]["whole"]})
    if len(roots)!=1 or native.get("native_actions")!=sum(map(len,WORDS)):
        raise ValueError("roots or source action counts mismatch")
    return {"kind":"AB_NATIVE_FIRST_UNKNOWN_EDGE_GEOMETRY_VERDICT_V1",
        "predeclared_unknown_edges":len(WORDS),
        "exact_unknown_edge_predictions":correct,
        "predicted_moving_edges":frozen["predicted_moved"],
        "predicted_blocked_edges":frozen["predicted_blocked"],
        "exact_moving_edges":moved_correct,
        "exact_blocked_edges":blocked_correct,
        "verified_known_prefix_positions":prefix_correct,
        "new_native_actions":sum(map(len,WORDS)),
        "rows":rows,"all_unknown_edge_predictions_passed":correct==len(WORDS),
        "hidden_state_or_F3_proven":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    with np.load(a.raw,allow_pickle=False) as frames:
        verdict=check(json.loads(a.frozen.read_text()),
                      json.loads(a.native.read_text()),frames)
    verdict["sha256"]={"frozen":sha256(a.frozen.read_bytes()).hexdigest(),
                       "native":sha256(a.native.read_bytes()).hexdigest(),
                       "raw":sha256(a.raw.read_bytes()).hexdigest()}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(verdict,indent=2)+"\n")
    print("AB_NATIVE_UNKNOWN_GEOMETRY_VERDICT "+json.dumps({
        "correct":verdict["exact_unknown_edge_predictions"],
        "tested":verdict["predeclared_unknown_edges"],
        "moving":verdict["exact_moving_edges"],
        "blocked":verdict["exact_blocked_edges"]},sort_keys=True))
    if not verdict["all_unknown_edge_predictions_passed"]:
        raise SystemExit("The original source-geometry rule was falsified; raw verdict preserved")

if __name__=="__main__":main()
