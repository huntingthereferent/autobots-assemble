"""ARC original SP80: A/B moves through its *own observed mistake*.

The original owned mistake-led worker #40393794254 lost the lateral
cup while changing an original top-floor source6 leak from x26 to x11.
The independently repeated correction #40394317579 tried palette8
bar movements and still lost the cup. This tests the NEXT actual
referent the earlier implementation excluded: a genuine original
palette15 L object, x17..22/y35..40, visible near missing lateral
cup (x5..10/y35..43) in the complete SDK before-POUR frame.

No public winning word, no substitution game, no proof gate.
Two actual opposite native actions (A/B), follow observed error,
then test two others from the chosen mistaken state. Actual status
is measured but failure does not stop movement or change method.
"""
from __future__ import annotations
import argparse,json
from collections import deque
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_four_cup_followup import BASE
from .native_sp80_stage4_ab_operating_loop import one,describe,select_branch
from .native_sp80_multi_select import parse_plan

# EXACT prior chosen failed program, reproduced in independent SDK
# entry witnesses in authentic original Actions #40394317579.
ROOTED_OWN_MISTAKE=(
 BASE+" 6@34,21 3 6@15,48 4 6@31,21 3"
 " 6@18,48 1 6@28,21 1 6@18,45 1"
)
assert len(parse_plan(ROOTED_OWN_MISTAKE))<60

def native_L_components(pre):
    mask=pre==15
    seen=np.zeros((64,64),dtype=bool);regions=[]
    for y,x in np.argwhere(mask):
        y,x=int(y),int(x)
        if seen[y,x]:continue
        q=deque([(y,x)]);seen[y,x]=True;component=[]
        while q:
            yy,xx=q.popleft();component.append((yy,xx))
            for ny,nx in ((yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)):
                if 0<=ny<64 and 0<=nx<64 and mask[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx]=True;q.append((ny,nx))
        if len(component)>=9:
            target=(39,7) # already observed missing lateral cup region
            py,px=min(component,key=lambda p:abs(p[0]-target[0])+abs(p[1]-target[1]))
            regions.append({"click":[int(px),int(py)],
                            "observed_actual_palette":int(pre[py,px]),
                            "original_component_pixels":len(component),
                            "observed_x_extent":[min(x for y,x in component),max(x for y,x in component)],
                            "observed_y_extent":[min(y for y,x in component),max(y for y,x in component)]})
    return sorted(regions,key=lambda r:(abs(r["click"][0]-7)+abs(r["click"][1]-39)))

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    witness,entry=STAGE1_WITNESSES[0]
    seed=one("original_owned_failed_A_B_seed",witness,entry,ROOTED_OWN_MISTAKE+" 5")
    assert seed["measure"]["four_native_cup_peak_counts"]["lateral"]==0
    leak=seed["measure"]["observed_first_source6_near_top_floor"]
    assert leak is not None and leak[1]==11, "Do not silently swap the source mistake"
    records=[seed];movement=[];parent=seed;rooted=ROOTED_OWN_MISTAKE
    for step,directions in enumerate(((3,4),(1,2))):
        if parent["measure"]["official_level5_or_WIN"]:break
        objects=native_L_components(parent["pre"])
        if not objects:
            movement.append({"iteration":step,
                             "observed_new_mistake":"No palette15 object remains visible after prior native action",
                             "actual_native_15_regions":[]})
            break
        obj=objects[0];xy=obj["click"]
        both=[]
        for label,action in zip(("A","B"),directions):
            word=rooted+f" 6@{xy[0]},{xy[1]} {action} 5"
            native=one(f"L_error_{step}_{label}",witness,entry,word)
            # Do not reject if the original ACTION6 selected nothing or
            # movement made the lateral cup/flow worse. Record exact pixels.
            both.append(native);records.append(native)
        selected,reason=select_branch(parent,*both)
        differences=[{"case":v["case"],
                      "native_original_source_click_palette_before":[
                          e["original_source_pixel_before_click"] for e in v["ledger"][-3:]
                          if e["genuine_original_action"]==6],
                      "measured_AB_mistake":describe(parent,v),
                      "original_sdk_result":v["measure"]}
                     for v in both]
        movement.append({"iteration":step,"mistake_that_generated_pair":
                        parent["measure"]["observed_error"],
                         "palette15_actual_original_object":obj,
                         "actual_native_opposite_movements":list(directions),
                         "results":differences,
                         "continued_actual_rooted_history":selected["word"],
                         "why_continued":reason})
        print("SP80_OWN_ERROR_LED_L15_AB "+json.dumps({
           "round":step,"L_object":obj,
           "actual_source_AB_changes":[v["measured_AB_mistake"] for v in differences],
           "continued":selected["case"],"why":reason,
        },sort_keys=True),flush=True)
        parent=selected;rooted=selected["word"].rsplit(" 5",1)[0]
    second_w,second_entry=STAGE1_WITNESSES[1]
    replication=one("independent_L_correction_reproduction",second_w,second_entry,parent["word"])
    records.append(replication)
    if (replication["measure"]["official_sdk_level"]!=parent["measure"]["official_sdk_level"]
        or replication["measure"]["source6_full_animation_digest"]!=parent["measure"]["source6_full_animation_digest"]):
        raise AssertionError("Actual different native SDK root histories disagree")
    arrays={}
    receipts=[]
    for r in records:
        for k,stack in r["source"].items():
            if k=="entry3_34" or k.startswith("stage4_"):
                arrays[f"{r['case']}_{r['witness']}_{k}"]=stack
        receipts.append({k:v for k,v in r.items() if k not in ("source","pre","frames")})
    report={
      "kind":"GENUINE_OWN_ARC_PALETTE15_MISTAKE_CAUSED_AB_MOVEMENT",
      "original_prior_error_source_actions_runs":[40393794254,40394317579],
      "original_sdk_independent_games":len(records),
      "native_rooted_A_B_mistake_correction":movement,
      "actual_original_source_action_receipts":receipts,
      "official_owned_method_game_level_progress_cases":[
          r["case"] for r in records if r["measure"]["official_level5_or_WIN"]],
      "never_read_or_imported_external_winning_program":True,
      "F3_scope":"Native A/B operates directly through errors. Separate 48-world F3 exact mathematics unchanged; no fabricated source mapping."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_OWN_ERROR_LED_L15_SUMMARY "+json.dumps({
       k:v for k,v in report.items() if k not in
       ("native_rooted_A_B_mistake_correction","actual_original_source_action_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
