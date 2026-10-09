"""SK48 public Level2 A/B stage 3, balanced direction exploration.

Starts at independently acquired two-color state from native next-color
search (not saved Level2 answer). No private game data/copies.
All branch parents must reproduce exact public frame after acknowledged RESET.
Preserves action depth and history to avoid invalid frame-only merges.
"""
from pathlib import Path
from hashlib import sha256
from collections import defaultdict,Counter
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
import numpy as np,json,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
w=json.loads((F/"sk48_l2_native_second_color_ab.json").read_text())["found_witnesses"][0]
SEED=tuple(w["path"])
OUT=F/"sk48_l2_native_third_color_frontier.json"
W=32
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;retries=0;bad=[]
def step(a):
 global calls
 o=g.step(a,data={});calls+=1
 return o
def state(o):return sha256(frame(o).tobytes()).hexdigest()
def enter(path):
 global retries
 for i in range(8):
  o=step(GameAction.RESET)
  if o.levels_completed==0:break
  retries+=1
 else:raise RuntimeError("UNKNOWN: RESET lacked native acknowledgement")
 for z in L1:o=step(GameAction.from_id(z))
 if o.levels_completed!=1:raise RuntimeError("UNKNOWN: replay did not enter L2")
 for z in path:o=step(GameAction.from_id(z))
 return o
def node(o,path):
 t=features(frame(o))
 best=max(t["candidates"],key=lambda r:(r["matched_prefix"],len(r["attached_row"])),default=None)
 p=best["matched_prefix"] if best else 0
 colors=tuple(best["attached_row"]) if best else ()
 y=best["head"][1] if best else 42
 a=frame(o)
 body=int(np.count_nonzero(a[y+2,5:55]==1)) if y+2<64 else 0
 # No reward for extension: contraction is a witnessed essential move.
 score=1000*p+8*len(colors)-4*(len(colors)-p)
 return {"path":list(path),"frame":state(o),"p":p,"colors":list(colors),
         "y":y,"body":body,"score":score,
         "native_level":int(o.levels_completed)}
def choose(cs):
 # Same frame at a different directional depth/history need not mean same future.
 noalias={}
 for c in cs:
  k=(c["frame"],tuple(c["path"][-3:]))
  if k not in noalias:noalias[k]=c
 vals=list(noalias.values())
 by_direction=defaultdict(list)
 for c in vals:by_direction[c["path"][-1]].append(c)
 for z,items in by_direction.items():
  items.sort(key=lambda c:(-c["score"],c["y"],c["body"],c["path"]))
 # Within each action preserve diverse head/length signatures first.
 arranged={}
 for z,items in by_direction.items():
  unique=[];rest=[];signatures=set()
  for c in items:
   signature=(c["p"],tuple(c["colors"]),c["y"],c["body"]//4,
              tuple(c["path"][-3:-1]))
   if signature not in signatures:
    signatures.add(signature);unique.append(c)
   else:rest.append(c)
  arranged[z]=unique+rest
 kept=[];seen_paths=set()
 for i in range(20):
  for z in (1,2,3,4):
   if i<len(arranged.get(z,[])):
    c=arranged[z][i]
    tp=tuple(c["path"])
    if tp not in seen_paths:
     kept.append(c);seen_paths.add(tp)
   if len(kept)>=W:return kept
 return kept
if OUT.exists():
 current=json.loads(OUT.read_text(encoding="utf-8"))
 if current.get("witnesses"):
  print("PRIOR_THIRD_COLOR",current["witnesses"],flush=True);raise SystemExit
 front=current["frontier"];d=current["extra_depth"]
 print("RESUME",d,len(front),flush=True)
else:
 root=enter(SEED);rootf=node(root,SEED)
 assert rootf["p"]>=2,rootf
 current={"seed":list(SEED),"method":"balanced phase-respecting native public A/B",
 "private_engine_reads":False,"saved_L2_action_route_loaded":False,
 "extra_depth":0,"frontier":[rootf],"completed":[],"witnesses":[]}
 front=[rootf];d=0
 print("THIRD_ROOT",rootf,flush=True)
started=time.monotonic()
while d<16:
 cs=[];witnesses=[]
 for parent in front:
  for z in (1,2,3,4):
   o=enter(parent["path"])
   if state(o)!=parent["frame"]:
    bad.append({"path":parent["path"],"expected":parent["frame"],"observed":state(o)})
    raise RuntimeError("UNSAFE parent replay mismatch: "+str(bad[-1]))
   after=step(GameAction.from_id(z))
   c=node(after,parent["path"]+[z])
   if c["p"]>=3 or after.levels_completed>=2:
    witnesses.append(c)
    print("NATIVE_THIRD_COLOR_OR_WIN",c,flush=True)
   elif after.state.name!="GAME_OVER":
    cs.append(c)
 if witnesses:
  current["witnesses"]=witnesses
  current["status"]="native third-color/Level2 witness"
  OUT.write_text(json.dumps(current,indent=2),encoding="utf-8")
  print("STAGE_3_DISCOVERED",len(witnesses),flush=True)
  break
 if not cs:break
 d+=1;front=choose(cs)
 current["extra_depth"]=d;current["frontier"]=front
 record={"extra_depth":d,"tested":len(cs),"retained":len(front),
       "best_prefix":max(c["p"] for c in front),
       "calls_session":calls,"reset_retries_session":retries,
       "seconds":round(time.monotonic()-started,1),
       "examples":[{"path":x["path"],"p":x["p"],"seq":x["colors"],"y":x["y"]}
                    for x in front[:4]]}
 current["completed"].append(record)
 OUT.write_text(json.dumps(current,indent=2),encoding="utf-8")
 print("THIRD_A_B",record,flush=True)
 if time.monotonic()-started>=43:
  print("BOUNDED_STAGE_CHECKPOINT",d,calls,flush=True);break
print("STAGE_3_RESULT","DEPTH",d,"FOUND",len(current["witnesses"]),
      "CALLS",calls,"REPLAY_BREAKS",len(bad),"SAVED",OUT,flush=True)
