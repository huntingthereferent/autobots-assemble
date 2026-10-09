"""SK48 Level6 fresh native verification of three reference-assisted swaps.

New SDK instance per trial; diverse previously validated upstream routes.
First-completion handoff preserves Level6 root. ACTION6 selects another
control using only the native public image, never private engine fields.
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
L5s=[x["actions"] for x in json.loads((F/"sk48_l5_native_fresh_swap_witnesses.json").read_text())["routes"] if x["passed"]]
W=json.loads((F/"sk48_l6_native_reference_intervention_ab.json").read_text())["winners"]
def heads(a):
 out=[]
 for y in range(0,49):
  for x in range(0,55):
   v=int(a[y,x])
   if v not in (6,15):continue
   b=a[y:y+6,x:x+6]
   if b.shape!=(6,6) or not(np.all(b[0,:]==v) and np.all(b[:,0]==v)):continue
   if int(b[1,1]) not in (0,4) or not any(int(t)!=v for t in b[1:5,1:5].flat):continue
   out.append((x,y,v))
 return sorted(set(out),key=lambda t:t[0])
def consume(e,path,level):
 for k,z in enumerate(path,1):
  o=e.step(GameAction.from_id(z),data={})
  if o.levels_completed>=level:break
 if o.levels_completed<level:raise RuntimeError(("stage not completed",level))
 return k,o
results=[]
for j,w in enumerate(W):
 trials=[]
 for n in range(2):
  e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
  upstream=[L1,L2s[(j+n)%len(L2s)],L3s[(j+2*n)%len(L3s)],
            L4s[(j+n)%len(L4s)],L5s[(j+3*n)%len(L5s)]]
  used=[]
  for level,path in enumerate(upstream,1):
   count,o=consume(e,path,level);used.append(count)
  root=sha256(frame(o).tobytes()).hexdigest()
  active=0;switches=[];first_completion=None
  for k,z in enumerate(w["path"],1):
   if z==6:
    controls=heads(frame(o))
    if len(controls)!=2:raise RuntimeError(("public controls lost",controls,k))
    other=1-active; x,y,_=controls[other]
    o=e.step(GameAction.ACTION6,data={"x":x+2,"y":y+2})
    switches.append([k,x+2,y+2])
    active=other
   else:o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>=6:
    first_completion=k;break
  trials.append({"trial":n,"L1toL5_consumed":used,"L6_entry_sha256":root,
       "L6_first_completion_at":first_completion,"native_levels_completed":int(o.levels_completed),
       "clicks":switches,"passed":first_completion is not None and int(o.levels_completed)>=6})
 row={"swap_index":w["index"],"route":w["path"],
      "all_pass":all(x["passed"] for x in trials),"trials":trials}
 results.append(row)
 print("LEVEL6_FRESH_NATIVE_SWAP","INDEX",w["index"],"PASS",row["all_pass"],
       "WIN",[x["L6_first_completion_at"] for x in trials],
       "ENTRY",[x["L6_entry_sha256"][:16] for x in trials],flush=True)
obj={"status":"reference-assisted verified Level6 alternative native routes",
 "public_pixel_control_selection":True,
 "first_completion_stage_gating":True,
 "fresh_trials":len(results)*2,"passing_routes":sum(x["all_pass"] for x in results),
 "results":results}
dest=F/"sk48_l6_native_fresh_swap_witnesses.json"
dest.write_text(json.dumps(obj,indent=2),encoding="utf-8")
print("LEVEL6_FRESH_SUMMARY",len(results),"PASSED",obj["passing_routes"],"SAVED",dest,flush=True)
