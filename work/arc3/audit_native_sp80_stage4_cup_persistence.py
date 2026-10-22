"""Authenticate and audit exact cup persistence through returned original SDK ACTION5 frames.

Reads archived source JSON/NPZ, not a locally simulated puzzle. Explicitly
separates intermediate source cup fills from final returned SDK frame and
official levels_completed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
from .native_sp80_multi_select import parse_plan

CUPS={
    "lateral":(5,35,10,43),
    "top_left":(17,5,25,10),
    "top_middle":(35,5,43,10),
    "top_right":(47,5,55,10),
}
EXPECTED=("lower_original","lower_up1","lower_down1","lower_left1","lower_right1")

def inspect(record,data):
    condition=record["condition"];witness=record["witness"]
    word=record["original_source_word"]
    n=len(parse_plan(word))
    root=data[condition+"_"+witness+"_entry3_34"][-1]
    frames=data[condition+"_"+witness+"_stage4_"+str(n)]
    if root.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Actual original SDK 64x64 frames required")
    filled={}
    for name,(x0,y0,x1,y1) in CUPS.items():
        initial=root[y0:y1+1,x0:x1+1]==11
        if int(initial.sum())!=45:raise AssertionError("Original 45px cup source differs")
        counts=[int(np.count_nonzero(initial & (frame[y0:y1+1,x0:x1+1]==13))) for frame in frames]
        filled[name]={"first_45":next((i for i,n in enumerate(counts) if n==45),None),
                      "last_45":next((i for i in range(len(counts)-1,-1,-1) if counts[i]==45),None),
                      "penultimate":counts[-2],
                      "final":counts[-1],
                      "full_frame_indices":[i for i,n in enumerate(counts) if n==45],
                      "frame_45_count":sum(n==45 for n in counts)}
    four=[i for i in range(len(frames))
          if all(i in filled[name]["full_frame_indices"] for name in CUPS)]
    return {"condition":condition,"witness":witness,
            "true_original_level":record["true_original_sdk_level"],
            "true_original_state":record["true_original_sdk_state"],
            "official_level5_or_WIN":record["official_level5_or_WIN"],
            "original_native_frame_count":len(frames),
            "original_source_cups":filled,
            "original_four_simultaneous_full_frame_indices":four,
            "source_total_palette13_penultimate":int(np.count_nonzero(frames[-2]==13)),
            "source_total_palette13_final":int(np.count_nonzero(frames[-1]==13)),
            "source_returned_final_diff_from_penultimate":int(np.count_nonzero(frames[-1]!=frames[-2])),
            "scope":"Frame palette13 observations only; SDK official level is the progression predicate."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--npz",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    source=json.loads(args.json.read_text())
    if source.get("kind")!="ORIGINAL_SP80_STAGE4_LOWER_L_ONE_FACTOR_POSITION_AUDIT" or source.get("native_sdk_reset_count")!=10:
        raise ValueError("Exact authentic native lower-L source required")
    with np.load(args.npz,allow_pickle=False) as archive:
        rows=[inspect(record,archive) for record in source["native_original_records"]]
    if len(rows)!=10 or set(r["condition"] for r in rows)!=set(EXPECTED):
        raise AssertionError("Missing frozen source cases")
    results={}
    for condition in EXPECTED:
        pair=[x for x in rows if x["condition"]==condition]
        if len(pair)!=2 or {x["witness"] for x in pair}!={"A","B"}:
            raise AssertionError("Original SDK A/B witnesses missing")
        for field in ("true_original_level","true_original_state","official_level5_or_WIN",
                      "original_native_frame_count","original_source_cups",
                      "original_four_simultaneous_full_frame_indices",
                      "source_total_palette13_penultimate",
                      "source_total_palette13_final",
                      "source_returned_final_diff_from_penultimate"):
            if pair[0][field]!=pair[1][field]:
                raise AssertionError("Original SDK A/B source disagreement "+condition+" "+field)
        results[condition]={"native_witnesses":2,
          "native_sdk_level":pair[0]["true_original_level"],
          "native_sdk_state":pair[0]["true_original_state"],
          "native_animation_frames":pair[0]["original_native_frame_count"],
          "four_cup_full_frame_indices":pair[0]["original_four_simultaneous_full_frame_indices"],
          "cup_persistence":{
             k:{"first_full":v["first_45"],"last_full":v["last_45"],
                 "penultimate":v["penultimate"],"final":v["final"]}
             for k,v in pair[0]["original_source_cups"].items()},
          "source_last_two_palette13":[pair[0]["source_total_palette13_penultimate"],
                                       pair[0]["source_total_palette13_final"]]}
    report={"kind":"ARC4_AUTHENTIC_SDK_POUR_CUP_PERSISTENCE",
      "source_original_sdk_run":39761014684,
      "source_original_sdk_artifact":12417598191,
      "native_original_records":rows,
      "paired_native_summaries":results,
      "official_level_histogram":dict(Counter(str(x["true_original_level"]) for x in rows)),
      "official_level5_or_WIN_count":sum(int(x["official_level5_or_WIN"]) for x in rows),
      "limit":"Filling a cup in intermediate original animation frames does not equate to persistent final state or official WIN. No private win rule inferred."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    print("ARC4_CUP_PERSISTENCE_SUMMARY "+json.dumps({
        "original_native_resets":len(rows),
        "official_levels":report["official_level_histogram"],
        "official_level5_or_WIN_count":report["official_level5_or_WIN_count"],
        "conditions":results},sort_keys=True))

if __name__=="__main__":
    main()
