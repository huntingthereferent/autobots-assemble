"""Original SP80 Level4: source-grounded finite right/upper coupled translation.

Genuine observed R2/U2 retains top-middle and all four cup windows while
compensated middle+L moves left spill to x14..16. Diagonally translate R/U
source contact by equal 3px increments, until upper bar left reaches x14.
Test two decoupled arms as finite mathematical controls.
Actual independent native SDK A/B resets; no F3 action map inferred.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_leftmost_upper_contact import measured_actual_native
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

PARENTS=(("D3L2_L3U2","2 2 2 3 3","3 3 3 1 1",23,41),
         ("D4L2_L4U2","2 2 2 2 3 3","3 3 3 3 1 1",20,44))
ARMS=(("C22",2,2),("X25",2,5),("C33",3,3),
      ("C44",4,4),("C55",5,5),("X52",5,2))
def move(n):return " ".join(["3"]*n)
def right_cmd(n):return "6@46,33 "+move(n)
def upper_cmd(n):return "6@34,21 "+move(n)
def word(mid,L,r,u):
    return " ".join((right_cmd(r),"6@24,33 "+mid+" 4",
                     "6@34,42 "+L+" 4",upper_cmd(u),"5"))
FROZEN=tuple((f"{p}_{tag}",word(mid,L,r,u))
  for p,mid,L,x,y in PARENTS for tag,r,u in ARMS)
assert len(FROZEN)==12==len({n for n,w in FROZEN})
assert tuple(w for w,_ in STAGE1_WITNESSES)==("A","B")
assert all(parse_plan(w)[-1][0]==5 and sum(a==5 for a,xy in parse_plan(w))==1
    and sum(a==6 for a,xy in parse_plan(w))==4 for n,w in FROZEN)

def selected_bbox(arr):
    ys,xs=np.nonzero(arr==9)
    if len(xs)!=27:raise ValueError("Expected genuine original selected 27-pixel component")
    return [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]

def observe(root,pre,stack):
    native=measured_actual_native(root,pre,stack)
    first={f"x{x}_{x+2}":None for x in (5,8,11,14,17,20)}
    for frame_i,frame in enumerate(stack):
        newly=(pre!=6)&(frame==6)
        for x in (5,8,11,14,17,20):
            label=f"x{x}_{x+2}"
            if first[label] is None and np.any(newly[5:8,x:x+3]):
                first[label]=frame_i
    cups=native["original_source_cup_max_palette13_pixels"]
    return {
        "genuine_original_source_metrics":native,
        "source_upper_left_new6_first_by_3px_band":first,
        "source_upper_left_offcup_wider_detected":
            any(first[k] is not None for k in ("x5_7","x8_10","x11_13","x14_16")),
        "native_cup_max_palette13":cups,
        "lateral_cup_full":cups["left_lateral"]==45,
        "topmiddle_cup_full":cups["top_middle"]==45,
        "native_four_cups_together":native["native_first_simultaneously_full_four_cups"] is not None,
        "prepour_original_hash":hash_frame(pre),
        "final_original_hash":hash_frame(stack[-1]),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    cases=[];arrays={};roots=set()
    for name,program in FROZEN:
        p,mname,lname=name.split("_",1)[0],None,None
        # Parent names include underscores; parse by known frozen suffix.
        for parent,base,l,l_x,m_y in PARENTS:
            prefix=parent+"_"
            if name.startswith(prefix):
                suffix=name[len(prefix):]
                mname,lname=suffix.split("_")
                break
        else:raise ValueError("Unrecognized original clean source parent")
        rsteps,usteps=next((r,u) for t,r,u in ARMS if t==lname)
        rightprefix=right_cmd(rsteps)
        right_idx=len(parse_plan(rightprefix))
        prefix_mid=rightprefix+" "+"6@24,33 "+base+" 4"
        mid_idx=len(parse_plan(prefix_mid))
        prefix_l=prefix_mid+" "+"6@34,42 "+l+" 4"
        l_idx=len(parse_plan(prefix_l))
        top_idx=len(parse_plan(prefix_l+" "+upper_cmd(usteps)))
        acts=parse_plan(program)
        for witness,entry in STAGE1_WITNESSES:
            trial,source=run_case(name,witness,entry,program)
            receipts=trial["genuine_original_stage4_action_ledger"]
            root=source["entry3_34"][-1]
            roots.add(hash_frame(root))
            complete=len(receipts)==len(acts)
            advance=bool(trial["official_original_level5_or_WIN"])
            if ([r["genuine_original_action"] for r in receipts]!=
                    [a for a,xy in acts[:len(receipts)]] or
                 (not complete and not advance) or
                 len(receipts)<l_idx):
                raise ValueError("Native SDK Level4 action word diverged or lower L not reached")
            right_selected=selected_bbox(source[f"stage4_{right_idx}"][-1])
            mid_selected=selected_bbox(source[f"stage4_{mid_idx}"][-1])
            l_selected=selected_bbox(source[f"stage4_{l_idx}"][-1])
            upper_selected=selected_bbox(source[f"stage4_{top_idx}"][-1])
            pre=source[f"stage4_{len(receipts)-1}"][-1]
            pour=source[f"stage4_{len(receipts)}"]
            measured=observe(root,pre,pour) if receipts[-1]["genuine_original_action"]==5 else None
            row={
              "case":name,"witness":witness,
              "frozen_original_stage4_word":program,
              "actual_source_right_action_index":right_idx,
              "actual_selected_right_bbox":right_selected,
              "actual_source_upper_action_index":top_idx,
              "actual_selected_upper_bbox":upper_selected,
              "actual_source_middle_action_index":mid_idx,
              "actual_selected_middle_bbox":mid_selected,
              "actual_source_L_action_index":l_idx,
              "actual_selected_L_bbox":l_selected,
              "actual_native_receipts":receipts,
              "original_word_complete":complete,
              "official_original_sdk_level":trial["true_original_sdk_final_level"],
              "official_original_sdk_state":trial["true_original_sdk_final_state"],
              "official_original_level5_or_WIN":advance,
              "measured_original_source":measured,
            }
            cases.append(row)
            for phase,stack in source.items():
                arrays[f"{name}_{witness}_{phase}"]=stack
            print("ARC4_DIAGONAL_NATIVE_CASE "+json.dumps({
              "case":name,"witness":witness,"middle_bbox":mid_selected,"L_bbox":l_selected,
              "official":row["official_original_sdk_level"],
              "win":advance,
              "lateral":measured["native_cup_max_palette13"]["left_lateral"] if measured else None,
              "topmiddle":measured["native_cup_max_palette13"]["top_middle"] if measured else None,
              "four":measured["native_four_cups_together"] if measured else None,
              "left_source":measured["source_upper_left_new6_first_by_3px_band"] if measured else None,
            },sort_keys=True),flush=True)
    if len(cases)!=24 or roots!={"fa8fd32d3bfd2c8b3ff7765aec373512"}:
        raise ValueError("Actual source original SDK root or case count changed")
    for name,program in FROZEN:
        pair=[r for r in cases if r["case"]==name]
        if len(pair)!=2 or [r["witness"] for r in pair]!=["A","B"] or (
            {k:v for k,v in pair[0].items() if k!="witness"} !=
            {k:v for k,v in pair[1].items() if k!="witness"}
        ):raise ValueError("Independent original SDK native A/B replay disagreement")
    out={
        "kind":"ORIGINAL_SP80_LEVEL4_NATIVE_MIDDLE_HEIGHT_SPILL_RELATION",
        "source_parent_run":40171009741,
        "true_original_level4_root":next(iter(roots)),
        "frozen_source_words":[list(p) for p in FROZEN],
        "original_sdk_resets":len(cases),
        "official_level5_or_WIN_count":sum(int(c["official_original_level5_or_WIN"]) for c in cases),
        "original_sdk_levels":dict(Counter(str(c["official_original_sdk_level"]) for c in cases)),
        "native_cases":cases,
        "finite_question":"Does true native UP1/HOLD/DOWN1 middle-bar height change the upper-left x14..16 overflow when middle RIGHT1 and L RIGHT1 jointly preserve all four cups, versus the baseline middle HOLD/L HOLD under identical vertical changes?",
        "math_scope":"Partial finite native original-source relationship with independent real A/B SDK histories, not formal F3 mathematical A/B operators, decoded physics or private native state."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n",encoding="utf8")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ARC4_MIDDLE_HEIGHT_SUMMARY "+json.dumps({
        "resets":len(cases),"official_progress":out["official_level5_or_WIN_count"],
        "level4_root":next(iter(roots)),
        "cases":[{
            "case":c["case"],
            "middle_bbox":c["actual_selected_middle_bbox"],
            "right_bbox":c["actual_selected_right_bbox"],
            "upper_bbox":c["actual_selected_upper_bbox"],
            "L_bbox":c["actual_selected_L_bbox"],
            "level":c["official_original_sdk_level"],
            "lateral":c["measured_original_source"]["native_cup_max_palette13"]["left_lateral"] if c["measured_original_source"] else None,
            "topmiddle":c["measured_original_source"]["native_cup_max_palette13"]["top_middle"] if c["measured_original_source"] else None,
            "four":c["measured_original_source"]["native_four_cups_together"] if c["measured_original_source"] else None,
            "source":c["measured_original_source"]["source_upper_left_new6_first_by_3px_band"] if c["measured_original_source"] else None,
        } for c in cases if c["witness"]=="A"],
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
