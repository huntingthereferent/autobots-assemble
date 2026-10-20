"""Preregister successor-equivalence test at the observed LS20 mixed terrain tile.

Three different *official native action histories* yielded exactly the same
raw 64x64 visible frame, at depth eight. Are their successors also equal when
the SAME native action is applied? This is a prospective visible-frame test,
NOT a claim of hidden-state identity, REA, F3 or generalized A/B equivalence.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .native_observation_bridge import frame_summary
from .native_geometry_unknown_edge_verify import position

PROTOCOL = "AB_LS20_SPECIAL_TILE_SUCCESSOR_EQUALITY_V1"
PREFIXES = ("11113323", "11113332", "33311413")
ACTIONS = "1234"
BASELINE_FRAME = "94380564157962f5deb754fc81783a1d"
BASELINE_GLYPH = (30,19)
# Independently replay the same original native failure in both earlier runs.
SOURCE_SHA256 = {
 "frozen-multi-edge.json": "c927b7f29d39a5a15bb2c3bb587155ed709aae6e7d30c594f0c478d7399eda7b",
 "native-multi-edge.json": "7025122684ce6aff64ffc6e3f73a450d2b0b640e7f51411bb113c4deab8b9991",
 "independent-verdict.json": "b22f258076713b4909e923ab05999c3ad6db37c1f908e316c1e5f5b4572f06a3",
 "native-multi-edge.npz": "88605dc6f7ab0dfa214e23f4ad9475281d0daa6ffc29f134686119c36706a58d",
}
FAILURE_INDICES = (38,41,63)

def source_hash(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def _replay(path:Path)->dict:
    for name,digest in SOURCE_SHA256.items():
        if source_hash(path/name)!=digest:
            raise ValueError("independent original native source identity changed: "+name)
    frozen=json.loads((path/"frozen-multi-edge.json").read_text())
    native=json.loads((path/"native-multi-edge.json").read_text())
    verdict=json.loads((path/"independent-verdict.json").read_text())
    if (frozen.get("kind")!="AB_NATIVE_MULTI_UNKNOWN_EDGE_FROZEN_V1" or
        native.get("kind")!="AB_REAL_NATIVE_MULTI_NEW_EDGE_SOURCE_V1" or
        native.get("game")!="ls20" or
        verdict.get("all_frozen_predictions_passed") is not False or
        len(verdict.get("counterexamples",[]))!=3 or
        verdict.get("total_trials")!=64 or
        len(native.get("native_trajectories",[]))!=64):
        raise ValueError("expected genuine independent falsification is absent")
    roots=set()
    reached=[]
    with np.load(path/"native-multi-edge.npz",allow_pickle=False) as arrays:
        if set(arrays.files)!={f"trial_{i:03d}" for i in range(64)}:
            raise ValueError("raw source incomplete")
        for index in FAILURE_INDICES:
            proposed=frozen["native_holdout_trials"][index]
            record=native["native_trajectories"][index]["native_path"]
            if (proposed["word"] not in PREFIXES or record.get("word")!=proposed["word"] or
                record.get("completed") is not True or
                record.get("interruption") is not None or
                record.get("steps")!=8 or len(record.get("states",[]))!=9):
                raise ValueError("prior native history not the verified eight-step prefix")
            frames=arrays[f"trial_{index:03d}"]
            if frames.shape!=(9,64,64) or frames.dtype!=np.uint8:
                raise ValueError("original native pixel source malformed")
            for step,frame in enumerate(frames):
                state=record["states"][step]
                if (state.get("index")!=step or
                    state.get("action")!=(None if step==0 else int(proposed["word"][step-1])) or
                    state.get("observation")!=frame_summary(frame)):
                    raise ValueError("original native raw frame fails independent replay")
            root=record["states"][0]["observation"]["whole"]
            roots.add(root)
            last=frames[-1]
            if (frame_summary(last)["whole"]!=BASELINE_FRAME or
                position(last)!=BASELINE_GLYPH or
                record["states"][-1]["levels_completed"]!=0 or
                record["states"][-1]["state"]!="GameState.NOT_FINISHED"):
                raise ValueError("the three histories do not reach the same witnessed source state")
            reached.append({"word":proposed["word"],"last_whole":BASELINE_FRAME,
                            "glyph":list(BASELINE_GLYPH),
                            "last_native_state":record["states"][-1]["state"]})
        if len(roots)!=1:
            raise ValueError("native original roots are unequal")
        first=arrays[f"trial_{FAILURE_INDICES[0]:03d}"][-1]
        if any(not np.array_equal(
            first, arrays[f"trial_{i:03d}"][-1]
        ) for i in FAILURE_INDICES[1:]):
            raise ValueError("the three claimed equal source frames are NOT equal")
    if tuple(r["word"] for r in reached)!=PREFIXES:
        raise ValueError("prior failure order not independently verified")
    return {"histories":reached,"original_root_sha16":next(iter(roots))}

def freeze(first:Path,second:Path)->dict:
    initial=_replay(first)
    repeat=_replay(second)
    if initial!=repeat:
        raise ValueError("independent native repeats did not agree")
    trials=[{"trial_id":f"{i}_{action}",
             "prefix":prefix,"action":action,"word":prefix+action,
             "source_last_sha16":BASELINE_FRAME,
             "source_last_position":list(BASELINE_GLYPH)}
            for i,prefix in enumerate(PREFIXES) for action in ACTIONS]
    if len(trials)!=12 or len({t["word"] for t in trials})!=12:
        raise AssertionError("preregistered native successor set incomplete")
    return {
        "kind":"AB_SOURCE_FROZEN_SPECIAL_TILE_SUCCESSOR_V1",
        "protocol":PROTOCOL,
        "original_and_repeat_sha256":SOURCE_SHA256,
        "prior_verified_same_full_visible_frame_sha16":BASELINE_FRAME,
        "prior_verified_glyph_position":list(BASELINE_GLYPH),
        "prior_native_root_sha16":initial["original_root_sha16"],
        "three_independently_reached_histories":initial["histories"],
        "native_actions":list(ACTIONS),
        "frozen_trials":trials,
        "frozen_hypotheses":[
          "For each action, all 3 distinct prefixes with the same raw visible frame have the same complete native successor visible frame.",
          "For every observed successor, native color-12 glyph displacement is either zero or exactly five pixels in that action direction.",
        ],
        "hypothesis_1_expected_equal_pairs_per_action":3,
        "hypothesis_1_expected_equal_pairs_total":12,
        "hypothesis_2_expected_transition_count":12,
        "successor_positions_NOT_PREDECLARED":True,
        "no_native_hidden_state_identity":True,
        "not_an_F3_or_REA_mapping":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--repeat",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=freeze(a.original,a.repeat)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_FROZEN_SPECIAL_TILE "+json.dumps({
      "source_frame":BASELINE_FRAME,
      "histories":len(PREFIXES),"distinct_successor_words":len(result["frozen_trials"]),
      "original_runs_verified":2},sort_keys=True))
if __name__=="__main__":main()
