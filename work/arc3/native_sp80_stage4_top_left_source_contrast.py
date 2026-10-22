"""Original SDK SP80 level4: top-left cup source-first contrast.

Frozen one-parent interventions and independent native witnesses.
An animation-frame comparison is a source observation, not a clock
equivalence, private objective model or level5 claim.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

PARENT = "6@46,33 3 6@24,33 2 2 2 3 3 6@34,42 3 3 3 1 1 6@34,21"
CONTROLS = (
    ("reselect", ""),
    ("left1", "3"),
    ("left2", "3 3"),
    ("left_then_right", "3 4"),
    ("left_then_up", "3 1"),
    ("left_then_down", "3 2"),
)
CUPS = {
    "lateral": (5,35,10,43),
    "top_left": (17,5,25,10),
    "top_middle": (35,5,43,10),
    "top_right": (47,5,55,10),
}
BORDERS = {
    "left": (slice(2,62),slice(2,5)),
    "top": (slice(2,5),slice(2,62)),
    "right": (slice(2,62),slice(59,62)),
    "bottom": (slice(59,63),slice(2,62)),
}

def full_region(frame, mask, coords):
    x0,y0,x1,y1 = coords
    return int(np.count_nonzero(mask & (frame[y0:y1+1,x0:x1+1]==13)))

def source_report(root, pre, frames):
    if root.shape!=(64,64) or pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Original SDK source 64x64 frames required")
    masks={}
    first={}
    max_filled={}
    for name,coords in CUPS.items():
        x0,y0,x1,y1=coords
        mask=(root[y0:y1+1,x0:x1+1]==11)
        if int(mask.sum())!=45:raise AssertionError("Authentic cup root differs")
        masks[name]=mask
        first[name]=None
        max_filled[name]=0
    edge={k:None for k in BORDERS}
    earliest_left_color13=None
    first_four=None
    for index,frame in enumerate(frames):
        simultaneous=0
        for name,coords in CUPS.items():
            count=full_region(frame,masks[name],coords)
            max_filled[name]=max(count,max_filled[name])
            if count==45:
                simultaneous+=1
                if first[name] is None:first[name]=index
        if simultaneous==4 and first_four is None:first_four=index
        if earliest_left_color13 is None and np.any(
            (pre[5:11,17:26]!=13)&(frame[5:11,17:26]==13)&masks["top_left"]
        ):earliest_left_color13=index
        for name,sl in BORDERS.items():
            if edge[name] is None and np.any(pre[sl]!=frame[sl]):edge[name]=index
    ys,xs=np.nonzero(pre==9)
    return {
        "root_hash":hash_frame(root), "pre_pour_hash":hash_frame(pre),
        "final_frame_hash":hash_frame(frames[-1]),
        "source_frame_count":len(frames),
        "source_first_full_cups":first,"source_max_filled_cups":max_filled,
        "source_first_four_simultaneous":first_four,
        "source_first_top_left_palette13":earliest_left_color13,
        "source_first_boundary_change":edge,
        "selected_bbox":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None,
    }

def comparison(base_pre,base_frames,other_pre,other_frames,root):
    changed=other_pre!=base_pre
    xy=np.argwhere(changed)
    pairs=Counter((int(base_pre[y,x]),int(other_pre[y,x])) for y,x in xy)
    masks={}
    for name,(x0,y0,x1,y1) in CUPS.items():
        m=np.zeros((64,64),dtype=bool)
        m[y0:y1+1,x0:x1+1]=(root[y0:y1+1,x0:x1+1]==11)
        masks[name]=m
    first_index=None
    first_count=0
    first_by_cup={name:None for name in CUPS}
    paired_count=min(len(base_frames),len(other_frames))
    for i in range(paired_count):
        d=base_frames[i]!=other_frames[i]
        if first_index is None and np.any(d):
            first_index=i
            first_count=int(np.count_nonzero(d))
        for name,mask in masks.items():
            if first_by_cup[name] is None and np.any(d & mask):
                first_by_cup[name]=i
    return {
        "source_prepour_differing_pixel_count":len(xy),
        "source_prepour_difference_bbox_xyxy":(
            [int(xy[:,1].min()),int(xy[:,0].min()),
             int(xy[:,1].max()),int(xy[:,0].max())] if len(xy) else None),
        "source_prepour_palette_pairs":[{"before":a,"after":b,"count":n}
                                       for (a,b),n in sorted(pairs.items())],
        "source_prepour_differing_in_each_source_cup":{
            key:int(np.count_nonzero(changed & mask)) for key,mask in masks.items()
        },
        "frame_index_alignment_only":True,
        "source_animation_paired_frame_count":paired_count,
        "source_first_animation_frame_difference":first_index,
        "source_first_difference_pixel_count":first_count,
        "source_first_differing_frame_in_cup_mask":first_by_cup,
        "limit":"Animation frame indices aligned by index, not an asserted common physical time.",
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    trials=[];stored={};refs={};roots=set()
    for name,control in CONTROLS:
        word=" ".join(piece for piece in (PARENT,control,"5") if piece)
        actions=parse_plan(word)
        assert len(actions)>1 and actions[-1][0]==5 and sum(a==5 for a,_ in actions)==1
        for witness,entry in STAGE1_WITNESSES:
            native,raw=run_case(name,witness,entry,word)
            root=raw["entry3_34"][-1]
            pre=raw["stage4_"+str(len(actions)-1)][-1]
            frames=raw["stage4_"+str(len(actions))]
            obs=source_report(root,pre,frames)
            roots.add(obs["root_hash"])
            row={"control":name,"native_witness":witness,
                "source_action_word":word,
                "sdk_level":native["true_original_sdk_final_level"],
                "sdk_state":native["true_original_sdk_final_state"],
                "official_level5_or_WIN":native["official_original_level5_or_WIN"],
                "source_observation":obs,
                "genuine_stage4_action_receipts":native["genuine_original_stage4_action_ledger"]}
            trials.append(row)
            refs[(name,witness)]=(root.copy(),pre.copy(),frames.copy())
            for label,arr in raw.items():
                stored[name+"_"+witness+"_"+label]=arr
            print("ARC4_LEFT_CONTRAST_CASE "+json.dumps({
                "control":name,"witness":witness,
                "sdk_level":row["sdk_level"],"sdk_state":row["sdk_state"],
                "source":obs},sort_keys=True),flush=True)
    if len(roots)!=1 or len(trials)!=len(CONTROLS)*2:
        raise AssertionError("Inconsistent independent stage4 original roots")
    for name,_ in CONTROLS:
        matches=[t for t in trials if t["control"]==name]
        assert len(matches)==2 and {x["native_witness"] for x in matches}=={"A","B"}
        for key in ("sdk_level","sdk_state","source_observation"):
            if matches[0][key]!=matches[1][key]:
                raise AssertionError("Original native witness disagreement: "+name+" "+key)
    differences={}
    for name,_ in CONTROLS:
        if name=="reselect":continue
        for base in ("reselect","left1"):
            if name==base:continue
            cmp=[]
            for witness,_ in STAGE1_WITNESSES:
                root,pre,frames=refs[(base,witness)]
                _,other_pre,other_frames=refs[(name,witness)]
                cmp.append(comparison(pre,frames,other_pre,other_frames,root))
            if cmp[0]!=cmp[1]:
                raise AssertionError("Two authentic witness source comparisons disagree")
            differences[base+"_vs_"+name]=cmp[0]
    report={"kind":"ARC4_ORIGINAL_SDK_TOP_LEFT_SOURCE_FIRST_CONTRAST",
        "original_sdk_resets":len(trials),
        "official_level5_or_WIN_count":sum(int(t["official_level5_or_WIN"]) for t in trials),
        "official_level_histogram":dict(Counter(str(t["sdk_level"]) for t in trials)),
        "predeclared_controls":CONTROLS,
        "native_cases":trials,"source_difference_comparisons":differences,
        "boundary":"All data are original frame/source receipts. No hidden mechanic or WIN is inferred."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**stored)
    print("ARC4_LEFT_CONTRAST_SUMMARY "+json.dumps({
        "original_sdk_resets":len(trials),
        "official_level5_or_WIN_count":report["official_level5_or_WIN_count"],
        "official_level_histogram":report["official_level_histogram"],
        "source_cases":{n:next(x["source_observation"] for x in trials if x["control"]==n)
                        for n,_ in CONTROLS},
        "first_source_differences":{k:{"source_prepour_differing_pixel_count":v["source_prepour_differing_pixel_count"],
                                     "source_first_animation_frame_difference":v["source_first_animation_frame_difference"],
                                     "source_first_differing_frame_in_cup_mask":v["source_first_differing_frame_in_cup_mask"]}
                                     for k,v in differences.items()},
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
