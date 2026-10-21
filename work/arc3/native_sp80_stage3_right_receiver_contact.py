"""Authentic SP80 SDK: lower-right receiving bar intercept at first new source branch.

Native #39562263772 first observed right-hand fourth-cup source-only
palette6 x53..55 by y26/29 (from a new x38..40,y17..19 interval,
frame9). Previous near-miss positions the original receiver bar by TEN
left moves from source initial bbox x44..55,y32..34 to x14..25,
so it cannot directly intercept that observed right branch at y32.
The upward bottom catcher branch #39563486480 did not change the
four-cup right spill signature across distinct bar heights.

NEW source-targeted contrast: keep the measured four-cup upstream
source configuration, retain or shift the ORIGINAL lower-right
receiver near the observed x53..55,y29..35 branch instead of moving
it ten steps left. Test true SDK output, not an invented physics model.
Only official source level>=4 or WIN counts as stage3 progress.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

UPPER="6@20,18 4 4 2 6@40,18 2"
MIDDLE="6@10,30 4 4 4 4"
CUPS=((8,16),(26,34),(38,46),(50,58))
ROWS=(19,26,29,32,35,41,47,52,56,58)

def lower(horizontal=0,steps=0,vertical=0,vertical_first=False):
    moves=([vertical]*abs(vertical) if vertical else [])
    # Vertical sign uses native actions, not signed scalar movement.
    vertical_words=([1]*(-vertical) if vertical<0 else [2]*vertical)
    horizontal_words=[horizontal]*steps
    word=vertical_words+horizontal_words if vertical_first else horizontal_words+vertical_words
    return " ".join(["6@46,33",*map(str,word)])

def bottom(right=1):
    return "6@40,42 "+" ".join(["4"]*right)

def plan(receiver,br):
    return " ".join((UPPER,MIDDLE,receiver,bottom(br),"5"))

# Selected x44..55,y32..34 original receiver can intersect an
# observed source branch near x53..55,y29..35.
FROZEN=(
    ("receiver_held_bottom1",plan(lower(),1)),
    ("receiver_held_bottom2",plan(lower(),2)),
    *( (f"receiver_left{k}_bottom{br}",plan(lower(3,k),br))
       for k in (1,2,3) for br in (1,2) ),
    *( (f"receiver_right{k}_bottom{br}",plan(lower(4,k),br))
       for k in (1,2) for br in (1,2) ),
    ("receiver_up1_bottom1",plan(lower(vertical=-1),1)),
    ("receiver_down1_bottom1",plan(lower(vertical=1),1)),
    ("receiver_up2_bottom1",plan(lower(vertical=-2),1)),
    ("receiver_down2_bottom1",plan(lower(vertical=2),1)),
    ("receiver_right1_up1_bottom2",plan(lower(4,1,-1),2)),
    ("receiver_right1_down1_bottom2",plan(lower(4,1,1),2)),
)
assert len(FROZEN)==18==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(w)[-1][0]==5 and sum(a==5 for a,xy in parse_plan(w))==1
           and len(parse_plan(w))<=28
           and all(xy is not None for a,xy in parse_plan(w) if a==6)
           for _,w in FROZEN)

def source_evidence(pre,animation):
    if pre.shape!=(64,64) or animation.ndim!=3 or animation.shape[1:]!=(64,64):
        raise AssertionError("Only authentic original SDK returned animation")
    first_cups=[None]*4;first_four=None;first_boundary=None
    first_right={str(y):None for y in ROWS}
    for t,frame in enumerate(animation):
        new_source=(pre!=6)&(frame==6)
        for y in ROWS:
            xs=np.flatnonzero(new_source[y,50:62])+50
            if first_right[str(y)] is None and xs.size:
                first_right[str(y)]={"original_frame":t,"actual_new_source_palette6_x":list(map(int,xs))}
        counts=[
            int(np.count_nonzero((pre[53:59,lo:hi+1]==11)&(frame[53:59,lo:hi+1]==13)))
            for lo,hi in CUPS
        ]
        for i,n in enumerate(counts):
            if n==45 and first_cups[i] is None:first_cups[i]=t
        if first_four is None and all(n==45 for n in counts): first_four=t
        border=(pre[59:63,2:62]!=frame[59:63,2:62])
        if border.any() and first_boundary is None:
            first_boundary={
                "original_frame":t,"original_bottom_changed_pixels":int(border.sum()),
                "first_bottom_source_palette6_x":list(map(int,np.flatnonzero(new_source[58]))),
            }
    components=[
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9) and 20<=c["bbox"][1]<=54
    ]
    return {
        "source_original_prepour_blake2b16":hash_frame(pre),
        "source_original_postpour_blake2b16":hash_frame(animation[-1]),
        "original_frame_count":len(animation),
        "actual_original_pre_pour_components":components,
        "original_visual_first_full_cups":first_cups,
        "first_four_visual_cup_frame":first_four,
        "first_tested_original_bottom_change":first_boundary,
        "first_actual_right_source_pixel_at_rows":first_right,
        "limits":"Source pixel observation is not a decoded causal liquid model or game success predicate.",
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows=[];raw={};roots=set()
    for name,word in FROZEN:
        steps=parse_plan(word)
        for witness,entry in STAGE1_WITNESSES:
            original,frames=real_trial(witness,entry,name,word)
            roots.add(original["original_verified_stage3_root"]["original_source_sha256"])
            pour=frames.get("stage3_"+str(len(steps)))
            prior=frames.get("stage3_"+str(len(steps)-1),frames["entry2_11"])[-1]
            measured=source_evidence(prior,pour) if pour is not None else None
            row={
                "native_precommitted_case":name,"independent_original_witness":witness,
                "original_sdk_action_word":word,
                "official_sdk_level":original["official_original_final_level"],
                "official_sdk_state":original["official_original_final_state"],
                "official_sdk_level4_or_WIN":original["official_original_level4_or_WIN"],
                "actual_original_source_animations":measured,
                "original_sdk_source_action_receipts":[
                    {k:v for k,v in e.items() if k!="full_original_source_frame_ledger"}
                    for e in original["original_stage3_intervention_events"]],
            }
            rows.append(row)
            for phase,stack in frames.items():raw[f"{name}_{witness}_{phase}"]=stack
            print("ORIGINAL_SP80_RIGHT_RECEIVER_CASE "+json.dumps({
                "case":name,"witness":witness,
                "level":row["official_sdk_level"],"state":row["official_sdk_state"],
                "source":measured,
            },sort_keys=True),flush=True)
    if len(rows)!=36 or len(roots)!=1:raise AssertionError("Original independent SDK source witness missing")
    wins=[{"case":x["native_precommitted_case"],"witness":x["independent_original_witness"],"word":x["original_sdk_action_word"]}
          for x in rows if x["official_sdk_level4_or_WIN"]]
    candidates=[{"case":x["native_precommitted_case"],"witness":x["independent_original_witness"]}
          for x in rows if x["actual_original_source_animations"] is not None
          and x["actual_original_source_animations"]["first_four_visual_cup_frame"] is not None
          and x["actual_original_source_animations"]["first_tested_original_bottom_change"] is None]
    result={
        "kind":"ORIGINAL_SP80_STAGE3_RIGHT_RECEIVER_FIRST_NEW_BRANCH",
        "source_antecedent_native_trial":39562263772,
        "original_sdk_independent_reset_games":len(rows),
        "frozen_source_words":FROZEN,
        "original_source_root_blake2b16":next(iter(roots)),
        "native_official_level4_or_WIN_count":len(wins),
        "original_official_progress_witnesses":wins,
        "source_visual_only_four_cups_no_test_boundary_cases":candidates,
        "real_sdk_level_histogram":dict(Counter(str(x["official_sdk_level"]) for x in rows)),
        "real_sdk_state_histogram":dict(Counter(str(x["official_sdk_state"]) for x in rows)),
        "original_native_full_action_receipts":rows,
        "limits":"Only original SDK level>=4 or WIN qualifies. Color interval measurements are not game physics. Preserve all original SDK returned native frame arrays NPZ, no other lane modifications.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("ORIGINAL_SP80_RIGHT_RECEIVER_SUMMARY "+json.dumps({k:v for k,v in result.items() if k not in ("frozen_source_words","original_native_full_action_receipts")},sort_keys=True))

if __name__=="__main__":
    main()
