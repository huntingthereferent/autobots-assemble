"""Native original SP80 Level4: simultaneous four-cup/no-new-upper-palette6
discriminator. Source frame pixels are NOT a decoded private objective.

Across 334 archived original SDK pour stacks, new palette6 at y5..7 was
followed one SDK-returned frame later by a top palette14 border flash.
The known stage4 parent has all four original cup windows source13-full,
but remains officially Level4. Test bounded upper-bar vs right-middle
bar placements and two action orders rather than replay old single moves.

NO hidden rules/physics, no synthetic game. Only real SDK level>=5/WIN
counts progression. Preserve complete actual SDK returned 64x64 frames.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE, read_pour
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

# Both native palette8 click centers were independently verified in source.
UPPER_CLICK="6@34,21"
RIGHT_CLICK="6@42,33"
# Native base places four lower objects in a previously verified full-cup geometry.
# Both source objects remain palette8 and independently selectable after BASE.
def phrase(label,direction,n):
    if not n:return label
    return label+" "+" ".join([str(direction)]*n)

FROZEN=tuple(
 (f"upperL{u}_rightL{r}",
  " ".join((BASE,phrase(UPPER_CLICK,3,u),phrase(RIGHT_CLICK,3,r),"5")))
 for u in (1,2,3,4) for r in (1,2,3,4)
)+tuple(
 (f"rightFirst_L{r}_upperL{u}",
  " ".join((BASE,phrase(RIGHT_CLICK,3,r),phrase(UPPER_CLICK,3,u),"5")))
 for u,r in ((2,1),(2,2),(2,3),(3,2))
)+tuple(
 (f"upperL2_rightL{r}_{vertical}",
  " ".join((BASE,phrase(UPPER_CLICK,3,2),phrase(RIGHT_CLICK,3,r),
            "1" if vertical=="up" else "2","5")))
 for r in (2,3,4) for vertical in ("up","down")
)
assert len(FROZEN)==26==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(word)[-1][0]==5 and
           sum(a==5 for a,xy in parse_plan(word))==1 and
           len(parse_plan(word))<=34 and
           all(xy is not None for a,xy in parse_plan(word) if a==6)
           for name,word in FROZEN)

def see_original(pre,root,frames):
    if (pre.shape!=(64,64) or root.shape!=(64,64) or
        frames.ndim!=3 or frames.shape[1:]!=(64,64)):
        raise AssertionError("Original 64x64 SDK source evidence required")
    newmask=(pre[5:8,5:59]!=6)
    border=(root[2:5,5:62]==1)
    newtimes=[t for t,f in enumerate(frames)
        if np.any(newmask&(f[5:8,5:59]==6))]
    flashtimes=[t for t,f in enumerate(frames)
        if np.any(border&(f[2:5,5:62]==14))]
    cells={}
    for x in range(5,59,3):
        if x+3>59:continue
        origin=pre[5:8,x:x+3]
        first=next((int(t) for t,f in enumerate(frames)
           if np.any((origin!=6)&(f[5:8,x:x+3]==6))),None)
        if first is not None:cells[f"x{x}-{x+2}"]=first
    return {
       "first_new_original_palette6_y5_7":int(newtimes[0]) if newtimes else None,
       "first_original_top_palette14_border":int(flashtimes[0]) if flashtimes else None,
       "any_new_upper_palette6":bool(newtimes),
       "any_original_top_border_flash":bool(flashtimes),
       "new_upper_palette6_cell_first_frames":cells,
       "pre_action_upper_palette6_pixel_count":int(np.count_nonzero(pre[5:8,5:59]==6)),
       "full_returned_sdk_frames":len(frames),
       "source_pre_frame_blake2b16":hash_frame(pre),
       "source_post_frame_blake2b16":hash_frame(frames[-1])
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();rows=[];raw_frames={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,allstacks=run_case(case,witness,entry,word)
            root=allstacks["entry3_34"][-1]
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            pre=allstacks[f"stage4_{n-1}"][-1]
            frames=allstacks[f"stage4_{n}"]
            observed=see_original(pre,root,frames)
            cups=read_pour(root,pre,frames)
            receipts=sdk["genuine_original_stage4_action_ledger"]
            for click in ([34,21],[42,33]):
                hits=[e for e in receipts if e["genuine_original_action"]==6
                   and e["real_native_click_xy"]==click]
                if len(hits)!=1 or hits[0]["original_source_pixel_before_click"]!=8:
                    raise AssertionError("Expected actual source palette8 selection at "+str(click))
            both=bool(cups["same_sdk_frame_full_four_cups"])
            hit=bool(both and not observed["any_new_upper_palette6"])
            row={
                "prospectively_frozen_case":case,"original_independent_entry":witness,
                "true_original_stage4_word":word,
                "official_original_level":sdk["true_original_sdk_final_level"],
                "official_original_state":sdk["true_original_sdk_final_state"],
                "official_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "genuine_original_sdk_source_upper_strip":observed,
                "genuine_original_sdk_cup_frames":cups,
                "original_four_cups_and_no_new_top_palette6":hit,
                "complete_native_action_receipts":receipts}
            rows.append(row)
            for phase,stack in allstacks.items():
                raw_frames[f"{case}_{witness}_{phase}"]=stack
            print("SP80_LEVEL4_UPPER_STRIP_COUNTEREXAMPLE_CASE "+json.dumps({
                "case":case,"witness":witness,
                "level":row["official_original_level"],
                "state":row["official_original_state"],
                "new_top_palette6":observed["any_new_upper_palette6"],
                "first_top_palette6":observed["first_new_original_palette6_y5_7"],
                "flash":observed["first_original_top_palette14_border"],
                "all_four_full_sdk_frames":cups["same_sdk_frame_full_four_cups"],
                "four_cup_without_upper_new6":hit,
            },sort_keys=True),flush=True)
    if len(rows)!=52 or len(roots)!=1:
        raise AssertionError("Missing independent original SDK source witness")
    for name,_ in FROZEN:
        a,b=[r for r in rows if r["prospectively_frozen_case"]==name]
        if any(a[field]!=b[field] for field in (
            "official_original_level","official_original_state",
            "genuine_original_sdk_source_upper_strip",
            "genuine_original_sdk_cup_frames",
            "original_four_cups_and_no_new_top_palette6")):
            raise AssertionError("Two native SDK entry witnesses disagree "+name)
    summary={
       "kind":"TRUE_ORIGINAL_NATIVE_SP80_LEVEL4_FOUR_CUP_NO_NEW_UPPER_PALETTE6_HOLDOUT",
       "original_sdk_fresh_games":len(rows),
       "antecedent_source_native_runs":[40232179104,40232416450],
       "identical_native_stage4_source_root":next(iter(roots)),
       "four_cup_no_new_upper_source_cases":list(sorted({
          r["prospectively_frozen_case"] for r in rows
          if r["original_four_cups_and_no_new_top_palette6"]})),
       "official_level5_or_WIN_cases":list(sorted({
          r["prospectively_frozen_case"] for r in rows if r["official_level5_or_WIN"]})),
       "official_original_level_counts":dict(Counter(str(r["official_original_level"]) for r in rows)),
       "official_original_state_counts":dict(Counter(str(r["official_original_state"]) for r in rows)),
       "source_pour_without_upper_new6":sum(
          int(not r["genuine_original_sdk_source_upper_strip"]["any_new_upper_palette6"]) for r in rows),
       "frozen_native_source_programs":FROZEN,
       "full_true_original_sdk_action_frame_receipts":rows,
       "limits":"Native SDK frame observations cannot assert private game rules. Only original level>=5/WIN is official success. No mathematics or canonical agent changes."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw_frames)
    print("SP80_LEVEL4_UPPER_STRIP_COUNTEREXAMPLE_SUMMARY "+
          json.dumps({k:v for k,v in summary.items() if k not in
          ("frozen_native_source_programs","full_true_original_sdk_action_frame_receipts")},
          sort_keys=True),flush=True)
if __name__=="__main__":main()
