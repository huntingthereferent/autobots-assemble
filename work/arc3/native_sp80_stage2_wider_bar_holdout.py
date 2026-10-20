"""Original SP80 stage2: wider source-bar offset coverage beyond short negatives.

Native source level2 has exactly four separately coordinate-selectable
observed color8/9 bars. Prior original-native 2^4 short shifts and
1/3-step controls (48 real games) produced ZERO official level3.
This FROZEN subsequent mixed larger-offset experiment uses an
orthogonal three-factor 27-program projection in four bar motions,
plus nine independent larger-corner controls. Each genuine native
program gets two new independent original SDK resets.

Source stage2 reached through real original 454545 and stage1 witness.
All ACTION6 clicks carry genuine coordinate x,y; retain all source
SDK returned frames, exact pixel-color event changes and official
levels_completed >=3 or WIN as sole success evidence.
There is NO assumed F3 mathematics or decoded game objective here.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from itertools import product
from pathlib import Path
import numpy as np
from .native_sp80_stage2_four_bar_clicks import play_source
from .native_sp80_stage2_four_bar_factorial import source_word

STEPS=(0,3,5)
# F/L/M independently span all combinations; U is a deterministic
# balanced 4th offset, not an outcome-dependent or retrofitted choice.
ORTHOGONAL=tuple(
 ("wide_oa_F%d_L%d_M%d_U%d"%(STEPS[i],STEPS[j],STEPS[k],STEPS[(i+j+k)%3]),
   source_word((STEPS[i],STEPS[j],STEPS[k],STEPS[(i+j+k)%3])))
 for i,j,k in product(range(3),repeat=3))
CORNERS=tuple(
 ("wide_corner_F%d_L%d_M%d_U%d"%(f,l,m,u),source_word((f,l,m,u)))
 for f,l,m,u in (
   (0,0,0,0),(3,3,3,3),(5,5,5,5),
   (3,3,5,5),(5,5,3,3),
   (5,3,5,3),(3,5,3,5),
   (5,0,5,0),(0,5,0,5)))
PROGRAMS=ORTHOGONAL+CORNERS
RESETS=2
assert len(ORTHOGONAL)==27 and len(CORNERS)==9
assert len(PROGRAMS)==36 and len({name for name,_ in PROGRAMS})==36
assert RESETS==2


def commit_evidence(trial):
    rows=[]
    for e in trial["true_native_all_original_action_events"]:
        if e["phase"]=="stage2" and e["real_source_action"]==5:
            rows.append({
                "source_real_action_step":e["phase_step"],
                "real_original_before_commit_bars":e.get("original_pre_action_bars"),
                "original_SDK_returned_frame_count":e.get("original_true_SDK_returned_frames"),
                "genuine_source_sdk_levels_after":e["source_level_after"],
                "native_original_source_state_after":e["source_SDK_state_after"],
            })
    return rows


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    trials,all_npz=[],{}
    for name,word in PROGRAMS:
        for rep in range(RESETS):
            trial,raw=play_source(name,word,rep)
            trial["source_genuine_precommit_four_bar_observation"]=commit_evidence(trial)
            trials.append(trial)
            for key,stack in raw.items():
                all_npz[f"{name}_rep{rep}_{key}"]=stack
    by={}
    for name,word in PROGRAMS:
        group=[t for t in trials if t["source_original_program_name"]==name]
        by[name]={
          "frozen_original_stage2_actions":word,
          "actual_SDK_level_after":[t["official_SDK_final_level"] for t in group],
          "source_SDK_state_after":[t["official_SDK_final_state"] for t in group],
          "source_native_stage3_or_WIN":[t["real_sdk_level3_or_win"] for t in group],
          "original_source_dispositions":[t["source_disposition"] for t in group],
          "actual_original_precommit_bar_geometry":[
              t["source_genuine_precommit_four_bar_observation"] for t in group],
        }
    out={
       "kind":"ORIGINAL_SP80_NATIVE_STAGE2_WIDER_FOUR_BAR_OFFSET_HOLDOUT",
       "predeclared_3_level_native_bar_offsets":STEPS,
       "precommitted_orthogonal_source_bar_words":ORTHOGONAL,
       "precommitted_wider_corner_controls":CORNERS,
       "fresh_original_sdk_resets_per_program":RESETS,
       "total_original_SP80_native_games":len(trials),
       "genuine_original_source_sdk_actions":sum(
            len(t["true_native_all_original_action_events"]) for t in trials),
       "actual_original_native_stage3_or_WIN_trials":sum(
            int(t["real_sdk_level3_or_win"]) for t in trials),
       "source_actual_dispositions":dict(Counter(t["source_disposition"] for t in trials)),
       "real_original_source_outcomes_by_program":by,
       "full_unfiltered_original_native_sdk_trial_evidence":trials,
       "limits":"Authentic original Arcade.NORMAL SDK. Three-level offset design prospective; real source level3/WIN only progress. Every source ACTION6 clicked color is recorded and source obs.frame stacks retained. Does not infer hidden mechanics, a game goal or F3 mathematical action mapping.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**all_npz)
    print("SP80_STAGE2_WIDE_HOLDOUT "+json.dumps({
      k:v for k,v in out.items()
      if k not in ("real_original_source_outcomes_by_program",
                   "full_unfiltered_original_native_sdk_trial_evidence")
    },sort_keys=True))
    print("SP80_STAGE2_WIDE_SOURCE_LEVELS "+json.dumps({
       name:{"levels":x["actual_SDK_level_after"],"states":x["source_SDK_state_after"]}
       for name,x in by.items()
    },sort_keys=True))
    if len(trials)!=len(PROGRAMS)*RESETS:
        raise RuntimeError("Genuine original independent stage2 source game count shortfall")
if __name__=="__main__":main()
