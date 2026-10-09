"""SK48 Level3 native-public A/B: next connected-color search from native 8.

Input seed was independently observed by public tether validation.
No saved Level3 route. All native RESETs positively acknowledged and
fresh parent replay frame verified. No game cloning or private objects.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from _sk48_public_connected_goal import connected_features
import numpy as np,json,hashlib,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
r=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=min((x for x in r if x["passed"] and x["different_from_saved_reference"]),key=lambda x:len(x["L2_actions"]))["L2_actions"]
SEED=[1]*4+[4]*3
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;retries=0
def step(z):
 global calls
 o=g.step(z,data={});calls+=1
 return o
def run(path):
 global retries
 for t in range(8):
  o=step(GameAction.RESET)
  if o.levels_completed==0:break
  retries+=1
 else:raise RuntimeError("RESET not acknowledged")
 for z in L1+L2+path:o=step(GameAction.from_id(z))
 if o.levels_completed<2:raise RuntimeError("L3 not reached")
 return o
root=run(SEED);f=connected_features(frame(root))
assert f["connected_prefix"]==1,f
root_hash=hashlib.sha256(frame(root).tobytes()).hexdigest()
programs=[]
for d in (1,2,3):
 for l in (0,1,2,3):
  for rr in (0,1,2,3,4,5,6):
   programs.append(("DOWN_then_LEFT_then_RIGHT",d,l,rr,[2]*d+[3]*l+[4]*rr))
   programs.append(("LEFT_then_DOWN_then_RIGHT",d,l,rr,[3]*l+[2]*d+[4]*rr))
   programs.append(("LEFT_then_RIGHT_then_DOWN",d,l,rr,[3]*l+[4]*rr+[2]*d))
seen=set();tests=[];witness=[];time0=time.monotonic()
for kind,d,l,rr,suffix in programs:
 if tuple(suffix) in seen:continue
 seen.add(tuple(suffix))
 o=run(SEED+suffix)
 q=connected_features(frame(o))
 row={"program":kind,"down":d,"left":l,"right":rr,
   "suffix":suffix,"prefix":q["connected_prefix"],
   "colors":[c["connected_colors"] for c in q["candidates"]],
   "head":q["controls"],"level":int(o.levels_completed),
   "sha":hashlib.sha256(frame(o).tobytes()).hexdigest()}
 tests.append(row)
 if q["connected_prefix"]>=2 or o.levels_completed>=3:
  witness.append(row);print("L3_NATIVE_SECOND_COLOR",row,flush=True)
 if len(tests)%25==0:
  print("L3_STAGE2_PROGRESS",len(tests),"HITS",len(witness),
        "CALLS",calls,"TIME",round(time.monotonic()-time0,2),flush=True)
 if len(witness)>=10 or time.monotonic()-time0>88:
  print("L3_STAGE2_BOUNDED",len(tests),flush=True)
  break
out=F/"sk48_l3_native_connected_second_color_ab.json"
out.write_text(json.dumps({"native_public_only":True,"saved_L3_route_loaded":False,
 "first_color_seed":SEED,"programs_enumerated":len(programs),
 "tested_distinct":len(tests),"witnesses":witness,"tests":tests,
 "native_calls":calls,"reset_retries":retries,
 "elapsed_seconds":round(time.monotonic()-time0,2)},indent=2),encoding="utf-8")
print("L3_SECOND_COLOR_RESULT","WITNESSES",len(witness),"OF",len(tests),
      "SAVED",out,flush=True)
