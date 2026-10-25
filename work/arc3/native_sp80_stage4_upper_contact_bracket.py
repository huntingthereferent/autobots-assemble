"""Original SDK SP80 Level4: upper-bar right-edge contact bracket at measured source x32-34.

Original source run 40164869118 confirmed right-middle LEFT2 shifts a new
color6 column to x32-34 while the top-middle native cup remains 0/45 for
upper LEFT6-8. Original source right bar edge is at x34 under LEFT2 and at
x31 under LEFT3. Freeze U1/U2/U3/U6 native upper source contact bracket
under right-middle LEFT1 or LEFT2 and two existing clean lower parents.
No simulator, inferred physics or F3-to-SDK mathematical action mapping.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_leftmost_upper_contact import measured_actual_native
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

PARENTS=(
 ("D3L2_L3U2","6@24,33 2 2 2 3 3","6@34,42 3 3 3 1 1"),
 ("D4L2_L4U2","6@24,33 2 2 2 2 3 3","6@34,42 3 3 3 3 1 1"),
)
RIGHT=(("R1","3"),("R2","3 3"))
UPPER=(("U1","3"),("U2","3 3"),("U3","3 3 3"),("U6","3 3 3 3 3 3"))

def native_word(mid,l,right,upper):
    return " ".join(("6@46,33 "+right,mid,l,"6@34,21 "+upper,"5"))

FROZEN=tuple((f"{parent}_{rn}_{un}",native_word(mid,l,rword,uword))
 for parent,mid,l in PARENTS for rn,rword in RIGHT for un,uword in UPPER)
assert len(FROZEN)==16==len({n for n,w in FROZEN})
assert tuple(n for n,_ in STAGE1_WITNESSES)==("A","B")
assert all(parse_plan(w)[-1][0]==5 and
           sum(a==5 for a,xy in parse_plan(w))==1 and
           sum(a==6 for a,xy in parse_plan(w))==4 for n,w in FROZEN)

def select_box(frame):
    y,x=np.nonzero(frame==9)
    return [int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None

def observations(root,pre,animation):
    m=measured_actual_native(root,pre,animation)
    cups=m["original_source_cup_max_palette13_pixels"]
    sites=m["first_original_color6_at_3_upper_sites"]
    edges=m["native_first_source_border_changes"]
    P=sites["leftmost_outside_cup"] is None
    Q=sites["upper_right_outside"] is None
    return {
      "original_sdk_pixel_observations":m,
      "P_no_leftmost_strand":P,
      "Q_no_rightmost_strand":Q,
      "P_and_Q":P and Q,
      "topmiddle_max_palette13":cups["top_middle"],
      "topmiddle_full":cups["top_middle"]==45,
      "simultaneous_four_cups":m["native_first_simultaneously_full_four_cups"] is not None,
      "no_top_right_border_change":edges["top"] is None and edges["right"] is None,
      "original_prepour_sha":hash_frame(pre),
      "original_last_frame_sha":hash_frame(animation[-1]),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    cases=[];raw={};roots=set()
    for name,word in FROZEN:
        actions=parse_plan(word)
        for witness,entry in STAGE1_WITNESSES:
            trial,source=run_case(name,witness,entry,word)
            root=source["entry3_34"][-1]
            roots.add(hash_frame(root))
            receipts=trial["genuine_original_stage4_action_ledger"]
            complete=len(receipts)==len(actions)
            advanced=bool(trial["official_original_level5_or_WIN"])
            if ([r["genuine_original_action"] for r in receipts]!=
                  [act for act,xy in actions[:len(receipts)]] or
                  (not complete and not advanced)):
                raise ValueError("genuine SDK Level4 action receipt drift")
            pre=source["stage4_"+str(len(receipts)-1)][-1] if len(receipts)>1 else root
            pour=source["stage4_"+str(len(receipts))]
            measured=observations(root,pre,pour) if receipts[-1]["genuine_original_action"]==5 else None
            row={
                "case":name,"witness":witness,"source_word":word,
                "official_native_level":trial["true_original_sdk_final_level"],
                "official_native_state":trial["true_original_sdk_final_state"],
                "official_level5_or_WIN":advanced,
                "executed_native_stage4_actions":len(receipts),
                "finished_frozen_word":complete,
                "actual_sdk_stage4_receipts":receipts,
                "selected_upper_original_bbox":select_box(pre) if complete else None,
                "original_sdk_source_measures":measured,
            }
            cases.append(row)
            for key,arr in source.items():
                raw[f"{name}_{witness}_{key}"]=arr
            print("ORIGINAL_ARC4_CONTACT_CASE "+json.dumps({
                "name":name,"witness":witness,
                "level":row["official_native_level"],
                "progress":advanced,
                "topmiddle":measured["topmiddle_max_palette13"] if measured else None,
                "P_and_Q":measured["P_and_Q"] if measured else None,
            },sort_keys=True),flush=True)
    if len(cases)!=32 or roots!={"fa8fd32d3bfd2c8b3ff7765aec373512"}:
        raise ValueError("original source Level4 entrance or A/B native reset count drift")
    for name,_ in FROZEN:
        pair=[r for r in cases if r["case"]==name]
        if len(pair)!=2 or {r["witness"] for r in pair}!={"A","B"} or (
            {k:v for k,v in pair[0].items() if k!="witness"} !=
            {k:v for k,v in pair[1].items() if k!="witness"}
        ):
            raise ValueError("genuine original SDK independent entry sources disagree")
    out={
      "kind":"ORIGINAL_ARC4_UPPER_RIGHT_EDGE_CONTACT_BRACKET",
      "source_parent_runs":[39639320303,40154160743],
      "genuine_original_sdk_level4_root":next(iter(roots)),
      "frozen_cases":[list(x) for x in FROZEN],
      "original_sdk_resets":len(cases),
      "actual_official_level5_or_WIN_count":sum(int(x["official_level5_or_WIN"]) for x in cases),
      "official_sdk_levels":dict(Counter(str(x["official_native_level"]) for x in cases)),
      "native_cases":cases,
      "finite_question":"Does moving the selected original upper object's right edge across the observed x32-34 stream (U2 edge x34 vs U3 edge x31) change top-middle cup13 filling under right-middle LEFT2?",
      "math_scope":"Finite native source observational transfer test, not global game law, no formal F3 A/B action homomorphism or inferred private physics."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"
")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("ORIGINAL_ARC4_CONTACT_SUMMARY "+json.dumps({
      "original_native_resets":len(cases),"official_advances":out["actual_official_level5_or_WIN_count"],
      "original_level4_root":next(iter(roots)),
      "source_cases":[{"case":r["case"],"level":r["official_native_level"],
        "topmiddle":r["original_sdk_source_measures"]["topmiddle_max_palette13"] if r["original_sdk_source_measures"] else None,
        "P":r["original_sdk_source_measures"]["P_no_leftmost_strand"] if r["original_sdk_source_measures"] else None,
        "Q":r["original_sdk_source_measures"]["Q_no_rightmost_strand"] if r["original_sdk_source_measures"] else None,
        "four":r["original_sdk_source_measures"]["simultaneous_four_cups"] if r["original_sdk_source_measures"] else None}
        for r in cases if r["witness"]=="A"]},sort_keys=True),flush=True)
if __name__=="__main__":main()
