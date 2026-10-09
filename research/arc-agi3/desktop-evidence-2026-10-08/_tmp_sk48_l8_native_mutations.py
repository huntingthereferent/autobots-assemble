"""SK48 final Level8: reference-assisted native A/B mutations.

Native public pixel ACTION6 control selection, first-completion handoff
for Levels1-7, and actual GameState.WIN required. No private game state.
Actions are mutations of old positive Level8, not blind discovery.
"""
from _sk48_native_public_stage_harness import F,routes,controls,run_level
from _sk48_public_goal_sensor import frame
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from hashlib import sha256
import json,logging,time
logging.disable(logging.CRITICAL)
P8=json.loads((F/"sk48_l8_native_positive_public_reference.json").read_text())["P8"]
L7=json.loads((F/"sk48_l7_native_fresh_swaps.json").read_text())["routes"][0]["route"]
options=routes()
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
retry=0;root=None
def begin():
 global root,retry
 for i in range(8):
  o=e.step(GameAction.RESET,data={})
  if o.levels_completed==0:break
  retry+=1
 else:raise RuntimeError("native reset not acknowledged")
 for level,rs in enumerate(options,1):
  o,k,s=run_level(e,o,rs[0],level)
 o,k,s=run_level(e,o,L7,7)
 h=sha256(frame(o).tobytes()).hexdigest()
 if root is None:root=h
 if h!=root:raise RuntimeError("native Level8 entry drift")
 return o
def test(seq):
 o=begin();active=0;clicks=[]
 for k,z in enumerate(seq,1):
  if z==6:
   hs=controls(frame(o))
   if len(hs)!=2:return {"win":False,"unknown":"visible controls","step":k}
   active=1-active;x,y,_=hs[active]
   o=e.step(GameAction.ACTION6,data={"x":x+2,"y":y+2})
   clicks.append([k,x+2,y+2])
  else:o=e.step(GameAction.from_id(z),data={})
  if o.state.name=="WIN":
   return {"win":True,"first_win_at":k,"clicks":clicks,"native_levels":int(o.levels_completed)}
 return {"win":False,"level":int(o.levels_completed),"state_name":o.state.name,"clicks":clicks}
base=test(P8)
assert base["win"] and base["first_win_at"]==24,base
cases=[]
for i in range(len(P8)):cases.append(("delete",i,P8[:i]+P8[i+1:]))
for i in range(len(P8)-1):
 if P8[i]==P8[i+1]:continue
 z=P8.copy();z[i],z[i+1]=z[i+1],z[i]
 cases.append(("swap",i,z))
t=time.monotonic();out=[];survivors=[]
for n,(kind,index,route) in enumerate(cases,1):
 r=test(route);rec={"kind":kind,"index":index,**r}
 if r["win"]:
  rec["path"]=route;survivors.append(rec)
  print("LEVEL8_NATIVE_MUTATION_WIN",kind,index,"AT",r["first_win_at"],flush=True)
 out.append(rec)
 if n%10==0:
  print("L8_AB_BATCH",n,"OF",len(cases),"WINS",len(survivors),
        "SEC",round(time.monotonic()-t,1),flush=True)
dest=F/"sk48_l8_native_reference_mutations_ab.json"
dest.write_text(json.dumps({"provenance":"reference-assisted, not blind ARC solution",
 "native_public_only":True,"baseline":base,"entry_sha256":root,
 "tested":len(out),"survivors":survivors,"all_tests":out,"reset_retries":retry},indent=2),encoding="utf-8")
print("L8_A_B_DONE","TESTS",len(out),"WINS",len(survivors),
 "SAVED",dest,flush=True)
