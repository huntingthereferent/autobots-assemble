"""SK48 native public-only Level6 switch protocol and old-positive calibration.
The old P6 sequence is a separate regression witness, not a blind solve.
Other control is selected solely from currently visible bordered 6x6 sprites.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
import ast,numpy as np,json,hashlib,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((r for r in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"] if r["passed"] and r["different_from_saved_reference"]),key=lambda r:len(r["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
L4=next(r["path"] for r in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if r["method"]=="swap_adjacent")
L5=json.loads((F/"sk48_l5_native_fresh_swap_witnesses.json").read_text())["routes"][0]["actions"]
tree=ast.parse((F/"_tmp_sk48_complete_replay.py").read_text())
P6=list(next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="P6" for t in n.targets)))
def heads(a):
 out=[]
 for y in range(0,49):
  for x in range(0,55):
   v=int(a[y,x])
   if v not in (6,15):continue
   b=a[y:y+6,x:x+6]
   if b.shape!=(6,6):continue
   if not(np.all(b[0,:]==v) and np.all(b[:,0]==v)):continue
   if not(int(b[1,1]) in (0,4) and any(int(q)!=v for q in b[1:5,1:5].flat)):continue
   out.append((x,y,v))
 return sorted(set(out),key=lambda z:z[0])
def execute(e,route,n):
 for i,z in enumerate(route,1):
  o=e.step(GameAction.from_id(z),data={})
  if o.levels_completed>=n:break
 if o.levels_completed<n:raise RuntimeError(("handoff",n))
 return i,o
for trial in range(2):
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 steps=[]
 for target,p in enumerate((L1,L2,L3,L4,L5),1):
  count,o=execute(e,p,target);steps.append(count)
 before=hashlib.sha256(frame(o).tobytes()).hexdigest()
 active=0;records=[]
 for k,z in enumerate(P6,1):
  if z==6:
   hs=heads(frame(o))
   if len(hs)!=2:raise RuntimeError(("heads",k,hs))
   other=1-active;x,y,_=hs[other]
   o=e.step(GameAction.ACTION6,data={"x":x+2,"y":y+2})
   records.append({"index":k,"clicked":(x+2,y+2),"control_before":active,"controls":hs})
   active=other
  else:o=e.step(GameAction.from_id(z),data={})
  if o.levels_completed>=6:break
 print("L6_POSITIVE_REFERENCE","TRIAL",trial,"P6_LENGTH",len(P6),"FIRST_WIN",k if o.levels_completed>=6 else None,
  "LEVEL",o.levels_completed,"UPSTREAM",steps,"ROOT",before,"SWITCHES",records,flush=True)
out=F/"sk48_l6_public_pixel_switch_positive_calibration.json"
out.write_text(json.dumps({"purpose":"old positive Level6 trace, separately calibrated",
  "no_private_engine":True,"native_public_switch_pixel_selection":True,
  "old_saved_P6_used":True,"P6":P6,"switch_witnesses":records,
  "native_first_completion":k if o.levels_completed>=6 else None,
  "last_level":int(o.levels_completed)},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
