"""SK48 Level6 controlled native A/B intervention of reference movements.

No private engine fields. Every ACTION6 selects the other of two 6x6
public bordered control heads by their current rendered pixels.
Positive-reference mutations are reference-assisted, not blind solving.
Stages 1-5 stop at their first native completion.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from hashlib import sha256
import numpy as np,json,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((x for x in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"] if x["passed"] and x["different_from_saved_reference"]),key=lambda x:len(x["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
L4=next(x["path"] for x in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if x["method"]=="swap_adjacent")
L5=json.loads((F/"sk48_l5_native_fresh_swap_witnesses.json").read_text())["routes"][0]["actions"]
REF=json.loads((F/"sk48_l6_public_pixel_switch_positive_calibration.json").read_text())["P6"]
def heads(a):
 out=[]
 for y in range(0,49):
  for x in range(0,55):
   v=int(a[y,x])
   if v not in (6,15):continue
   block=a[y:y+6,x:x+6]
   if block.shape!=(6,6):continue
   if not (np.all(block[0,:]==v) and np.all(block[:,0]==v)):continue
   if int(block[1,1]) not in (0,4):continue
   if not any(int(t)!=v for t in block[1:5,1:5].flat):continue
   out.append((x,y,v))
 return sorted(set(out),key=lambda t:t[0])
game=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;retries=0;root=None
def step(z,data=None):
 global calls
 o=game.step(z,data={} if data is None else data)
 calls+=1
 return o
def trial(path):
 global retries,root
 for r in range(8):
  o=step(GameAction.RESET)
  if o.levels_completed==0:break
  retries+=1
 else:raise RuntimeError("native reset not acknowledged")
 for goal,p in enumerate((L1,L2,L3,L4,L5),1):
  for z in p:
   o=step(GameAction.from_id(z))
   if o.levels_completed>=goal:break
  if o.levels_completed!=goal:raise RuntimeError(("stage handoff",goal))
 h=sha256(frame(o).tobytes()).hexdigest()
 if root is None:root=h
 if root!=h:raise RuntimeError("L6 native root drift")
 active=0;switches=[]
 for i,z in enumerate(path,1):
  if z==6:
   controls=heads(frame(o))
   if len(controls)!=2:
    return {"success":False,"reason":"public control detection","step":i,"controls":controls}
   choose=1-active;x,y,_=controls[choose]
   o=step(GameAction.ACTION6,{"x":x+2,"y":y+2})
   switches.append([i,x+2,y+2])
   active=choose
  else:o=step(GameAction.from_id(z))
  if o.levels_completed>=6:
   return {"success":True,"first_completion":i,"switches":switches,"level":int(o.levels_completed)}
 return {"success":False,"level":int(o.levels_completed),"switches":switches}
base=trial(REF)
assert base["success"] and base["first_completion"]==36,base
cases=[]
for i in range(len(REF)):
 cases.append(("delete",i,REF[:i]+REF[i+1:]))
for i in range(len(REF)-1):
 if REF[i]==REF[i+1]:continue
 swapped=REF.copy()
 swapped[i],swapped[i+1]=swapped[i+1],swapped[i]
 cases.append(("swap",i,swapped))
data=[];winners=[];start=time.monotonic()
for n,(kind,index,path) in enumerate(cases,1):
 r=trial(path)
 witness={"type":kind,"index":index,"edited_from":REF[index],
          "path":path if r["success"] else None,**r}
 data.append(witness)
 if r["success"]:
  winners.append(witness)
  print("L6_NATIVE_A_B_SURVIVES",kind,index,"WIN_AT",r["first_completion"],
        "SWITCHES",r["switches"],flush=True)
 if n%12==0:
  print("L6_A_B_TESTED",n,"OF",len(cases),"WIN",len(winners),
    "CALLS",calls,"SEC",round(time.monotonic()-start,1),flush=True)
out=F/"sk48_l6_native_reference_intervention_ab.json"
out.write_text(json.dumps({"method":"native positive-reference action intervention",
 "source":"saved route, NOT blind discovery","root_hash":root,
 "baseline":base,"tested":len(data),"winners":winners,"tests":data,
 "native_calls":calls,"reset_retries":retries,
 "seconds":round(time.monotonic()-start,2)},indent=2),encoding="utf-8")
print("L6_A_B_DONE","TESTED",len(data),"SURVIVED",len(winners),
  "BY_TYPE",{k:sum(w["type"]==k for w in winners) for k in ("delete","swap")},
  "SAVED",out,flush=True)
