"""A/B test native RESET acknowledgment after each L2 action."""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import logging,json,numpy as np,hashlib
from pathlib import Path
logging.disable(logging.CRITICAL)
folder=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
l1=json.loads((folder/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
def frame(o):return np.asarray(o.frame[-1],dtype=np.uint8).copy()
def h(a):return hashlib.sha256(a.tobytes()).hexdigest()
rows=[]
for action in (1,2,3,4,7):
 env=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for z in l1:enter=env.step(GameAction.from_id(z),data={})
 start=frame(enter)
 probed=env.step(GameAction.from_id(action),data={})
 ack=0
 for n in range(1,9):
  restarted=env.step(GameAction.RESET,data={})
  if restarted.levels_completed==0:
   ack=n;break
 if ack:
  for z in l1:again=env.step(GameAction.from_id(z),data={})
  exact=np.array_equal(start,frame(again))
  ended=again.levels_completed
 else:
  exact=False;ended=restarted.levels_completed
 item={"action":action,"reset_attempts_required":ack,"restored_identical_entry":bool(exact),
       "levels_after_replay":int(ended),"initial_l2_sha256":h(start)}
 rows.append(item);print("ACK_VERIFICATION",json.dumps(item),flush=True)
p=folder/"sk48_level2_reset_ack_verified.json"
p.write_text(json.dumps({"tests":rows,"all_pass":all(x["restored_identical_entry"] for x in rows)},indent=2),encoding="utf-8")
print("SAVED",p,flush=True)
