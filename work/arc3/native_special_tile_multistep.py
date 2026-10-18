"""Predeclared multistep native LS20 visible-frame congruence challenge.

Three original distinct action histories reach the same *complete visible*
native frame at depth eight. This experiment asks whether equal suffix words
preserve full visible-frame equality at EACH later depth. Raw prior source is
SHA256 pinned and replayed. This never assumes hidden-state equality or F3.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .native_special_tile_successor import (
    PREFIXES, ACTIONS, BASELINE_FRAME, BASELINE_GLYPH
)
from .native_observation_bridge import frame_summary
from .native_geometry_unknown_edge_verify import position

PROTOCOL="AB_LS20_SPECIAL_TILE_MULTI_SUFFIX_V1"
SUFFIXES=(
    "12","21","34","43",
    "1212","2121","3434","4343","1234","4321",
    "121212","343434",
)
RETURN_SUFFIXES=("12","21","34","43")
PRIOR_SHA256={
    "frozen-successors.json":"484c129b5a56379344973261757b7e429ae68b738718a9edef1a7addadadf4ae",
    "native-successors.json":"8d188a70a936e183e745eb49d66e25514468763845c559c9a086c48e936579d0",
    "native-successors.npz":"0e9d311a127f525f531577ba449d299e2c31f95d26cdc9505d89a1286e180463",
    "independent-verdict.json":"ca39c9b7cc0b87557c00f1481cab112ab814294a1d63183003c5c5714f1c1196",
}

def sha(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def verify_source(root:Path)->dict:
    for filename,digest in PRIOR_SHA256.items():
        if sha(root/filename)!=digest:
            raise ValueError("independent source bytes no longer match provenance: "+filename)
    frozen=json.loads((root/"frozen-successors.json").read_text())
    native=json.loads((root/"native-successors.json").read_text())
    verdict=json.loads((root/"independent-verdict.json").read_text())
    if (frozen.get("kind")!="AB_SOURCE_FROZEN_SPECIAL_TILE_SUCCESSOR_V1" or
        native.get("kind")!="AB_OFFICIAL_NATIVE_SPECIAL_TILE_SUCCESSOR_CAPTURE_V1" or
        native.get("game")!="ls20" or
        verdict.get("visible_successor_equal_pairs")!=12 or
        verdict.get("five_pixel_cardinal_or_block_correct")!=12 or
        verdict.get("complete_trials")!=12 or
        len(frozen.get("frozen_trials",[]))!=12 or
        len(native.get("trials",[]))!=12):
        raise ValueError("earlier independent one-step native congruence unsupported")
    roots=set()
    with np.load(root/"native-successors.npz",allow_pickle=False) as frames:
        if set(frames.files)!={f"trial_{n:02d}" for n in range(12)}:
            raise ValueError("previous complete native pixel archive missing a trajectory")
        first_group={}
        for i,(registered,source) in enumerate(zip(
            frozen["frozen_trials"],native["trials"]
        )):
            word=PREFIXES[i//4]+ACTIONS[i%4]
            key=f"trial_{i:02d}"
            path=source.get("path")
            if (registered.get("word")!=word or source.get("key")!=key or
                path.get("word")!=word or path.get("completed") is not True or
                path.get("interruption") is not None or path.get("steps")!=len(word)):
                raise ValueError("previous source native word changed")
            snapshots=frames[key]
            if snapshots.shape!=(len(word)+1,64,64) or snapshots.dtype!=np.uint8:
                raise ValueError("invalid earlier native raw pixels")
            if len(path.get("states",[]))!=len(word)+1:
                raise ValueError("native source states missing")
            for t,image in enumerate(snapshots):
                meta=path["states"][t]
                if (meta.get("index")!=t or
                    meta.get("action")!=(None if t==0 else int(word[t-1])) or
                    meta.get("observation")!=frame_summary(image)):
                    raise ValueError("earlier source step not verified against raw pixel data")
            if (frame_summary(snapshots[8])["whole"]!=BASELINE_FRAME or
                position(snapshots[8])!=BASELINE_GLYPH or
                path["states"][8]["state"]!="GameState.NOT_FINISHED"):
                raise ValueError("original equal-frame source did not replay")
            action=ACTIONS[i%4]
            raw=snapshots[-1].tobytes()
            if action in first_group and first_group[action]!=raw:
                raise ValueError("previous one-step source already differs across histories")
            first_group[action]=raw
            roots.add(path["states"][0]["observation"]["whole"])
    if len(roots)!=1 or sorted(roots)!=native.get("root_hashes"):
        raise ValueError("original source root changed")
    return {"native_root_sha16":next(iter(roots)),
            "original_depth8_frame_sha16":BASELINE_FRAME,
            "independently_replayed_prior_native_paths":12,
            "independently_replayed_prior_one_action_groups":4}

def freeze(source:Path)->dict:
    prior=verify_source(source)
    if len(SUFFIXES)!=12 or len(set(SUFFIXES))!=12 or any(
        not 2<=len(w)<=6 or any(c not in ACTIONS for c in w)
        for w in SUFFIXES
    ):
        raise ValueError("invalid or duplicated frozen suffix words")
    trials=[{"id":f"{i:02d}_{j:02d}",
             "history":prefix,"suffix":suffix,"word":prefix+suffix,
             "native_steps_before_suffix":8,
             "source_full_frame_sha16":BASELINE_FRAME,
             "prediction_same_full_frame_for_equal_suffix":True}
            for j,suffix in enumerate(SUFFIXES)
            for i,prefix in enumerate(PREFIXES)]
    if len(trials)!=36 or len({r["word"] for r in trials})!=36:
        raise ValueError("full 36 native continuation holdouts not independent")
    return {
        "kind":"AB_SOURCE_FROZEN_SPECIAL_TILE_MULTI_SUFFIX_V1",
        "protocol":PROTOCOL,
        "prior_source_sha256":PRIOR_SHA256,
        "prior_replayed":prior,
        "histories":list(PREFIXES),
        "frozen_suffixes":list(SUFFIXES),
        "return_hypothesis_suffixes":list(RETURN_SUFFIXES),
        "registered_trials":trials,
        "native_trajectories":len(trials),
        "predicted_full_frame_unordered_pairs":3*sum(map(len,SUFFIXES)),
        "predicted_trace_pixel_masks":3*sum(map(len,SUFFIXES)),
        "predicted_return_to_original_glyph":3*len(RETURN_SUFFIXES),
        "prediction_visible_trace_at_depth_t":"exact rows 61:63, columns 13+t:55; t=9..14",
        "return_hypothesis":"for suffixes 12,21,34,43, glyph returns to row30,col19 but full frame differs from depth8",
        "previous_falsified_terrain_predicate_not_used":True,
        "same_visible_not_same_hidden_state":True,
        "no_F3_or_REA_correspondence":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=freeze(a.source)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_FROZEN_MULTISTEP_SPECIAL_TILE "+json.dumps({
        "trials":len(result["registered_trials"]),
        "suffixes":len(SUFFIXES),
        "raw_full_frame_pair_predictions":result["predicted_full_frame_unordered_pairs"],
        "trace_masks":result["predicted_trace_pixel_masks"],
        "native_actions":sum(len(t["word"]) for t in result["registered_trials"])
    },sort_keys=True))
if __name__=="__main__":
    main()
