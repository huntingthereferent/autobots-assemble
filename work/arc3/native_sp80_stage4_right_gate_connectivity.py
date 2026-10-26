"""ARC4 original native SP80: selected right-middle gate vs observed A/B inlet linkage.

GROUNDED PRE-TEST (genuine original SDK artifact #12628356360):
BASE pre-POUR native palette8 right-middle source bar is x38..52/y32..34.
At original native ACTION5 full-four-cup frame23, palette6 is one
675-pixel four-neighbor source component containing BOTH bottom
source patches A=x20..22/y56..58, B=x44..46/y56..58.
The path between upper-left and right sources crosses source water
cells around x35..55/y35..37 just *below* that selectable bar.
Its original palette8 click point (42,33) was verified in native runs.

Causal A/B: preserve the 21-action real original full-cup geometry,
then actually select that native right-middle palette8 bar and move
it UP/DOWN/LEFT/RIGHT (small predetermined moves). Ask whether the
two source-water inlet components separate DURING a 4-cup-complete
SDK returned frame. Native level>=5/WIN alone counts advancement.
F3-48 mathematics remains separately checked and unmodified.
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

ORIGINAL_BAR_CLICK="6@42,33"
FROZEN=(
  ("existing_four_cup_source", ""),
  ("reselect_gate", ORIGINAL_BAR_CLICK),
  ("gate_up1", ORIGINAL_BAR_CLICK+" 1"),
  ("gate_down1", ORIGINAL_BAR_CLICK+" 2"),
  ("gate_down2", ORIGINAL_BAR_CLICK+" 2 2"),
  ("gate_left1", ORIGINAL_BAR_CLICK+" 3"),
  ("gate_right1", ORIGINAL_BAR_CLICK+" 4"),
  ("gate_down_then_left", ORIGINAL_BAR_CLICK+" 2 3"),
  ("gate_down_then_right", ORIGINAL_BAR_CLICK+" 2 4"),
)
assert len(FROZEN)==9 and len(STAGE1_WITNESSES)==2
assert len(parse_plan(BASE))==21
assert all(len(parse_plan(BASE+" "+suffix+" 5"))<=30 for case,suffix in FROZEN)

def blake(a):
    return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()

def frame_graph_observations(frames,full_cup_frames):
    every=[];full=set(full_cup_frames)
    for t,frame in enumerate(frames):
        components=source_4_neighbor_components(frame)
        a=any(c["touches_original_A_inlet"] for c in components)
        b=any(c["touches_original_B_inlet"] for c in components)
        connected=any(c["touches_original_A_inlet"] and c["touches_original_B_inlet"]
                      for c in components)
        # Inspect original source junction immediately below right bar,
        # never confuse palette connectivity with private fluid physics.
        band=frame[35:38,35:56]
        mid_band=int(np.count_nonzero(band==6))
        every.append({
            "sdk_returned_frame":int(t),
            "original_source_A_present":bool(a),
            "original_source_B_present":bool(b),
            "both_inlets_original_4_neighbor_connected":bool(connected),
            "four_original_cups_simultaneously_full":t in full,
            "palette6_pixels_in_right_middle_connection_band":mid_band,
            "all_native_source_components":components,
        })
    return {
        "all_actual_returned_frame_graphs":every,
        "both_source_inlets_disconnected_full_four_cup_frames":[x["sdk_returned_frame"]
             for x in every if x["four_original_cups_simultaneously_full"] and
              x["original_source_A_present"] and x["original_source_B_present"] and
              not x["both_inlets_original_4_neighbor_connected"]],
        "inlets_connected_full_cup_frames":[x["sdk_returned_frame"]
             for x in every if x["four_original_cups_simultaneously_full"] and
              x["both_inlets_original_4_neighbor_connected"]],
        "frames_with_both_real_inlets_present_but_separate":[x["sdk_returned_frame"]
             for x in every if x["original_source_A_present"] and
                x["original_source_B_present"] and not
                x["both_inlets_original_4_neighbor_connected"]],
        "first_4_cup_frame_band_palette6_pixels":next(
            (x["palette6_pixels_in_right_middle_connection_band"] for x in every
             if x["four_original_cups_simultaneously_full"]),None)
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();f3=f3_calibration()
    rows=[];raw_arrays={};roots=set()
    for case,suffix in FROZEN:
        word=" ".join(v for v in (BASE,suffix,"5") if v)
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,stacks=run_case(case,witness,entry,word)
            root=stacks["entry3_34"][-1]
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            before=stacks[f"stage4_{n-1}"][-1]
            animation=stacks[f"stage4_{n}"]
            assert before.shape==(64,64) and animation.ndim==3 and animation.shape[1:]==(64,64)
            if int(root[33,42])!=9:
                raise AssertionError("Original right-middle root source pixel palette9 changed")
            base_n=len(parse_plan(BASE))
            extra=sdk["genuine_original_stage4_action_ledger"][base_n:]
            if suffix:
                first=extra[0]
                if (first["genuine_original_action"]!=6 or
                    first["real_native_click_xy"]!=[42,33] or
                    first["original_source_pixel_before_click"]!=8):
                    raise AssertionError("Right-middle bar not genuinely palette8 selectable after BASE")
            if len(extra)!=len(parse_plan(suffix))+1 or extra[-1]["genuine_original_action"]!=5:
                raise AssertionError("Missing actual original SDK frozen action")
            cups=read_pour(root,before,animation)
            source=frame_graph_observations(animation,cups["same_sdk_frame_full_four_cups"])
            report={
                "case":case,"independent_original_sdk_entry":witness,
                "true_stage4_source_word":word,
                "real_selected_gate_click_pixel":extra[0]["original_source_pixel_before_click"] if suffix else None,
                "actual_native_bar_edit_receipts":extra[:-1],
                "native_original_prepour_full_frame_digest":hash_frame(before),
                "native_original_prepour_without_clock_digest":blake(before[:63]),
                "actual_original_full_returned_pour_digest":blake(animation),
                "actual_original_nonclock_returned_pour_digest":blake(animation[:,:63]),
                "native_observed_four_cup_source_measures":cups,
                "actual_original_A_B_source_graph_observations":source,
                "original_native_official_level":sdk["true_original_sdk_final_level"],
                "original_native_official_state":sdk["true_original_sdk_final_state"],
                "official_native_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "last_real_original_sdk_action_receipt":extra[-1],
            }
            rows.append(report)
            raw_arrays[f"{case}_{witness}_before"]=before
            raw_arrays[f"{case}_{witness}_actual_native_pour"]=animation
            print("SP80_ORIGINAL_RIGHT_GATE_AB_CASE "+json.dumps({
                "case":case,"witness":witness,
                "native_level":report["original_native_official_level"],
                "native_state":report["original_native_official_state"],
                "native_full_four_frames":cups["same_sdk_frame_full_four_cups"],
                "native_separate_inlets_while_four_full":
                    source["both_source_inlets_disconnected_full_four_cup_frames"],
                "source_separate_inlets_all_frames":
                    source["frames_with_both_real_inlets_present_but_separate"],
                "junction_water_pixels_at_first_four_full":
                    source["first_4_cup_frame_band_palette6_pixels"],
                "source_before_nonclock_hash":
                    report["native_original_prepour_without_clock_digest"]
            },sort_keys=True),flush=True)
    assert len(rows)==18 and len(roots)==1
    for case,_ in FROZEN:
        pair=[r for r in rows if r["case"]==case]
        assert len(pair)==2
        for k in ("native_original_prepour_full_frame_digest",
                  "actual_original_full_returned_pour_digest",
                  "native_observed_four_cup_source_measures",
                  "actual_original_A_B_source_graph_observations",
                  "original_native_official_level","original_native_official_state"):
            if pair[0][k]!=pair[1][k]:
                raise AssertionError("Independent original SDK witnesses differ at "+case+" "+k)
    summary={
        "kind":"ORIGINAL_NATIVE_SP80_STAGE4_RIGHT_MIDDLE_BAR_TWO_INLET_CONNECTIVITY_AB",
        "independent_genuine_original_sdk_games":len(rows),
        "same_verified_true_native_stage4_root":next(iter(roots)),
        "original_native_pour_at_stage4_action_before_budget":True,
        "four_cups_full_but_two_source_components_cases":sorted(set(r["case"] for r in rows
             if r["actual_original_A_B_source_graph_observations"]
               ["both_source_inlets_disconnected_full_four_cup_frames"])),
        "all_cases_with_source_inlet_disconnection":sorted(set(r["case"] for r in rows
             if r["actual_original_A_B_source_graph_observations"]
               ["frames_with_both_real_inlets_present_but_separate"])),
        "true_sdk_levels_histogram":dict(Counter(str(r["original_native_official_level"]) for r in rows)),
        "true_sdk_states_histogram":dict(Counter(r["original_native_official_state"] for r in rows)),
        "original_sdk_level5_or_WIN_cases":[r["case"] for r in rows if r["official_native_level5_or_WIN"]],
        "separate_exact_f3_rooted_math_certificates":f3,
        "prospectively_frozen_original_source_interventions":FROZEN,
        "all_actual_original_sdk_source_receipts":rows,
        "limitation":"Palette6 connectivity is an observable graph only; no decoded private fluid mechanics or global SDK success predicate. Only official level>=5/WIN is progression."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw_arrays)
    print("SP80_ORIGINAL_RIGHT_GATE_AB_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k not in
          ("prospectively_frozen_original_source_interventions",
           "all_actual_original_sdk_source_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
