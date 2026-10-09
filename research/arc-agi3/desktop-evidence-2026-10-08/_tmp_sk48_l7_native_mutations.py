"""SK48 native Level7 A/B: one-action deletion and adjacent action swap.

Uses old positive 51-action route as a reference-assisted control.
No private engine access; public pixel head selection. Native RESET ack,
staged entrance at the first completion of Levels1-6. No background jobs.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_native_public_stage_harness import F,routes,controls,run_level
from _sk48_public_goal_sensor import frame
import json,hashlib,logging,time
logging.disable(logging.CRITICAL)
P=json.loads((F/"sk48_l7_positive_reference_public_control.json").read_text())["P7"]
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
opts=routes();count=0;retries=0;known=None
def step(z,data=None):
 global count
 o=e.step(z,data={} if data is None else data);count+=1;return o
def start():
 global retries,known,count
 for i in range(8):
  o=step(GameAction.RESET)
  if o.levels_completed==0:break
  retries+=1
 else:raise RuntimeError("RESET unacknowledged")
 for stage,rs in enumerate(opts,1):
  used=rs[0]
  if stage==6:
   # verified non-reference Level6 action-route
   pass
  active=0
  for z in used:
   if z==6:
    hs=controls(frame(o))
    if len(hs)!=2:raise RuntimeError(("control missing",stage,hs))
    active=1-active;x,y,_=hs[active]
    o=step(GameAction.ACTION6,{"x":x+2,"y":y+2})
   else:o=step(GameAction.from_id(z))
   if o.levels_completed>=stage:break
  if o.levels_completed!=stage:raise RuntimeError(("bad stage",stage))
 h=hashlib.sha256(frame(o).tobytes()).hexdigest()
 if known is None:known=h
 if h!=known:raise RuntimeError("L7 entry changed")
 return o
def test(seq):
 o=start();active=0;clicks=[]
 for k,z in enumerate(seq,1):
  if z==6:
   hs=controls(frame(o))
   if len(hs)!=2:return {"success":False,"error":"public control miss","at":k}
   active=1-active;x,y,_=hs[active]
   o=step(GameAction.ACTION6,{"x":x+2,"y":y+2})
   clicks.append([k,x+2,y+2])
  else:o=step(GameAction.from_id(z))
  if o.levels_completed>=7:return {"success":True,"first_at":k,
    "clicks":clicks,"native_level":int(o.levels_completed)}
 return {"success":False,"native_level":int(o.levels_completed),"clicks":clicks}
base=test(P)
assert base["success"] and base["first_at"]==len(P),base
cases=[]
for i in range(len(P)):cases.append(("delete",i,P[:i]+P[i+1:]))
for i in range(len(P)-1):
 if P[i]==P[i+1]:continue
 z=P.copy();z[i],z[i+1]=z[i+1],z[i]
 cases.append(("swap",i,z))
results=[];survivors=[];t=time.monotonic()
for n,(kind,i,seq) in enumerate(cases,1):
 r=test(seq)
 item={"kind":kind,"index":i,**r}
 if r["success"]:
  item["path"]=seq
  survivors.append(item)
  print("L7_A_B_SUCCESS",kind,i,"STEP",r["first_at"],flush=True)
 results.append(item)
 if n%15==0:
  print("L7_A_B_BATCH",n,"OF",len(cases),"SURVIVORS",len(survivors),
        "CALLS",count,"SECONDS",round(time.monotonic()-t,1),flush=True)
out=F/"sk48_l7_native_reference_mutations_ab.json"
out.write_text(json.dumps({"source":"saved Level7 positive reference action list",
 "native_public_only":True,"reference_assisted":True,"entry_sha":known,
 "baseline":base,"tested":len(results),"results":results,"survivors":survivors,
 "native_calls":count,"reset_retries":retries},indent=2),encoding="utf-8")
print("L7_MUTATIONS_DONE","TOTAL",len(results),"WINS",len(survivors),
 "DELETIONS",sum(z["kind"]=="delete" for z in survivors),
 "SWAPS",sum(z["kind"]=="swap" for z in survivors),"SAVED",out,flush=True)
