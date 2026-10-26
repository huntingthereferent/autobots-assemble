"""ARC4: original SDK A/B at verified upstream A-to-B path cut.

Authentic original SDK frame23 in the previously verified four-cup
BASE returns a shortest original palette6 four-neighbor path from
native inlet A=(21,57) to B=(45,57), length 88 edges, that passes
the horizontal 6-cells x23..35,y25 directly under the movable
native upper bar x29..40,y20..22. The earlier lower-bar intervention
did NOT affect any water pixels; stop moving it. Original source
controls show the right-middle bar DOES affect the palette6 mask.

Precommit upper bar RIGHT1 or RIGHT2, with none/LEFT1/LEFT2
right-middle compensations, rather than search an arbitrary grid.
Original palettes/click receipts, graph source route, real cup pixels,
and official levels are evaluated from native SDK frames only.
F3 mathematical rooted pair certificate is separately rechecked.
"""
from __future__ import annotations
import argparse,json
from collections import Counter,deque
from pathlib import Path
from hashlib import blake2b
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE,read_pour
from .native_sp80_stage4_dual_inlet_contact import source_4_neighbor_components
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

UP="6@34,21";MID="6@42,33"
FROZEN=(
    ("known_full_four_baseline",""),
    ("upper_right1","6@34,21 4"),
    ("upper_right1_middle_left1","6@34,21 4 6@42,33 3"),
    ("upper_right1_middle_left2","6@34,21 4 6@42,33 3 3"),
    ("upper_right2_middle_left1","6@34,21 4 4 6@42,33 3"),
    ("upper_right2_middle_left2","6@34,21 4 4 6@42,33 3 3"),
)
assert len(FROZEN)==6 and len(STAGE1_WITNESSES)==2
assert len(parse_plan(BASE))==21
assert all(len(parse_plan(" ".join(s for s in (BASE,suffix,"5") if s)))<100
           for case,suffix in FROZEN)

def digest(a):return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()

def true_original_shortest_source_path(frame):
    start=(57,21);goal=(57,45)
    if frame[start]!=6 or frame[goal]!=6:return None
    queue=deque([start]);prior={start:None}
    while queue:
        y,x=queue.popleft()
        if (y,x)==goal:break
        for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0<=yy<64 and 0<=xx<64 and frame[yy,xx]==6 and (yy,xx) not in prior:
                prior[(yy,xx)]=(y,x);queue.append((yy,xx))
    if goal not in prior:return None
    points=[];cursor=goal
    while cursor is not None:
        points.append(cursor);cursor=prior[cursor]
    points.reverse()
    return {
        "actual_native_shortest_water_path_edges":len(points)-1,
        "crosses_original_upper_horizontal_bridge_y23_25_x23_43":
            any(23<=y<=25 and 29<=x<=34 for y,x in points),
        "water_cells_on_central_bridge_y25_x23_43":int(np.count_nonzero(
            frame[25,23:44]==6)),
        "true_original_path_sample_across_bridge":[[int(x),int(y)]
            for y,x in points if 23<=y<=25 and 29<=x<=35],
    }

