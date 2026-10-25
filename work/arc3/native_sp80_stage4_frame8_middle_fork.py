"""Original SP80 Level4: discriminate frame-8 lower-L fork by middle-bar lateral offset.

Native SDK run 40177191960 shows palette6 source divergence at ACTION5
frame8: x20..22/y38..40 versus x23..25/y35..37, next to selected
native lower-L piece. Prior two-axis L vertical neighbors failed
to fill both left cups simultaneously (run 40177465663).
This experiment instead moves the LEFT-MIDDLE source bar horizontally
relative to that native L while fixing the upper bars and original
verified clean parent. Only original SDK level>=5/WIN is progress.
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

RIGHT="6@46,33 3"
PARENTS=(
 ("A","6@24,33 2 2 2 3 3","6@34,42 3 3 3 1 1",(18,42),(27,36)),
 ("B","6@24,33 2 2 2 2 3 3","6@34,42 3 3 3 3 1 1",(18,45),(24,36)),
)
CUPS={"lateral":(5,35,10,43),"top_left":(17,5,25,10),
      "top_middle":(35,5,43,10),"top_right":(47,5,55,10)}
FORK={"lateral_branch":(38,41,20,23),"top_branch":(35,38,23,26)}
# native selections: middle ACTION6 at rooted source pixel8, L at source pixel15
FROZEN=tuple(
 (f"{name}_mid{vname}_{order}_{hname}_L{lname}",
  " ".join((RIGHT,mid,L,f"6@{mxy[0]},{mxy[1]}",
    " ".join((v,h) if order=="VH" else (h,v)),
    f"6@{lxy[0]},{lxy[1]}",lm,"5")),mxy,lxy)
 for name,mid,L,mxy,lxy in PARENTS
 for vname,v in (("up1","1"),("down1","2"))
 for hname,h in (("left1","3"),("right1","4"))
 for order in ("VH","HV")
 for lname,lm in (("left1","3"),("right1","4"))
)
assert len(FROZEN)==32==len({x[0] for x in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(word)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(word))==1
    and len(parse_plan(word))<=25
    and all(xy is not None for a,xy in parse_plan(word) if a==6)
    for _,word,*_ in FROZEN)

def native_readout(root,pre,frames):
    if root.shape!=(64,64) or pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Original native SDK source images required")
    first_full={k:None for k in CUPS}
    max_cup={k:0 for k in CUPS}
    first_both=None;first_four=None;max_left_same=0
    first_fork={k:None for k in FORK}
    frame8={}
    source_cells=[]
    for t,frame in enumerate(frames):
        extra=(pre!=6)&(frame==6)
        sites={}
        for k,(y0,y1,x0,x1) in FORK.items():
            pts=np.argwhere(extra[y0:y1,x0:x1])
            sites[k]=int(len(pts))
            if t==8:frame8[k]=sites[k]
            if first_fork[k] is None and sites[k]:
                first_fork[k]={"frame":t,"original_yx":[[int(y+y0),int(x+x0)] for y,x in pts]}
        if 3<=t<=12:
            source_cells.append({"native_sdk_frame":t,"new_palette6_pixels":sites})
        cups={}
        for k,(x0,y0,x1,y1) in CUPS.items():
            mask=(root[y0:y1+1,x0:x1+1]==11)
            if int(mask.sum())!=45:raise AssertionError("Source native cup geometry changed")
            n=int(np.count_nonzero(mask & (frame[y0:y1+1,x0:x1+1]==13)))
            cups[k]=n;max_cup[k]=max(max_cup[k],n)
            if n==45 and first_full[k] is None:first_full[k]=t
        max_left_same=max(max_left_same,cups["lateral"]+cups["top_left"])
        if first_both is None and cups["lateral"]==cups["top_left"]==45:first_both=t
        if first_four is None and all(n==45 for n in cups.values()):first_four=t
    return {
        "source_prepour_blake2b16":hash_frame(pre),
        "original_native_final_blake2b16":hash_frame(frames[-1]),
        "original_sdk_returned_animation_frames":len(frames),
        "frame8_new_palette6_at_source_fork":frame8,
        "first_native_palette6_fork_cell_arrivals":first_fork,
        "native_source_fork_frames_3_to_12":source_cells,
        "first_original_full_cup_frames":first_full,
        "max_actual_cup_pixels_to13":max_cup,
        "max_left_two_cups_in_same_frame_out_of90":max_left_same,
        "first_simultaneous_two_left_cups_full":first_both,
        "first_simultaneous_four_cups_full":first_four,
        "source_only":"Original SDK frames are observations, not verified hidden fluid mechanics.",
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();receipts=[];arrays={};roots=set()
    for case,word,middle_xy,L_xy in FROZEN:
        steps=parse_plan(word);n=len(steps)
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            pre=raw["stage4_"+str(n-1)][-1];animation=raw["stage4_"+str(n)]
            measurement=native_readout(root,pre,animation)
            motion=[{
                "sdk_index":evt["index"],"native_action":evt["genuine_original_action"],
                "native_click_xy":evt["real_native_click_xy"],
                "actual_clicked_source_palette":evt["original_source_pixel_before_click"],
                "native_selected_after":selected(raw["stage4_"+str(evt["index"])][-1]),
                "actual_source_frame_after":evt["source_frame_after_blake2b16"]}
                for evt in sdk["genuine_original_stage4_action_ledger"]
                if evt["genuine_original_action"] in (1,2,3,4,6)]
            if not any(m["native_click_xy"]==list(middle_xy) and m["actual_clicked_source_palette"]==8 for m in motion):
                raise AssertionError("Middle piece genuine source selection absent")
            if not any(m["native_click_xy"]==list(L_xy) and m["actual_clicked_source_palette"]==15 for m in motion):
                raise AssertionError("Lower L original source selection absent")
            row={
                "prospectively_frozen_case":case,
                "independent_original_sdk_entry":witness,
                "actual_original_native_word":word,
                "official_original_final_level":sdk["true_original_sdk_final_level"],
                "official_original_final_state":sdk["true_original_sdk_final_state"],
                "native_sdk_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "actual_original_sdk_fork_and_cup_metrics":measurement,
                "actual_original_native_selected_motion":motion,
                "all_true_original_sdk_action_receipts":sdk["genuine_original_stage4_action_ledger"]}
            receipts.append(row)
            for phase,fs in raw.items():arrays[f"{case}_{witness}_{phase}"]=fs
            print("SP80_LEVEL4_FRAME8_FORK_CASE "+json.dumps({
                "case":case,"witness":witness,"level":row["official_original_final_level"],
                "state":row["official_original_final_state"],
                "fork8":measurement["frame8_new_palette6_at_source_fork"],
                "max_left_same":measurement["max_left_two_cups_in_same_frame_out_of90"],
                "cups":measurement["max_actual_cup_pixels_to13"]},sort_keys=True),flush=True)
    if len(receipts)!=64 or len(roots)!=1:raise AssertionError("Missing independent original source runs")
    for case,*_ in FROZEN:
        pair=[r for r in receipts if r["prospectively_frozen_case"]==case]
        if len(pair)!=2 or any(pair[0][key]!=pair[1][key] for key in
           ("official_original_final_level","official_original_final_state",
            "actual_original_sdk_fork_and_cup_metrics","actual_original_native_selected_motion")):
            raise AssertionError("Original SDK paired witness discrepancy "+case)
    summary={
        "kind":"GENUINE_ORIGINAL_SP80_LEVEL4_FRAME8_LOWER_SOURCE_FORK_MIDDLE_OFFSET",
        "antecedent_original_native_runs":[40177191960,40177465663],
        "native_original_sdk_games":len(receipts),
        "same_original_level4_root_blake2b16":next(iter(roots)),
        "official_level5_or_WIN":[r["prospectively_frozen_case"] for r in receipts if r["native_sdk_level5_or_WIN"]],
        "actual_original_native_level_histogram":dict(Counter(str(r["official_original_final_level"]) for r in receipts)),
        "actual_original_native_state_histogram":dict(Counter(str(r["official_original_final_state"]) for r in receipts)),
        "frozen_original_native_words":FROZEN,
        "true_original_sdk_action_and_frame_receipts":receipts,
        "limits":"Only official SDK levels_completed>=5/WIN is game advancement; native pixels are observations. F3-48 mathematics and canonical agent unchanged.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_LEVEL4_FRAME8_FORK_SUMMARY "+json.dumps({k:v for k,v in summary.items()
        if k not in ("frozen_original_native_words","true_original_sdk_action_and_frame_receipts")},sort_keys=True),flush=True)
if __name__=="__main__":main()
