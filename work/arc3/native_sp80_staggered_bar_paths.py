"""Genuine original SP80 staggered three-bar placements and native pulse paths.

Earlier independently source-authenticated aligned right edges x39,43,
47,51 yielded 0 native level2 in 42 genuine stage1 trials.
The full ACTION5 SDK animation shows actual moving color6 pixel paths;
that is a visible native effect, NOT a decoded beam mechanic or goal.
Freeze distinct staggered bar edges and same-edge negative controls
before SDK native execution. Capture actual bar positions before ACTION5,
per-returned-frame source color6 contact with upper y0..12,
the full returned SDK frames, and ONLY official level progress.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_action5_frame_stacks import one
from .native_sp80_multi_select import parse_plan

# (F,L,U) = original first 20x4 at y36, middle 12x4 y24,
# upper 12x4 y16. Numbers are proposed right edges on 4px lattice.
EDGES=(
 ("all_same",(43,43,43)),
 ("left_stair",(43,39,35)),
 ("right_stair",(43,47,51)),
 ("left_wide",(43,35,43)),
 ("right_wide",(43,51,43)),
 ("zig_left_right",(43,35,51)),
 ("zig_right_left",(43,47,35)),
 ("upper_left",(43,43,39)),
 ("upper_right",(43,43,47)),
 ("middle_left",(43,39,43)),
 ("near_left_stair",(39,35,31)),
 ("far_right_stair",(47,51,55)),
)
ORDER=("FLU","ULF")
NATIVE_CLICKS={"F":"6@24,37","L":"6@32,25","U":"6@12,17"}
ROOT_RIGHT={"F":39,"L":39,"U":19}

def freeze_word(edges,order,commit="5"):
    positions=dict(zip("FLU",edges))
    tokens=[]
    for item in order:
        delta=positions[item]-ROOT_RIGHT[item]
        if delta%4:raise AssertionError("Not on observed four-pixel native lattice")
        tokens.append(NATIVE_CLICKS[item])
        tokens.extend([("4" if delta>0 else "3")]*abs(delta//4))
    tokens.extend(commit.split())
    return " ".join(tokens)

PLANS=tuple(
  (name+"_"+order,freeze_word(edges,order))
  for name,edges in EDGES for order in ORDER
)+(
 ("left_stair_repeat5",freeze_word((43,39,35),"FLU","5 5 5")),
 ("right_stair_repeat5",freeze_word((43,47,51),"ULF","5 5 5")),
 ("zig_left_repeat5",freeze_word((43,35,51),"FLU","5 5 5")),
 ("aligned_repeat5",freeze_word((43,43,43),"ULF","5 5 5")),
)
RESETS=2
assert len(PLANS)==28 and len(set(n for n,_ in PLANS))==28
assert RESETS==2
assert all(parse_plan(w)[-1][0]==5 and
   all(a!=6 or xy is not None for a,xy in parse_plan(w))
   for _,w in PLANS)

REGIONS={"F":(36,40),"L":(24,28),"U":(16,20)}
def source_regions(img):
    output={}
    for name,(start,end) in REGIONS.items():
        ys,xs=np.nonzero(np.isin(img[start:end],[8,9]))
        output[name+"_real_bbox"]=(
           [int(xs.min()),int(ys.min()+start),int(xs.max()),int(ys.max()+start)]
           if len(xs) else None)
        output[name+"_native_color9_cells"]=int(np.count_nonzero(img[start:end]==9))
        output[name+"_native_color8_cells"]=int(np.count_nonzero(img[start:end]==8))
    return output

def observe_A5(trial,raw):
    out=[]
    for ev in trial["real_sdk_observation_ledger"]:
        if ev["phase"]!="context" or ev["native_action_id"]!=5:continue
        i=ev["phase_action_number"]
        stack=raw.get("context_"+str(i))
        if stack is None:
            out.append({"step":i,"status":"UNKNOWN_SDK_NO_FULL_FRAMES"});continue
        previous=raw["entry_6"][-1] if i==1 else raw["context_"+str(i-1)][-1]
        top_cols={}
        contacts=[]
        for frame_i,frame in enumerate(stack):
            y,x=np.nonzero(frame[:13]==6)
            cols=sorted({int(col) for col in x})
            top_cols[str(frame_i)]=cols
            if cols:contacts.append(frame_i)
        out.append({
            "actual_original_step":i,
            "real_source_before_placement":source_regions(previous),
            "actual_sdk_returned_full_frame_count":len(stack),
            "top_y0_to12_native_color6_x_columns_by_frame":top_cols,
            "real_native_frames_with_color6_in_upper_region":contacts,
            "actual_original_post_frame_placement":source_regions(stack[-1]),
            "native_sdk_level_after":ev["original_source_level_after"],
            "native_sdk_state_after":ev["original_source_state_after"],
        })
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    trials,arrays=[],{}
    for name,word in PLANS:
      for replicate in range(RESETS):
        trial,raw=one(name,word,replicate)
        trial["native_staggered_A5_observations"]=observe_A5(trial,raw)
        trials.append(trial)
        for k,arr in raw.items():
          arrays[f"{name}_reset{replicate}_{k}"]=arr
    outcomes={}
    for name,word in PLANS:
      values=[t for t in trials if t["name"]==name]
      outcomes[name]={
        "original_native_program":word,
        "genuine_resets":len(values),
        "native_levels":[t["original_last_source_level"] for t in values],
        "native_states":[t["original_last_source_state"] for t in values],
        "native_level2_or_WIN":[t["native_level2_or_win"] for t in values],
        "real_source_A5":[t["native_staggered_A5_observations"] for t in values],
      }
    payload={
      "kind":"ORIGINAL_SP80_GENUINE_STAGGERED_THREE_BAR_NATIVE_A5_PATHS",
      "prospective_original_bar_right_edges":EDGES,
      "frozen_original_SDK_action_programs":PLANS,
      "native_resets_per_program":RESETS,
      "genuine_original_SDK_games":len(trials),
      "actual_original_SDK_calls":sum(t["actual_native_calls"] for t in trials),
      "real_original_native_level2_or_WIN":sum(int(t["native_level2_or_win"]) for t in trials),
      "sdk_dispositions":dict(Counter(t["actual_source_disposition"] for t in trials)),
      "per_program":outcomes,
      "full_native_original_SDK_trial_records":trials,
      "limits":"Actual original Arcade.NORMAL game SDK. Color6 upper-region pulse is an observable pixel event NOT hidden beam physics or decoded objective. Every ACTION6 uses genuine data x,y and every SDK returned frame is retained. Native levels_completed >= 2 or WIN alone counts as progress.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(payload,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_STAGGERED_BARS "+json.dumps({
      k:v for k,v in payload.items()
      if k not in ("full_native_original_SDK_trial_records","per_program")
    },sort_keys=True))
    if len(trials)!=len(PLANS)*RESETS:
      raise RuntimeError("Missing actual original native resets")
if __name__=="__main__":main()
