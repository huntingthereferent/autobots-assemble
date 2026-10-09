from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from pathlib import Path
import json,numpy as np,hashlib,logging
logging.disable(logging.CRITICAL)
route=json.loads(Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
env=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def sig(o):return hashlib.sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:20]
print('INITIAL_LEVEL0',env.observation_space.levels_completed,sig(env.observation_space),flush=True)
for z in route:o=env.step(GameAction.from_id(z),data={})
print("L2_ENTRY",o.levels_completed,o.state.name,sig(o),flush=True)
q=env.step(GameAction.RESET,data={})
print("RESET_ON_L2",q.levels_completed,q.state.name,sig(q),"FRAME_EQUAL",sig(q)==sig(o),flush=True)
m=env.step(GameAction.ACTION1,data={})
print("PROBE",m.levels_completed,m.state.name,sig(m),flush=True)
r=env.step(GameAction.RESET,data={})
print("RESET_AFTER_PROBE",r.levels_completed,r.state.name,sig(r),"EQUAL_L2_ENTRY",sig(r)==sig(o),flush=True)
