from __future__ import annotations
from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from pathlib import Path
import numpy as np, collections
script=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\_tmp_sk48_complete_replay.py").read_text()
ns={}
exec(script.split("for trial in (0,1):")[0],ns)
prefix=ns["prefix"]; P6=ns["P6"]
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
r=e.observation_space
for i,z in enumerate(prefix+P6[:4]):
 r=e.step(GameAction.from_id(z), data={})
print("LEVEL",r.levels_completed,"STATUS",r.state.name,"ACTIONS",len(prefix)+4,flush=True)
a=np.asarray(r.frame[-1],dtype=np.int16).reshape(64,64)
g=e._game
objects=list(g.xpmcmtbcv.items())
for i,(key,mate) in enumerate(objects):
 print("AUDIT_ONLY",i,"KEY",int(key.x),int(key.y),"MATE",int(mate.x),int(mate.y),"ACTIVE",("key" if key is g.vzvypfsnt else "mate"),flush=True)
print("COLORS",collections.Counter(a.ravel()),flush=True)
chars="0123456789ABCDEF"
print("VISIBLE_ASCII_START",flush=True)
for y in range(64):
 print(f"{y:02d} "+''.join(chars[int(v)] for v in a[y]),flush=True)
print("VISIBLE_ASCII_END",flush=True)
