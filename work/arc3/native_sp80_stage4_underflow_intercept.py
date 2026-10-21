"""Authentic original SDK SP80 level4: intercept lateral cup underflow at y44.

Original SDK first level4 all-four-cup animation in merged PR #372,
L-shaped 27px piece LEFT5/UP1, visibly fills the left lateral cup
[5,35,10,43] at frame11. Authentic returned frames contain a newly
palette6 horizontal interval at y44 extending left to x5 by frame11;
the entire x2..4 left border visibly changes palette1->14 at frame12.
Level4 remains NOT_FINISHED. PR #374 verified this event is retained
with several L neighbor positions; PR #375 tested left-middle bar
UP1/2, DOWN1/2 and short lateral moves without eliminating it.

New, specifically distinct source-contact hypothesis: lower the
separate movable left-middle red 27px bar from original bbox
x20..28/y32..34 toward row y44 and move it left to potentially
change the observed under-cup horizontal source branch, while HOLDING
the independently reproduced right-middle LEFT1 and L LEFT5/UP1
four-cup geometry. Compare DOWN3..5 × LEFT1..4 and reversed order.
Track actual source selected piece bboxes after each native action,
not a physics emulator. Only original SDK levels>=5 or WIN is progress.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

RIGHT="6@46,33 3"
L="6@34,42 3 3 3 3 3 1"
MID_CLICK="6@24,33"
CUP_BOXES={"lateral_left":(5,35,10,43),"upper_left":(17,5,25,10),
           "upper_middle":(35,5,43,10),"upper_right":(47,5,55,10)}
OBS_ROWS=(35,38,41,44,47,50)
def word(before=None,after=None):
    items=[RIGHT]
    if before is not None:items.append(MID_CLICK+" "+before)
    items.append(L)
    if after is not None:items.append(MID_CLICK+" "+after)
    items.append("5")
    return " ".join(items)

FROZEN=(
    ("four_cup_parent",word()),
    *((f"mid_down{k}",word(before=" ".join(["2"]*k))) for k in range(1,6)),
    *((f"mid_down{d}_left{l}",word(before=" ".join(["2"]*d+["3"]*l)))
      for d in (3,4) for l in (1,2,3,4)),
    *((f"mid_left{l}_down{d}",word(before=" ".join(["3"]*l+["2"]*d)))
      for l in (2,3) for d in (3,4)),
    ("mid_after_L_down3_left3",word(after="2 2 2 3 3 3")),
    ("mid_after_L_down4_left3",word(after="2 2 2 2 3 3 3")),
)
assert len(FROZEN)==20==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(w)[-1][0]==5 and sum(a==5 for a,xy in parse_plan(w))==1
           and len(parse_plan(w))<=22
           and all(xy is not None for a,xy in parse_plan(w) if a==6)
           for _,w in FROZEN)

def xbands(xs):
    xs=list(map(int,xs))
    if not xs:return []
    out=[];lo=hi=xs[0]
    for x in xs[1:]:
        if x>hi+1:out.append([lo,hi]);lo=x
        hi=x
    out.append([lo,hi])
    return out

def selected(frame):
    return [
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(frame)
        if c["palette"] in (9,15) and 20<=c["bbox"][1]<=53
    ]

def read_original(root,pre,frames):
    if root.shape!=(64,64) or pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Genuine original SDK 64x64 frame arrays required")
    first_full={k:None for k in CUP_BOXES}
    max_fill={k:0 for k in CUP_BOXES}
    first_new6={str(y):None for y in OBS_ROWS}
    border_frame=None;border_episode=[];prev=False
    for t,f in enumerate(frames):
        extra=(pre!=6)&(f==6)
        for y in OBS_ROWS:
            xs=np.flatnonzero(extra[y,3:31])+3
            if xs.size and first_new6[str(y)] is None:
                first_new6[str(y)]={"frame":t,"native_palette6_x_bands":xbands(xs)}
        for name,(x0,y0,x1,y1) in CUP_BOXES.items():
            original=root[y0:y1+1,x0:x1+1]==11
            if int(original.sum())!=45:raise AssertionError("Original source cup region changed")
            n=int(np.count_nonzero(original & (f[y0:y1+1,x0:x1+1]==13)))
            max_fill[name]=max(max_fill[name],n)
            if n==45 and first_full[name] is None:first_full[name]=t
        changed=bool(np.any(pre[2:62,2:5]!=f[2:62,2:5]))
        if changed and not prev:border_episode.append(t)
        prev=changed
        if changed and border_frame is None:
            pairs,counts=np.unique(np.stack((
                pre[2:62,2:5][pre[2:62,2:5]!=f[2:62,2:5]],
                f[2:62,2:5][pre[2:62,2:5]!=f[2:62,2:5]],
            ),axis=1),axis=0,return_counts=True)
            border_frame={"source_frame":t,"actual_left_border_transitions":[[int(v[0]),int(v[1]),int(c)] for v,c in zip(pairs,counts)]}
    return {
        "original_native_prepour_blake2b16":hash_frame(pre),
        "original_native_after_pour_blake2b16":hash_frame(frames[-1]),
        "original_sdk_pour_frame_count":len(frames),
        "source_four_cup_full_frames":first_full,
        "actual_original_cup_color13_max":max_fill,
        "first_left_border_source_change":border_frame,
        "left_border_source_change_episodes":border_episode,
        "first_source_new_palette6_near_underflow":first_new6,
        "original_prepour_selected_regions":selected(pre),
        "limits":"Source pixel changes are observational, not a decoded fluid model or success rule.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    records=[];stacks_all={};roots=set()
    for case,program in FROZEN:
        parsed=parse_plan(program)
        for witness,entry in STAGE1_WITNESSES:
            result,stacks=run_case(case,witness,entry,program)
            roots.add(result["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=stacks["entry3_34"][-1]
            pre=stacks.get("stage4_"+str(len(parsed)-1),stacks["entry3_34"])[-1]
            returned=stacks["stage4_"+str(len(parsed))]
            obs=read_original(root,pre,returned)
            actual_step_selection=[
                {"sdk_step":e["index"],"action":e["genuine_original_action"],
                 "click_xy":e["real_native_click_xy"],
                 "original_native_preclick_palette":e["original_source_pixel_before_click"],
                 "genuine_source_after_hash":e["source_frame_after_blake2b16"],
                 "native_selected_regions_after":selected(stacks["stage4_"+str(e["index"])][-1])}
                for e in result["genuine_original_stage4_action_ledger"]
                if e["genuine_original_action"] in (1,2,3,4,6)
            ]
            record={
                "frozen_original_sdk_case":case,
                "authentic_independent_stage4_witness":witness,
                "original_native_stage4_word":program,
                "official_original_sdk_final_level":result["true_original_sdk_final_level"],
                "official_original_sdk_final_state":result["true_original_sdk_final_state"],
                "native_original_level5_or_WIN":result["official_original_level5_or_WIN"],
                "actual_original_source_frame_metrics":obs,
                "actual_original_native_selected_movements":actual_step_selection,
                "genuine_original_sdk_action_receipts":result["genuine_original_stage4_action_ledger"],
            }
            records.append(record)
            for name,frames in stacks.items():stacks_all[f"{case}_{witness}_{name}"]=frames
            print("ORIGINAL_SP80_UNDERFLOW_INTERCEPT_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_level":record["official_original_sdk_final_level"],
                "official_state":record["official_original_sdk_final_state"],
                "source":obs,"native_selection":actual_step_selection,
            },sort_keys=True),flush=True)
    if len(records)!=40 or len(roots)!=1:raise AssertionError("Actual original SDK native entry roots mismatch")
    for case,_ in FROZEN:
        pair=[r for r in records if r["frozen_original_sdk_case"]==case]
        if len(pair)!=2 or (
            pair[0]["official_original_sdk_final_level"]!=pair[1]["official_original_sdk_final_level"]
            or pair[0]["official_original_sdk_final_state"]!=pair[1]["official_original_sdk_final_state"]
            or pair[0]["actual_original_source_frame_metrics"]!=pair[1]["actual_original_source_frame_metrics"]
            or pair[0]["actual_original_native_selected_movements"]!=pair[1]["actual_original_native_selected_movements"]
        ):raise AssertionError("Genuine original independent SDK witnesses differ "+case)
    successes=[{
        "case":r["frozen_original_sdk_case"],
        "witness":r["authentic_independent_stage4_witness"],
        "actual_original_stage4_word":r["original_native_stage4_word"],
        "official_level":r["official_original_sdk_final_level"],
        "official_state":r["official_original_sdk_final_state"]}
        for r in records if r["native_original_level5_or_WIN"]]
    four=[
        {"case":r["frozen_original_sdk_case"],"witness":r["authentic_independent_stage4_witness"],
         "left_boundary_first":r["actual_original_source_frame_metrics"]["first_left_border_source_change"]}
        for r in records if all(v==45 for v in r["actual_original_source_frame_metrics"]["actual_original_cup_color13_max"].values())
    ]
    summary={
        "kind":"AUTHENTIC_ORIGINAL_SP80_LEVEL4_LATERAL_CUP_UNDERFLOW_INTERCEPT",
        "source_antecedent_original_run":39628603248,
        "genuine_original_sdk_resets":len(records),
        "predeclared_sdk_source_words":FROZEN,
        "original_source_stage4_root_blake2b16":next(iter(roots)),
        "genuine_original_sdk_level5_or_WIN_count":len(successes),
        "true_original_sdk_progress_witnesses":successes,
        "native_all_four_cup_visual_cases":four,
        "official_original_level_histogram":dict(Counter(str(r["official_original_sdk_final_level"]) for r in records)),
        "official_original_state_histogram":dict(Counter(str(r["official_original_sdk_final_state"]) for r in records)),
        "full_source_original_native_receipts":records,
        "limits":"Native SDK official level>=5 or WIN alone signifies progress; cup palette and boundary masks are not a substitute or proved fluid physics.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**stacks_all)
    print("ORIGINAL_SP80_UNDERFLOW_INTERCEPT_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("predeclared_sdk_source_words","full_source_original_native_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":
    main()
