"""SK48 Level5 native fresh-game A/B swap verification.

Seven old-positive-reference-derived, adjacent-action swapped Level5
candidates. Vary verified L2/L3/L4 upstream routes and terminate each
stage at its native first completion. Never use private SDK state.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from hashlib import sha256
import json,numpy as np,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2s=[x["L2_actions"] for x in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"] if x["passed"] and x["different_from_saved_reference"]]
L3s=[x["L3_path"] for x in json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"] if x["passed"] and x["different_from_saved_reference"]]
L4s=[x["path"] for x in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if x["method"]=="swap_adjacent"]
winners=json.loads((F/"sk48_l5_native_adjacent_swap_ab.json").read_text())["winners"]
def execute_to_level(e,path,n):
 for k,a in enumerate(path,1):
  o=e.step(GameAction.from_id(a),data={})
  if o.levels_completed>=n:break
 if o.levels_completed<n:raise RuntimeError(("did not complete stage",n))
 return k,o
out=[]
for j,w in enumerate(winners):
 checks=[]
 for trial in range(2):
  e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
  paths=[L1,L2s[(j+trial)%len(L2s)],L3s[(j+trial)%len(L3s)],L4s[(j+trial)%len(L4s)]]
  consumed=[]
  for level,path in enumerate(paths,1):
   used,o=execute_to_level(e,path,level)
   consumed.append(used)
  start_sha=sha256(frame(o).tobytes()).hexdigest()
  used,o=execute_to_level(e,w["full_route"],5)
  check={"trial":trial,"consumed_per_prior_stage":consumed,
   "native_L5_entry_sha":start_sha,"native_L5_completion_at":used,
   "reported_levels_completed":int(o.levels_completed),
   "passed":int(o.levels_completed)>=5 and used<=len(w["full_route"])}
  checks.append(check)
 row={"swap_index":w["swap_index"],"actions":w["full_route"],"fresh_trials":checks,
      "passed":all(c["passed"] for c in checks)}
 out.append(row)
 print("L5_FRESH_ORDER_AB",j,"SWAP",w["swap_index"],"PASS",row["passed"],
       "ENTRY_SHA",[v["native_L5_entry_sha"][:16] for v in checks],
       "WIN_AT",[v["native_L5_completion_at"] for v in checks],flush=True)
p=F/"sk48_l5_native_fresh_swap_witnesses.json"
p.write_text(json.dumps({"native_only":True,"reference_assisted":True,
 "tested_alternative_routes":len(out),"fresh_trials":2*len(out),
 "passing_routes":sum(x["passed"] for x in out),"routes":out},indent=2),encoding="utf-8")
print("L5_FRESH_SUMMARY","PASSED",sum(x["passed"] for x in out),
      "OF",len(out),"SAVED",p,flush=True)
