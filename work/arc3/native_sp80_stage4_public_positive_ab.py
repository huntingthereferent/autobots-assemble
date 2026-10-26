"""ARC4 SP80 independent ORIGINAL SDK replication of a PUBLISHED level5 trace.

Public third-party SOURCE (external positive-control proposal, not our
discovery or a claimed explanation of game physics):
https://github.com/synchopate/arc-agi-crystalline/blob/main/solvers/recorded_solutions.json
sp80, action positions 48..64 inclusive (after the fourth public
winning ACTION5) has 17 native actions. The public repo *claims* 6/6.
This worker must **not** treat that as proof. The original native SDK
official levels_completed>=5/WIN is the ONLY win oracle.

Two independent true verified Stage0->4 SDK entries; compare
A: previously original 21-action BASE + ACTION5 4-cup failure
B: independently published 17-action Stage4 candidate.
Record true selection palettes, complete original 64x64 frames, official
level before/after every true action, and all spill/cup observations.
The old F3 48-law rooted mathematics is recalibrated but not edited
or conflated with the native original six-action game.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
from hashlib import blake2b
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE,read_pour
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

EXTERNAL_PUBLISHED_ACTIONS=(
  "3 3 1 6@25,34 4 1 1 6@34,22 3 2 "
  "6@34,43 4 4 4 1 1 5")
CASES=(
 ("own_original_native_full_cups_failed",BASE+" 5"),
 ("independent_published_stage5_action_trace",EXTERNAL_PUBLISHED_ACTIONS),
)
assert len(parse_plan(EXTERNAL_PUBLISHED_ACTIONS))==17
assert [xy for a,xy in parse_plan(EXTERNAL_PUBLISHED_ACTIONS) if a==6]==[
 (25,34),(34,22),(34,43)]
assert all(parse_plan(w)[-1][0]==5 for name,w in CASES)
assert len(STAGE1_WITNESSES)==2

def digest(arr):
    return blake2b(np.ascontiguousarray(arr).tobytes(),digest_size=16).hexdigest()

def first_spill_line_signal(pre,animation):
    # LEVEL5 (index4) is drawn upside-down; public community description
    # says top horizontal and right vertical floor/spill lines.
    # Exclude the top-right corner overlap between sides.
    top=(slice(2,5),slice(5,59))
    right=(slice(5,59),slice(59,62))
    def first(scope):
        y,x=scope
        mask=(pre[y,x]==1)
        return next((int(t) for t,f in enumerate(animation)
                     if np.any(mask&(f[y,x]==14))),None)
    return {"first_original_TOP_floor_line_palette1_to14":first(top),
            "first_original_RIGHT_vertical_spill_line_palette1_to14":first(right),
            "top_right_corner_excluded_from_both_measurements":True}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();math=f3_calibration()
    rows=[];arrays={};roots=set()
    for case,word in CASES:
        actions=parse_plan(word);n=len(actions)
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            ledger=sdk["genuine_original_stage4_action_ledger"]
            if not ledger:raise AssertionError("Missing authentic original SDK trial")
            pour_steps=[r for r in ledger if r["genuine_original_action"]==5]
            if len(pour_steps)!=1:
                raise AssertionError("Expected exactly one genuine SDK pour")
            last=pour_steps[-1];i=last["index"]
            if i!=n or last["genuine_original_action"]!=5:
                raise AssertionError("Source trial ended before expected original pour")
            pre=raw[f"stage4_{i-1}"][-1]
            frames=raw[f"stage4_{i}"]
            if frames.ndim!=3 or frames.shape[1:]!=(64,64):
                raise AssertionError("Missing original 64x64 returned SDK animation")
            clicks=[r for r in ledger if r["genuine_original_action"]==6]
            if case=="independent_published_stage5_action_trace":
                expected=[([25,34],8),([34,22],8),([34,43],15)]
                if len(clicks)!=3 or any(
                     r["real_native_click_xy"]!=xy or
                     r["original_source_pixel_before_click"]!=palette
                     for r,(xy,palette) in zip(clicks,expected)):
                    raise AssertionError("Public native program click palettes do not match actual rooted original board")
            cups=read_pour(root,pre,frames)
            warnings=first_spill_line_signal(pre,frames)
            result={
              "trial_origin":"originally researched BASE" if case.startswith("own_") else
                  "published external independent action witness replayed natively",
              "case":case,"original_independent_entry":witness,
              "exact_source_stage4_word":word,
              "official_original_sdk_final_level":sdk["true_original_sdk_final_level"],
              "official_original_sdk_final_state":sdk["true_original_sdk_final_state"],
              "official_native_level5_or_WIN":sdk["official_original_level5_or_WIN"],
              "actual_original_action5_level_before":last["original_sdk_level_before"],
              "actual_original_action5_level_after":last["original_sdk_level_after"],
              "real_native_selected_source_palette_receipts":clicks,
              "authentic_rooted_original_frame_before_pour_digest":hash_frame(pre),
              "real_original_sdk_returned_pour_frame_count":len(frames),
              "true_original_sdk_returned_pour_blake2b16":digest(frames),
              "genuine_native_source_cup_metrics":cups,
              "actual_source_floor_spill_line_metrics":warnings,
              "full_genuine_original_sdk_stage4_action_ledger":ledger,
            }
            rows.append(result)
            arrays[f"{case}_{witness}_pre"]=pre
            arrays[f"{case}_{witness}_true_native_pour"]=frames
            print("SP80_TRUE_NATIVE_EXTERNAL_AB_CASE "+json.dumps({
                "case":case,"entry":witness,
                "official_level":result["official_original_sdk_final_level"],
                "official_state":result["official_original_sdk_final_state"],
                "original_action5_native_level_delta":[
                  result["actual_original_action5_level_before"],
                  result["actual_original_action5_level_after"]],
                "native_returned_frame_count":len(frames),
                "four_cups_full_source_frames":cups["same_sdk_frame_full_four_cups"],
                "actual_spill_line_first":warnings,
                "real_source_clicked_palettes":[r["original_source_pixel_before_click"] for r in clicks],
            },sort_keys=True),flush=True)
    if len(rows)!=4 or len(roots)!=1:raise AssertionError("Independent original SDK entries disagree")
    for case,_ in CASES:
        a,b=[r for r in rows if r["case"]==case]
        for k in ("official_original_sdk_final_level","official_original_sdk_final_state",
                  "true_original_sdk_returned_pour_blake2b16",
                  "genuine_native_source_cup_metrics","actual_source_floor_spill_line_metrics"):
            if a[k]!=b[k]:raise AssertionError("True native SDK source witnesses diverged "+case)
    result={
        "kind":"TRUE_ORIGINAL_SP80_STAGE4_INDEPENDENT_PUBLIC_ACTION_TRACE_REPLICATION_AB",
        "source_public_comparator_url":"https://github.com/synchopate/arc-agi-crystalline/blob/main/solvers/recorded_solutions.json",
        "published_game_solution_segment":"sp80 zero-based positions 48..64, true game fifth level",
        "genuine_original_normal_sdk_reset_games":len(rows),
        "native_verified_common_stage4_source_root":next(iter(roots)),
        "official_native_level5_or_WIN":[r["case"] for r in rows if r["official_native_level5_or_WIN"]],
        "true_original_sdk_level_counts":dict(Counter(str(r["official_original_sdk_final_level"]) for r in rows)),
        "distinct_control_source_words":CASES,
        "existing_48_law_F3_root_certificate_separately_executed":math,
        "complete_original_sdk_native_replay_receipts":rows,
        "limitation":"The public action trace is attributed external evidence, not authored here. It is not SDK proof until genuinely reproduced, and SDK after_level>=5/WIN alone confirms progression. Do not copy external solver code or modify original F3/canonical agent."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_TRUE_NATIVE_EXTERNAL_AB_SUMMARY "+json.dumps({
       k:v for k,v in result.items() if k not in
         ("distinct_control_source_words","complete_original_sdk_native_replay_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
