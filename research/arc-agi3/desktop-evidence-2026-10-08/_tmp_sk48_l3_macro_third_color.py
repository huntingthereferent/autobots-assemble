"""SK48 Level3 A/B macro family for third ordered color 9.
Reference-assisted operator type; no saved L3 route in this execution.
Each candidate starts at L3 via independently verified L1/L2 routes,
then replays a native two-color witness and tests the next operator.
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
rr=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=min((r for r in rr if r["passed"] and r["different_from_saved_reference"]),key=lambda r:len(r["L2_actions"]))["L2_actions"]
s2=json.loads((F/"sk48_l3_native_macro_second_color_ab.json").read_text())
SEED=s2["seed"];pivots=[];known=set()
for c in s2["two_color_witnesses"]:
 if c["hash"] not in known:
  known.add(c["hash"]);pivots.append(c)
PIVOTS=pivots[:3]
print("THREE_COLOR_PIVOTS",[(p["macro"],p["head"]) for p in PIVOTS],flush=True)
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;retry=0
def step(z):
 global calls
 o=g.step(z,data={});calls+=1;return o
def run(path):
 global retry
 for i in range(8):
  o=step(GameAction.RESET)
  if o.levels_completed==0:break
  retry+=1
 else:raise RuntimeError("RESET not acknowledged")
 for z in L1+L2+path:o=step(GameAction.from_id(z))
 if o.levels_completed<2:raise RuntimeError("L3 not reached")
 return o
records=[];wins=[];begin=time.monotonic()
for k,p in enumerate(PIVOTS):
 pivot=SEED+p["suffix"]
 r=run(pivot)
 assert connected_features(frame(r))["connected_prefix"]>=2
 for a in (1,2):
  for b in (2,3,4,5):
   for c in (2,3,4):
    for d in (1,2,3):
     suffix=[1]*a+[3]*b+[1]*c+[4]*d
     o=run(pivot+suffix)
     q=connected_features(frame(o))
     row={"pivot":k,"macro":[a,b,c,d],"suffix":suffix,
          "path":pivot+suffix,"prefix":q["connected_prefix"],
          "colors":[w["connected_colors"] for w in q["candidates"]],
          "level":int(o.levels_completed),
          "hash":sha256(frame(o).tobytes()).hexdigest()}
     records.append(row)
     if row["prefix"]>=3 or row["level"]>=3:
      wins.append(row)
      print("NATIVE_L3_THIRD_COLOR",row,flush=True)
   if len(records)%36==0:
    print("THIRD_COLOR_PROGRESS",len(records),"HITS",len(wins),
          "CALLS",calls,"SEC",round(time.monotonic()-begin,2),flush=True)
  if len(wins)>=12:break
 if len(wins)>=12:break
out=F/"sk48_l3_native_macro_third_color_ab.json"
out.write_text(json.dumps({"method":"reference-assisted macro operator family",
 "saved_L3_route_used":False,"source_two_color_witnesses":len(PIVOTS),
 "native_tests":len(records),"third_color_witnesses":wins,"tests":records,
 "native_calls":calls,"reset_retries":retry},indent=2),encoding="utf-8")
print("THIRD_COLOR_RESULT",len(wins),"OF",len(records),"SAVED",out,flush=True)
