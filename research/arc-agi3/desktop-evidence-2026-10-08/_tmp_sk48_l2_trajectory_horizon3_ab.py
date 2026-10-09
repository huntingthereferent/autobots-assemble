"""SK48 A/B horizon three uses full native trace, not terminal frame only."""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from itertools import product
from hashlib import sha256
from collections import defaultdict,Counter
import json,numpy as np,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
groups={0:[(),()],1:[(1,),(3,)],2:[(1,1),(2,4)],
        3:[(1,1,1),(2,3,1)]}
def state(o):
 return f"{o.levels_completed}:{o.state.name}:"+sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:18]
root=None
def enter(hist):
 global root
 for i in range(8):
  o=g.step(GameAction.RESET,data={})
  if o.levels_completed==0:break
 else:raise RuntimeError("RESET ack wall")
 for z in L1:o=g.step(GameAction.from_id(z),data={})
 if root is None:root=state(o)
 if state(o)!=root:raise RuntimeError("Level 2 entry drift")
 for z in hist:
  g.step(GameAction.from_id(z),data={})
  o=g.step(GameAction.ACTION7,data={})
  if state(o)!=root:raise RuntimeError("no public return from undo")
 return o
summary=Counter();bad=[];examples={};start=time.monotonic()
for index,suffix in enumerate(product((1,2,3,4),repeat=3),1):
 traces={}
 for count,histories in groups.items():
  candidates=[]
  for hist in histories:
   enter(hist)
   result=[]
   for z in suffix:
    o=g.step(GameAction.from_id(z),data={})
    result.append(state(o))
   candidates.append(tuple(result))
  if candidates[0]!=candidates[1]:
   bad.append({"suffix":suffix,"count":count,"histories":histories,
               "traces":candidates})
  traces[count]=candidates[0]
 signature_to_phase=defaultdict(list)
 for count,trace in traces.items():signature_to_phase[trace].append(count)
 partition=tuple(sorted(tuple(c) for c in signature_to_phase.values()))
 summary[str(partition)]+=1
 if index in (1,16,32,48,64):
  print("TRAJECTORY_A_B",index,"PARTITION",partition,"BROKEN_SAMECOUNT",len(bad),flush=True)
 examples["".join(map(str,suffix))]={"partition":partition,
                                  "phase_trajectories":traces}
report={"game":"sk48","level":2,"history":"0-3 cycles of ACTIONn,ACTION7",
  "full_horizon3_suffixes":64,"histories_per_count":2,
  "public_root_same":True,
  "partition_counts":dict(summary),"within_count_conflicts":bad,
  "native_public_only":True,"no_game_clone":True,
  "examples":examples,
  "elapsed_seconds":round(time.monotonic()-start,2)}
out=F/"sk48_l2_native_trajectory_horizon3_ab.json"
out.write_text(json.dumps(report,indent=2),encoding="utf-8")
print("NATIVE_TRAJECTORY_RESULT","PARTITIONS",dict(summary),"SAMECOUNT_CONFLICTS",len(bad),"TIME",report["elapsed_seconds"],flush=True)
print("SAVED",out,flush=True)
