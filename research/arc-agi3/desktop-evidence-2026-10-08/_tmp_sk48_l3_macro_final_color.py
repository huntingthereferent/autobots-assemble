"""SK48 Level3 public-native A/B final color macro.
Reference-assisted macro hypothesis only, no stored Level3 route read.
Native completion levels_completed>=3 is final oracle.
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
L2=min((v for v in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
 if v["passed"] and v["different_from_saved_reference"]),key=lambda v:len(v["L2_actions"]))["L2_actions"]
infile=json.loads((F/"sk48_l3_native_macro_third_color_ab.json").read_text())
pivots=[];seen=set()
for w in infile["third_color_witnesses"]:
 if w["hash"] not in seen:
  seen.add(w["hash"]);pivots.append(w)
P=pivots[:3]
print("FINAL_COLOR_PIVOTS",[(len(p["path"]),p["macro"]) for p in P],flush=True)
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48");calls=0;extra=0
def step(z):
 global calls
 o=g.step(z,data={});calls+=1;return o
def native(path):
 global extra
 for t in range(8):
  o=step(GameAction.RESET)
  if o.levels_completed==0:break
  extra+=1
 else:raise RuntimeError("native reset not acknowledged")
 for z in L1+L2+path:o=step(GameAction.from_id(z))
 return o
allruns=[];fourth=[];wins=[];t0=time.monotonic()
for j,pivot in enumerate(P):
 assert connected_features(frame(native(pivot["path"])))["connected_prefix"]>=3
 for d in (2,3,4):
  for l in (1,2,3):
   for u in (3,4,5):
    for r in (1,2,3):
     suffix=[2]*d+[3]*l+[1]*u+[4]*r
     route=pivot["path"]+suffix
     o=native(route);f=connected_features(frame(o))
     n=int(o.levels_completed)
     row={"pivot":j,"macro":[d,l,u,r],"suffix":suffix,
          "route":route,"connected_prefix":f["connected_prefix"],
          "native_levels_completed":n,"native_sha":sha256(frame(o).tobytes()).hexdigest()}
     allruns.append(row)
     if f["connected_prefix"]>=4 or n>=3:
      fourth.append(row)
      print("L3_FOURTH_NATIVE",{"p":j,"macro":row["macro"],"len":len(route),
        "prefix":row["connected_prefix"],"levels":n},flush=True)
     if n>=3:
      wins.append(row)
      print("L3_NATIVE_LEVEL4_ENTRY",{"pivot":j,"macro":row["macro"],"actions":len(route)},flush=True)
  print("L3_FINAL_PIVOT",j,"DOWN",d,"TESTS",len(allruns),"CONNECTED",len(fourth),
        "NATIVE_WINS",len(wins),"SEC",round(time.monotonic()-t0,1),flush=True)
 if len(wins)>=12:break
out=F/"sk48_l3_native_macro_final_color_ab.json"
out.write_text(json.dumps({"game":"sk48","purpose":"reference-assisted macro variants",
 "saved_Level3_route_loaded":False,"native_tests":len(allruns),
 "fourth_color_matches":fourth,"native_Level3_wins":wins,
 "native_calls":calls,"reset_retry":extra,"tests":allruns},indent=2),encoding="utf-8")
print("L3_MACRO_FINAL","NATIVE_WINS",len(wins),"TESTED",len(allruns),
      "SAVED",out,flush=True)
