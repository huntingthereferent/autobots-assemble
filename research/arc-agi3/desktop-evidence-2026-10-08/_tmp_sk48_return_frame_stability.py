from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from pathlib import Path
import json,numpy as np,hashlib,logging
logging.disable(logging.CRITICAL)
route=json.loads(Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
game=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def key(o):
 return (int(o.levels_completed),o.state.name,hashlib.sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:18])
def go():
 o=game.step(GameAction.RESET,data={})
 for z in route:o=game.step(GameAction.from_id(z),data={})
 print("INSIDE1",key(o),flush=True)
 print("INSIDE2",key(o),flush=True)
 return o
for trial in range(3):
 obj=go()
 print("OUTSIDE1",key(obj),"GAME",key(game.observation_space),flush=True)
 print("OUTSIDE2",key(obj),"GAME",key(game.observation_space),flush=True)
