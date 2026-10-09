"""SK48 L2 cold route-free A/B search from native public observations.

Allowed prior route: independently discovered Level1 entrance ONLY.
Forbidden: saved L2 routes, partial L2 milestone paths, private engine.
The abstract sensor is pre-existing and derived from prior research; this
is ROUTE-BLIND testing, not an untouched-game blind ARC challenge.
Retain full action path to preserve phase and preserve low-score frontier.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame, features
from _sk48_public_connected_goal import connected_features
from hashlib import sha256
from collections import defaultdict
import numpy as np,json,logging,time,random
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
OUT=F/"sk48_l2_route_blind_a_b_search_2026-10-08.json"
rng=random.Random(480508)
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;retries=0;root=None;top=[]
def step(z):
 global calls
 o=e.step(z,data={});calls+=1;return o
def replay(path):
 global retries,root
 for i in range(8):
  o=step(GameAction.RESET)
  if o.levels_completed==0:break
  retries+=1
 else:raise RuntimeError("RESET did not reach root; native UNKNOWN")
 for z in L1:
  o=step(GameAction.from_id(z))
  if o.levels_completed==1:break
 if o.levels_completed!=1:raise RuntimeError("L1 route failed")
 now=sha256(frame(o).tobytes()).hexdigest()
 if root is None:root=now
 if now!=root:raise RuntimeError("Native L2 root diverged")
 for z in path:
  o=step(GameAction.from_id(z))
  if o.levels_completed>=2:break
 return o
def profile(o,path):
 a=frame(o);f=connected_features(a);g=features(a)
 if not g["target"]:raise RuntimeError("Native public target missing")
 seq=max((x["connected_colors"] for x in f["candidates"]),key=len,default=[])
 prefix=f["connected_prefix"]
 xh,yh,_=f["controls"][0]
 tile=g["target"][min(prefix,len(g["target"])-1)]
 yy,xx=np.where(a[:53,:]==tile)
 if len(xx):
  # goal tile starts at its 4x4 pixel native position
  tx,ty=int(xx.min()),int(yy.min())
 else:tx,ty=46,25
 # Head moves by six pixels; 1/2 body marks at row y+2 indicate extents.
 bodypos=np.where(np.isin(a[yh+2,11:55],(1,2)))[0]+11
 tip=int(bodypos.max()) if len(bodypos) else xh+6
 closeness=abs(yh-(ty-1))/6 + abs(tip-tx)/6
 # Choose a genuinely connected color over mere row alignment.
 value=2500*prefix-14*closeness+2*len(seq)
 return {"p":list(path),"score":round(value,2),"prefix":prefix,
         "visible_attached":seq,"aligned":g["best_prefix"],
         "next_color":tile,"next_tile":(tx,ty),
         "head_y":yh,"tip_x":tip,
         "hash":sha256(a.tobytes()).hexdigest(),
         "levels":int(o.levels_completed)}
def diverse(nodes,W=36):
 # Do not equate full frames with native states. Full paths are retained.
 # Keep survivors across head height, number of connected colors and
 # extended/retracted body spans, plus some lower-ranked counterfactuals.
 groups=defaultdict(list)
 for n in nodes:
  key=(n["prefix"],n["head_y"],min(8,n["tip_x"]//6),
       tuple(n["p"][-2:]))
  groups[key].append(n)
 picks=[]
 for grp in groups.values():
  grp.sort(key=lambda n:(-n["score"],len(n["p"])))
  picks.append(grp[0])
 picks.sort(key=lambda n:(-n["score"],rng.random()))
 chosen=picks[:W//2]
 # Diverse later half: sample from remaining across scores.
 remains=picks[W//2:]
 if len(remains)>W-len(chosen):
  remains=rng.sample(remains,W-len(chosen))
 chosen+=remains
 return chosen
clock=time.monotonic()
o=replay([])
r=profile(o,[])
print("COLD_L2_ROOT",r,"GOAL_FROM_NATIVE_FRAME",flush=True)
front=[r];visited=set();records=[];first=[];second=[]
for depth in range(1,19):
 children=[];uniques=set()
 for node in front:
  for z in (1,2,3,4):
   path=node["p"]+[z]
   o=replay(path)
   child=profile(o,path)
   # Key includes history; public image alone is known to be unsafe.
   sig=(child["hash"],tuple(path[-4:]),len(path)%4)
   if sig in uniques:continue
   uniques.add(sig)
   if child["prefix"]>=1 or child["levels"]>=2:
    first.append(child)
    if len(first)<=3 or child["prefix"]>=2:
     print("COLD_L2_PROGRESS",depth,child,flush=True)
   if child["prefix"]>=2 or child["levels"]>=2:
    second.append(child)
    print("COLD_L2_TWO_COLORS",depth,child,flush=True)
    break
   if child["levels"]>=1 and o.state.name!="GAME_OVER":
    children.append(child)
  if second:break
 if second:break
 front=diverse(children)
 rec={"depth":depth,"native_children":len(children),
  "survivors":len(front),"prefix1_seen":len(first),
  "best_native_prefix":max((c["prefix"] for c in children),default=0),
  "native_calls":calls,"seconds":round(time.monotonic()-clock,2)}
 records.append(rec)
 print("COLD_L2_BFS",rec,flush=True)
 if not front or calls>48000 or time.monotonic()-clock>63:
  print("COLD_L2_BOUNDED_STOP",depth,"CALLS",calls,flush=True);break
result={"method":"native-public route-blind, prior visual sensor and L1 reference allowed",
 "saved_L2_solution_loaded":False,"saved_L2_partial_seed_loaded":False,
 "private_game_state_read":False,"blind_unseen_task_claim":False,
 "goal_from_public":list(features(frame(replay([])))["target"]),
 "native_L2_root_sha":root,"record":records,
 "first_color_witness":min(first,key=lambda w:len(w["p"])) if first else None,
 "second_color_witness":min(second,key=lambda w:len(w["p"])) if second else None,
 "native_calls":calls,"reset_retries":retries,
 "elapsed_seconds":round(time.monotonic()-clock,2)}
OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
print("COLD_L2_RESULT","FIRST",bool(first),"SECOND",bool(second),
 "NATIVE_CALLS",calls,"SAVED",OUT,flush=True)
