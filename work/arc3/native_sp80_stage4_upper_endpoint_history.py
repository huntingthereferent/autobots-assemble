"""Original SP80 SDK: can equal visible upper-bar endpoints differ after ACTION5?

Prospectively frozen from 2026-10-24 native source run #40124724989.
Direct RIGHT1 leaves 2/4 cups full; LEFT1 fills 4/4; reselect fills 3/4.
This original-native test distinguishes final selected upper-bar geometry from
movement history, with a small local right-neighborhood. No emulation,
objective inference, image-only WIN or invented engine semantics.
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
FROZEN = (
    ("reselect", ""),
    ("right1", "4"),
    ("right2", "4 4"),
    ("left1", "3"),
    ("left1_right2", "3 4 4"),
    ("right1_left1", "4 3"),
    ("right1_up1", "4 1"),
    ("right1_down1", "4 2"),
)
MATCHED = (
    ("right1", "left1_right2"),
    ("reselect", "right1_left1"),
    ("right1", "right2"),
    ("right1", "right1_up1"),
    ("right1", "right1_down1"),
    ("reselect", "left1"),
)
CUPS = {
    "lateral": (5,35,10,43),
    "top_left": (17,5,25,10),
    "top_middle": (35,5,43,10),
    "top_right": (47,5,55,10),
}
assert len(FROZEN) == 8 == len(set(x[0] for x in FROZEN))
assert tuple(name for name, _ in STAGE1_WITNESSES) == ("A", "B")

def word(tail):
    return " ".join(s for s in (PARENT, tail, "5") if s)

def first_source_event(pre, frames, row):
    outside = np.ones(64, dtype=bool)
    for x0,y0,x1,y1 in CUPS.values():
        if y0 <= row <= y1:
            outside[x0:x1+1] = False
    for t, frame in enumerate(frames):
        pixels = np.flatnonzero(outside & (pre[row] != 6) & (frame[row] == 6))
        if len(pixels):
            return {"frame":int(t),"x":[int(x) for x in pixels]}
    return None

def source_observations(root, pre, frames):
    if root.shape != (64,64) or pre.shape != (64,64) or frames.ndim != 3 or frames.shape[1:] != (64,64):
        raise AssertionError("genuine original SDK 64x64 arrays required")
    first = {name:None for name in CUPS}
    maximum = {name:0 for name in CUPS}
    masks = {}
    for name,(x0,y0,x1,y1) in CUPS.items():
        region = root[y0:y1+1,x0:x1+1] == 11
        if int(region.sum()) != 45:
            raise AssertionError("original source cup mask changed")
        masks[name] = region
    four = None
    for t, frame in enumerate(frames):
        full = 0
        for name,(x0,y0,x1,y1) in CUPS.items():
            amount = int(np.count_nonzero(masks[name] & (frame[y0:y1+1,x0:x1+1] == 13)))
            maximum[name] = max(maximum[name],amount)
            if amount == 45:
                full += 1
                if first[name] is None:
                    first[name] = t
        if full == 4 and four is None:
            four = t
    yy,xx = np.nonzero(pre == 9)
    return {
        "source_stage4_root_hash":hash_frame(root),
        "original_prepour_hash":hash_frame(pre),
        "original_last_frame_hash":hash_frame(frames[-1]),
        "original_frame_count":len(frames),
        "selected_source_bbox":[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],
        "first_full_cup_frames":first,
        "maximum_original_cup13_pixels":maximum,
        "first_four_simultaneous_frame":four,
        "off_cup_row5_first_new6":first_source_event(pre,frames,5),
        "off_cup_row8_first_new6":first_source_event(pre,frames,8),
    }

def actual_frame_pair(a, b, cups=CUPS):
    apre, af = a
    bpre, bf = b
    if apre.shape != bpre.shape or af.ndim != 3 or bf.ndim != 3:
        raise AssertionError("original SDK source contrast incomplete")
    regions = {}
    for name,(x0,y0,x1,y1) in cups.items():
        found = next((int(i) for i in range(min(len(af),len(bf)))
                      if np.any(af[i,y0:y1+1,x0:x1+1] != bf[i,y0:y1+1,x0:x1+1])),None)
        regions[name] = found
    interior_first = next((int(i) for i in range(min(len(af),len(bf)))
                           if not np.array_equal(af[i,:63],bf[i,:63])),None)
    row63_first = next((int(i) for i in range(min(len(af),len(bf)))
                        if not np.array_equal(af[i,63],bf[i,63])),None)
    return {
        "prepour_differing_pixel_count":int(np.count_nonzero(apre!=bpre)),
        "prepour_interior_differing_pixel_count":int(np.count_nonzero(apre[:63]!=bpre[:63])),
        "prepour_bottom_row_differing_pixel_count":int(np.count_nonzero(apre[63]!=bpre[63])),
        "paired_frames":min(len(af),len(bf)),
        "animation_frame_counts":[len(af),len(bf)],
        "first_different_original_frame_in_rows0_62":interior_first,
        "first_different_original_frame_in_row63":row63_first,
        "first_differing_frame_by_cup":regions,
        "limits":"Frame indices are SDK returned-array indices; no physical clock or hidden-state model asserted.",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    rows = []; stored = {}; rawpairs = {}; roots=set()
    for case, tail in FROZEN:
        source_word = word(tail)
        actions = parse_plan(source_word)
        if actions[-1][0] != 5 or sum(x==5 for x,_ in actions)!=1 or len(actions)>26:
            raise AssertionError("frozen original SDK word altered")
        for witness, entry in STAGE1_WITNESSES:
            native, arrays = run_case(case,witness,entry,source_word)
            root = arrays["entry3_34"][-1]
            pre = arrays["stage4_"+str(len(actions)-1)][-1]
            frames = arrays["stage4_"+str(len(actions))]
            measured = source_observations(root,pre,frames)
            roots.add(measured["source_stage4_root_hash"])
            rows.append({
                "case":case,"witness":witness,"original_word":source_word,
                "official_level":native["true_original_sdk_final_level"],
                "official_state":native["true_original_sdk_final_state"],
                "official_level5_or_WIN":native["official_original_level5_or_WIN"],
                "source":measured,
                "native_action_receipts":native["genuine_original_stage4_action_ledger"],
            })
            rawpairs[(case,witness)] = (pre.copy(),frames.copy())
            for name, frameset in arrays.items():
                stored[case+"_"+witness+"_"+name]=frameset
            print("ARC4_HISTORY_CASE "+json.dumps({
                "case":case,"witness":witness,"official_level":native["true_original_sdk_final_level"],
                "official_state":native["true_original_sdk_final_state"],"source":measured},
                sort_keys=True),flush=True)
    if len(rows)!=16 or len(roots)!=1:
        raise AssertionError("independent native entry source receipts incomplete")
    for case,_ in FROZEN:
        a,b=[r for r in rows if r["case"]==case]
        if (a["witness"],b["witness"])!=("A","B") or any(
            a[key]!=b[key] for key in ("official_level","official_state","official_level5_or_WIN","source")
        ):
            raise AssertionError("original SDK independent witnesses disagree: "+case)
    relations={}
    for lhs,rhs in MATCHED:
        aa=actual_frame_pair(rawpairs[(lhs,"A")],rawpairs[(rhs,"A")])
        bb=actual_frame_pair(rawpairs[(lhs,"B")],rawpairs[(rhs,"B")])
        if aa!=bb:
            raise AssertionError("A/B original SDK comparison divergence: "+lhs+"/"+rhs)
        relations[lhs+"_vs_"+rhs]=aa
    outcomes={
        "kind":"ORIGINAL_SP80_UPPER_ENDPOINT_HISTORY_DISCRIMINATOR",
        "parent_provenance_native_run":40124724989,
        "original_sdk_resets":len(rows),
        "frozen_parent":PARENT,
        "frozen_controls":FROZEN,
        "frozen_matched_relations":MATCHED,
        "root_source_hash":next(iter(roots)),
        "official_level5_or_WIN_count":sum(int(x["official_level5_or_WIN"]) for x in rows),
        "official_level_histogram":dict(Counter(str(x["official_level"]) for x in rows)),
        "native_cases":rows,"actual_native_pairwise_relations":relations,
        "limits":"No hidden physics, no image-only WIN, no ARC-like maze substitution. Native official levels_completed>=5/WIN alone counts.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(outcomes,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**stored)
    print("ARC4_HISTORY_SUMMARY "+json.dumps({
        "original_sdk_resets":len(rows),
        "official_level_histogram":outcomes["official_level_histogram"],
        "official_level5_or_WIN_count":outcomes["official_level5_or_WIN_count"],
        "native_controls":{k:next(r["source"] for r in rows if r["case"]==k) for k,_ in FROZEN},
        "matched_relations":relations,
    },sort_keys=True),flush=True)
if __name__ == "__main__":
    main()