def measure(frame,root):
    cuprect=((slice(35,44),slice(5,11)),
             (slice(5,11),slice(17,26)),
             (slice(5,11),slice(35,44)),
             (slice(5,11),slice(47,56)))
    cnt=[int(np.count_nonzero((root[y,x]==11)&(frame[y,x]==13)))
         for y,x in cuprect]
    allfull=all(v==45 for v in cnt)
    source=source_4_neighbor_components(frame)
    joined=any(v["touches_original_A_inlet"] and v["touches_original_B_inlet"] for v in source)
    both=any(v["touches_original_A_inlet"] for v in source) and any(
         v["touches_original_B_inlet"] for v in source)
    return {
        "four_original_source_cup_palette13_counts":cnt,
        "four_original_source_cups_full":allfull,
        "both_original_inlets_present":both,
        "both_original_inlets_palette6_connected":joined,
        "source6_water_pixels_on_upper_bridge":int(np.count_nonzero(
            frame[23:26,23:44]==6)),
        "original_true_shortest_path":true_original_shortest_source_path(frame),
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();certificate=f3_calibration()
    rows=[];rawout={};roots=set()
    for name,suffix in FROZEN:
        word=" ".join(q for q in (BASE,suffix,"5") if q)
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,arrays=run_case(name,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=arrays["entry3_34"][-1];pre=arrays[f"stage4_{n-1}"][-1]
            animation=arrays[f"stage4_{n}"]
            ledger=sdk["genuine_original_stage4_action_ledger"]
            assert len(ledger)==n and ledger[-1]["genuine_original_action"]==5
            movements=ledger[len(parse_plan(BASE)):-1]
            if suffix:
                clicks=[r for r in movements if r["genuine_original_action"]==6]
                if not clicks or clicks[0]["real_native_click_xy"]!=[34,21] or clicks[0]["original_source_pixel_before_click"]!=8:
                    raise AssertionError("Original upper water-forming bar source selection not grounded")
                if len(clicks)>1 and (
                    clicks[1]["real_native_click_xy"]!=[42,33] or
                    clicks[1]["original_source_pixel_before_click"]!=8):
                    raise AssertionError("Original right-middle water-forming bar source selection changed")
            cupsummary=read_pour(root,pre,animation)
            frameprobes=[measure(f,root) for f in animation]
            full=[i for i,o in enumerate(frameprobes) if o["four_original_source_cups_full"]]
            disconnected=[i for i,o in enumerate(frameprobes) if
                          o["four_original_source_cups_full"] and
                          o["both_original_inlets_present"] and
                          not o["both_original_inlets_palette6_connected"]]
            best_frame=max(range(len(frameprobes)),
                           key=lambda i:sum(frameprobes[i]["four_original_source_cup_palette13_counts"]))
            chosen=full[0] if full else best_frame
            probes=frameprobes[chosen]
            result={
               "prospective_original_sdk_case":name,
               "independent_true_sdk_entry":witness,
               "true_original_stage4_action_word":word,
               "native_source_prepour_without_bottom_clock_hash":digest(pre[:63]),
               "original_pour_native_nonclock_array_hash":digest(animation[:,:63]),
               "source_returned_frame_count":len(animation),
               "genuine_original_upper_and_middle_receipts":movements,
               "observed_full_four_original_source_cup_frames":full,
               "all_full_four_cup_with_separate_inlets":disconnected,
               "original_native_best_source_cup_score":sum(frameprobes[best_frame]["four_original_source_cup_palette13_counts"]),
               "native_observed_frame_selected":chosen,
               "native_source_frame_graph_at_selected_frame":probes,
               "genuine_original_pour_frame_graphs":frameprobes,
               "actual_original_sdk_level":sdk["true_original_sdk_final_level"],
               "actual_original_sdk_state":sdk["true_original_sdk_final_state"],
               "official_sdk_level5_or_WIN":sdk["official_original_level5_or_WIN"],
               "true_original_sdk_stage4_action_ledger":ledger,
            }
            rows.append(result)
            rawout[f"{name}_{witness}_pre"]=pre
            rawout[f"{name}_{witness}_native_pour"]=animation
            print("SP80_ORIGINAL_UPPER_BRIDGE_AB_CASE "+json.dumps({
               "name":name,"entry":witness,
               "level":result["actual_original_sdk_level"],
               "state":result["actual_original_sdk_state"],
               "four_cups_full_frames":full,
               "first_disconnected_and_full":disconnected[0] if disconnected else None,
               "best_cup_pixels":result["original_native_best_source_cup_score"],
               "water_upper_bridge":probes["source6_water_pixels_on_upper_bridge"],
               "water_path_length":(probes["original_true_shortest_path"] or {}).get(
                  "actual_native_shortest_water_path_edges"),
               "both_inlets_connected":probes["both_original_inlets_palette6_connected"],
               "four_cup_source_counts":probes["four_original_source_cup_palette13_counts"]
             },sort_keys=True),flush=True)
    if len(rows)!=12 or len(roots)!=1:raise AssertionError("Original independently reset SDK games missing")
    for case,_ in FROZEN:
        a,b=[r for r in rows if r["prospective_original_sdk_case"]==case]
        for k in ("original_pour_native_nonclock_array_hash","observed_full_four_original_source_cup_frames",
                  "native_source_frame_graph_at_selected_frame","genuine_original_pour_frame_graphs",
                  "actual_original_sdk_level","actual_original_sdk_state"):
            if a[k]!=b[k]:
                raise AssertionError("True native original entry witnesses disagree "+case)
    report={
       "kind":"ORIGINAL_SP80_STAGE4_UPPER_MIDDLE_BRIDGE_ACTION_AB",
       "actual_independent_normal_sdk_games":len(rows),
       "true_original_stage4_root":next(iter(roots)),
       "four_cups_full_separate_inlets_cases":sorted(set(r["prospective_original_sdk_case"]
            for r in rows if r["all_full_four_cup_with_separate_inlets"])),
       "official_native_level5_or_WIN":[r["prospective_original_sdk_case"]
            for r in rows if r["official_sdk_level5_or_WIN"]],
       "official_level_histogram":dict(Counter(str(r["actual_original_sdk_level"]) for r in rows)),
       "official_state_histogram":dict(Counter(r["actual_original_sdk_state"] for r in rows)),
       "calibrated_F3_48_math_separate":certificate,
       "original_predeclared_actual_source_words":FROZEN,
       "true_original_sdk_action_and_frame_receipts":rows,
       "limit":"One selected source water path is only a projection; connectivity is not a proven goal. Genuine original SDK level>=5/WIN is the only progress condition."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**rawout)
    print("SP80_ORIGINAL_UPPER_BRIDGE_AB_SUMMARY "+json.dumps({
       k:v for k,v in report.items() if k not in
        ("original_predeclared_actual_source_words","true_original_sdk_action_and_frame_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
