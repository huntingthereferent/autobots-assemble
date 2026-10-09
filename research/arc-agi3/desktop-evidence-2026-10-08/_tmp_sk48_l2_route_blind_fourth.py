"""SK48 route-blind Level2 final-color native A/B search.

Reads ONLY earlier cold route-blind third-color witness, independent
Level1 entrance path, and public native frame. No saved successful L2
history or previous Level2 macro checkpoint read. Prior sensor/heuristic
knowledge means this is NOT an entirely unseen-task blind challenge.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
from _sk48_public_connected_goal import connected_features
from hashlib import sha256
import numpy as np,json,logging,random,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
P1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
seedfile=json.loads((F/"sk48_l2_route_blind_third_color_2026-10-08.json").read_text())
SEED=seedfile["first_third_color"]["p"]
assert SEED and seedfile["first_third_color"]["prefix"]==3
for rep in range(2):
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for a in P1+SEED:o=e.step(GameAction.from_id(a),data={})
 ft=connected_features(frame(o))
 assert int(o.levels_completed)==1 and ft["connected_prefix"]>=3
 print("ROUTE_BLIND_THIRD_SEED_FRESH",rep,"PREFIX",ft["connected_prefix"],flush=True)
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
rng=random.Random(480812);calls=0;retries=0;parent_sha=None
def action(z):
 global calls
 o=g.step(z,data={});calls+=1;return o
def replay(path):
 global retries,parent_sha
 for i in range(8):
  o=action(GameAction.RESET)
  if o.levels_completed==0:break
  retries+=1
 else:raise RuntimeError("native reset acknowledgment UNKNOWN")
 for a in P1:
  o=action(GameAction.from_id(a))
  if o.levels_completed>=1:break
 assert o.levels_completed==1
 h=sha256(frame(o).tobytes()).hexdigest()
 if parent_sha is None:parent_sha=h
 if h!=parent_sha:raise RuntimeError("L2 root hash mismatch")
 for a in path:
  o=action(GameAction.from_id(a))
  if o.levels_completed>=2:break
 return o
def inspect(o,p):
 a=frame(o);fit=connected_features(a);t=fit["reference"]
 k=fit["connected_prefix"]
 if o.levels_completed>=2:
  return {"p":p,"prefix":4,"actual_completion":True,
          "native_level":int(o.levels_completed),
          "score":99999,"sha":sha256(a.tobytes()).hexdigest()}
 h=fit["controls"][0];y=h[1]
 target=t[min(k,len(t)-1)]
 ys,xs=np.where(a[:53,:]==target)
 tx=int(xs.min()) if len(xs) else 36
 ty=int(ys.min()) if len(ys) else 13
 body=np.where(np.isin(a[y+2,11:55],(1,2)))[0]
 tip=int(body.max()+11) if len(body) else 17
 neardist=(abs(y-(ty-1))+abs(tip-tx))/6
 return {"p":p,"prefix":k,"actual_completion":False,
  "head_y":y,"tip_x":tip,"next_color":int(target),
  "target_xy":[tx,ty],
  "native_level":int(o.levels_completed),
  "score":round(1300*k-14*neardist+0.3*len(p),2),
  "sha":sha256(a.tobytes()).hexdigest()}
def select(candidates,width=70):
 # Full parent path always carried, never merge only by public frame.
 aliases={}
 for c in candidates:
  k=(c["sha"],tuple(c["p"][-4:]),len(c["p"])%4)
  if k not in aliases:aliases[k]=c
 ranking=sorted(aliases.values(),key=lambda c:(-c["score"],rng.random()))
 elite=ranking[:width//2];remaining=ranking[width//2:]
 if len(remaining)>width-len(elite):
  remaining=rng.sample(remaining,width-len(elite))
 return elite+remaining
start=time.monotonic();witness=[];stages=[]
root=replay(SEED)
print("ROUTE_BLIND_FOURTH_ROOT",inspect(root,SEED),flush=True)
front=[inspect(root,SEED)]
for depth in range(1,13):
 children=[];best=None
 for node in front:
  for z in (1,2,3,4):
   p=node["p"]+[z]
   o=replay(p);child=inspect(o,p)
   if best is None or child["score"]>best["score"]:best=child
   if child["prefix"]>=4:
    witness.append(child)
    print("ROUTE_BLIND_FOURTH_WITNESS",child,flush=True)
    break
   if o.state.name!="GAME_OVER":children.append(child)
  if witness:break
 if witness:break
 front=select(children)
 state={"extra_depth":depth,"branch_count":len(children),
  "retained_count":len(front),"best_prefix":best["prefix"] if best else 0,
  "native_calls":calls,"elapsed":round(time.monotonic()-start,2)}
 stages.append(state)
 print("ROUTE_BLIND_FOURTH_DEPTH",state,flush=True)
 if not front or calls>82000 or time.monotonic()-start>72:break
out=F/"sk48_l2_route_blind_fourth_color_2026-10-08.json"
result={"purpose":"cold route-blind final Level2 goal, phase-preserving native A/B",
 "allowed_inputs":"Level1 entrance, current-run route-blind Level2 partial third-color witness",
 "saved_L2_solution_loaded":False,"saved_L2_macro_loaded":False,
 "actual_native_Level2_completion":any(w["actual_completion"] for w in witness),
 "witness":witness[0] if witness else None,
 "initial_seed":SEED,"search_trace":stages,"calls":calls,
 "reset_retries":retries,"elapsed_seconds":round(time.monotonic()-start,2)}
out.write_text(json.dumps(result,indent=2),encoding="utf-8")
print("ROUTE_BLIND_FOURTH_DONE",len(witness),
  "NATIVE_COMPLETED",result["actual_native_Level2_completion"],
  "NATIVE_CALLS",calls,"SAVED",out,flush=True)
