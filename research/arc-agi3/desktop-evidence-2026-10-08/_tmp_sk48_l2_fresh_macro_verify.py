"""SK48 Level2 macro A/B fresh-game replay validator.

Inputs are independently observed stage-2 native witness and discovered
macro variants, NOT the saved Level2 action sequence. Every route is
replayed twice on a newly created Arcade instance and checked at level 2.
The old Level2 route is used solely in a post-hoc equality audit.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from hashlib import sha256
import json,numpy as np,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
src=json.loads((F/"sk48_l2_native_macro_fourth_color_ab.json").read_text())
cases=[x for x in src["wins_provisional"] if x.get("complete_path")]
# The saved original route is used only to measure novelty after the search.
old_ref=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
results=[]
for i,c in enumerate(cases):
 route=tuple(c["complete_path"])
 trials=[]
 for j in range(2):
  e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
  before=e.observation_space
  root_after=None;at2=None
  for z in L1:
   before=e.step(GameAction.from_id(z),data={})
  root_after=before.levels_completed
  for k,z in enumerate(route,1):
   after=e.step(GameAction.from_id(z),data={})
   if after.levels_completed>=2:
    at2=k;break
  trial={"trial":j,"L1_levels":int(root_after),
         "native_after_L2_levels":int(after.levels_completed),
         "L2_completion_at":at2,"L2_route_len":len(route),
         "correct":int(after.levels_completed)>=2 and at2==len(route),
         "end_sha256":sha256(np.asarray(after.frame[-1],dtype=np.uint8).tobytes()).hexdigest()}
  trials.append(trial)
 obs={"case":i,"pivot":c["pivot"],"macro":[c["a"],c["b"],c["c"]],
      "L2_actions":list(route),
      "different_from_saved_reference":route!=old_ref,
      "trials":trials,"passed":all(x["correct"] for x in trials)}
 results.append(obs)
 print("FRESH_L2_AB",i,"LENGTH",len(route),"PASSED",obs["passed"],
       "DIFFERENT_REFERENCE",obs["different_from_saved_reference"],
       "MILESTONES",[x["L2_completion_at"] for x in trials],flush=True)
out=F/"sk48_l2_fresh_macro_completion_witnesses.json"
out.write_text(json.dumps({"game":"sk48","method":"public native SDK fresh replay of discovered macro programs",
        "tested_routes":len(results),"fresh_trials":sum(len(x["trials"]) for x in results),
        "passing_routes":sum(x["passed"] for x in results),
        "distinct_from_old_saved_p2":sum(x["different_from_saved_reference"] for x in results),
        "results":results},indent=2),encoding="utf-8")
print("FRESH_L2_RESULT","ALL_PASS",all(x["passed"] for x in results),
      "N_CASES",len(results),"ALT",sum(x["different_from_saved_reference"] for x in results),
      "SAVED",out,flush=True)
