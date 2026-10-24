"""Original ARC SP80: matched upper-bar position, different actual SDK histories.

Retains genuine entrance witnesses and original 64x64 frame stacks;
same final selected bounding box is checked, not assumed. No fake state.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_top_left_source_contrast import PARENT, source_report, CUPS
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

HISTORIES=(
    ("direct_left1","3"),
    ("left_right_left","3 4 3"),
    ("left_up_down","3 1 2"),
    ("left_down_up","3 2 1"),
    ("left_left_right","3 3 4"),
)

def compare(reference, actual, root, base_frames, other_frames):
    diff=(reference!=actual)
    where=np.argwhere(diff)
    palette=Counter((int(reference[y,x]),int(actual[y,x])) for y,x in where)
    n=min(len(base_frames),len(other_frames))
    first=None
    first_cups={k:None for k in CUPS}
    for t in range(n):
        changed=base_frames[t]!=other_frames[t]
        if first is None and np.any(changed):first=t
        for name,(x0,y0,x1,y1) in CUPS.items():
            mask=(root[y0:y1+1,x0:x1+1]==11)
            if first_cups[name] is None and np.any(
                changed[y0:y1+1,x0:x1+1] & mask
            ):first_cups[name]=t
    return {"source_prepour_different_pixel_count":int(np.count_nonzero(diff)),
            "source_prepour_bbox":(
                [int(where[:,1].min()),int(where[:,0].min()),
                 int(where[:,1].max()),int(where[:,0].max())] if len(where) else None),
            "source_prepour_palette_changes":[
                {"source_before":a,"source_after":b,"count":n}
                for (a,b),n in sorted(palette.items())],
            "source_frame_index_alignment_only":True,
            "first_animation_difference_index":first,
            "first_animation_difference_in_cup":first_cups,
            "compared_native_frame_indices":n,
            "limit":"Same selected bounding box does not imply the rest of source state is the same."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows=[];frames_out={};native_refs={};roots=set()
    for name,movement in HISTORIES:
        word=" ".join([PARENT,movement,"5"])
        actions=parse_plan(word)
        assert sum(a==5 for a,xy in actions)==1 and actions[-1][0]==5
        for witness,entry in STAGE1_WITNESSES:
            native,stacks=run_case(name,witness,entry,word)
            root=stacks["entry3_34"][-1]
            pre=stacks["stage4_"+str(len(actions)-1)][-1]
            frames=stacks["stage4_"+str(len(actions))]
            observed=source_report(root,pre,frames)
            roots.add(observed["root_hash"])
            rows.append({"history":name,"witness":witness,
                         "actual_native_sdk_word":word,
                         "actual_level":native["true_original_sdk_final_level"],
                         "actual_state":native["true_original_sdk_final_state"],
                         "official_level5_or_WIN":native["official_original_level5_or_WIN"],
                         "source":observed,
                         "original_action_receipts":native["genuine_original_stage4_action_ledger"]})
            native_refs[(name,witness)]=(root.copy(),pre.copy(),frames.copy())
            for label,stack in stacks.items():frames_out[name+"_"+witness+"_"+label]=stack
            print("ARC4_HISTORY_CASE "+json.dumps({
                "history":name,"witness":witness,
                "official_level":rows[-1]["actual_level"],
                "official_state":rows[-1]["actual_state"],
                "source":observed},sort_keys=True),flush=True)
    if len(roots)!=1:raise AssertionError("Independent authentic stage4 source roots disagree")
    contrasts={}
    for name,_ in HISTORIES:
        pair=[r for r in rows if r["history"]==name]
        if len(pair)!=2 or {r["witness"] for r in pair}!={"A","B"}:
            raise AssertionError("Missing independent native entrance")
        for key in ("actual_level","actual_state","source"):
            if pair[0][key]!=pair[1][key]:raise AssertionError("Native A/B sources differ: "+name+" "+key)
        if name=="direct_left1":continue
        aligned=[]
        for witness,_ in STAGE1_WITNESSES:
            root,base_pre,base_frames=native_refs[("direct_left1",witness)]
            _,other_pre,other_frames=native_refs[(name,witness)]
            aligned.append(compare(base_pre,other_pre,root,base_frames,other_frames))
        if aligned[0]!=aligned[1]:raise AssertionError("Native A/B contrast differs "+name)
        contrasts[name]=aligned[0]
    reference=next(x["source"] for x in rows if x["history"]=="direct_left1")
    same_coordinates={name:next(x["source"] for x in rows if x["history"]==name)["selected_bbox"]==reference["selected_bbox"] for name,_ in HISTORIES}
    report={"kind":"ARC4_SAME_POSITION_DIFFERENT_HISTORY_GENUINE_NATIVE",
            "independent_native_resets":len(rows),
            "official_level_histogram":dict(Counter(str(r["actual_level"]) for r in rows)),
            "official_level5_or_WIN_count":sum(int(r["official_level5_or_WIN"]) for r in rows),
            "tested_frozen_histories":HISTORIES,
            "same_selected_bbox_as_direct_left1":same_coordinates,
            "native_source_contrasts":contrasts,
            "native_rows":rows,
            "limit":"SDK measurements only. Same selected bbox is not state equivalence or a game objective."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames_out)
    print("ARC4_HISTORY_SUMMARY "+json.dumps({
        "independent_native_resets":len(rows),
        "official_level_histogram":report["official_level_histogram"],
        "official_level5_or_WIN_count":report["official_level5_or_WIN_count"],
        "same_selected_bbox_as_direct_left1":same_coordinates,
        "source_cases":{name:next(x["source"] for x in rows if x["history"]==name)
                        for name,_ in HISTORIES},
        "source_differences":{k:{"pre_pour_count":v["source_prepour_different_pixel_count"],
                                "first_cup_difference":v["first_animation_difference_in_cup"]}
                              for k,v in contrasts.items()},
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
