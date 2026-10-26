"""ARC4: original normal SP80 SDK bottom-bar intervention at observed
ALTERNATIVE source6 bridge, x32..45 / y44..46.

Source evidence genuine run #40315154593 and exact original NPZ
artifact #12646576816: right-middle source gate UP1 reduces native
palette6 flow in y35..37/x35..55 from 63 to 9 pixels, yet the two
inlets STILL form a four-neighbor-connected source6 component at
four-cup fill because the actual returned animation also contains
source6 bridge x32..45/y44..46.

Existing selected lower bar at native BASE pre-POUR: original palette8
x11..19/y47..49, genuinely selectable at 15,48; action4 moves it
right in source 3-pixel units. Freeze gate-UP1, then move lower bar
right (4/5/6 steps) plus UP1 to intersect observed lower water
bridge. Measure BOTH cup reachability and inlet connectivity on
EVERY authentic SDK returned frame; official level>=5/WIN only.

No synthetic fluid simulation, no private success-rule assertion.
Existing F3 rooted/nonrooted exact math is calibrated separately.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from hashlib import blake2b
import numpy as np
from collections import deque
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE,read_pour
from .native_sp80_stage4_dual_inlet_contact import source_4_neighbor_components
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

GATE_UP1="6@42,33 1"
LOWER_CLICK="6@15,48"
RIGHT="4"
FROZEN=(
    ("gate_up1_no_lower_change", ""),
    ("gate_up1_lower_reselect", LOWER_CLICK),
    ("gate_up1_lower_right4_up1", LOWER_CLICK+" "+" ".join([RIGHT]*4)+" 1"),
    ("gate_up1_lower_right5_up1", LOWER_CLICK+" "+" ".join([RIGHT]*5)+" 1"),
    ("gate_up1_lower_right6_up1", LOWER_CLICK+" "+" ".join([RIGHT]*6)+" 1"),
    ("gate_up1_lower_up1_right5", LOWER_CLICK+" 1 "+" ".join([RIGHT]*5)),
    ("gate_up1_lower_right6_up2", LOWER_CLICK+" "+" ".join([RIGHT]*6)+" 1 1"),
    ("gate_up1_lower_right6_only", LOWER_CLICK+" "+" ".join([RIGHT]*6)),
)
assert len(FROZEN)==8==len({x[0] for x in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert len(parse_plan(BASE))==21
assert all(len(parse_plan(" ".join([BASE,GATE_UP1,suffix,"5"])))<100
           for name,suffix in FROZEN)
def digest(a):
    return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()
def native_palette8_9_selected_region(frame):
    """Pure NumPy + standard-library 4-connected native pixel objects."""
    found=[]
    for palette in (8,9):
        mask=frame==palette
        seen=np.zeros(mask.shape,dtype=bool)
        for y,x in np.argwhere(mask):
            y=int(y);x=int(x)
            if seen[y,x]:continue
            q=deque([(y,x)]);seen[y,x]=True
            pixels=[]
            while q:
                yy,xx=q.popleft();pixels.append((yy,xx))
                for ny,nx in ((yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)):
                    if 0<=ny<64 and 0<=nx<64 and mask[ny,nx] and not seen[ny,nx]:
                        seen[ny,nx]=True;q.append((ny,nx))
            if len(pixels)>=9:
                found.append({"palette":palette,
                              "x_min":min(x for y,x in pixels),
                              "x_max":max(x for y,x in pixels),
                              "y_min":min(y for y,x in pixels),
                              "y_max":max(y for y,x in pixels),
                              "pixels":len(pixels)})
    return found
def source_inlet_connected(frame):
    comp=source_4_neighbor_components(frame)
    return {
       "both_original_source_patches_in_same_component":any(
           x["touches_original_A_inlet"] and x["touches_original_B_inlet"] for x in comp),
       "separate_source_patches_present":any(x["touches_original_A_inlet"] for x in comp)
                                       and any(x["touches_original_B_inlet"] for x in comp),
       "native_number_source6_components":len(comp),
       "native_palette6_pixels_at_surviving_bridge_x32_45_y44_46":
           int(np.count_nonzero(frame[44:47,32:46]==6)),
       "native_palette6_pixels_at_first_upper_bridge_x35_55_y35_37":
           int(np.count_nonzero(frame[35:38,35:56]==6))
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();f3=f3_calibration()
    rows=[];arrays={};roots=set()
    base_n=len(parse_plan(BASE));gate_n=len(parse_plan(GATE_UP1))
    for case,suffix in FROZEN:
        word=" ".join(s for s in (BASE,GATE_UP1,suffix,"5") if s)
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            pre=raw[f"stage4_{n-1}"][-1];frames=raw[f"stage4_{n}"]
            assert frames.ndim==3 and frames.shape[1:]==(64,64)
            receipts=sdk["genuine_original_stage4_action_ledger"]
            assert len(receipts)==n and receipts[-1]["genuine_original_action"]==5
            g=receipts[base_n]
            if (g["genuine_original_action"]!=6 or
                g["real_native_click_xy"]!=[42,33] or
                g["original_source_pixel_before_click"]!=8):
                raise AssertionError("Native verified right-middle gate click changed")
            lower=receipts[base_n+gate_n:-1]
            if suffix:
                if (lower[0]["genuine_original_action"]!=6 or
                    lower[0]["real_native_click_xy"]!=[15,48] or
                    lower[0]["original_source_pixel_before_click"]!=8):
                    raise AssertionError("Native verified lower bar selection changed")
            cups=read_pour(root,pre,frames)
            full=cups["same_sdk_frame_full_four_cups"]
            per_frame=[source_inlet_connected(frame) for frame in frames]
            both_present_sep=[int(t) for t,g in enumerate(per_frame)
                              if g["separate_source_patches_present"] and
                              not g["both_original_source_patches_in_same_component"]]
            full_sep=[t for t in full if t in both_present_sep]
            sample=full[0] if full else min(23,len(frames)-1)
            row={
                "case":case,"independent_native_stage1_entry":witness,
                "actual_original_sdk_stage4_action_word":word,
                "native_verified_root_hash":
                    sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"],
                "selected_original_bottom_bar_positions_before_pour":
                    native_palette8_9_selected_region(pre),
                "original_nongameover_sdk_final_level":sdk["true_original_sdk_final_level"],
                "official_original_sdk_state":sdk["true_original_sdk_final_state"],
                "official_native_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "genuine_last_bar_action_receipts":lower,
                "original_four_cup_source_occupancy":cups,
                "all_true_native_sdk_frame_graphs":per_frame,
                "genuine_first_simultaneous_four_cup_frame":full[0] if full else None,
                "both_native_inlets_separate_when_all_four_full":full_sep,
                "both_native_inlets_separate_at_any_original_returned_frame":both_present_sep,
                "native_graph_at_first_full_or_control_frame":per_frame[sample],
                "full_original_sdk_prepour_source_hash":hash_frame(pre),
                "full_original_sdk_source_animation_hash":digest(frames),
                "original_sdk_action_ledger":receipts
            }
            rows.append(row);arrays[f"{case}_{witness}_pre"]=pre
            arrays[f"{case}_{witness}_native_pour"]=frames
            print("SP80_ORIGINAL_LOWER_BRIDGE_AB_CASE "+json.dumps({
                "case":case,"witness":witness,"level":row["original_nongameover_sdk_final_level"],
                "official":row["official_original_sdk_state"],
                "first_full_four":row["genuine_first_simultaneous_four_cup_frame"],
                "split_while_full":full_sep,
                "split_at_any_native_frame":both_present_sep,
                "native_surviving_bridge_pixels_at_probe_frame":per_frame[sample][
                  "native_palette6_pixels_at_surviving_bridge_x32_45_y44_46"],
                "selected_bar_source_regions":row["selected_original_bottom_bar_positions_before_pour"]
            },sort_keys=True),flush=True)
    if len(rows)!=16 or len(roots)!=1:raise AssertionError("Independent original SDK resets missing")
    for case,_ in FROZEN:
        a,b=[r for r in rows if r["case"]==case]
        for field in ("selected_original_bottom_bar_positions_before_pour",
                      "original_nongameover_sdk_final_level","official_original_sdk_state",
                      "original_four_cup_source_occupancy","all_true_native_sdk_frame_graphs",
                      "both_native_inlets_separate_when_all_four_full",
                      "full_original_sdk_source_animation_hash"):
            if a[field]!=b[field]:
                raise AssertionError("Actual native SDK entry witness mismatch "+case+" "+field)
    result={
        "kind":"GENUINE_ORIGINAL_SP80_STAGE4_LOWER_SOURCE_BRIDGE_BAR_CAUSAL_AB",
        "original_sdk_independently_reset_games":len(rows),
        "same_native_original_stage4_entry_source_hash":next(iter(roots)),
        "both_inlets_separate_while_all_four_full_cases":sorted(set(
            x["case"] for x in rows if x["both_native_inlets_separate_when_all_four_full"])),
        "both_inlets_separate_at_any_frame_cases":sorted(set(
            x["case"] for x in rows if x["both_native_inlets_separate_at_any_original_returned_frame"])),
        "original_level5_or_WIN":[x["case"] for x in rows if x["official_native_level5_or_WIN"]],
        "original_native_levels_histogram":dict(Counter(str(x["original_nongameover_sdk_final_level"]) for x in rows)),
        "original_native_states_histogram":dict(Counter(x["official_original_sdk_state"] for x in rows)),
        "mathematical_F3_exact_rooted_certificate_separate":f3,
        "frozen_original_sdk_source_programs":FROZEN,
        "full_authentic_sdk_action_and_source_evidence":rows,
        "scope":"These are observed palette6 4-neighbor graph relationships, not proven private goal predicates. Native level>=5/WIN alone is advancement. No F3/SDK action mapping."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_ORIGINAL_LOWER_BRIDGE_AB_SUMMARY "+json.dumps({
         k:v for k,v in result.items() if k not in
         ("frozen_original_sdk_source_programs","full_authentic_sdk_action_and_source_evidence")
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
