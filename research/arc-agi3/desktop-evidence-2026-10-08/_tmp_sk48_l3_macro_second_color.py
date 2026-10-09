"""SK48 Level3 A/B movement macro: next ordered color (8,12).

The macro family is motivated by a *separate* positive regression.
No saved Level3 route is read here. SDK reset and native public
frame only. Paths with exact public tether connection are witnesses.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from _sk48_public_connected_goal import connected_features
from hashlib import sha256
import json,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
r=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=min((x for x in r if x["passed"] and x["different_from_saved_reference"]),key=lambda x:len(x["L2_actions"]))["L2_actions"]
SEED=[1]*4+[4]*3
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48");calls=0;retry=0
def step(a):
 global calls
 o=g.step(a,data={});calls+=1;return o
def native(path):
 global retry
 for t in range(9):
  o=step(GameAction.RESET)
  if o.levels_completed==0:break
  retry+=1
 else:raise RuntimeError("no native reset acknowledgement")
 for a in L1+L2+path:o=step(GameAction.from_id(a))
 if o.levels_completed<2:raise RuntimeError("did not enter Level3")
 return o
r0=native(SEED)
assert connected_features(frame(r0))["connected_prefix"]==1
seen=set();test=[];hits=[];t0=time.monotonic()
for a in (1,2,3):
 for b in (0,1,2):
  for c in (0,1,2):
   for d in (1,2,3,4,5,6):
    suffix=[2]*a+[3]*b+[2]*c+[4]*d
    if tuple(suffix) in seen:continue
    seen.add(tuple(suffix))
    o=native(SEED+suffix)
    q=connected_features(frame(o))
    row={"macro":[a,b,c,d],"suffix":suffix,
         "prefix":q["connected_prefix"],
         "colors":[i["connected_colors"] for i in q["candidates"]],
         "level":int(o.levels_completed),"head":q["controls"],
         "hash":sha256(frame(o).tobytes()).hexdigest()}
    test.append(row)
    if row["prefix"]>=2 or row["level"]>=3:
     hits.append(row)
     print("L3_TWO_COLOR_MACRO_WITNESS",row,flush=True)
  print("L3_MACRO_STAGE2",a,b,"TESTED",len(test),"HITS",len(hits),
        "CALLS",calls,"S",round(time.monotonic()-t0,1),flush=True)
out=F/"sk48_l3_native_macro_second_color_ab.json"
out.write_text(json.dumps({"source":"native public SDK, positive-reference-inspired macro",
 "saved_Level3_route_read":False,"seed":SEED,"tested":len(test),
 "two_color_witnesses":hits,"native_calls":calls,"reset_retries":retry,
 "experiments":test},indent=2),encoding="utf-8")
print("L3_MACRO_STAGE2_RESULT","TESTED",len(test),"HITS",len(hits),"SAVED",out,flush=True)
