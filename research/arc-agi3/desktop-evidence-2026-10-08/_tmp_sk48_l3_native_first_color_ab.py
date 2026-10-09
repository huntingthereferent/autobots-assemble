"""SK48 Level 3 native A/B geometry and first-color movement operators.

Public SDK frames only. L1 is the independently discovered native route.
L2 uses fresh-verified alternative, NOT saved old Level 2 route.
No private game state or environment clones.
"""
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np, json, logging, hashlib, time
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
r=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=min((x for x in r if x["passed"] and x["different_from_saved_reference"]),key=lambda x:len(x["L2_actions"]))["L2_actions"]
def fresh():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for a in L1+L2:o=e.step(GameAction.from_id(a),data={})
 assert o.levels_completed==2,o.levels_completed
 return e,o
e,root=fresh();a=frame(root)
print("NATIVE_LEVEL3_ENTRY","L1_LEN",len(L1),"L2_ALT_LEN",len(L2),
      "TARGET",features(a)["target"],flush=True)
for color in (8,9,12,14,11):
 ys,xs=np.where(a[:53,:]==color)
 print("PLAYFIELD_COLOR",color,"PIXELS",len(xs),"BBOX",
       [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None,flush=True)
 if color==11:print("COLOR11_POINTS",list(zip(xs.tolist(),ys.tolist())),flush=True)
records=[];beg=time.monotonic()
# Mutually contrasting runs, always new SDK instance. No saved L3 routes.
programs=[]
for rr in range(1,8):
 for uu in range(1,8):
  programs.append(("R_then_U",rr,uu,[4]*rr+[1]*uu))
  programs.append(("U_then_R",rr,uu,[1]*uu+[4]*rr))
for kind,rr,uu,seq in programs:
 e,o=fresh();before=frame(o).copy()
 for k,z in enumerate(seq,1):
  o=e.step(GameAction.from_id(z),data={})
  f=features(frame(o))
  if f["best_prefix"]>=1 or o.levels_completed>=3:break
 f=features(frame(o));arr=frame(o)
 rec={"family":kind,"R":rr,"U":uu,"path":seq[:k],
      "actions_executed":k,"matched":f["best_prefix"],
      "colors":[c["attached_row"] for c in f["candidates"]],
      "head":f["heads"],"level":int(o.levels_completed),
      "frame":hashlib.sha256(arr.tobytes()).hexdigest()}
 records.append(rec)
 if rec["matched"]>=1 or rec["level"]>=3:
  print("L3_COLOR8_WITNESS",rec,flush=True)
print("L3_SEARCH_SUMMARY","TESTED",len(records),"POSITIVE",
       sum(x["matched"]>=1 for x in records),"LEVEL3_WINS",
       sum(x["level"]>=3 for x in records),"SEC",round(time.monotonic()-beg,2),flush=True)
out=F/"sk48_l3_native_geometry_and_first_color_ab.json"
out.write_text(json.dumps({"level":3,"source":"native public SDK",
 "input_L2":"fresh-verified alternative route",
 "saved_L3_route_read":False,"geometry":{"reference":list(features(a)["target"])},
 "search":records},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
