"""SK48 native Level2 route-blind next-color search.

Seed is from the new route-blind Level2 search performed today.
No existing saved L2 positive macro/route files are read.
Fresh replays first verify 8->12, then live native A/B expands diverse
suffixes, retaining full paths and observed public connected sequences.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
from _sk48_public_connected_goal import connected_features
from hashlib import sha256
from collections import defaultdict
import json,time,random,logging,numpy as np
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
P1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
base=json.loads((F/"sk48_l2_route_blind_a_b_search_2026-10-08.json").read_text())
SEED=base["second_color_witness"]["p"]
assert SEED and base["second_color_witness"]["prefix"]==2
for check in (0,1):
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for a in P1+SEED:o=e.step(GameAction.from_id(a),data={})
 q=connected_features(frame(o))
 assert o.levels_completed==1 and q["connected_prefix"]>=2
 print("ROUTE_BLIND_SEED_REPLAY",check,"PREFIX",q["connected_prefix"],
       "NATIVE_FRAME",sha256(frame(o).tobytes()).hexdigest(),flush=True)
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;reset_retry=0;root_hash=None;rng=random.Random(4811)
def action(z):
 global calls
 o=g.step(z,data={});calls+=1;return o
def run(p):
 global reset_retry,root_hash
 for n in range(8):
  o=action(GameAction.RESET)
  if o.levels_completed==0:break
  reset_retry+=1
 else:raise RuntimeError("reset not acknowledged")
 for a in P1:
  o=action(GameAction.from_id(a))
  if o.levels_completed>=1:break
 assert o.levels_completed==1
 h=sha256(frame(o).tobytes()).hexdigest()
 if root_hash is None:root_hash=h
 if h!=root_hash:raise RuntimeError("root mismatch")
 for a in p:
  o=action(GameAction.from_id(a))
  if o.levels_completed>=2:break
 return o
def observe(o,p):
 a=frame(o);f=connected_features(a)
 goal=f["reference"]
 k=f["connected_prefix"]
 h=f["controls"][0] if f["controls"] else (5,42,6)
 y=h[1]
 wanted=int(goal[k]) if k<len(goal) else int(goal[-1])
 ys,xs=np.where(a[:53,:]==wanted)
 tx=int(xs.min()) if len(xs) else 48
 ty=int(ys.min()) if len(ys) else 13
 occupied=np.where(np.isin(a[y+2,11:55],(1,2)))[0]
 tip=int(occupied.max()+11) if len(occupied) else 17
 closeness=(abs((ty-1)-y)+abs(tx-tip))/6
 # Goal relation lexicographic; penalty is a soft tie-breaker only.
 sc=k*1000-10*closeness+0.25*len(p)
 return {"p":p,"prefix":k,"goal":list(goal),"next":wanted,
   "x_y_target":[tx,ty],"head_y":y,"tip":tip,
   "score":round(sc,3),"hash":sha256(a.tobytes()).hexdigest(),
   "levels":int(o.levels_completed)}
def pick(items,width=64):
 # One path per observable shape + phase/historical relation bucket.
 unique={}
 for it in items:
  k=(it["hash"],tuple(it["p"][-3:]),len(it["p"])%4)
  unique.setdefault(k,it)
 ranked=sorted(unique.values(),key=lambda x:(-x["score"],rng.random()))
 kept=ranked[:width//2]
 rest=ranked[width//2:]
 if len(rest)>width-len(kept):
  # Keep low-rank alternatives as potential necessary retracts.
  rest=rng.sample(rest,width-len(kept))
 kept+=rest
 return kept
OUT=F/"sk48_l2_route_blind_third_color_2026-10-08.json"
start=time.monotonic()
root=run(SEED);parent=observe(root,list(SEED))
print("ROUTE_BLIND_STAGE3_ROOT",parent,flush=True)
front=[parent];milestones=[];found=[];best=parent;depth_finished=0
for dep in range(1,14):
 children=[];first_hits=0
 for i,state in enumerate(front):
  for z in (1,2,3,4):
   path=state["p"]+[z]
   r=run(path);node=observe(r,path)
   if node["score"]>best["score"]:best=node
   if node["prefix"]>=3 or node["levels"]>=2:
    found.append(node);print("ROUTE_BLIND_THIRD_COLOR",node,flush=True);break
   if r.state.name!="GAME_OVER":children.append(node)
  if found:break
 if found:break
 front=pick(children)
 depth_finished=dep
 rec={"extra_depth":dep,"children":len(children),"retained":len(front),
   "highest_prefix":max((x["prefix"] for x in children),default=0),
   "native_actions_including_replay":calls,
   "elapsed_s":round(time.monotonic()-start,2)}
 milestones.append(rec)
 print("ROUTE_BLIND_STAGE3",rec,flush=True)
 if not front or calls>65000 or time.monotonic()-start>67:break
result={"source":"route-blind public-native A/B continuation from newly generated second-color witness",
 "prior_saved_positive_l2_read":False,"prior_seed_partial_route_read":False,
 "native_third_color_found":bool(found),"seed":SEED,
 "first_third_color":found[0] if found else None,
 "best_observed":best,"milestones":milestones,
 "native_calls":calls,"reset_retries":reset_retry,
 "elapsed_seconds":round(time.monotonic()-start,2)}
OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
print("ROUTE_BLIND_STAGE3_RESULT",bool(found),"CALLS",calls,"SAVED",OUT,flush=True)
