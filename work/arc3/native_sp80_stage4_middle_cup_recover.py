"""Original SP80 upper branch A/B: can a disjoint 135/180 stream
recover the missing 45 top-middle cup pixels by vertically offsetting
the two demonstrably flow-causal bars?

Authentic prior #40380594843: moving upper original palette8 bar
RIGHT1 and middle-right original palette8 bar LEFT1 created two
separate live source6 components but top-middle cup remained 0/45.
Source row around x44..46/y5 is just beyond top-middle cup x35..43.
The present bounded native tests adjust upper or right-middle vertical
alignment, not an unfounded 48-cell grid sweep. F3 rooted proof
calibration remains distinct from private SDK fluid logic.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from hashlib import blake2b
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE,read_pour
from .native_sp80_stage4_dual_inlet_contact import source_4_neighbor_components
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

FROZEN=(
 ("known_separated_135_cup_source","6@34,21 4 6@42,33 3"),
 ("upper_up1_maintain_sep","6@34,21 4 1 6@42,33 3"),
 ("upper_down1_maintain_sep","6@34,21 4 2 6@42,33 3"),
 ("middle_up1_maintain_sep","6@34,21 4 6@42,33 3 1"),
 ("middle_down1_maintain_sep","6@34,21 4 6@42,33 3 2"),
 ("upper_down1_middle_up1","6@34,21 4 2 6@42,33 3 1"),
)
assert len(FROZEN)==6 and len(STAGE1_WITNESSES)==2
assert all(len(parse_plan(BASE+" "+w+" 5"))<100 for n,w in FROZEN)

def digest(a):return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()

def native_inlet_occupancy(frame):
    comps=source_4_neighbor_components(frame)
    both=any(c["touches_original_A_inlet"] for c in comps) and any(
         c["touches_original_B_inlet"] for c in comps)
    joined=any(c["touches_original_A_inlet"] and c["touches_original_B_inlet"] for c in comps)
    return both,joined

def measure_frame(frame,root):
    rect=(
      (slice(35,44),slice(5,11)),
      (slice(5,11),slice(17,26)),
      (slice(5,11),slice(35,44)),
      (slice(5,11),slice(47,56)),
    )
    cups=[int(np.count_nonzero((root[y,x]==11)&(frame[y,x]==13))) for y,x in rect]
    present,connected=native_inlet_occupancy(frame)
    return {
      "authentic_original_cup_pixel_counts":cups,
      "original_source_inputs_both_present":present,
      "original_source_inputs_connected":connected,
      "original_palette6_feeding_middle_cup_x35_46_y5_13":
            int(np.count_nonzero(frame[5:14,35:47]==6)),
      "original_source6_at_center_outlet_y5_7_x35_49":
            int(np.count_nonzero(frame[5:8,35:50]==6)),
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    theory=f3_calibration()
    rows=[];arrays={};roots=set()
    for name,addition in FROZEN:
        word=BASE+" "+addition+" 5"
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(name,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            frames=raw[f"stage4_{n}"]
            pre=raw[f"stage4_{n-1}"][-1]
            if frames.ndim!=3 or frames.shape[1:]!=(64,64):
                raise AssertionError("Native original SP80 frames missing")
            ledger=sdk["genuine_original_stage4_action_ledger"]
            extra=ledger[len(parse_plan(BASE)):-1]
            clicks=[x for x in extra if x["genuine_original_action"]==6]
            if (len(clicks)!=2 or clicks[0]["real_native_click_xy"]!=[34,21] or
                clicks[1]["real_native_click_xy"]!=[42,33] or
                clicks[0]["original_source_pixel_before_click"]!=8 or
                clicks[1]["original_source_pixel_before_click"]!=8):
                raise AssertionError("Original two native right/upper palette8 objects not selected")
            obs=[measure_frame(f,root) for f in frames]
            peak=max(sum(q["authentic_original_cup_pixel_counts"]) for q in obs)
            strongest=[i for i,v in enumerate(obs)
                       if sum(v["authentic_original_cup_pixel_counts"])==peak]
            full=[i for i,v in enumerate(obs) if v["authentic_original_cup_pixel_counts"]==[45]*4]
            sep=[i for i,v in enumerate(obs) if v["original_source_inputs_both_present"] and
                 not v["original_source_inputs_connected"]]
            full_sep=[i for i in full if i in sep]
            best_middle=max(v["authentic_original_cup_pixel_counts"][2] for v in obs)
            record={
               "frozen_original_sdk_case":name,
               "independent_native_original_entry":witness,
               "true_original_sdk_stage4_action_word":word,
               "authentic_sdk_bar_selection_receipts":clicks,
               "true_original_prepour_full_source_digest":hash_frame(pre),
               "original_native_animation_nonclock_digest":digest(frames[:,:63]),
               "actual_sdk_all_animation_frame_measurements":obs,
               "original_four_cup_all_full_frames":full,
               "original_four_cup_all_full_and_inlets_separate_frames":full_sep,
               "original_two_source_inlets_separate_frames":sep,
               "highest_source_cup_pixel_total":peak,
               "maximum_top_middle_cup_pixels":best_middle,
               "native_observation_at_max_cup_frame":obs[strongest[0]],
               "true_original_sdk_final_level":sdk["true_original_sdk_final_level"],
               "true_original_sdk_final_state":sdk["true_original_sdk_final_state"],
               "official_original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
               "real_original_sdk_stage4_action_receipts":ledger,
            }
            rows.append(record)
            arrays[f"{name}_{witness}_original_prepour"]=pre
            arrays[f"{name}_{witness}_original_pour_frames"]=frames
            print("SP80_NATIVE_MIDDLE_CUP_RECOVERY_AB_CASE "+json.dumps({
               "case":name,"witness":witness,
               "sdk_level":record["true_original_sdk_final_level"],
               "sdk_state":record["true_original_sdk_final_state"],
               "maximum_cup_pixel_counts":record["native_observation_at_max_cup_frame"][
                  "authentic_original_cup_pixel_counts"],
               "maximum_top_middle_pixels":best_middle,
               "any_source_sep_frames":len(sep),
               "four_cup_full_frames":full,
               "four_cup_disconnected_frames":full_sep,
            },sort_keys=True),flush=True)
    if len(rows)!=12 or len(roots)!=1:raise AssertionError("Missing independent native SDK games")
    for case,_ in FROZEN:
        a,b=[r for r in rows if r["frozen_original_sdk_case"]==case]
        for key in ("original_native_animation_nonclock_digest",
                    "actual_sdk_all_animation_frame_measurements",
                    "true_original_sdk_final_level","true_original_sdk_final_state"):
            if a[key]!=b[key]:raise AssertionError("Independent true original SDK witness disagreement "+case)
    report={
      "kind":"ORIGINAL_NATIVE_SP80_UPPER_MIDDLE_CUP_RECOVERY_DISJOINT_SOURCE_AB",
      "genuine_original_sdk_reset_games":len(rows),
      "true_native_stage4_root":next(iter(roots)),
      "maximum_top_middle_cup_pixels_by_case":{
          r["frozen_original_sdk_case"]:r["maximum_top_middle_cup_pixels"]
          for r in rows if r["independent_native_original_entry"]==STAGE1_WITNESSES[0][0]},
      "genuine_full_cup_and_separate_source_cases":sorted(set(r["frozen_original_sdk_case"]
          for r in rows if r["original_four_cup_all_full_and_inlets_separate_frames"])),
      "official_original_level5_or_WIN_cases":sorted(set(r["frozen_original_sdk_case"]
          for r in rows if r["official_original_level5_or_WIN"])),
      "original_sdk_level_histogram":dict(Counter(str(r["true_original_sdk_final_level"]) for r in rows)),
      "separate_existing_F3_math_rooted_certificate":theory,
      "prospectively_frozen_native_source_cases":FROZEN,
      "original_native_complete_action_and_source_evidence":rows,
      "limit":"Original source palette6 components and palette13 cups are observations, not hidden rules. Official levels_completed>=5/WIN alone is progress."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_NATIVE_MIDDLE_CUP_RECOVERY_AB_SUMMARY "+json.dumps({
       k:v for k,v in report.items() if k not in
        ("prospectively_frozen_native_source_cases","original_native_complete_action_and_source_evidence")
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
