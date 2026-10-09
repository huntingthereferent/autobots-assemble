"""SK48 Level2 goal-relation beam (public-native observations, no saved L2 route).

The target is read from native bottom visual legend. Progress is ordered colors
attached to visible control. A/B retains action depth and last 3 actions beside
frame: false frame-only merges are forbidden. Branches replay from native RESET.
This is reference-assisted hypothesis design, not blind independent discovery.
"""
from pathlib import Path
from hashlib import sha256
from collections import defaultdict,Counter
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
import json,time,logging,numpy as np
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
OUT=F/"sk48_l2_goal_relation_beam_checkpoint.json"
W=24
arcade=Arcade(operation_mode=OperationMode.NORMAL)
game=arcade.make("sk48")
calls=0;retries=0;replay_mismatches=[]
def action(a):
 global calls
 o=game.step(a,data={});calls+=1
 return o
def kh(o):return sha256(frame(o).tobytes()).hexdigest()
def enter(path):
 global retries
 for i in range(8):
  o=action(GameAction.RESET)
  if o.levels_completed==0:break
  retries+=1
 else:raise RuntimeError("UNKNOWN: unacknowledged native reset")
 for z in L1:o=action(GameAction.from_id(z))
 if o.levels_completed!=1:raise RuntimeError("UNKNOWN: L1 no longer reaches L2")
 for z in path:o=action(GameAction.from_id(z))
 return o
def evaluate(o,path):
 ft=features(frame(o))
 target=ft["target"]
 best=max(ft["candidates"],key=lambda q:(q["matched_prefix"],len(q["attached_row"])),default=None)
 prefix=(best["matched_prefix"] if best else 0)
 seq=(best["attached_row"] if best else ())
 head=(best["head"] if best else (0,42,0))
 hd_y=head[1]
 body=int(np.count_nonzero(frame(o)[hd_y+2,5:55]==1)) if hd_y+2<64 else 0
 score=1000*prefix+12*len(seq)-5*max(len(seq)-prefix,0)-.18*abs(hd_y-18)+.3*body
 # Preserve possibilities with different lengths and head position in A/B.
 grp=(prefix,hd_y,tuple(seq[:4]),min(6,body//6))
 return {"path":path,"frame":kh(o),"score":round(score,2),
         "prefix":prefix,"seq":list(seq),"head_y":hd_y,"body":body,
         "group":str(grp),"target":list(target),
         "native_level":int(o.levels_completed)}
def select(children):
 byhash={}
 for c in children:
  # Same pixel hash at different action histories does NOT prove equivalent.
  alias=(c["frame"],tuple(c["path"][-3:]))
  if alias not in byhash or c["score"]>byhash[alias]["score"]:byhash[alias]=c
 ordered=sorted(byhash.values(),key=lambda c:(-c["score"],-c["prefix"],c["path"]))
 result=[];bygrp=Counter()
 for c in ordered:
  if bygrp[c["group"]]>=3:continue
  result.append(c);bygrp[c["group"]]+=1
  if len(result)==W:break
 if len(result)<W:
  already={id(v) for v in result}
  for c in ordered:
   if id(c) in already:continue
   result.append(c)
   if len(result)>=W:break
 return result
if OUT.exists():
 state=json.loads(OUT.read_text(encoding="utf-8"))
 if state.get("solution"):
  print("PRIOR_SOLVE",state["solution"],flush=True);raise SystemExit
 front=state["frontier"];depth=state["depth"]
 print("RESUME_DEPTH",depth,"FRONTIER",len(front),"BEST",max(c["score"] for c in front),flush=True)
else:
 root=enter(())
 root_c=evaluate(root,[])
 state={"method":"single SDK instance native resets, public visual ordering",
        "uses_saved_Level2_route":False,"used_private_engine":False,
        "depth":0,"frontier":[root_c],"milestones":[],
        "solution":None,"last_result":"open"}
 front=[root_c];depth=0
 print("ROOT_SENSOR",root_c,flush=True)
clock=time.monotonic()
while depth<35:
 candidates=[];failed=0
 for idx,node in enumerate(front):
  parent=node["path"]
  for z in (1,2,3,4):
   o=enter(parent)
   if kh(o)!=node["frame"]:
    mismatch={"at_depth":depth,"path":parent,"expected":node["frame"],"native":kh(o)}
    replay_mismatches.append(mismatch)
    state["last_result"]="UNKNOWN replay mismatch"
    OUT.write_text(json.dumps(state,indent=2),encoding="utf-8")
    raise RuntimeError(str(mismatch))
   after=action(GameAction.from_id(z))
   child=evaluate(after,parent+[z])
   if after.levels_completed>=2:
    state["solution"]={"path":child["path"],"native_completed":int(after.levels_completed),
      "action_count":len(child["path"]),"source":"native public action and frame"}
    state["last_result"]="native L2 completion"
    OUT.write_text(json.dumps(state,indent=2),encoding="utf-8")
    print("NATIVE_L2_NEW_ROUTE",state["solution"],"NATIVE_CALLS",calls,flush=True)
    raise SystemExit
   if after.state.name=="GAME_OVER":
    failed+=1;continue
   candidates.append(child)
  if idx%10==0 and time.monotonic()-clock>85:
   # Do not save partial frontier as a completed depth.
   print("RESOURCE_WALL_PARTIAL",depth,len(candidates),"OF",len(front)*4,flush=True)
   state["last_result"]="UNKNOWN interrupted within depth"
   OUT.write_text(json.dumps(state,indent=2),encoding="utf-8")
   raise SystemExit
 if not candidates:break
 front=select(candidates)
 depth+=1
 state["depth"]=depth;state["frontier"]=front
 record={"depth":depth,"expanded":len(candidates),"retained":len(front),
         "max_prefix":max(c["prefix"] for c in candidates),
         "best_score":max(c["score"] for c in front),
         "native_calls_session":calls,"reset_retries_session":retries,
         "seconds":round(time.monotonic()-clock,1),
         "top_paths":[{"p":c["path"],"prefix":c["prefix"],"head_y":c["head_y"],
                       "seq":c["seq"]} for c in front[:3]]}
 state["milestones"].append(record)
 OUT.write_text(json.dumps(state,indent=2),encoding="utf-8")
 print("GOAL_BEAM",record,flush=True)
 if time.monotonic()-clock>42:
  print("BOUNDED_CHECKPOINT",depth,"NATIVE_CALLS",calls,flush=True)
  break
print("SESSION_RESULT","DEPTH",depth,"FRONTIER",len(front),
      "BEST_PREFIX",max(c["prefix"] for c in front),
      "NATIVE_CALLS",calls,"REPLAY_MISMATCHES",len(replay_mismatches),flush=True)
