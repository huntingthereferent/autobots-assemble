"""Original SP80 Level4: bounded left-middle source-adjacency displacement.

Native source run 40166014281 shows genuine selected left-middle bar x14..22
at y41..43 or y44..46, immediately to the RIGHT of the observed ascending
palette6 stream at x11..13. The independently observed 45/45 top-middle
contact is kept fixed: right-middle LEFT2 + upper LEFT2 (edge x34).
Freeze native LEFT1/HOLD/RIGHT1/RIGHT2 adjustments to the LEFT-MIDDLE bar;
no asserted game physics or invented formal F3-to-SDK generator map.

Original native Level4 reset; full original 64x64 SDK returned arrays;
official levels_completed>=5/WIN remains the sole progress oracle.
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

RIGHT_FIXED="6@46,33 3 3"
UPPER_FIXED="6@34,21 3 3"
PARENTS=(
 ("D3L2_L3U2","2 2 2 3 3","6@34,42 3 3 3 1 1",41),
 ("D4L2_L4U2","2 2 2 2 3 3","6@34,42 3 3 3 3 1 1",44),
)
MIDDLE_MOVES=(("LEFT1","3"),("HOLD",""),("RIGHT1","4"),("RIGHT2","4 4"))
def plan(base,middle,l):
    return " ".join(p for p in (
        RIGHT_FIXED, "6@24,33 "+base+(" "+middle if middle else ""),
        l, UPPER_FIXED, "5") if p)
FROZEN=tuple(
 (f"{parent}_{move}",plan(base,commands,l))
 for parent,base,l,y in PARENTS
 for move,commands in MIDDLE_MOVES
)
assert len(FROZEN)==8==len({name for name,word in FROZEN})
assert tuple(name for name,word in STAGE1_WITNESSES)==("A","B")
assert all(parse_plan(word)[-1][0]==5 and
           sum(a==5 for a,xy in parse_plan(word))==1 and
           sum(a==6 for a,xy in parse_plan(word))==4
           for name,word in FROZEN)

def target_middle_bbox(root,mid_frames):
    ys,xs=np.nonzero(mid_frames==9)
    if len(xs)!=27:
        raise ValueError("Original left-middle selected bar must be exactly 27 source pixels")
    return [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]

def source_probe(root,pre,pour):
    m=measured_actual_native(root,pre,pour)
    cup=m["original_source_cup_max_palette13_pixels"]
    site=m["first_original_color6_at_3_upper_sites"]
    first={name:None for name in ("x5_7","x8_10","x11_13","x14_16","x17_19","x20_22")}
    for frame_id,frame in enumerate(pour):
        new=(pre!=6)&(frame==6)
        for name in first:
            x0=int(name.split("_")[0][1:])
            if first[name] is None and np.any(new[5:8,x0:x0+3]):
                first[name]=frame_id
    return {
       "genuine_source_measurements":m,
       "first_new_palette6_upper_left_by_column":first,
       "upper_left_offcup_any_x5_16":any(first[k] is not None
                                          for k in ("x5_7","x8_10","x11_13","x14_16")),
       "leftmost_x11_13_new6":site["leftmost_outside_cup"] is not None,
       "all_four_cups_simultaneous":m["native_first_simultaneously_full_four_cups"] is not None,
       "topmiddle_max13":cup["top_middle"],
       "top_left_max13":cup["top_left"],
       "selected_upper_original_prepour_hash":hash_frame(pre),
       "original_sdk_pour_last_hash":hash_frame(pour[-1]),
    }
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    rows=[];frames={};roots=set()
    for name,word in FROZEN:
        commands=parse_plan(word)
        parent,move=name.rsplit("_",1)
        pd={p:(base,l,y) for p,base,l,y in PARENTS}
        base,l,y=pd[parent]
        # Source-selected original left-middle bar after the last bar move,
        # immediately before the separate real lower-L ACTION6 selection.
        mid_actions=len(parse_plan(" ".join((
            RIGHT_FIXED,"6@24,33 "+base+
              (" "+dict(MIDDLE_MOVES)[move] if dict(MIDDLE_MOVES)[move] else "")
        ))))
        for witness,entry in STAGE1_WITNESSES:
            actual,native=run_case(name,witness,entry,word)
            ledger=actual["genuine_original_stage4_action_ledger"]
            root=native["entry3_34"][-1]
            roots.add(hash_frame(root))
            complete=len(ledger)==len(commands)
            won=bool(actual["official_original_level5_or_WIN"])
            if ([e["genuine_original_action"] for e in ledger] !=
                [a for a,xy in commands[:len(ledger)]] or
                (not complete and not won)):
                raise ValueError("Genuine original SDK frozen Level4 source program diverged")
            if len(ledger)<mid_actions:
                raise ValueError("Original native left-middle move did not return")
            mid_end=native["stage4_"+str(mid_actions)][-1]
            mid_bbox=target_middle_bbox(root,mid_end)
            pre=native["stage4_"+str(len(ledger)-1)][-1]
            final=native["stage4_"+str(len(ledger))]
            observed=source_probe(root,pre,final) if ledger[-1]["genuine_original_action"]==5 else None
            row={
              "case":name,"witness":witness,"frozen_original_stage4_word":word,
              "original_native_mid_last_action_index":mid_actions,
              "original_native_mid_selected_bbox":mid_bbox,
              "original_native_frozen_word_complete":complete,
              "original_native_actions_executed":len(ledger),
              "official_original_sdk_level":actual["true_original_sdk_final_level"],
              "official_original_sdk_state":actual["true_original_sdk_final_state"],
              "official_original_sdk_level5_or_WIN":won,
              "actual_native_stage4_action_ledger":ledger,
              "original_native_observation":observed,
            }
            rows.append(row)
            for key,stack in native.items():frames[f"{name}_{witness}_{key}"]=stack
            print("ARC4_MID_SOURCE_OFFSET_CASE "+json.dumps({
               "case":name,"witness":witness,"middle_selected_bbox":mid_bbox,
               "official_level":row["official_original_sdk_level"],
               "new_level5":won,
               "upper_left_offcup":observed["first_new_palette6_upper_left_by_column"] if observed else None,
               "four_cups":observed["all_four_cups_simultaneous"] if observed else None,
               "topmiddle":observed["topmiddle_max13"] if observed else None,
            },sort_keys=True),flush=True)
    if len(rows)!=16 or roots!={"fa8fd32d3bfd2c8b3ff7765aec373512"}:
        raise ValueError("Actual original SDK level4 root or independent native A/B reset count drift")
    for name,word in FROZEN:
        a,b=[row for row in rows if row["case"]==name]
        if a["witness"]!="A" or b["witness"]!="B" or (
          {k:v for k,v in a.items() if k!="witness"} !=
          {k:v for k,v in b.items() if k!="witness"}
        ):raise ValueError("Actual original SDK independently reset A/B disagreement")
    out={
      "kind":"ORIGINAL_SP80_LEVEL4_NATIVE_LEFT_MIDDLE_SOURCE_ADJACENCY",
      "parent_native_run":40166014281,
      "native_level4_root":next(iter(roots)),
      "frozen_words":[list(x) for x in FROZEN],
      "original_native_sdk_resets":len(rows),
      "genuine_original_level5_or_WIN_count":sum(int(row["official_original_sdk_level5_or_WIN"]) for row in rows),
      "genuine_original_sdk_final_levels":dict(Counter(str(row["official_original_sdk_level"]) for row in rows)),
      "original_native_cases":rows,
      "finite_math_question":"Does shifting observed left-middle 9x3 original bar one 3px source tile LEFT or RIGHT1/2 from x14..22 displace the neighboring ascending source x11..13 and preserve all four original cup windows and official status under proven R2 U2 contact?",
      "limits":"Finite original SDK source relationship, not decoded fluid-engine physics or mapping to formal F3 A/B operators. Only actual SDK levels_completed>=5/WIN is progression."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n",encoding="utf8")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames)
    print("ARC4_MID_SOURCE_OFFSET_SUMMARY "+json.dumps({
      "resets":len(rows),"native_advances":out["genuine_original_level5_or_WIN_count"],
      "level4_root":next(iter(roots)),
      "source_cases":[{
         "case":row["case"],"bbox":row["original_native_mid_selected_bbox"],
         "left_offcup":row["original_native_observation"]["first_new_palette6_upper_left_by_column"] if row["original_native_observation"] else None,
         "four":row["original_native_observation"]["all_four_cups_simultaneous"] if row["original_native_observation"] else None,
         "topmiddle":row["original_native_observation"]["topmiddle_max13"] if row["original_native_observation"] else None,
         "level":row["official_original_sdk_level"]
      } for row in rows if row["witness"]=="A"]},sort_keys=True),flush=True)
if __name__=="__main__":main()
