"""SK48 higher-order A/B closure: depth-2 from visually identical rollback histories.

Native public frames only. Compares representative histories of 0/1/2
rollback cycles with representative 3-cycle histories. Every tested
two-action continuation is executed from a verified reset/replay.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from itertools import product
from hashlib import sha256
from collections import defaultdict
import numpy as np,json,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
game=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def K(o):
 return (int(o.levels_completed),o.state.name,sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:20])
root=None
def enter(hist):
 global root
 for k in range(8):
  obs=game.step(GameAction.RESET,data={})
  if obs.levels_completed==0:break
 else:raise RuntimeError("RESET not acknowledged")
 for z in L1:obs=game.step(GameAction.from_id(z),data={})
 if root is None:root=K(obs)
 if K(obs)!=root:raise RuntimeError("L2 replay drift")
 for z in hist:
  game.step(GameAction.from_id(z),data={})
  obs=game.step(GameAction.ACTION7,data={})
  if K(obs)!=root:raise RuntimeError(("ROLLBACK_NOT_VISIBLE_PARENT",hist,z,K(obs)))
 return obs
classes={"phase_0_2":[(),(1,),(2,),(4,),(1,1),(2,2),(1,2),(2,1)],
         "phase_3":[(1,2,3),(3,2,1),(1,1,1),(2,2,2),(3,3,3),(4,4,4),(2,4,1)]}
summary={};start=time.monotonic()
for family,histories in classes.items():
 outputs=defaultdict(list)
 for idx,(x,y) in enumerate(product((1,2,3,4),repeat=2)):
  binmap=defaultdict(list)
  for hist in histories:
   enter(hist)
   first=game.step(GameAction.from_id(x),data={})
   last=game.step(GameAction.from_id(y),data={})
   binmap[K(last)].append(list(hist))
  outputs[str(x)+str(y)]=[{"signature":k,"size":len(v),"histories":v} for k,v in binmap.items()]
  if len(binmap)>1:
   print("AB_HORIZON2_BREAK",family,(x,y),"CLASSES",len(binmap),flush=True)
 equality=sum(len(v)==1 for v in outputs.values())
 summary[family]={"histories":len(histories),"depth2_suffixes_tested":16,
                   "equal_suffixes":equality,
                   "split_suffixes":[k for k,v in outputs.items() if len(v)>1],
                   "continuations":outputs}
 print("PHASE2_CONTINUATION",family,"HISTORIES",len(histories),
       "CLOSED_SUFFIXES",equality,"OF",16,"SECONDS",round(time.monotonic()-start,1),flush=True)
all_closed=all(v["equal_suffixes"]==16 for v in summary.values())
ref0=[group["signature"] for group in summary["phase_0_2"]["continuations"]["11"]]
ref3=[group["signature"] for group in summary["phase_3"]["continuations"]["11"]]
result={"experiment":"SK48 Level2 public A/B two-step continuation",
        "no_private_engine":True,"no_clone":True,
        "all_within_phase_closed":all_closed,
        "phase_0_vs_phase_3_distinct_after_11":ref0!=ref3,
        "summary":summary}
out=F/"sk48_l2_undo_phase_horizon2_ab.json"
out.write_text(json.dumps(result,indent=2),encoding="utf-8")
print("RESULT",json.dumps({k:v for k,v in result.items() if k!="summary"}),flush=True)
print("SAVED",out,flush=True)
