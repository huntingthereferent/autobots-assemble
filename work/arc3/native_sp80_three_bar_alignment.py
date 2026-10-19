"""Original public SDK SP80 stage1: jointly align three selectable native bars.

Observed authentic stage1 root (not game engine source):
 selected native color9: x20..39, y36..39; lower unselected color8:
 x28..39,y24..27; upper unselected color8:x8..19,y16..19.
 Native ACTION6 real x/y selects bar; ACTION4 moves selected bar right
 four pixels in the tested game. Visible bottom glyph occupies x40..43.
 That glyph is NOT established as the objective.

Freeze equal-source-right-edge 39/43/47/51 alignments before new original
 game resets. Compare 4 authentic source click/selection orders per
 alignment, plus ACTION5-repeat controls. Save every SDK-returned frame.
 Only actual levels_completed>=2 or WIN is native success.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_action5_frame_stacks import one
from .native_sp80_multi_select import parse_plan

# Original root right-edge 39,39,19. Their observed width differs.
# For the upper x8..19 bar, five native right movements reach x28..39.
# All values are original source observed frame coordinates, not goals.
ALIGNMENTS=(
 ("right39",(0,0,5)),
 ("right43",(1,1,6)),
 ("right47",(2,2,7)),
 ("right51",(3,3,8)),
)
COORDS={"F":"6@24,37","L":"6@32,25","U":"6@12,17"}
ORDERS=("FLU","ULF","FUL","LUF")
def build(target,counts,order,suffix="5"):
    moves=dict(zip("FLU",counts))
    tokens=[]
    for item in order:
        tokens.append(COORDS[item])
        tokens.extend(["4"]*moves[item])
    tokens.extend(suffix.split())
    return " ".join(tokens)

PROGRAMS=tuple(
 (target+"_"+order,build(target,counts,order))
 for target,counts in ALIGNMENTS for order in ORDERS
)+(
 ("right43_triple_action5",build("right43",(1,1,6),"FLU","5 5 5")),
 ("right47_triple_action5",build("right47",(2,2,7),"ULF","5 5 5")),
 ("right39_triple_action5",build("right39",(0,0,5),"FUL","5 5 5")),
 ("right51_triple_action5",build("right51",(3,3,8),"LUF","5 5 5")),
 ("no_click_triple_action5","5 5 5"),
)
RESETS=2
assert len(PROGRAMS)==21 and len({n for n,_ in PROGRAMS})==21
assert RESETS==2
assert all(parse_plan(word)[-1][0]==5 and
   all(a!=6 or xy is not None for a,xy in parse_plan(word))
   for _,word in PROGRAMS)

REGIONS={"U":(16,20),"L":(24,28),"F":(36,40)}
def region_profile(a):
    profile={}
    for name,(y0,y1) in REGIONS.items():
        region=a[y0:y1]
        for color in (8,9):
            y,x=np.nonzero(region==color)
            profile[name+"_color"+str(color)+"_bbox"]=(
                [int(x.min()),int(y.min()+y0),int(x.max()),int(y.max()+y0)]
                if len(x) else None)
            profile[name+"_color"+str(color)+"_count"]=int(len(x))
    return profile

def actual_position_evidence(trial,source):
    ledger=trial["real_sdk_observation_ledger"]
    result=[]
    for e in ledger:
      if e["phase"]!="context":continue
      step=e["phase_action_number"]
      if "context_"+str(step) not in source:
         result.append({"step":step,"status":"UNKNOWN_NATIVE_FRAME"});continue
      frame=source["context_"+str(step)][-1]
      result.append({
          "original_context_step":step,
          "native_action":e["native_action_id"],
          "original_coordinate_argument":e["native_click_xy"],
          "true_pixel_at_click_before":e["actual_native_pre_click_pixel"],
          "native_SDK_response_frame_count":e["source_animation"]["true_original_returned_frames"],
          "actual_original_visible_bars_after":region_profile(frame),
          "SDK_levels_completed":e["original_source_level_after"],
          "SDK_game_state":e["original_source_state_after"],
      })
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    trials,stacks=[],{}
    for name,word in PROGRAMS:
      for r in range(RESETS):
        trial,raw=one(name,word,r)
        trial["original_source_bar_region_ledger"]=actual_position_evidence(trial,raw)
        trials.append(trial)
        for phase,array in raw.items():
          stacks[f"{name}_reset{r}_{phase}"]=array
    outcomes={}
    for name,word in PROGRAMS:
      records=[t for t in trials if t["name"]==name]
      outcomes[name]={
        "frozen_actual_native_word":word,
        "real_source_native_levels":[t["original_last_source_level"] for t in records],
        "real_source_native_states":[t["original_last_source_state"] for t in records],
        "original_SDK_advanced_to_level2_or_WIN":[t["native_level2_or_win"] for t in records],
        "authentic_dispositions":[t["actual_source_disposition"] for t in records],
        "pre_FIRST_ACTION5_original_bar_region":[next((
             t["original_source_bar_region_ledger"][i-1]["actual_original_visible_bars_after"]
             for i,e in enumerate(t["original_source_bar_region_ledger"])
             if e.get("native_action")==5 and i>0
        ),None) for t in records],
        "final_source_bar_region":[
             t["original_source_bar_region_ledger"][-1].get("actual_original_visible_bars_after")
             if t["original_source_bar_region_ledger"] else None for t in records],
      }
    output={
     "kind":"ORIGINAL_SP80_STAGE1_THREE_BAR_HORIZONTAL_ALIGNMENT",
     "fixed_original_native_alignment_controls":ALIGNMENTS,
     "frozen_source_original_action_programs":PROGRAMS,
     "independent_resets_per_program":RESETS,
     "true_original_SP80_native_games":len(trials),
     "original_SDK_actions":sum(t["actual_native_calls"] for t in trials),
     "genuine_native_level2_or_WIN":sum(int(t["native_level2_or_win"]) for t in trials),
     "actual_original_dispositions":dict(Counter(t["actual_source_disposition"] for t in trials)),
     "source_per_program":outcomes,
     "untouched_original_native_trial_evidence":trials,
     "limitations":"Horizontal bar alignment against observed x coordinates is tested, not a known goal. Genuine Arcade.NORMAL original SDK source only; click x/y required for ACTION6. Preserve all returned frames, true native levels and counterexamples. No game clone or F3 mathematical mapping.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**stacks)
    print("SP80_THREE_BAR_ALIGN "+json.dumps({
        k:v for k,v in output.items() if k not in ("untouched_original_native_trial_evidence","source_per_program")
    },sort_keys=True))
    if len(trials)!=len(PROGRAMS)*RESETS:
        raise RuntimeError("Genuine native source reset count mismatch")
if __name__=="__main__":main()
