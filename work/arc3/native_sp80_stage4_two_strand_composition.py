"""Original ARC SDK SP80 LEVEL 4: finite two-overflow composition test.

Native-only intervention is chosen from two independent archived source facts:
(1) upper LEFT6 removes x11..13/y5..7 first-arrival but retains visually four
cups in clean contexts (source run 39639320303, original artifact 12364922294);
(2) right-middle LEFT2 removes x56..58/y5..7 first-arrival but retains four
cups with upper LEFT1 (source run 39636999616, original artifact 12363215552).

Test the exact 2x2 product (right LEFT1/LEFT2 × upper LEFT1/LEFT6),
under each of two independently source-proven clean lower constructions.
No undocumented ARC physics or derived F3 action mapping is assumed. The
finite mathematical question is whether two observed properties compose.
Only the ORIGINAL SDK level>=5 or WIN establishes game progress.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from collections import Counter

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_leftmost_upper_contact import (
    measured_actual_native, CUPS, UPPER_SITES,
)
from .native_sp80_legal_pairs import hash_frame
from .native_sp80_multi_select import parse_plan

PARENTS=(
    ("D3L2_L3U2", "6@24,33 2 2 2 3 3", "6@34,42 3 3 3 1 1"),
    ("D4L2_L4U2", "6@24,33 2 2 2 2 3 3", "6@34,42 3 3 3 3 1 1"),
)
RIGHT=(("R1","3"),("R2","3 3"))
UPPER=(("U1","3"),("U6","3 3 3 3 3 3"))

def build_word(mid,l,right,upper):
    return " ".join(("6@46,33 "+right,mid,l,"6@34,21 "+upper,"5"))

FROZEN=tuple(
    (f"{name}_{rname}_{uname}",build_word(mid,l,rword,uword))
    for name,mid,l in PARENTS
    for rname,rword in RIGHT
    for uname,uword in UPPER
)
assert len(FROZEN)==8==len({name for name,_ in FROZEN})
assert tuple(name for name,_ in STAGE1_WITNESSES)==("A","B")
assert all(parse_plan(word)[-1][0]==5 and
           sum(action==5 for action,xy in parse_plan(word))==1 and
           all(xy is not None for action,xy in parse_plan(word) if action==6)
           for _,word in FROZEN)

def source_referent(root,pre,animation):
    observation=measured_actual_native(root,pre,animation)
    cup_max=observation["original_source_cup_max_palette13_pixels"]
    sites=observation["first_original_color6_at_3_upper_sites"]
    borders=observation["native_first_source_border_changes"]
    return {
        "measured_original_native":observation,
        "visual_four_cups_simultaneously_full":
            observation["native_first_simultaneously_full_four_cups"] is not None,
        "upper_left_source_strand_absent":
            sites["leftmost_outside_cup"] is None,
        "upper_right_source_strand_absent":
            sites["upper_right_outside"] is None,
        "both_tested_upstream_strands_absent":
            sites["leftmost_outside_cup"] is None and
            sites["upper_right_outside"] is None,
        "no_measured_top_or_right_border_change":
            borders["top"] is None and borders["right"] is None,
        "observed_full_cup_count_max":
            sum(int(value==45) for value in cup_max.values()),
        "source_stage4_root_hash":hash_frame(root),
        "source_original_prepour_hash":hash_frame(pre),
        "source_original_last_frame_hash":hash_frame(animation[-1]),
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    records=[];frames={};roots=set()
    for name,word in FROZEN:
        actions=parse_plan(word)
        for witness,stage1 in STAGE1_WITNESSES:
            sdk,raw=run_case(name,witness,stage1,word)
            actual=sdk["genuine_original_stage4_action_ledger"]
            root=raw["entry3_34"][-1]
            roots.add(hash_frame(root))
            require_actions=[a for a,_ in actions]
            actual_actions=[entry["genuine_original_action"] for entry in actual]
            if actual_actions!=require_actions[:len(actual_actions)]:
                raise AssertionError("Genuine SDK action word diverged")
            complete=len(actual)==len(actions)
            advance=sdk["official_original_level5_or_WIN"]
            if not complete and not advance:
                raise AssertionError("Original SDK missing action receipt before completion")
            pre=raw["stage4_"+str(len(actual)-1)][-1] if len(actual)>1 else root
            laststack=raw["stage4_"+str(len(actual))]
            measured=source_referent(root,pre,laststack) if actual[-1]["genuine_original_action"]==5 else None
            record={
                "case":name,"witness":witness,
                "frozen_original_source_word":word,
                "actual_executed_stage4_actions":len(actual),
                "native_complete_frozen_program":complete,
                "official_original_sdk_level":sdk["true_original_sdk_final_level"],
                "official_original_sdk_state":sdk["true_original_sdk_final_state"],
                "official_level5_or_WIN":bool(advance),
                "genuine_original_sdk_stage4_action_ledger":actual,
                "original_source_observation":measured,
            }
            records.append(record)
            for key,arr in raw.items():
                frames[f"{name}_{witness}_{key}"]=arr
            print("ARC4_ORIGINAL_NATIVE_COMPOSITION_CASE "+json.dumps({
                "case":name,"witness":witness,
                "official_sdk_level":record["official_original_sdk_level"],
                "official_progress":bool(advance),
                "source_four_full":measured["visual_four_cups_simultaneously_full"] if measured else None,
                "source_two_strands_absent":measured["both_tested_upstream_strands_absent"] if measured else None,
                "source_top_right_borders_clear":measured["no_measured_top_or_right_border_change"] if measured else None,
            },sort_keys=True),flush=True)
    if len(records)!=16 or len(roots)!=1:
        raise AssertionError("Source independent native A/B root/case drift")
    for name,_ in FROZEN:
        a,b=[record for record in records if record["case"]==name]
        if {x["witness"] for x in (a,b)}!={"A","B"}:
            raise AssertionError("Native original witness entry label mismatch")
        if {k:v for k,v in a.items() if k!="witness"}!={
                k:v for k,v in b.items() if k!="witness"}:
            raise AssertionError("Original independent SDK trial A/B disagreement")
    result={
        "kind":"ORIGINAL_SP80_STAGE4_TWO_SOURCE_STRAND_COMPOSITION",
        "original_sdk_level4_root_hash":next(iter(roots)),
        "frozen_level4_programs":[list(item) for item in FROZEN],
        "native_original_source_resets":len(records),
        "native_original_source_a_b_replays":2,
        "official_original_level5_or_WIN_count":
            sum(int(record["official_level5_or_WIN"]) for record in records),
        "official_original_sdk_level_histogram":
            dict(Counter(str(record["official_original_sdk_level"]) for record in records)),
        "original_native_cases":records,
        "precommitted_composition_question":
            "Does RIGHT LEFT2 compose with TOP LEFT6 to remove both independently observed upper side strands, retaining four cups and altering boundary contact?",
        "math_admission":"Finite empirical conjunction of two native source predicates; no proven map to F3 A/B",
        "provenance":[
            "original-native-run:39639320303;artifact:12364922294",
            "original-native-run:39636999616;artifact:12363215552",
        ],
        "limits":"Real SDK frames, receipts, source colors are evidence; only original SDK levels_completed>=5/WIN is progress. No inferred fluid model, game emulation, or finite-field generator identity.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames)
    print("ARC4_ORIGINAL_TWO_STRAND_SUMMARY "+json.dumps({
        "original_native_resets":len(records),
        "official_progress":result["official_original_level5_or_WIN_count"],
        "source_root":result["original_sdk_level4_root_hash"],
        "case_outcomes":[{
            "case":r["case"],
            "official_level":r["official_original_sdk_level"],
            "four_cups":r["original_source_observation"]["visual_four_cups_simultaneously_full"] if r["original_source_observation"] else None,
            "both_upstream_strands_absent":r["original_source_observation"]["both_tested_upstream_strands_absent"] if r["original_source_observation"] else None,
            "no_top_right_border_change":r["original_source_observation"]["no_measured_top_or_right_border_change"] if r["original_source_observation"] else None,
        } for r in records if r["witness"]=="A"],
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
