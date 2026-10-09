"""SK48 delayed reset-history A/B; no private state or copied game."""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import logging,json,hashlib,numpy as np,collections
logging.disable(logging.CRITICAL)
folder=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((folder/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
def picture(o):return np.asarray(o.frame[-1],dtype=np.uint8).copy().reshape(64,64)
def hashpix(a):return hashlib.sha256(a.tobytes()).hexdigest()
def enter_l2(env):
  for z in L1:r=env.step(GameAction.from_id(z),data={})
  assert r.levels_completed==1, ("did not reach L2",r.levels_completed)
  return picture(r)
results=[]
for probe in (None,1,2,3,4,7):
  game=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
  initial_level0=picture(game.observation_space)
  l2_first=enter_l2(game)
  state_after_probe=None
  if probe is not None:
    state_after_probe=game.step(GameAction.from_id(probe),data={})
  reset=game.step(GameAction.RESET,data={})
  initial_after_reset=picture(reset)
  l2_again=enter_l2(game)
  changed=np.where(l2_first!=l2_again)
  area=(int(changed[1].min()),int(changed[0].min()),
        int(changed[1].max()),int(changed[0].max())) if len(changed[0]) else None
  replay={"probe":probe,
      "first_l2_frame":hashpix(l2_first),
      "second_l2_frame":hashpix(l2_again),
      "same_l0_frame_after_reset":bool(np.array_equal(initial_level0,initial_after_reset)),
      "same_l2_frame_after_reentry":bool(np.array_equal(l2_first,l2_again)),
      "changed_l2_pixels":len(changed[0]),"changed_box":area,
      "levels_after_reset":int(reset.levels_completed)}
  results.append(replay)
  print("RESET_HISTORY_AB",json.dumps(replay),flush=True)
p=folder/"sk48_l2_reset_history_ab.json"
p.write_text(json.dumps({"game":"sk48","experiment":"previous level 2 action then native reset and same witnessed level 1 path",
 "used_private_engine":False,"used_clone":False,"results":results},indent=2),encoding="utf-8")
print("SAVED",p,flush=True)
