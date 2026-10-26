"""Original SDK SP80 Level4: official progress tests around verified four-cup witness.

Authentic run 40179237019 reproduced four simultaneous 45/45 source cups
frames 23..30 in both independent original game-entry histories, but
SDK official level stayed4 NOT_FINISHED. This bounded native-only test
holds the observed geometry and varies last selected object, same-pose
motion history, and repeat ACT5 after the exact visual witness. It is
NOT an inferred hidden objective or a synthetic fluid model.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_upstream_junction import selected
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

BASE="6@46,33 3 6@24,33 2 2 2 2 3 3 6@34,42 3 3 3 3 1 1 6@18,45 2 3 6@24,36 3"
FROZEN=(
 ("four_cup_parent",BASE+" 5"),
 ("second_pour",BASE+" 5 5"),
 ("third_pour",BASE+" 5 5 5"),
 ("after_first_up1",BASE+" 5 1 5"),
 ("after_first_down1",BASE+" 5 2 5"),
 ("after_first_left1",BASE+" 5 3 5"),
 ("after_first_right1",BASE+" 5 4 5"),
 ("final_select_middle",BASE+" 6@15,48 5"),
 ("final_select_right",BASE+" 6@46,33 5"),
 ("final_select_upper",BASE+" 6@34,21 5"),
 ("final_reselect_L",BASE+" 6@18,36 5"),
 ("final_middle_return_RL",BASE+" 6@15,48 4 3 6@18,36 5"),
 ("final_middle_return_LR",BASE+" 6@15,48 3 4 6@18,36 5"),
 ("final_middle_reclick_L",BASE+" 6@15,48 6@18,36 5"),
 ("reverse_final_two_selection","6@46,33 3 6@24,33 2 2 2 2 3 3 6@34,42 3 3 3 3 1 1 3 6@18,45 2 3 5"),
)
assert len(FROZEN)==15==len({k for k,w in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(w)[-1][0]==5 and
    sum(a==5 for a,xy in parse_plan(w)) in (1,2,3) and
    len(parse_plan(w))<=29 and
    all(xy is not None for a,xy in parse_plan(w) if a==6)
    for _,w in FROZEN)
CUPS={"lateral":(5,35,10,43),"top_left":(17,5,25,10),
      "top_middle":(35,5,43,10),"top_right":(47,5,55,10)}

def read_pour(root,pre,frames):
    if root.shape!=(64,64) or pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Only original SDK returned 64x64 source frames accepted")
    first={k:None for k in CUPS};max_fill={k:0 for k in CUPS}
    simultaneous=[];both=[];border_first={k:None for k in ("left","right","top","bottom")}
    borders={"left":(slice(2,62),slice(2,5)),
             "right":(slice(2,62),slice(59,62)),
             "top":(slice(2,5),slice(2,62)),
             "bottom":(slice(59,62),slice(2,62))}
    for t,frame in enumerate(frames):
        counts={}
        for name,(x0,y0,x1,y1) in CUPS.items():
            source=root[y0:y1+1,x0:x1+1]==11
            if int(source.sum())!=45:raise AssertionError("Original SDK source cup changed")
            count=int(np.count_nonzero(source&(frame[y0:y1+1,x0:x1+1]==13)))
            counts[name]=count;max_fill[name]=max(max_fill[name],count)
            if first[name] is None and count==45:first[name]=t
        if counts["lateral"]==counts["top_left"]==45:both.append(t)
        if all(n==45 for n in counts.values()):simultaneous.append(t)
        for name,(ys,xs) in borders.items():
            if border_first[name] is None and np.any((pre[ys,xs]==1)&(frame[ys,xs]==14)):
                border_first[name]=t
    return {
        "source_frame_count":len(frames),"pre_hash":hash_frame(pre),
        "post_hash":hash_frame(frames[-1]),
        "first_complete_original_cups":first,"max_original_cup_palette13":max_fill,
        "same_sdk_frame_full_two_left_cups":both,
        "same_sdk_frame_full_four_cups":simultaneous,
        "original_border_palette1_to14_first":border_first,
        "source_only":"Visual cup fill and border blink are not official SDK progress."}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();rows=[];arrays={};roots=set()
    for case,word in FROZEN:
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            root=raw["entry3_34"][-1]
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            receipts=sdk["genuine_original_stage4_action_ledger"]
            pours=[]
            for e in receipts:
                if e["genuine_original_action"]!=5:continue
                i=e["index"];key="stage4_"+str(i)
                if key not in raw:continue
                pre=raw["stage4_"+str(i-1)][-1] if i>1 else root
                pours.append({
                    "native_step":i,
                    "level_before":e["original_sdk_level_before"],
                    "level_after":e["original_sdk_level_after"],
                    "state_after":e["original_sdk_state_after"],
                    "genuine_original_source_measure":read_pour(root,pre,raw[key]),
                })
            row={
                "frozen_case":case,"independent_native_witness":witness,
                "original_source_stage4_word":word,
                "true_original_sdk_level":sdk["true_original_sdk_final_level"],
                "true_original_sdk_state":sdk["true_original_sdk_final_state"],
                "official_original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "original_sdk_pour_sequence":pours,
                "genuine_selected_and_click_receipts":[{
                    "sdk_action_index":e["index"],
                    "native_action":e["genuine_original_action"],
                    "actual_click":e["real_native_click_xy"],
                    "source_click_pixel":e["original_source_pixel_before_click"],
                    "selected_after":selected(raw["stage4_"+str(e["index"])][-1]),
                } for e in receipts if e["genuine_original_action"] in (1,2,3,4,6)],
                "full_original_native_action_ledger":receipts,
            }
            rows.append(row)
            for k,v in raw.items():arrays[f"{case}_{witness}_{k}"]=v
            print("SP80_LEVEL4_FOURCUP_FOLLOWUP_CASE "+json.dumps({
                "case":case,"witness":witness,
                "level":row["true_original_sdk_level"],
                "state":row["true_original_sdk_state"],
                "pours":[{
                    "index":e["native_step"],"level":e["level_after"],
                    "four_cup":e["genuine_original_source_measure"]["same_sdk_frame_full_four_cups"],
                    "border":e["genuine_original_source_measure"]["original_border_palette1_to14_first"]}
                    for e in pours]},sort_keys=True),flush=True)
    if len(rows)!=30 or len(roots)!=1:raise AssertionError("True independent original SDK resets missing")
    for case,_ in FROZEN:
        a,b=[r for r in rows if r["frozen_case"]==case]
        if any(a[k]!=b[k] for k in ("true_original_sdk_level","true_original_sdk_state",
                                    "original_sdk_pour_sequence","genuine_selected_and_click_receipts")):
            raise AssertionError("Different original native source witnesses "+case)
    progress=[{"case":r["frozen_case"],"witness":r["independent_native_witness"],
               "original_level":r["true_original_sdk_level"]}
               for r in rows if r["official_original_level5_or_WIN"]]
    result={
        "kind":"TRUE_ORIGINAL_SP80_LEVEL4_FOUR_CUP_VISUAL_WITNESS_OFFICIAL_PROGRESS_CONTROLS",
        "source_original_antecedent_native_run":40179237019,
        "genuine_independently_reset_sdk_games":len(rows),
        "same_original_level4_root":next(iter(roots)),
        "official_level5_or_WIN_cases":progress,
        "official_sdk_level_histogram":dict(Counter(str(r["true_original_sdk_level"]) for r in rows)),
        "official_sdk_state_histogram":dict(Counter(str(r["true_original_sdk_state"]) for r in rows)),
        "frozen_source_words":FROZEN,
        "complete_original_sdk_game_receipts":rows,
        "limits":"Only original SDK levels_completed>=5/WIN counts as progression; no substitute engine or F3-48 correspondence assumed."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_LEVEL4_FOURCUP_FOLLOWUP_SUMMARY "+json.dumps({k:v for k,v in result.items() if
            k not in ("frozen_source_words","complete_original_sdk_game_receipts")},sort_keys=True),flush=True)
if __name__=="__main__":main()
