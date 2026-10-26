"""Next owned SP80 source A/B from actual selected-L null-flow error.

Run 40420384579: last chosen original SDK word ended in
6@17,37 RIGHT UP LEFT DOWN; selected L x17..22,y35..40,
lateral cup 0/45, floor water x11,y5. Vertical L changes
the selected object without changing the measured water.
Do not load published winning words or alter F3 mathematics.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_ab_selected_L_continuity import TRUE_PREVIOUS_SELECTED_L
from .native_sp80_stage4_ab_operating_loop import one, describe, source_bars
from .native_sp80_multi_select import parse_plan

ROOT = TRUE_PREVIOUS_SELECTED_L + " 1 3 2"
assert len(parse_plan(ROOT)) < 70

def next_contact(frame, used):
    # Actual source components; ignore the already selected palette9 L.
    bars = [b for b in source_bars(frame)
            if b["color_before_click"] == 8]
    bars.sort(key=lambda b: (
        any(abs(b["click"][0]-x)+abs(b["click"][1]-y)<7 for x,y in used),
        abs(b["click"][0]-7)+abs(b["click"][1]-39),
        -b["cells"]))
    return bars

def difference(parent, candidate):
    a, b = parent["measure"], candidate["measure"]
    d = describe(parent, candidate)
    d["cup_changes"] = {
        k: [a["four_native_cup_peak_counts"][k], v]
        for k,v in b["four_native_cup_peak_counts"].items()
        if a["four_native_cup_peak_counts"][k] != v}
    d["first_real_water_before"] = a["observed_first_source6_near_top_floor"]
    d["first_real_water_after"] = b["observed_first_source6_near_top_floor"]
    d["warning_before"] = a["floor_lines"]
    d["warning_after"] = b["floor_lines"]
    d["official_original_sdk_level"] = b["official_sdk_level"]
    d["official_level5_or_WIN"] = b["official_level5_or_WIN"]
    if parent["frames"].shape == candidate["frames"].shape:
        d["changed_original_source6_pixels"] = int(np.count_nonzero(
            (parent["frames"] == 6) != (candidate["frames"] == 6)))
    else:
        d["changed_original_source6_pixels"] = None
    return d

def follow(parent, pair, round_index):
    d = [difference(parent, v) for v in pair]
    for i, v in enumerate(pair):
        if v["measure"]["official_level5_or_WIN"]:
            return v, "official original SDK level advancement", d
    def signature(t):
        return (len(t["cup_changes"]),
                int(t["first_real_water_before"] != t["first_real_water_after"]),
                int(t["warning_before"] != t["warning_after"]),
                t["changed_original_source6_pixels"] or 0,
                int(t["original_source6_animation_changed"]))
    scores = [signature(t) for t in d]
    idx = (round_index % 2) if scores[0] == scores[1] else (
        0 if scores[0] > scores[1] else 1)
    return pair[idx], "follow measured SDK distinction, even if worse or unchanged", d

def main():
    p=argparse.ArgumentParser(); p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    witness, entrance=STAGE1_WITNESSES[0]
    parent=one("observed_null_flow_parent",witness,entrance,ROOT+" 5")
    records=[parent]; rounds=[]; used=[]; rooted=ROOT
    for i, moves in enumerate(((3,4),(1,2),(3,4))):
        if parent["measure"]["official_level5_or_WIN"]:
            break
        observed=next_contact(parent["pre"],used)
        if not observed:
            rounds.append({"round":i,"technical_observation":
                           "no other source palette8 contact visible",
                           "parent_error":parent["measure"]["observed_error"]})
            break
        contact=observed[0]
        x,y=contact["click"]; used.append((x,y))
        pair=[]; boundaries=[]
        for name,move in zip(("A","B"),moves):
            word=rooted+f" 6@{x},{y} {move} 5"
            try:
                trial=one(f"next_contact_{i}_{name}",witness,entrance,word)
                records.append(trial); pair.append(trial)
            except Exception as exc:
                boundaries.append({"candidate":name,"source_word":word,
                                   "native_error":str(exc),
                                   "exception_type":type(exc).__name__})
        if len(pair)!=2:
            rounds.append({"round":i,"contact":contact,
                           "technical_boundaries":boundaries,
                           "observed_parent_error":parent["measure"]["observed_error"]})
            if not pair: break
            chosen=pair[0]; reason="other original action hit SDK boundary"
            changes=[difference(parent,chosen)]
        else:
            chosen,reason,changes=follow(parent,pair,i)
        rounds.append({"round":i,
                       "observed_parent_error":parent["measure"]["observed_error"],
                       "source_contacts":observed,
                       "source8_contact":contact,
                       "opposite_native_actions":list(moves),
                       "paired_results":[{"case":v["case"],"real_difference":d}
                                         for v,d in zip(pair,changes)],
                       "sdk_boundaries":boundaries,
                       "followed_real_case":chosen["case"],
                       "reason":reason})
        print("ARC4_NEXT_SOURCE_AB "+json.dumps(rounds[-1],sort_keys=True),
              flush=True)
        parent=chosen
        rooted=chosen["word"].rsplit(" 5",1)[0]
    witness2, entrance2=STAGE1_WITNESSES[1]
    replay=one("independent_original_entry",witness2,entrance2,parent["word"])
    records.append(replay)
    same=(replay["measure"]["official_sdk_level"]==
          parent["measure"]["official_sdk_level"] and
          replay["measure"]["source6_full_animation_digest"]==
          parent["measure"]["source6_full_animation_digest"])
    arrays={}; receipts=[]
    for t in records:
        for key,stack in t["source"].items():
            if key=="entry3_34" or key.startswith("stage4_"):
                arrays[f'{t["case"]}_{t["witness"]}_{key}']=stack
        receipts.append({k:v for k,v in t.items()
                         if k not in ("pre","frames","source")})
    report={"kind":"OWN_SP80_NATIVE_NEXT_SOURCE_CONTACT_AB",
            "rooted_error_from_run":40420384579,
            "rooted_original_failed_word":ROOT,
            "original_root_error":records[0]["measure"]["observed_error"],
            "native_ab_corrections":rounds,
            "actual_sdk_game_count":len(records),
            "independent_original_entry_matches":same,
            "next_actual_rooted_word":parent["word"],
            "next_actual_observed_error":parent["measure"]["observed_error"],
            "official_level5_or_WIN_cases":[t["case"] for t in records
                                          if t["measure"]["official_level5_or_WIN"]],
            "full_sdk_action_receipts":receipts,
            "published_solution_used":False,
            "F3_mathematics_changed":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ARC4_NEXT_SOURCE_AB_SUMMARY "+json.dumps({
        "games":len(records),"rounds":len(rounds),"independent_match":same,
        "official_progress":report["official_level5_or_WIN_cases"],
        "last_error":report["next_actual_observed_error"],
        "last_word":parent["word"]},sort_keys=True),flush=True)
    if not same: raise AssertionError("Original independent SDK witness differs")

if __name__=="__main__": main()
