"""Original SP80 SDK: localize the downstream right edge of the catcher.

Original source frames from native run #39600351518 (PR #363)
directly show a four-cup/no-stage4 arrangement:
* linked middle x10,30: right4/up1;
* bottom catcher x40,42: left2/up3, selected bbox x32..43/y32..34;
* original palette6 first descends at x44..46,y32 after upper contacts,
  continues along the right of the catcher, and then newly appears
  at x47..49,y56..58 on source animation frame27;
* original y59..62 bottom-line color changes at frame28.
This is measured original SDK imagery, not decoded fluid causation.

Direct next intervention: alter the ACTUAL right-hand extent and
vertical placement of that one original catcher, while holding the
linked middle and the other four native selection groups fixed.
Controls alter only the linked middle, far-left receiver or upper bar.
The only valid progression oracle is actual original SDK level>=4/WIN.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

UPPER_SELECTED = "6@20,18 4 4 2"
UPPER_OTHER = "6@40,18 2"
MIDDLE_UP1 = "6@10,30 4 4 4 4 1"
RECEIVER_UP1_LEFT10 = "6@46,33 1 " + " ".join(["3"]*10)
CUP_WINDOWS=((8,16),(26,34),(38,46),(50,58))
OBSERVE_ROWS=(19,26,29,32,35,38,41,44,47,50,52,55,56,58)

def catcher(left,up,vertical_first=False):
    assert 1<=left<=3 and 1<=up<=5
    horizontal=["3"]*left
    vertical=["1"]*up
    return " ".join(["6@40,42",*(vertical+horizontal if vertical_first else horizontal+vertical)])

def receiving_bar(left=10,vertical=-1):
    assert 8<=left<=12 and -2<=vertical<=0
    moves=([str(1)]*(-vertical) if vertical<0 else [])
    return " ".join(["6@46,33",*moves,*["3"]*left])

def source_word(catch_left=2,catch_up=3,
                mid=MIDDLE_UP1,receiver=RECEIVER_UP1_LEFT10,
                selected=UPPER_SELECTED,other=UPPER_OTHER,
                vertical_first=False):
    return " ".join((
        selected,other,mid,receiver,
        catcher(catch_left,catch_up,vertical_first),
        "5",
    ))

FROZEN=(
    *(
        (f"catch_left{left}_up{up}",source_word(catch_left=left,catch_up=up))
        for left in (1,2,3) for up in (2,3,4)
    ),
    *(
        (f"catch_left{left}_up{up}",source_word(catch_left=left,catch_up=up))
        for left in (2,3) for up in (1,5)
    ),
    ("middle_right4_held_catch_left2_up3",
     source_word(mid="6@10,30 4 4 4 4")),
    ("middle_right4_up2_catch_left2_up3",
     source_word(mid="6@10,30 4 4 4 4 1 1")),
    ("middle_right4_down1_catch_left2_up3",
     source_word(mid="6@10,30 4 4 4 4 2")),
    ("middle_right3_catch_left2_up3",
     source_word(mid="6@10,30 4 4 4")),
    ("middle_right5_up1_catch_left2_up3",
     source_word(mid="6@10,30 4 4 4 4 4 1")),
    *(
        (f"receiver_left{left}_catch_left2_up3",
         source_word(receiver=receiving_bar(left=left)))
        for left in (9,11)
    ),
    ("receiver_heldheight_left10_catch_left2_up3",
     source_word(receiver=receiving_bar(left=10,vertical=0))),
    ("receiver_up2_left10_catch_left2_up3",
     source_word(receiver=receiving_bar(left=10,vertical=-2))),
    ("upfirst_catch_left2_up3",
     source_word(catch_left=2,catch_up=3,vertical_first=True)),
    ("upper_selected_down2_catch_left2_up3",
     source_word(selected="6@20,18 4 4 2 2")),
    ("upper_other_down2_catch_left2_up3",
     source_word(other="6@40,18 2 2")),
)
assert len(FROZEN)==25==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(word)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(word))==1
    and all(xy is not None for a,xy in parse_plan(word) if a==6)
    and len(parse_plan(word))<=40
    for _,word in FROZEN
)

def intervals(xs):
    xs=list(map(int,xs))
    if not xs:return []
    out=[];lo=last=xs[0]
    for x in xs[1:]:
        if x>last+1:
            out.append([lo,last]);lo=x
        last=x
    out.append([lo,last])
    return out

def measure_source(pre,frames):
    if pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Original SDK 64x64 pre/pour frames required")
    first_cups=[None]*4
    first_all=None
    first_bottom=None
    bottom_episodes=[]
    was_bottom=False
    first_new_right={str(y):None for y in OBSERVE_ROWS}
    first_at_contact=None
    third_cup_max=0
    for i,f in enumerate(frames):
        source_new=(pre!=6)&(f==6)
        for row in OBSERVE_ROWS:
            xs=np.flatnonzero(source_new[row,40:62])+40
            if first_new_right[str(row)] is None and xs.size:
                first_new_right[str(row)]={
                    "original_sdk_frame":i,
                    "actual_source_new_palette6_x_intervals":intervals(xs),
                }
        if first_at_contact is None and source_new[32,44:47].any():
            first_at_contact={
                "original_sdk_frame":i,
                "actual_source_new_palette6_x":list(map(
                    int,np.flatnonzero(source_new[32,44:47])+44
                )),
            }
        counts=[
            int(np.count_nonzero(
                (pre[53:59,lo:hi+1]==11)&(f[53:59,lo:hi+1]==13)
            )) for lo,hi in CUP_WINDOWS
        ]
        third_cup_max=max(third_cup_max,counts[2])
        for k,val in enumerate(counts):
            if val==45 and first_cups[k] is None:first_cups[k]=i
        if first_all is None and all(val==45 for val in counts):first_all=i
        actual_change=pre[59:63,2:62]!=f[59:63,2:62]
        active=bool(actual_change.any())
        if active and not was_bottom:bottom_episodes.append(i)
        was_bottom=active
        if active and first_bottom is None:
            first_bottom={
                "original_sdk_frame":i,
                "actual_source_changed_bottom_pixel_count":int(actual_change.sum()),
                "actual_new_palette6_y56_intervals":intervals(np.flatnonzero(source_new[56])),
                "actual_new_palette6_y58_intervals":intervals(np.flatnonzero(source_new[58])),
            }
    comps=[
        {"palette":c["palette"],"bbox":c["bbox"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9) and 14<=c["bbox"][1]<=54
    ]
    return {
        "original_pre_pour_blake2b16":hash_frame(pre),
        "original_after_pour_blake2b16":hash_frame(frames[-1]),
        "original_sdk_source_frame_count":len(frames),
        "actual_native_pre_pour_components":comps,
        "first_right_contact_source_new6_x44_46_y32":first_at_contact,
        "first_new_right_original_source_by_row":first_new_right,
        "original_source_each_cup_first_full_frame":first_cups,
        "original_source_third_cup_max_changed_pixels":third_cup_max,
        "original_first_four_visually_full_cup_frame":first_all,
        "first_genuine_tested_source_bottom_change":first_bottom,
        "source_bottom_change_episode_frames":bottom_episodes,
        "scope":"Actual original SDK pixels are partial observational evidence, not decoded physics or level objective.",
    }

def self_test():
    assert intervals([])==[]
    assert intervals([2,3,7,10,11])==[[2,3],[7,7],[10,11]]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    self_test()
    rows=[];arrays={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            trial,source=real_trial(witness,entry,case,word)
            roots.add(trial["original_verified_stage3_root"]["original_source_sha256"])
            returned=source.get("stage3_"+str(n))
            before=source.get("stage3_"+str(n-1),source["entry2_11"])[-1]
            measured=measure_source(before,returned) if returned is not None else None
            row={
                "original_precommitted_sdk_case":case,
                "real_native_entry_witness":witness,
                "actual_original_sdk_word":word,
                "original_sdk_official_final_level":trial["official_original_final_level"],
                "original_sdk_official_final_state":trial["official_original_final_state"],
                "genuine_sdk_level4_or_WIN":trial["official_original_level4_or_WIN"],
                "original_sdk_trial_disposition":trial["trial_disposition"],
                "genuine_original_frame_evidence":measured,
                "true_original_sdk_action_ledger":[
                    {k:v for k,v in event.items() if k!="full_original_source_frame_ledger"}
                    for event in trial["original_stage3_intervention_events"]
                ],
            }
            rows.append(row)
            for name,stack in source.items():
                arrays[f"{case}_{witness}_{name}"]=stack
            print("ORIGINAL_SP80_EDGE_CONTACT_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_level":row["original_sdk_official_final_level"],
                "official_state":row["original_sdk_official_final_state"],
                "source":measured,
            },sort_keys=True),flush=True)
    if len(rows)!=50 or len(roots)!=1:
        raise AssertionError("Missing independently reset original SP80 source witnesses")
    for case,_ in FROZEN:
        matches=[r for r in rows if r["original_precommitted_sdk_case"]==case]
        if len(matches)!=2 or (
            matches[0]["original_sdk_official_final_level"]!=matches[1]["original_sdk_official_final_level"]
            or matches[0]["original_sdk_official_final_state"]!=matches[1]["original_sdk_official_final_state"]
            or matches[0]["genuine_original_frame_evidence"]!=matches[1]["genuine_original_frame_evidence"]
        ):
            raise AssertionError("Original independent A/B source mismatch: "+case)
    gains=[
        {"case":r["original_precommitted_sdk_case"],
         "witness":r["real_native_entry_witness"],
         "word":r["actual_original_sdk_word"],
         "official_level":r["original_sdk_official_final_level"],
         "official_state":r["original_sdk_official_final_state"]}
        for r in rows if r["genuine_sdk_level4_or_WIN"]
    ]
    four_clean=[
        {"case":r["original_precommitted_sdk_case"],
         "witness":r["real_native_entry_witness"]}
        for r in rows
        if r["genuine_original_frame_evidence"] is not None
        and r["genuine_original_frame_evidence"]["original_first_four_visually_full_cup_frame"] is not None
        and r["genuine_original_frame_evidence"]["first_genuine_tested_source_bottom_change"] is None
    ]
    summary={
        "kind":"AUTHENTIC_ORIGINAL_SP80_STAGE3_RIGHT_CATCHER_EDGE_CONTACT",
        "native_source_antecedent_run":39600351518,
        "genuine_original_sdk_resets":len(rows),
        "prospectively_frozen_original_words":FROZEN,
        "true_native_stage3_source_root_blake2b16":next(iter(roots)),
        "official_original_sdk_level4_or_WIN_count":len(gains),
        "true_original_sdk_advances":gains,
        "visual_four_cups_no_tested_bottom_change":four_clean,
        "actual_official_original_level_histogram":dict(Counter(str(r["original_sdk_official_final_level"]) for r in rows)),
        "actual_official_original_state_histogram":dict(Counter(str(r["original_sdk_official_final_state"]) for r in rows)),
        "genuine_sdk_original_action_and_frame_receipts":rows,
        "limits":"Only actual original SDK official levels_completed>=4 or WIN demonstrates progress. Colors, cup windows and bottom region are bounded source observations not an engine simulation or a proven physical contact law. Full original returned frame stacks retained in NPZ.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_EDGE_CONTACT_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospectively_frozen_original_words","genuine_sdk_original_action_and_frame_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
