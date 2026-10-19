"""Original SP80 stage1 joint bar translations, with native ACTION5 commit timing.

Actual original stage0 source progress correlated with net-right-three
native 4px movements of the one 20x4 selected bar. Independent stage1
single-bar trials, same-edge alignments, staggered alignments, top glyph
clicks, and temporary 240 upper color13 pulses all FAILED SDK level2.
Do not presume stage0's relationship transfers as a game objective.

Freeze a bounded independent ORIGINAL SDK three-bar offset factorial:
each of three genuinely selected bar objects translated right by 0,2,3
original ACTION4 movements. Each (F,L,U) cell is tested with the same
selection order and one terminal ACTION5. Add matched order and ACTION5
AFTER EACH bar controls on (3,3,3), plus several 1/4 offset controls.
Real pre-ACTION5 bar positions, source SDK level and full 64x64 frame
stacks are recorded; progress means native levels_completed>=2 or WIN.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from itertools import product
from pathlib import Path
import numpy as np
from .native_sp80_action5_frame_stacks import one
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

BAR_ORDER="FLU"
BAR_CLICKS={"F":"6@24,37","L":"6@32,25","U":"6@12,17"}
BAR_BANDS={"F":(36,40),"L":(24,28),"U":(16,20)}
SOURCE_EXPECTED_WIDTHS={"F":20,"L":12,"U":12}
COUNTS=(0,2,3)
RESETS=2

def word(steps,order="FLU",commit_each=False,repeats=1):
    moves=dict(zip("FLU",steps))
    actions=[]
    for bar in order:
        actions.append(BAR_CLICKS[bar])
        actions.extend(["4"]*moves[bar])
        if commit_each:
            actions.append("5")
    if not commit_each:
        actions.extend(["5"]*repeats)
    return " ".join(actions)

MAIN=tuple(
    ("factorial_F%d_L%d_U%d"%(f,l,u),word((f,l,u)))
    for f,l,u in product(COUNTS,repeat=3)
)
CONTROLS=tuple(
    ("control_F%d_L%d_U%d"%(f,l,u),word((f,l,u)))
    for f,l,u in ((1,1,1),(4,4,4),(1,3,3),(3,1,3),(3,3,1))
)
ORDERS=tuple(
    ("all3_order_"+order+"_single_commit",word((3,3,3),order))
    for order in ("ULF","LUF","FUL")
)
STEPWISE=tuple(
    ("all3_order_"+order+"_commit_after_each",word((3,3,3),order,True))
    for order in ("FLU","ULF","LUF","FUL")
)
PROGRAMS=MAIN+CONTROLS+ORDERS+STEPWISE
assert len(MAIN)==27 and len(PROGRAMS)==39
assert len({n for n,_ in PROGRAMS})==39
assert all(parse_plan(p)[-1][0]==5 and all(
    a!=6 or xy is not None for a,xy in parse_plan(p))
    for _,p in PROGRAMS)
assert RESETS==2


def bar_regions(a):
    result={}
    for name,(y0,y1) in BAR_BANDS.items():
        region=a[y0:y1]
        ys,xs=np.nonzero(np.isin(region,[8,9]))
        result[name]={
            "original_source_nonbackground_bar_pixels":int(len(xs)),
            "source_actual_box":[int(xs.min()),int(ys.min()+y0),
                int(xs.max()),int(ys.max()+y0)] if len(xs) else None,
            "native_color8_cells":int(np.count_nonzero(region==8)),
            "native_color9_cells":int(np.count_nonzero(region==9)),
        }
    return result


def selected_and_commit_evidence(trial,raw):
    result=[]
    for e in trial["real_sdk_observation_ledger"]:
        if e.get("phase")!="context":continue
        k=e["phase_action_number"]
        arr=raw.get("context_"+str(k))
        if arr is None or "source_animation" not in e:
            result.append({"sdk_step":k,"native_action":e.get("native_action_id"),
                           "status":"UNKNOWN_NONSTANDARD_FRAME"})
            continue
        before=raw["entry_6"][-1] if k==1 else raw["context_"+str(k-1)][-1]
        after=arr[-1]
        row={
            "source_sdk_step":k,
            "native_source_action_id":e["native_action_id"],
            "actual_source_click_xy":e["native_click_xy"],
            "source_preclick_true_pixel_color":e["actual_native_pre_click_pixel"],
            "actual_source_sdk_returned_frames":int(len(arr)),
            "original_SDK_level_after":e["original_source_level_after"],
            "original_SDK_state_after":e["original_source_state_after"],
        }
        if e["native_action_id"] in (5,6):
            row.update({
               "original_native_preimage_sha":hash_frame(before),
               "source_original_preaction_bar_regions":bar_regions(before),
               "source_actual_postaction_bar_regions":bar_regions(after),
               "source_actual_before_to_final_color_changes":
                   e["source_animation"]["original_before_to_final_pixel_count"],
               "source_color6_at_top_in_any_frame":int(sum(
                    np.any(frame[:13]==6) for frame in arr)),
            })
        result.append(row)
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    trials,stacks=[],{}
    for name,actions in PROGRAMS:
        for replicate in range(RESETS):
            trial,raw=one(name,actions,replicate)
            trial["new_native_multibar_observation"]=selected_and_commit_evidence(trial,raw)
            trials.append(trial)
            for phase,arr in raw.items():
                stacks[f"{name}_rep{replicate}_{phase}"]=arr
    per={}
    for name,actions in PROGRAMS:
        rows=[t for t in trials if t["name"]==name]
        per[name]={
            "predeclared_original_native_actions":actions,
            "genuine_resets":len(rows),
            "SDK_original_level_at_end":[r["original_last_source_level"] for r in rows],
            "SDK_original_state_at_end":[r["original_last_source_state"] for r in rows],
            "real_source_level2_or_WIN":[r["native_level2_or_win"] for r in rows],
            "genuine_source_disposition":[r["actual_source_disposition"] for r in rows],
            "actual_pre_ACTION5_bar_regions":[[
              e["source_original_preaction_bar_regions"] for e in r["new_native_multibar_observation"]
              if e.get("native_source_action_id")==5 and "source_original_preaction_bar_regions" in e
            ] for r in rows],
            "source_SDK_actual_action5_returned_frame_counts":[[
              e["actual_source_sdk_returned_frames"] for e in r["new_native_multibar_observation"]
              if e.get("native_source_action_id")==5
            ] for r in rows],
            "source_clicks":[[
              [e["actual_source_click_xy"],e["source_preclick_true_pixel_color"]]
              for e in r["new_native_multibar_observation"]
              if e.get("native_source_action_id")==6
            ] for r in rows],
        }
    output={
        "kind":"GENUINE_ORIGINAL_SP80_STAGE1_JOINT_SELECTED_BAR_DISPLACEMENT_AND_COMMIT",
        "prospectively_frozen_3_bar_rightward_steps":COUNTS,
        "stage1_actual_native_controls":CONTROLS+ORDERS+STEPWISE,
        "original_predeclared_programs":PROGRAMS,
        "independent_original_sdk_resets_per_program":RESETS,
        "genuine_source_original_SP80_games":len(trials),
        "native_source_SDK_action_responses":sum(t["actual_native_calls"] for t in trials),
        "source_original_level2_or_WIN":sum(int(t["native_level2_or_win"]) for t in trials),
        "source_original_dispositions":dict(Counter(t["actual_source_disposition"] for t in trials)),
        "source_actual_program_outcomes":per,
        "untouched_original_SDK_trial_evidence":trials,
        "limitations":"A bounded source-native motion factorial, not assumed puzzle target. Proper ACTION6 coordinate clicks of three genuine bars. All original SDK returned images preserved. Stage1 progress requires actual levels_completed >=2 or WIN. Prior native stage0 horizontal condition is not assumed transferable. No cloned SP80, hidden physics or F3 math correspondence.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**stacks)
    print("SP80_JOINT_BAR_DISPLACEMENT "+json.dumps({
       k:v for k,v in output.items()
       if k not in ("source_actual_program_outcomes","untouched_original_SDK_trial_evidence")
    },sort_keys=True))
    if len(trials)!=len(PROGRAMS)*RESETS:
        raise RuntimeError("Original SP80 independent game resets missing")

if __name__=="__main__":
    main()
