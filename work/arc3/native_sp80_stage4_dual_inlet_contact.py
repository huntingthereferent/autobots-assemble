"""Original SP80 Stage4 dual-inlet contact A/B.

Read-only source: stage4 original entry root contains TWO disjoint
native palette6 inlet cells x20..22/y56..58 and x44..46/y56..58.
All inspected four-cup-complete original returned frames in six saved
archives (88 full-cup frames) showed ONE 4-connected palette6 component
linking both inlets. This is a *source projection* of unknown original
SP80 physics, not a decoded hidden objective.

Bounded native causal discriminator: hold previously verified BASE 21
action four-cup geometry identical, then click actual inlet A, inlet
B, both in each order, a palette12 background negative control, or the
known palette8 bar positive reselect control, then genuine ACTION5.
Measure original frame changes, source component connectivity, border
warning timing, all four real SDK cup windows, and official progress.
Do NOT substitute a synthetic game or assert source1/source2 ownership.
"""
from __future__ import annotations
import argparse,json
from collections import Counter,deque
from hashlib import blake2b
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE,read_pour
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

A=(21,57);B=(45,57);BG=(28,54);BAR=(15,48)
CASES=(
 ("baseline",""),
 ("inlet_A","6@21,57"),
 ("inlet_B","6@45,57"),
 ("inlet_A_then_B","6@21,57 6@45,57"),
 ("inlet_B_then_A","6@45,57 6@21,57"),
 ("background_control","6@28,54"),
 ("bar_reselect_control","6@15,48"),
)
assert len(CASES)==7==len({n for n,w in CASES})
assert len(STAGE1_WITNESSES)==2
assert len(parse_plan(BASE))==21
assert all(len(parse_plan(BASE+" "+w+" 5"))<100 for n,w in CASES)
def stackdigest(a):
    return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()
def source_4_neighbor_components(frame):
    binary=frame==6
    seen=np.zeros(binary.shape,dtype=bool);components=[]
    height,width=binary.shape
    for y,x in np.argwhere(binary):
        y=int(y);x=int(x)
        if seen[y,x]:continue
        q=deque([(y,x)]);seen[y,x]=True;size=0;touch_a=False;touch_b=False
        while q:
            yy,xx=q.popleft();size+=1
            if 56<=yy<=58 and 20<=xx<=22:touch_a=True
            if 56<=yy<=58 and 44<=xx<=46:touch_b=True
            for ny,nx in ((yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)):
                if 0<=ny<height and 0<=nx<width and binary[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx]=True;q.append((ny,nx))
        components.append({"source_palette6_pixels":size,
            "touches_original_A_inlet":touch_a,
            "touches_original_B_inlet":touch_b})
    return sorted(components,key=lambda c:-c["source_palette6_pixels"])
