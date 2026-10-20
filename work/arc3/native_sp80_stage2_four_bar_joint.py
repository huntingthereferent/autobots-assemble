"""Original SDK stage2 four-bar joint displacement factorial.

Actual source stage2 entry is reached ONLY through verified native
stage0 454545 and source stage1->2 witness. The initial stage2 screen
contains FOUR genuine color8/color9 selectable bars. Individual
movement/click tests all remained SDK level2 (48 original-game resets).

Before new native execution freeze a 36-cell 4-bar movement crossing:
 bottom selected 24px bar: 0 or 2 LEFT action3 steps
 lower 24px bar: 2,3 or 4 RIGHT action4 steps
 middle right 20px bar: 0 or 2 LEFT action3 steps
 upper left 16px bar: 2,3 or 4 RIGHT action4 steps.
Every bar uses source coordinate-bearing ACTION6, finishing ACTION5.
Control native click order and intermediate commit on two center cells.
No prior stage's objective is presumed. Official SDK levels_completed>=3
or WIN alone counts as actual further game progress.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from itertools import product
from pathlib import Path
import numpy as np
from .native_sp80_stage2_action_inventory import trial,source_bars
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

CLICKS={"B":"6@42,41","L":"6@12,33","M":"6@50,29","U":"6@12,21"}
MOVE={"B":"3","L":"4","M":"3","U":"4"}
CHOICES={"B":(0,2),"L":(2,3,4),"M":(0,2),"U":(2,3,4)}
RESETS=2

def word(steps,order="BLMU",commit_each=False):
    vals=dict(zip("BLMU",steps))
    out=[]
    for item in order:
        out.append(CLICKS[item])
        out.extend([MOVE[item]]*vals[item])
        if commit_each:out.append("5")
    if not commit_each:out.append("5")
    return " ".join(out)

MAIN=tuple(
 ("F_B%d_L%d_M%d_U%d"%(b,l,m,u),word((b,l,m,u)))
 for b,l,m,u in product(CHOICES["B"],CHOICES["L"],CHOICES["M"],CHOICES["U"])
)
CONTROLS=(
 ("middle_B0_L3_M0_U3_reverse",word((0,3,0,3),"UMLB")),
 ("middle_B2_L3_M2_U3_reverse",word((2,3,2,3),"UMLB")),
 ("middle_B0_L3_M0_U3_commit_each",word((0,3,0,3),"BLMU",True)),
 ("middle_B2_L3_M2_U3_commit_each",word((2,3,2,3),"BLMU",True)),
)
PROGRAMS=MAIN+CONTROLS
assert len(MAIN)==36 and len(PROGRAMS)==40 and RESETS==2
assert len({n for n,_ in PROGRAMS})==len(PROGRAMS)
assert all(parse_plan(p)[-1][0]==5 and
   all(a!=6 or xy is not None for a,xy in parse_plan(p))
   for _,p in PROGRAMS)


def actual_first_A5_preimage(row,frames):
    outcomes=[]
    for e in row["source_original_SDK_ledger"]:
        if e["phase"]!="stage2" or e["native_action"]!=5:continue
        step=e["step"]
        before=(frames["stage1_9"][-1] if step==1
                else frames["stage2_"+str(step-1)][-1])
        after=frames["stage2_"+str(step)][-1]
        outcomes.append({
           "native_source_context_step":step,
           "true_native_source_preaction_bar_positions":source_bars(before),
           "native_source_before_frame_hash":hash_frame(before),
           "authentic_sdk_after_level":e["source_postlevel"],
           "authentic_sdk_after_state":e["source_poststate"],
           "real_original_SDK_returned_images":e["real_original_SDK_animation"]["true_original_returned_frames"],
           "actual_native_after_source_bar_positions":source_bars(after),
        })
    return outcomes


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    all_trials,arrays=[],{}
    for name,actions in PROGRAMS:
        for rep in range(RESETS):
            evidence,raw=trial(name,actions,rep)
            evidence["native_joint_stage2_action5_events"]=actual_first_A5_preimage(evidence,raw)
            all_trials.append(evidence)
            for phase,stack in raw.items():
                arrays[f"{name}_rep{rep}_{phase}"]=stack
    programs={}
    for name,actions in PROGRAMS:
        rows=[x for x in all_trials if x["program"]==name]
        programs[name]={
          "original_native_source_action_word":actions,
          "real_sdk_final_levels":[x["original_SDK_level_at_end"] for x in rows],
          "real_sdk_final_states":[x["original_SDK_state_at_end"] for x in rows],
          "real_sdk_level3_or_WIN":[x["actual_native_level3_or_WIN"] for x in rows],
          "source_actual_game_dispositions":[x["real_source_disposition"] for x in rows],
          "original_source_action5_preimage_positions":[x["native_joint_stage2_action5_events"] for x in rows],
          "stage2_authentic_advertised_actions":[x["stage2_entry_advertised_legal_actions"] for x in rows],
        }
    out={
      "kind":"GENUINE_ORIGINAL_SP80_STAGE2_JOINT_FOUR_BAR_MOTION_NATIVE_OBJECTIVE",
      "source_frozen_stage2_four_bar_step_counts":CHOICES,
      "original_source_precommitted_stage2_action_words":PROGRAMS,
      "independent_original_SDK_resets_per_word":RESETS,
      "genuine_original_SP80_stage2_games":len(all_trials),
      "accepted_source_native_SDK_actions":sum(x["actual_SDK_action_calls"] for x in all_trials),
      "SDK_original_level3_or_WIN":sum(int(x["actual_native_level3_or_WIN"]) for x in all_trials),
      "real_original_SDK_dispositions":dict(Counter(x["real_source_disposition"] for x in all_trials)),
      "source_per_program_outcomes":programs,
      "complete_original_source_native_game_evidence":all_trials,
      "limits":"Authentic original source SDK stage2 entry via verified witness, no inferred game goal. 4-bar visible translations are source-native controls. Only level >=3 or WIN is success. Original full returned images retained. No copied game, stage1 goal transfer or F3 mathematical law mapping.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_STAGE2_FOUR_BAR_JOINT "+json.dumps({
      k:v for k,v in out.items()
      if k not in ("complete_original_source_native_game_evidence","source_per_program_outcomes")
    },sort_keys=True))
    if len(all_trials)!=len(PROGRAMS)*RESETS:
        raise RuntimeError("Incomplete source original stage2 game resets")

if __name__=="__main__":
    main()
