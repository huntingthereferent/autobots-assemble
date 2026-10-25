"""Original native SP80 Level4: finite 2D upper contact at R2 x32..34 source.

Original SDK run 40165524676 reproduced the U2 upper selected right edge x34
versus U3 right edge x31 and a 45/45 versus 0/45 top-middle cup
breakpoint on right-middle LEFT2 in both clean lower parents. Test the
original upper object UP1 / DOWN1 from each precisely measured source
geometry against unperturbed controls. Original SDK A/B entry histories,
complete source frames, click receipts, official Level4/5 oracle retained.
Finite native observational mathematics, not F3 action translation or
a decoded physical fluid simulation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import Counter
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
RIGHT_FIXED="6@46,33 3 3"
UPPER=(("U2","3 3"),("U3","3 3 3"))
VERTICAL=(("HOLD",""),("UP1","1"),("DOWN1","2"))

def program(mid,l,upper,vertical):
    return " ".join(part for part in (
        RIGHT_FIXED,mid,l,"6@34,21 "+upper+(" "+vertical if vertical else ""),"5"
    ) if part)

FROZEN=tuple(
    (f"{parent}_{upper_name}_{vertical_name}",program(mid,l,upper,vertical))
    for parent,mid,l in PARENTS for upper_name,upper in UPPER
    for vertical_name,vertical in VERTICAL
)
assert len(FROZEN)==12==len({name for name,_ in FROZEN})
assert tuple(name for name,_ in STAGE1_WITNESSES)==("A","B")
assert all(parse_plan(word)[-1][0]==5 and
           sum(action==5 for action,xy in parse_plan(word))==1 and
           sum(action==6 for action,xy in parse_plan(word))==4
           for _,word in FROZEN)

def selected_bbox(frame):
    y,x=np.nonzero(frame==9)
    if not len(x):
        return None
    return [int(x.min()),int(y.min()),int(x.max()),int(y.max())]

def source_observe(root,pre,poured):
    m=measured_actual_native(root,pre,poured)
    cup=m["original_source_cup_max_palette13_pixels"]
    first=m["first_original_color6_at_3_upper_sites"]
    border=m["native_first_source_border_changes"]
    P=first["leftmost_outside_cup"] is None
    Q=first["upper_right_outside"] is None
    return {
        "original_source_measurements":m,
        "P_leftmost_suppressed":P,
        "Q_rightmost_suppressed":Q,
        "P_and_Q":P and Q,
        "R_topmiddle_cup_full":cup["top_middle"]==45,
        "R_four_cups_simultaneously_full":
            m["native_first_simultaneously_full_four_cups"] is not None,
        "top_right_border_unchanged":border["top"] is None and border["right"] is None,
        "source_original_prepour_hash":hash_frame(pre),
        "source_original_pour_last_hash":hash_frame(poured[-1]),
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    records=[];saved={};roots=set()
    for name,word in FROZEN:
        actions=parse_plan(word)
        for witness,entry in STAGE1_WITNESSES:
            genuine,arrays=run_case(name,witness,entry,word)
            ledger=genuine["genuine_original_stage4_action_ledger"]
            root=arrays["entry3_34"][-1]
            roots.add(hash_frame(root))
            native_ids=[r["genuine_original_action"] for r in ledger]
            if native_ids!=[aid for aid,_ in actions[:len(ledger)]]:
                raise AssertionError("Actual source action ledger does not match frozen Level4 plan")
            complete=len(ledger)==len(actions)
            won=bool(genuine["official_original_level5_or_WIN"])
            if not complete and not won:
                raise AssertionError("Native SDK stopped without official advancement")
            pre=arrays["stage4_"+str(len(ledger)-1)][-1] if len(ledger)>1 else root
            animation=arrays["stage4_"+str(len(ledger))]
            measured=source_observe(root,pre,animation) if ledger[-1]["genuine_original_action"]==5 else None
            # Frozen vertical is the FINAL optional movement immediately before ACTION5.
            ending=name.rsplit("_",1)[-1]
            if complete and ending in ("UP1","DOWN1"):
                prior=arrays["stage4_"+str(len(ledger)-2)][-1]
                before_vertical=selected_bbox(prior)
            else:
                before_vertical=selected_bbox(pre) if complete else None
            case={
                "case":name,"witness":witness,"frozen_stage4_source_word":word,
                "original_sdk_executed_actions":len(ledger),
                "original_sdk_complete_source_word":complete,
                "original_sdk_official_level":genuine["true_original_sdk_final_level"],
                "original_sdk_official_state":genuine["true_original_sdk_final_state"],
                "official_level5_or_WIN":won,
                "original_source_selected_before_vertical":before_vertical,
                "original_source_selected_before_pour":selected_bbox(pre) if complete else None,
                "original_sdk_stage4_action_ledger":ledger,
                "original_sdk_native_visual_measurements":measured,
            }
            records.append(case)
            for key,arr in arrays.items():
                saved[name+"_"+witness+"_"+key]=arr
            print("ORIGINAL_ARC4_VERTICAL_CASE "+json.dumps({
                "case":name,"witness":witness,"sdk_level":case["original_sdk_official_level"],
                "official_advance":won,
                "selected_before_pour":case["original_source_selected_before_pour"],
                "P_and_Q":measured["P_and_Q"] if measured else None,
                "topmiddle_full":measured["R_topmiddle_cup_full"] if measured else None,
                "four_cups_full":measured["R_four_cups_simultaneously_full"] if measured else None,
            },sort_keys=True),flush=True)
    if len(records)!=24 or len(roots)!=1:
        raise AssertionError("Original native A/B case or Level4 source root mismatch")
    for name,_ in FROZEN:
        pair=[record for record in records if record["case"]==name]
        if len(pair)!=2 or {record["witness"] for record in pair}!={"A","B"}:
            raise AssertionError("Original independent native SDK A/B replays missing")
        if {k:v for k,v in pair[0].items() if k!="witness"}!={
                k:v for k,v in pair[1].items() if k!="witness"}:
            raise AssertionError("Independent original SDK replay drift: "+name)
    output={
        "kind":"ORIGINAL_ARC4_UPPER_CONTACT_XY_VERTICAL_BRACKET",
        "original_level4_source_root_blake2b16":next(iter(roots)),
        "frozen_stage4_source_words":[list(x) for x in FROZEN],
        "original_sdk_native_resets":len(records),
        "independent_original_native_witnesses":["A","B"],
        "official_sdk_level5_or_WIN_count":sum(int(r["official_level5_or_WIN"]) for r in records),
        "official_sdk_final_level_histogram":dict(Counter(str(r["original_sdk_official_level"]) for r in records)),
        "original_native_cases":records,
        "finite_question":"For original right-middle LEFT2 and upper LEFT2 (x34 edge) versus LEFT3 (x31 edge), do true UP1/DOWN1 upper native actions preserve or break the observed top-middle cup13 filling threshold?",
        "math_scope":"conditional finite native source predicate test observed finite 2D contact (x34 vs x31, y17/20/23) with cup response; no formal F3 A/B-to-SDK operator map",
        "native_antecedent_run":40165524676,
        "limits":"Only original source SDK levels_completed>=5/WIN is new progress, no inferred fluid physics or source-image win.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2)+"\n",encoding="utf8")
    np.savez_compressed(args.out.with_suffix(".npz"),**saved)
    print("ORIGINAL_ARC4_CONTACT_XY_SUMMARY "+json.dumps({
        "resets":len(records),
        "progress":output["official_sdk_level5_or_WIN_count"],
        "root":next(iter(roots)),
        "control_outcomes":[{"case":r["case"],"level":r["original_sdk_official_level"],
            "P_and_Q":r["original_sdk_native_visual_measurements"]["P_and_Q"] if r["original_sdk_native_visual_measurements"] else None,
            "topmiddle_full":r["original_sdk_native_visual_measurements"]["R_topmiddle_cup_full"] if r["original_sdk_native_visual_measurements"] else None,
            "four_full":r["original_sdk_native_visual_measurements"]["R_four_cups_simultaneously_full"] if r["original_sdk_native_visual_measurements"] else None,
        } for r in records if r["witness"]=="A"],
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
