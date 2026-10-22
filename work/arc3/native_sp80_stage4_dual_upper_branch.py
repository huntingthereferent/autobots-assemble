"""Native original SP80 level4: coupled removal of two visible off-cup top strands.

Source-archived original Arcade.NORMAL SDK native #39639320303 shows that
true TOP LEFT6 moves the selected 36-pixel top bar to bbox x11..22/y20..22
and eliminates the former x11..13/y5 stream, but does not eliminate
top/right border palette1->14 or advance the official level4.

Independently native run #39636999616 showed RIGHT-MIDDLE LEFT2
eliminates new x56..58/y5 strand (present at RIGHT-MIDDLE LEFT1)
while all four visible cup windows can still fill, without eliminating
the top/right border. The two separate controls have NOT previously
been combined in the same source level4 game.

Original native #39639320303 frames also measure FIRST new fluid6
at row y5 one frame before the original source top-border transition
for all reviewed parent/control variants, even though the x-column
and animation time move. This is an empirical temporal correlation,
not proof of hidden engine rules.

Freeze a small actual SDK upper top+right-middle interaction experiment
on both independently source-proven clean-four-cup lower arrangements;
record first new source palette6 OUTSIDE original upper cup windows at
row y5, individual columns, full cup timing, all border changes and
ACTUAL SDK level. Never substitute image pixels for SDK victory.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

PARENTS=(
    ("middleD3L2_L3U2","6@24,33 2 2 2 3 3","6@34,42 3 3 3 1 1"),
    ("middleD4L2_L4U2","6@24,33 2 2 2 2 3 3","6@34,42 3 3 3 3 1 1"),
)
# One earlier original-source anchor + 12 FIRST paired-intervention
# controls in each of the two independent clean lower geometries.
COMBOS=(
    ("source_anchor_topL1_rightL1","3","3"),
    ("topL5_rightL2","3 3 3 3 3","3 3"),
    ("topL5_rightL3","3 3 3 3 3","3 3 3"),
    ("topL6_rightL2","3 3 3 3 3 3","3 3"),
    ("topL6_rightL3","3 3 3 3 3 3","3 3 3"),
    ("topL7_rightL2","3 3 3 3 3 3 3","3 3"),
    ("topL7_rightL3","3 3 3 3 3 3 3","3 3 3"),
    ("topL8_rightL2","3 3 3 3 3 3 3 3","3 3"),
    ("topL8_rightL3","3 3 3 3 3 3 3 3","3 3 3"),
    ("topL6_rightL2_up1","3 3 3 3 3 3","3 3 1"),
    ("topL6_rightL2_down1","3 3 3 3 3 3","3 3 2"),
    ("topL7_rightL2_up1","3 3 3 3 3 3 3","3 3 1"),
    ("topL7_rightL2_down1","3 3 3 3 3 3 3","3 3 2"),
)
FROZEN=tuple(
    (f"{parent}_{test}",
     " ".join(("6@46,33 "+r_moves,middle,l_shaped,
               "6@34,21 "+top_moves,"5")))
    for parent,middle,l_shaped in PARENTS
    for test,top_moves,r_moves in COMBOS
)
assert len(FROZEN)==26==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(word)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(word))==1
    and all(xy is not None for a,xy in parse_plan(word) if a==6)
    and len(parse_plan(word))<=30
    for _,word in FROZEN
)
CUPS={
    "lateral_left":(5,35,10,43),
    "top_left":(17,5,25,10),
    "top_middle":(35,5,43,10),
    "top_right":(47,5,55,10),
}
EDGES={
    "left":(slice(2,62),slice(2,5)),
    "right":(slice(2,62),slice(59,62)),
    "top":(slice(2,5),slice(2,62)),
    "bottom":(slice(59,62),slice(2,62)),
}
SITES=((8,10),(11,13),(14,16),(20,22),(26,28),(32,34),
       (38,40),(44,46),(50,52),(56,58))

def bands(xs):
    xs=list(map(int,xs))
    if not xs:return []
    spans=[];start=last=xs[0]
    for x in xs[1:]:
        if x>last+1:
            spans.append([start,last])
            start=x
        last=x
    spans.append([start,last])
    return spans

def selected(frame):
    return [
        {"palette":c["palette"],"bbox":c["bbox"],"pixels":c["pixels"]}
        for c in color_components(frame)
        if c["palette"]==9 and 16<=c["bbox"][1]<=55
    ]

def metrics(root,pre,frames):
    if (root.shape!=(64,64) or pre.shape!=(64,64)
        or frames.ndim!=3 or frames.shape[1:]!=(64,64)):
        raise AssertionError("Actual original SDK source frame size expected")
    outside_top=(root[5,5:59]!=11)
    full={k:None for k in CUPS}
    max_pixels={k:0 for k in CUPS}
    four_simultaneous=None
    first_offcup_row5=None
    first_y5_fullrow=None
    first_y8_fullrow=None
    first_sites={f"x{lo}_{hi}":None for lo,hi in SITES}
    borders={k:None for k in EDGES}
    episodes={k:[] for k in EDGES}
    previously={k:False for k in EDGES}
    for t,frame in enumerate(frames):
        new6=(pre!=6)&(frame==6)
        y5=np.flatnonzero(new6[5,5:59])+5
        y8=np.flatnonzero(new6[8,5:59])+5
        off=np.flatnonzero(new6[5,5:59] & outside_top)+5
        if y5.size and first_y5_fullrow is None:
            first_y5_fullrow={"frame":t,"new_source6_x_bands":bands(y5)}
        if y8.size and first_y8_fullrow is None:
            first_y8_fullrow={"frame":t,"new_source6_x_bands":bands(y8)}
        if off.size and first_offcup_row5 is None:
            first_offcup_row5={"frame":t,"new_source6_offcup_x_bands":bands(off)}
        for lo,hi in SITES:
            key=f"x{lo}_{hi}"
            if first_sites[key] is None and new6[5,lo:hi+1].any():
                first_sites[key]=t
        nfull=0
        for name,(x0,y0,x1,y1) in CUPS.items():
            mask=root[y0:y1+1,x0:x1+1]==11
            if int(mask.sum())!=45:
                raise AssertionError("Original SDK source cup geometry changed")
            count=int(np.count_nonzero(mask & (frame[y0:y1+1,x0:x1+1]==13)))
            max_pixels[name]=max(max_pixels[name],count)
            if count==45 and full[name] is None:full[name]=t
            nfull+=int(count==45)
        if nfull==4 and four_simultaneous is None:four_simultaneous=t
        for edge,(ys,xs) in EDGES.items():
            diff=(pre[ys,xs]!=frame[ys,xs])
            active=bool(diff.any())
            if active and not previously[edge]:episodes[edge].append(t)
            previously[edge]=active
            if active and borders[edge] is None:
                old=pre[ys,xs][diff];new=frame[ys,xs][diff]
                vals,counts=np.unique(np.stack((old,new),axis=1),axis=0,return_counts=True)
                borders[edge]={
                    "frame":t,"changed_original_pixels":int(diff.sum()),
                    "palette_transitions":[[int(v[0]),int(v[1]),int(n)] for v,n in zip(vals,counts)]
                }
    return {
        "actual_sdk_original_prepour_hash":hash_frame(pre),
        "actual_sdk_original_final_pour_hash":hash_frame(frames[-1]),
        "real_native_pour_frame_count":len(frames),
        "native_cup_first_full_frames":full,
        "native_cup_max_palette13_pixels":max_pixels,
        "native_first_simultaneous_four_cups":four_simultaneous,
        "native_first_new_source6_row8":first_y8_fullrow,
        "native_first_new_source6_row5":first_y5_fullrow,
        "native_first_new_source6_OUTSIDE_upper_cups_row5":first_offcup_row5,
        "native_first_new_source6_at_row5_x_groups":first_sites,
        "first_genuine_native_border_color_change":borders,
        "genuine_native_border_change_episodes":episodes,
        "original_selected_components_before_pour":selected(pre),
        "scope":"Source pixel transitions are observation only; original SDK official level>=5 or WIN alone constitutes progress."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    records=[];stacks={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            pre=raw["stage4_"+str(n-1)][-1]
            outcome=metrics(root,pre,raw["stage4_"+str(n)])
            actions=[
                {"step":event["index"],
                 "actual_original_sdk_action":event["genuine_original_action"],
                 "native_click_xy":event["real_native_click_xy"],
                 "native_preclick_palette":event["original_source_pixel_before_click"],
                 "true_source_selected_after":selected(raw["stage4_"+str(event["index"])][-1]),
                 "actual_original_frame_hash":event["source_frame_after_blake2b16"]}
                for event in sdk["genuine_original_stage4_action_ledger"]
                if event["genuine_original_action"] in (1,2,3,4,6)
            ]
            result={
                "prospective_original_case":case,
                "independent_original_stage4_witness":witness,
                "actual_original_stage4_action_word":word,
                "official_native_sdk_final_level":sdk["true_original_sdk_final_level"],
                "official_native_sdk_final_state":sdk["true_original_sdk_final_state"],
                "actual_native_sdk_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "genuine_original_frame_observations":outcome,
                "native_source_selected_action_receipts":actions,
                "full_sdk_original_action_receipts":sdk["genuine_original_stage4_action_ledger"],
            }
            records.append(result)
            for step,arr in raw.items():stacks[f"{case}_{witness}_{step}"]=arr
            print("ORIGINAL_SP80_DUAL_UPPER_BRANCH_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_level":result["official_native_sdk_final_level"],
                "official_state":result["official_native_sdk_final_state"],
                "frame_observations":outcome,
            },sort_keys=True),flush=True)
    if len(records)!=52 or len(roots)!=1:
        raise AssertionError("Genuine original SDK entry or result missing")
    for case,_ in FROZEN:
        pair=[v for v in records if v["prospective_original_case"]==case]
        if len(pair)!=2 or (
            pair[0]["official_native_sdk_final_level"]!=pair[1]["official_native_sdk_final_level"]
            or pair[0]["official_native_sdk_final_state"]!=pair[1]["official_native_sdk_final_state"]
            or pair[0]["genuine_original_frame_observations"]!=pair[1]["genuine_original_frame_observations"]
            or pair[0]["native_source_selected_action_receipts"]!=pair[1]["native_source_selected_action_receipts"]
        ):raise AssertionError("Actual original independent A/B SDK mismatch "+case)
    advances=[
        {"case":r["prospective_original_case"],
         "witness":r["independent_original_stage4_witness"],
         "word":r["actual_original_stage4_action_word"],
         "official_level":r["official_native_sdk_final_level"],
         "official_state":r["official_native_sdk_final_state"]}
        for r in records if r["actual_native_sdk_level5_or_WIN"]
    ]
    fours=[
        {"case":r["prospective_original_case"],
         "witness":r["independent_original_stage4_witness"],
         "first_upper_offcup":r["genuine_original_frame_observations"]["native_first_new_source6_OUTSIDE_upper_cups_row5"],
         "first_borders":r["genuine_original_frame_observations"]["first_genuine_native_border_color_change"]}
        for r in records if r["genuine_original_frame_observations"]["native_first_simultaneous_four_cups"] is not None
    ]
    summary={
        "kind":"TRUE_ORIGINAL_SP80_STAGE4_COUPLED_UPPER_STREAM_SOURCE_CONTACT",
        "independent_original_antecedent_runs":[39636999616,39639320303],
        "genuine_original_sdk_fresh_resets":len(records),
        "prospectively_frozen_genuine_source_words":FROZEN,
        "true_original_level4_source_root_hash":next(iter(roots)),
        "official_original_level5_or_WIN_count":len(advances),
        "official_original_level5_witnesses":advances,
        "visually_four_cup_source_with_upper_site_and_border_evidence":fours,
        "original_sdk_final_level_histogram":dict(Counter(str(x["official_native_sdk_final_level"]) for x in records)),
        "original_sdk_final_state_histogram":dict(Counter(str(x["official_native_sdk_final_state"]) for x in records)),
        "full_original_native_sdk_action_frame_receipts":records,
        "limits":"Actual Arcade.NORMAL SP80 official levels_completed>=5/WIN alone is advancement. Palette6 and edge14 pixels are bounded rendered source observations, not a proven fluid model or image victory. No other lanes or rights changed.",
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**stacks)
    print("ORIGINAL_SP80_DUAL_UPPER_BRANCH_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospectively_frozen_genuine_source_words","full_original_native_sdk_action_frame_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":
    main()