def first_border_flashes(root,pre,frames):
    scopes={
      "upper":(slice(2,5),slice(2,62)),
      "right":(slice(2,62),slice(59,62)),
      "lower":(slice(59,62),slice(2,62)),
      "left":(slice(2,62),slice(2,5))}
    return {name:next((int(t) for t,frame in enumerate(frames)
            if np.any((pre[ys,xs]==1)&(frame[ys,xs]==14))),None)
            for name,(ys,xs) in scopes.items()}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    certificate=f3_calibration()
    records=[];source_arrays={};roots=set()
    for name,suffix in CASES:
        word=(BASE+" "+suffix+" 5").replace("  "," ")
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            item,raw=run_case(name,witness,entry,word)
            roots.add(item["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            if int(root[A[1],A[0]])!=6 or int(root[B[1],B[0]])!=6:
                raise AssertionError("Original two native palette6 inlet coordinates changed")
            if int(root[BG[1],BG[0]])!=12 or int(root[BAR[1],BAR[0]])!=12:
                # The known bar reselect point must be checked in pre-pour,
                # not assumed to be a bar already on the source reset.
                if int(root[BG[1],BG[0]])!=12:
                    raise AssertionError("Source background negative-control not grounded")
            before=raw[f"stage4_{n-1}"][-1];frames=raw[f"stage4_{n}"]
            if frames.ndim!=3 or frames.shape[1:]!=(64,64):
                raise AssertionError("Genuine 64x64 original native array absent")
            source_clicks=[r for r in item["genuine_original_stage4_action_ledger"]
                if r["index"]>len(parse_plan(BASE)) and r["genuine_original_action"]==6]
            expect=len(parse_plan(suffix)) if suffix else 0
            if len(source_clicks)!=expect:
                raise AssertionError("Native SDK input action receipts incomplete")
            for receipt in source_clicks:
                xy=receipt["real_native_click_xy"]
                if xy==list(A) or xy==list(B):
                    if receipt["original_source_pixel_before_click"]!=6:
                        raise AssertionError("Real inlet ACTION6 not delivered to palette6")
                elif xy==list(BG):
                    if receipt["original_source_pixel_before_click"]!=12:
                        raise AssertionError("Real background palette12 click changed")
                elif xy==list(BAR):
                    if receipt["original_source_pixel_before_click"] not in (8,9):
                        raise AssertionError("Known native selected bar palette changed")
                else:raise AssertionError("Unexpected native source contact")
            cups=read_pour(root,before,frames)
            first=cups["same_sdk_frame_full_four_cups"]
            at=frames[first[0]] if first else frames[min(21,len(frames)-1)]
            topology=source_4_neighbor_components(at)
            metrics={
                "pre_source_full_image_hash":hash_frame(before),
                "pre_source_without_y63_hash":stackdigest(before[:63]),
                "returned_native_all_frames_hash":stackdigest(frames),
                "returned_native_all_frames_excluding_y63_hash":stackdigest(frames[:,:63]),
                "four_source_cups_simultaneously_full_frames":first,
                "first_original_border_flash_by_side":first_border_flashes(root,before,frames),
                "source_palette6_connected_components_at_first_four_full_or_frame21":topology,
                "source_both_inlets_in_same_connected_palette6_component":
                    any(c["touches_original_A_inlet"] and c["touches_original_B_inlet"] for c in topology),
            }
            result={
                "case":name,"original_stage1_entry":witness,
                "frozen_original_stage4_action_word":word,
                "source_inlet_A_xy":list(A),"source_inlet_B_xy":list(B),
                "actual_native_input_click_receipts":source_clicks,
                "true_sdk_official_final_level":item["true_original_sdk_final_level"],
                "true_sdk_official_final_state":item["true_original_sdk_final_state"],
                "official_level5_or_WIN":item["official_original_level5_or_WIN"],
                "native_original_source_metrics":metrics,
                "genuine_original_stage4_action_ledger":item["genuine_original_stage4_action_ledger"]}
            records.append(result)
            source_arrays[f"{name}_{witness}_pre"]=before
            source_arrays[f"{name}_{witness}_native_pour"]=frames
            print("SP80_LEVEL4_DUAL_INLET_CASE "+json.dumps({
                "case":name,"entry":witness,
                "official_level":result["true_sdk_official_final_level"],
                "official_state":result["true_sdk_official_final_state"],
                "clicked_palettes":[r["original_source_pixel_before_click"] for r in source_clicks],
                "full_four_start":first[0] if first else None,
                "inlets_connected":metrics["source_both_inlets_in_same_connected_palette6_component"],
                "components":topology,"side_flash":metrics["first_original_border_flash_by_side"],
                "nonclock_pour":metrics["returned_native_all_frames_excluding_y63_hash"]
            },sort_keys=True),flush=True)
    if len(records)!=14 or len(roots)!=1:raise AssertionError("Original A/B entry reset mismatch")
    for name,_ in CASES:
        one,two=[r for r in records if r["case"]==name]
        for k in ("true_sdk_official_final_level","true_sdk_official_final_state",
                  "actual_native_input_click_receipts","native_original_source_metrics"):
            if one[k]!=two[k]:
                raise AssertionError("Independent original native source witnesses disagree "+name)
    controls={r["case"]:r for r in records if r["original_stage1_entry"]==STAGE1_WITNESSES[0][0]}
    baseline=controls["baseline"]["native_original_source_metrics"]
    shifts=[{"case":case,"geometry_changed":v["native_original_source_metrics"]
             ["pre_source_without_y63_hash"]!=baseline["pre_source_without_y63_hash"],
             "flow_outside_clock_changed":v["native_original_source_metrics"]
             ["returned_native_all_frames_excluding_y63_hash"]!=baseline["returned_native_all_frames_excluding_y63_hash"]}
            for case,v in controls.items() if case!="baseline"]
    report={
        "kind":"ORIGINAL_SP80_STAGE4_TWO_INLET_SOURCE_SELECTION_AB",
        "authentic_independent_normal_sdk_games":len(records),
        "original_native_stage4_root":next(iter(roots)),
        "root_palette6_source_inlets":{"A":A,"B":B},
        "original_geometry_change_by_source_contact":shifts,
        "official_level5_or_WIN":[r["case"] for r in records if r["official_level5_or_WIN"]],
        "original_sdk_level_histogram":dict(Counter(str(r["true_sdk_official_final_level"]) for r in records)),
        "original_sdk_state_histogram":dict(Counter(r["true_sdk_official_final_state"] for r in records)),
        "F3_48_rooted_math_checked_separately":certificate,
        "prospective_native_original_source_words":CASES,
        "complete_original_sdk_action_and_frame_receipts":records,
        "limitations":"Observed palette6 graph is a rendering projection only, not a decoded rule about source ownership. Clicks on inlet/background pixels may have no effect. Only official SDK level>=5/WIN is advancement."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**source_arrays)
    print("SP80_LEVEL4_DUAL_INLET_SUMMARY "+json.dumps({
        k:v for k,v in report.items() if k not in
            ("prospective_native_original_source_words","complete_original_sdk_action_and_frame_receipts")
        },sort_keys=True),flush=True)
if __name__=="__main__":main()
