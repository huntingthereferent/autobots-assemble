"""Original ARC3 SP80 stage3: source-measured two-stream contact timing.

This experiment is a bounded successor to native runs #39553891447 and
#39554383725, NOT an alternative physics model, image-only solver or
claimed level advance. Authentic level3 source frame has top fixed palette4
spout x23..25 and middle palette4 marker x17..19. Native ACTION5 returns
actual 64x64 frame stacks. Source-only flow observations at y16,19,26,29,
35,41,52,55,58 and pixel timing are measured, not inferred semantics.

Change joint height of upper bar (where early source branch contacts
observed upper row) and linked middle marked piece (second native stream).
One original ACTION5 per independent game; only native SDK level4 or WIN
qualifies. The exact 20 plans below are frozen prior to SDK execution.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

# Original source geometry / clicks verified by level3 source map.
UPPER=(
    ("selected_right2","6@20,18 4 4"),
    ("other_left2","6@40,18 3 3"),
)
MID_RIGHT4="6@10,30 4 4 4 4"
LOWER_LEFT10="6@46,33 "+" ".join(["3"]*10)
BOTTOM_RIGHT2="6@40,42 4 4"
VERTICAL=(("up1",1),("held",None),("down1",2))
SOURCE_ROWS=(16,19,26,29,35,41,52,55,58)
CUPS=((8,16),(26,34),(38,46),(50,58))

def vertical_tail(direction):
    return "" if direction is None else " "+str(direction)

def plan(uword,udir,mdir):
    return " ".join([
        uword+vertical_tail(udir),
        MID_RIGHT4+vertical_tail(mdir),
        LOWER_LEFT10,BOTTOM_RIGHT2,"5",
    ])

FROZEN=tuple(
    (f"{uname}_upper_{uh}_mid_{mh}",plan(uword,ud,md))
    for uname,uword in UPPER
    for uh,ud in VERTICAL
    for mh,md in VERTICAL
)+(
    # Heldout ordering controls at identical commanded total displacement.
    ("selected_up1_before_right2_mid_held"," ".join([
        "6@20,18 1 4 4",MID_RIGHT4,LOWER_LEFT10,BOTTOM_RIGHT2,"5"])),
    ("other_down1_before_left2_mid_held"," ".join([
        "6@40,18 2 3 3",MID_RIGHT4,LOWER_LEFT10,BOTTOM_RIGHT2,"5"])),
)
assert len(FROZEN)==20==len(set(n for n,_ in FROZEN))
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(w)[-1][0]==5
    and sum(a==5 for a,_ in parse_plan(w))==1
    and all(xy is not None for a,xy in parse_plan(w) if a==6)
    and len(parse_plan(w))<=32
    for _,w in FROZEN
)

def runs(xs):
    """Consecutive pixel x intervals, no assertion of source connectivity."""
    if len(xs)==0:return []
    s=int(xs[0]);p=s;out=[]
    for val in xs[1:]:
        v=int(val)
        if v>p+1:
            out.append([s,p]);s=v
        p=v
    out.append([s,p])
    return out

def observe_source(pre,animation):
    if pre.shape!=(64,64) or animation.ndim!=3:
        raise AssertionError("Expected actual original SDK 64x64 frame stack")
    arrivals={str(y):None for y in SOURCE_ROWS}
    first_two_intervals={str(y):None for y in SOURCE_ROWS}
    first_bottom=None
    first_four=None
    per_cup=[None]*4
    simultaneous_max=0
    for t,frame in enumerate(animation):
        if frame.shape!=pre.shape:
            raise AssertionError("Source animation frame geometry differs")
        # New source blue pixels in a fixed observation row, relative to
        # authentic immediately-pre-pour SDK pixels (not computed fluid).
        for y in SOURCE_ROWS:
            mask=(pre[y]!=6)&(frame[y]==6)
            segments=runs(np.flatnonzero(mask))
            ky=str(y)
            if segments and arrivals[ky] is None:
                arrivals[ky]={"frame":t,"observed_x_intervals":segments}
            if len(segments)>=2 and first_two_intervals[ky] is None:
                first_two_intervals[ky]={"frame":t,"observed_x_intervals":segments}
        counts=[
            int(np.count_nonzero((pre[53:59,lo:hi+1]==11)&
                                    (frame[53:59,lo:hi+1]==13)))
            for lo,hi in CUPS
        ]
        for i,value in enumerate(counts):
            if value==45 and per_cup[i] is None:per_cup[i]=t
        number=sum(value==45 for value in counts)
        simultaneous_max=max(simultaneous_max,number)
        if number==4 and first_four is None:first_four=t
        changed=(pre[59:63,2:62]!=frame[59:63,2:62])
        if first_bottom is None and changed.any():
            first_bottom={
                "frame":t,
                "genuine_sdk_changed_pixels":int(changed.sum()),
                "new_source_palette6_x_at_y58":[int(v) for v in
                    np.flatnonzero((pre[58]!=6)&(frame[58]==6))],
            }
    components=[
        {"palette":c["palette"],"bbox":c["bbox"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9) and c["bbox"][1]<=52
    ]
    return {
        "original_sdk_prepour_blake2b16":hash_frame(pre),
        "original_sdk_postpour_blake2b16":hash_frame(animation[-1]),
        "genuine_sdk_animation_frame_count":len(animation),
        "actual_prepour_palette4_8_9_components":components,
        "first_new_source_palette6_at_y":arrivals,
        "first_multiple_disjoint_new_source6_x_intervals_at_y":first_two_intervals,
        "first_four_source_cup_regions_same_frame":first_four,
        "max_source_cup_regions_same_frame":simultaneous_max,
        "first_actual_palette11_to13_cup_frames":per_cup,
        "first_genuine_bottom_region_change":first_bottom,
        "limitation":"Pixel intervals mean only source palette6 frame changes. They do not establish physical splitting, a leak cause, or a win rule.",
    }

def self_test():
    assert runs(np.array([],dtype=int))==[]
    assert runs(np.array([2,3,4,9,11,12]))==[[2,4],[9,9],[11,12]]
    pre=np.zeros((64,64),dtype=np.uint8)
    post=np.stack([pre.copy() for _ in range(3)])
    post[1,16,2:5]=6
    post[2,16,2:5]=6;post[2,16,9:12]=6
    measured=observe_source(pre,post)
    assert measured["first_new_source_palette6_at_y"]["16"]["frame"]==1
    assert measured["first_multiple_disjoint_new_source6_x_intervals_at_y"]["16"]["frame"]==2
    assert measured["first_genuine_bottom_region_change"] is None

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    self_test()
    records=[];raw_arrays={};roots=set()
    for case,word in FROZEN:
        length=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            source,stacks=real_trial(witness,entry,case,word)
            roots.add(source["original_verified_stage3_root"]["original_source_sha256"])
            frames=stacks.get("stage3_"+str(length))
            pre=stacks.get("stage3_"+str(length-1),stacks["entry2_11"])[-1]
            visual=observe_source(pre,frames) if frames is not None else None
            row={
                "frozen_source_case":case,
                "independent_actual_original_witness":witness,
                "original_native_action_word":word,
                "true_original_sdk_final_level":source["official_original_final_level"],
                "true_original_sdk_final_state":source["official_original_final_state"],
                "source_original_level4_or_WIN":source["official_original_level4_or_WIN"],
                "native_trial_disposition":source["trial_disposition"],
                "native_original_frame_observations":visual,
                "actual_original_sdk_action_receipts":[
                    {k:v for k,v in event.items()
                     if k!="full_original_source_frame_ledger"}
                    for event in source["full_original_sdk_action_events"]
                ],
            }
            records.append(row)
            for key,stack in stacks.items():
                raw_arrays[f"{case}_{witness}_{key}"]=stack
            print("ORIGINAL_SP80_TWO_STREAM_CONTACT_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_level":row["true_original_sdk_final_level"],
                "official_state":row["true_original_sdk_final_state"],
                "source_observation":visual,
            },sort_keys=True),flush=True)
    if len(records)!=40 or len(roots)!=1:
        raise AssertionError("Missing original SDK independent source reset witnesses")
    actual_advances=[
        {"case":r["frozen_source_case"],"witness":r["independent_actual_original_witness"],
         "official_sdk_level":r["true_original_sdk_final_level"],
         "official_sdk_state":r["true_original_sdk_final_state"],
         "native_original_word":r["original_native_action_word"]}
        for r in records if r["source_original_level4_or_WIN"]
    ]
    source_fours_no_boundary=[
        {"case":r["frozen_source_case"],"witness":r["independent_actual_original_witness"]}
        for r in records if r["native_original_frame_observations"] is not None
        and r["native_original_frame_observations"]["max_source_cup_regions_same_frame"]==4
        and r["native_original_frame_observations"]["first_genuine_bottom_region_change"] is None
    ]
    result={
        "kind":"AUTHENTIC_ORIGINAL_SP80_STAGE3_UPPER_AND_MIDDLE_CONTACT_TIMING",
        "recorded_original_source_antecedent_runs":[39553891447,39554383725],
        "independent_genuine_original_sdk_reset_games":len(records),
        "prospective_source_action_words":FROZEN,
        "original_native_stage3_root_blake2b16":next(iter(roots)),
        "actual_original_sdk_level4_or_WIN_count":len(actual_advances),
        "genuine_native_progress_records":actual_advances,
        "visual_only_four_cups_no_test_boundary_cases":source_fours_no_boundary,
        "official_original_sdk_end_levels":dict(Counter(str(r["true_original_sdk_final_level"]) for r in records)),
        "official_original_sdk_end_states":dict(Counter(str(r["true_original_sdk_final_state"]) for r in records)),
        "true_original_SDK_source_records":records,
        "limits":"Actual pixel row arrival/disjointness is not a decoded stream bifurcation or physical mechanism; only the SDK's official level>=4/WIN is progress. Raw original returned frames in NPZ; no invented engine, change to other lanes or license.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw_arrays)
    print("ORIGINAL_SP80_TWO_STREAM_CONTACT_SUMMARY "+json.dumps({
        k:v for k,v in result.items()
        if k not in ("prospective_source_action_words","true_original_SDK_source_records")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
