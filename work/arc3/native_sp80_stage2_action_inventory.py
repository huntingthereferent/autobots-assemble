"""Genuine original SP80 SDK stage2 baseline and bounded action inventory.

Original official source 0->1 prefix = 454545. Actual independently
verified native stage1->2 = 6@24,37 4 4 6@32,25 6@12,17 4 4 4 5.
Both stage changes MUST be witnessed from SDK levels_completed before
continuing into the original level2 frame. That source frame has four
color8/color9 bars, not the three from level1. Do not port old goals.

Freeze first original level2 legal ACTION1..6, properly clicked real
observed stage2 bars and short bounded movements into ACTION5. Save
ALL complete original returned 64x64 frames and true SDK states.
Any level3/WIN reported ONLY from SDK progression.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
import numpy as np
from .native_sp80_action5_frame_stacks import native_stack,frame_record_before_after
from .native_sp80_legal_pairs import state,legal,hash_frame
from .native_sp80_multi_select import parse_plan

SOURCE_STAGE0="454545"
SOURCE_STAGE1="6@24,37 4 4 6@32,25 6@12,17 4 4 4 5"
SOURCE_STAGE2_ENTRY_SHA256="b23d0e2243bc716d36e8602c7d30758a687250f142263510d2bc36432b5f35b4"
STAGE2_ROOT_BARS={
 "selected_lower_24px":(42,41,9),
 "unselected_lower_24px":(12,33,8),
 "unselected_mid_20px":(50,29,8),
 "unselected_upper_16px":(12,21,8),
}
PROGRAMS=(
 ("native_ACTION1","1"),
 ("native_ACTION2","2"),
 ("native_ACTION3","3"),
 ("native_ACTION4","4"),
 ("native_ACTION5","5"),
 ("selected_first_click","6@42,41"),
 ("lower_24_click","6@12,33"),
 ("middle_20_click","6@50,29"),
 ("upper_16_click","6@12,21"),
 ("white_glyph_click","6@6,5"),
 ("first_RIGHT_then_A5","4 5"),
 ("first_LEFT_then_A5","3 5"),
 ("first_UP_then_A5","1 5"),
 ("first_DOWN_then_A5","2 5"),
 ("first_RIGHTx2_then_A5","4 4 5"),
 ("first_LEFTx2_then_A5","3 3 5"),
 ("first_RIGHTx3_then_A5","4 4 4 5"),
 ("first_LEFTx3_then_A5","3 3 3 5"),
 ("upper_16_selected_then_RIGHTx2_A5","6@12,21 4 4 5"),
 ("middle_20_selected_then_LEFTx2_A5","6@50,29 3 3 5"),
 ("lower_24_selected_then_RIGHTx2_A5","6@12,33 4 4 5"),
 ("selected_lower_then_LEFTx2_A5","6@42,41 3 3 5"),
 ("upper_then_middle_click_A5","6@12,21 6@50,29 5"),
 ("middle_then_lower_click_A5","6@50,29 6@12,33 5"),
)
RESETS=2
assert len(PROGRAMS)==len({n for n,_ in PROGRAMS})==24
assert RESETS==2
assert all(all(n!=6 or xy is not None for n,xy in parse_plan(w))
           for _,w in PROGRAMS)
BANDS={"upper_16px":(20,24),"middle_20px":(28,32),
       "lower_24px":(32,36),"selected_lower_24px":(40,44)}

def source_bars(img):
    result={}
    for name,(lo,hi) in BANDS.items():
        region=img[lo:hi]
        y,x=np.nonzero(np.isin(region,[8,9]))
        result[name]={
            "native_source_bbox":(
                [int(x.min()),int(y.min()+lo),int(x.max()),int(y.max()+lo)]
                if len(x) else None),
            "actual_native_color8":int(np.count_nonzero(region==8)),
            "actual_native_color9":int(np.count_nonzero(region==9)),
        }
    return result

def trial(name,stage2word,replicate):
    sdk=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=sdk.make("sp80")
    if env is None:raise RuntimeError("Real original SP80 source SDK unavailable")
    observation=env.reset()
    stack,meta=native_stack(observation)
    if stack is None or int(getattr(observation,"levels_completed",-1))!=0:
        raise RuntimeError("Missing genuine original SP80 stage0 reset")
    raw={"reset":stack}
    prev=stack[-1]
    entries=[];calls=0
    def take(n,xy,phase,step):
        nonlocal observation,prev,calls
        allowed=legal(observation)
        before_level=int(getattr(observation,"levels_completed",-1))
        before_state=state(observation)
        if n not in allowed:
            return {"phase":phase,"step":step,"native_action":n,
              "source_status":"UNKNOWN_ACTION_UNAVAILABLE",
              "source_legal_actions_before":allowed},False
        kw={"data":{"x":int(xy[0]),"y":int(xy[1])}} if xy is not None else {}
        if n==6 and xy is None:
            raise AssertionError("SDK ACTION6 requires original x and y")
        pixel=int(prev[xy[1],xy[0]]) if xy is not None else None
        before_image=prev
        ans=env.step(getattr(GameAction,"ACTION"+str(n)),**kw)
        calls+=1
        if ans is None:
            return {"phase":phase,"step":step,"native_action":n,
                    "source_status":"UNKNOWN_NULL_NATIVE_RESPONSE"},False
        arr,info=native_stack(ans)
        after_level=int(getattr(ans,"levels_completed",-1))
        after_state=state(ans)
        e={
          "phase":phase,"step":step,"native_action":n,
          "source_prelevel":before_level,"source_postlevel":after_level,
          "source_prestate":before_state,"source_poststate":after_state,
          "genuine_native_available_actions_before":allowed,
          "genuine_native_available_actions_after":legal(ans),
          "original_native_click_xy":list(xy) if xy is not None else None,
          "original_native_preclick_color":pixel,
          "original_SDK_frame_admission":info,
          "original_SDK_advanced_level":after_level>before_level,
        }
        if arr is not None:
            raw[f"{phase}_{step}"]=arr
            e["real_original_SDK_animation"]=frame_record_before_after(prev,arr)
            prev=arr[-1]
            if phase=="stage2":
                e["source_bar_regions_before"]=source_bars(before_image)
                e["source_bar_regions_after"]=source_bars(prev)
            e["source_original_final_frame_hash"]=hash_frame(prev)
        else:
            e["source_status"]=("NATIVE_TERMINAL_"+after_state
                if after_state in ("WIN","GAME_OVER") else "UNKNOWN_SDK_FRAME")
        observation=ans
        entries.append(e)
        return e,arr is not None
    for idx,c in enumerate(SOURCE_STAGE0,1):
        e,valid=take(int(c),None,"stage0",idx)
        if not valid or state(observation) in ("GAME_OVER","WIN"):
            raise RuntimeError("Official original stage0 witness invalid")
    if int(getattr(observation,"levels_completed",-1))!=1:
        raise RuntimeError("Expected original native level1 witness absent")
    for idx,(n,xy) in enumerate(parse_plan(SOURCE_STAGE1),1):
        e,valid=take(n,xy,"stage1",idx)
        if not valid or state(observation) in ("GAME_OVER","WIN"):
            raise RuntimeError("Original level2 witness failed during prerequisite")
        if idx<len(parse_plan(SOURCE_STAGE1)) and e["source_postlevel"]!=1:
            raise RuntimeError("Unexpected original SDK early stage2 in prerequisite")
    if int(getattr(observation,"levels_completed",-1))!=2 or state(observation)!="NOT_FINISHED":
        raise RuntimeError("Verified original native stage2 entry was not reproduced")
    source_entry_bars=source_bars(prev)
    source_entry_hash=hash_frame(prev)
    source_entry_actions=legal(observation)
    boundary=None
    for idx,(n,xy) in enumerate(parse_plan(stage2word),1):
        e,valid=take(n,xy,"stage2",idx)
        if not valid:
            boundary=e.get("source_status","UNKNOWN_FRAME");break
        if state(observation) in ("GAME_OVER","WIN"):
            boundary="NATIVE_TERMINAL_"+state(observation);break
        if int(getattr(observation,"levels_completed",-1))!=2:
            boundary="NATIVE_LEVEL_CHANGED";break
    final_level=int(getattr(observation,"levels_completed",-1))
    return {
       "program":name,"stage2_native_source_word":stage2word,"replicate":replicate,
       "actual_SDK_action_calls":calls,"original_SDK_level_at_end":final_level,
       "original_SDK_state_at_end":state(observation),
       "actual_native_level3_or_WIN":bool(final_level>=3 or state(observation)=="WIN"),
       "real_source_disposition":boundary or "COMPLETE",
       "original_stage2_entry_sha":source_entry_hash,
       "stage2_entry_advertised_legal_actions":source_entry_actions,
       "stage2_actual_entry_bars":source_entry_bars,
       "source_original_SDK_ledger":entries,
       "limits":"Actual original Arcade.NORMAL SP80. Official native SDK level/terminal labels only. All returned images saved. Genuine stage2 known witness, no hidden physics or F3 law assumption.",
    },raw

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    observed,all_arrays=[],{}
    for name,word in PROGRAMS:
        for rep in range(RESETS):
            row,frames=trial(name,word,rep)
            observed.append(row)
            for phase,frames in frames.items():
                all_arrays[f"{name}_rep{rep}_{phase}"]=frames
    outcomes={}
    for name,word in PROGRAMS:
        rows=[t for t in observed if t["program"]==name]
        outcomes[name]={
          "source_program":word,
          "genuine_original_SDK_levels":[t["original_SDK_level_at_end"] for t in rows],
          "genuine_original_states":[t["original_SDK_state_at_end"] for t in rows],
          "source_progress_to_level3_or_WIN":[t["actual_native_level3_or_WIN"] for t in rows],
          "original_source_dispositions":[t["real_source_disposition"] for t in rows],
          "genuine_stage2_actions_advertised":[t["stage2_entry_advertised_legal_actions"] for t in rows],
          "real_stage2_entry_bar_regions":[t["stage2_actual_entry_bars"] for t in rows],
          "source_actual_stage2_events":[
             [e for e in t["source_original_SDK_ledger"] if e["phase"]=="stage2"]
             for t in rows],
        }
    out={
      "kind":"GENUINE_ORIGINAL_SP80_SOURCE_STAGE2_LEGAL_ACTION_AND_FIRST_MOVEMENT_INVENTORY",
      "genuine_original_native_stage0_prefix":SOURCE_STAGE0,
      "independently_reproduced_original_stage1_to_stage2_word":SOURCE_STAGE1,
      "frozen_real_stage2_action_programs":PROGRAMS,
      "independent_source_SDK_resets_per_stage2_program":RESETS,
      "actual_source_original_SP80_games":len(observed),
      "actual_original_SDK_action_responses":sum(t["actual_SDK_action_calls"] for t in observed),
      "native_level3_or_WIN":sum(int(t["actual_native_level3_or_WIN"]) for t in observed),
      "original_source_dispositions":dict(Counter(t["real_source_disposition"] for t in observed)),
      "real_original_stage2_per_program":outcomes,
      "complete_native_original_SDK_evidence":observed,
      "limits":"Actual original 6-level game, source stage2 entry via independently verified word. Source bars observed, no known objective. Native >=3 or WIN alone indicates later progress. Full returned frames preserved; no F3 math mapping.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**all_arrays)
    print("SP80_STAGE2_NATIVE_INVENTORY "+json.dumps({
      k:v for k,v in out.items() if k not in ("complete_native_original_SDK_evidence","real_original_stage2_per_program")
    },sort_keys=True))
    if len(observed)!=len(PROGRAMS)*RESETS:
        raise RuntimeError("Some original native SDK stage2 reset missing")
if __name__=="__main__":main()
