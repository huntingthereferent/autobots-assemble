"""Compare two actual SP80 level4 native words on independent entrance histories."""
import argparse
import json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

CUPS = {"lateral":(5,35,10,43),"top_left":(17,5,25,10),"top_middle":(35,5,43,10),"top_right":(47,5,55,10)}
BORDERS = {"left":(slice(2,62),slice(2,5)),"right":(slice(2,62),slice(59,62)),"top":(slice(2,5),slice(2,62)),"bottom":(slice(59,63),slice(2,62))}

def observe(root,pre,frames):
    if root.shape!=(64,64) or pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Authentic original SDK 64x64 frames required")
    first={k:None for k in CUPS}
    borders={k:None for k in BORDERS}
    offcup={"row5":None,"row8":None}
    outside=np.ones((64,64),dtype=bool)
    for x0,y0,x1,y1 in CUPS.values(): outside[y0:y1+1,x0:x1+1]=False
    four=None
    for t,frame in enumerate(frames):
        count=0
        for k,(x0,y0,x1,y1) in CUPS.items():
            mask=root[y0:y1+1,x0:x1+1]==11
            if int(mask.sum())!=45:raise AssertionError("Authentic root cup source mismatch")
            full=int(np.count_nonzero(mask & (frame[y0:y1+1,x0:x1+1]==13)))==45
            count+=int(full)
            if full and first[k] is None:first[k]=t
        if count==4 and four is None:four=t
        for k,region in BORDERS.items():
            if borders[k] is None and np.any(pre[region]!=frame[region]):borders[k]=t
        new6=(pre!=6)&(frame==6)&outside
        for name,y in (("row5",5),("row8",8)):
            if offcup[name] is None:
                xs=np.flatnonzero(new6[y,8:59])+8
                if len(xs):offcup[name]={"frame":t,"x":[int(v) for v in xs]}
    ys,xs=np.nonzero(pre==9)
    return {"root_hash":hash_frame(root),"pre_hash":hash_frame(pre),
        "final_hash":hash_frame(frames[-1]),"first_cup_full":first,
        "first_four_cups":four,"first_borders":borders,"first_offcup6":offcup,
        "selected_bbox":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None,
        "source_frame_count":len(frames)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--plan",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    a=ap.parse_args()
    p=json.loads(a.plan.read_text())
    original=parse_plan(p["original_native_action_word"])
    changed=parse_plan(p["intervention_native_action_word"])
    if p.get("kind")!="ARC4_SOURCE_PINNED_INTERVENTION_PLAN" or not p.get("preserves_existing_native_selection_without_extra_click"):
        raise ValueError("Source-pinned one-movement plan required")
    if len(changed)!=len(original)+1 or changed[:-2]!=original[:-1] or changed[-2][0]!=p["new_native_action"] or changed[-1][0]!=5:
        raise ValueError("Unexpected native word, click or pour")
    records=[];archives={};roots=set()
    for condition,word in (("original",p["original_native_action_word"]),("one_extra_move",p["intervention_native_action_word"])):
        for witness,entry in STAGE1_WITNESSES:
            native,raw=run_case(condition,witness,entry,word)
            n=len(parse_plan(word))
            obs=observe(raw["entry3_34"][-1],raw["stage4_"+str(n-1)][-1],raw["stage4_"+str(n)])
            roots.add(obs["root_hash"])
            row={"condition":condition,"witness":witness,
                "official_level":native["true_original_sdk_final_level"],
                "official_state":native["true_original_sdk_final_state"],
                "official_level5_or_WIN":native["official_original_level5_or_WIN"],
                "source":obs,"original_native_action_receipts":native["genuine_original_stage4_action_ledger"]}
            records.append(row)
            for key,value in raw.items():archives[condition+"_"+witness+"_"+key]=value
            print("ARC4_PAIRED_CASE "+json.dumps({"condition":condition,"witness":witness,"level":row["official_level"],"state":row["official_state"],"source":obs},sort_keys=True),flush=True)
    if len(roots)!=1:raise AssertionError("Native stage4 roots disagree")
    for condition in ("original","one_extra_move"):
        pair=[x for x in records if x["condition"]==condition]
        if len(pair)!=2 or pair[0]["source"]!=pair[1]["source"] or pair[0]["official_level"]!=pair[1]["official_level"] or pair[0]["official_state"]!=pair[1]["official_state"]:
            raise AssertionError("Independent SDK witnesses disagree: "+condition)
    src={x["condition"]:x["source"] for x in records if x["witness"]=="A"}
    summary={"kind":"ARC4_NATIVE_PAIRED_SINGLE_MOVEMENT","source_plan":p,
        "independent_native_resets":len(records),
        "official_level_histogram":dict(Counter(str(x["official_level"]) for x in records)),
        "official_level5_or_WIN_count":sum(int(x["official_level5_or_WIN"]) for x in records),
        "source_comparison":{"prepours_differ":src["original"]["pre_hash"]!=src["one_extra_move"]["pre_hash"],
            "final_frames_differ":src["original"]["final_hash"]!=src["one_extra_move"]["final_hash"],
            "original":src["original"],"one_extra_move":src["one_extra_move"]},
        "native_records":records,
        "scope":"Original SDK observations, not a decoded objective or inferred private mechanics."}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**archives)
    print("ARC4_PAIRED_SUMMARY "+json.dumps({k:v for k,v in summary.items() if k in ("independent_native_resets","official_level_histogram","official_level5_or_WIN_count","source_comparison")},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
